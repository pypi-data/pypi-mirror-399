# geo_tier_engine.py
"""Provides the core logic for tiering and spatial decluttering.

This module contains the `GeoTierEngine`, which is responsible for assigning each
scored item to a final output tier. Its goal is to produce a "map-ready" set of
tiers that are both thematically coherent and spatially decluttered, ensuring that
a map shows the most important items without visual overlap at appropriate zoom
levels.

### The Greedy Placement Algorithm

The engine uses a **greedy, iterative, top-down algorithm**. The core principle is
that **once an item is placed in a tier, it cannot be displaced by a
lower-scoring item.** This guarantees that the most important features are always
preserved on the map.

This greedy approach  produces a correct and stable result because
of two fundamental preconditions:

1.  **Data is Processed by Score Order:** The  dataset is sorted by the importance
    score  at the beginning of the process.
2.  **Tiers are processed from Most Restrictive to Least :** The engine
    sorts the tiers to ensure the most restrictive (highest score
    threshold, largest separation) are processed first.

The process for each tier follows a pipeline:

Preparation
1.  **Data Preparation:** Input data is loaded, projected to a meter-based CRS
    (e.g., World Mercator) for  distance calculations, and sorted by
    score.
2. **Tier Preparation:** Tiers are sorted from Most Restrictive to Least

Processing
1.  **Threshold Check:** The engine identifies unassigned items meeting
    the current tier's score rules.
2.  **Separation Check:** Candidates are checked against the spatial index of
    already placed items. If the candidate is not too close to an already placed item
    it's added to the spatial index and assigned the tier ID, otherwise it simply
    remains in the unassigned list.
3.  The process repeats for the next tier.

To make this process computationally efficient, the engine uses an R-tree for fast
spatial queries.
"""

import logging
from typing import Any

import geopandas as gpd
import numpy as np
import pandas as pd

from GeoTier.geo_tier_config import GeoTierConfig
from GeoTier.spatial_index import SpatialIndex

# Use a projected CRS for accurate distance calculations in meters.
PROJECTED_CRS = "EPSG:3395"


class GeoTierEngine:
    """Applies score based and spatial tiering to a scored dataset.

    This is the primary service class for the GeoTier library. It orchestrates
    the entire workflow of transforming a  list of scored points into a
    map-ready dataset with two distinct tier assignments:

    *   An **`output_score_tier_column`**  based purely on score.
    *   An **`output_resolved_tier_column`** for visibility filtering, which
        guarantees that all features within the same tier are separated by the configured distance.

    The engine is configured via a `GeoTier Config` file and operates on a
    pandas DataFrame.

    Attributes:
        config (GeoTierConfig): The validated configuration object.
        logger (logging.Logger): The logger instance used for progress messages.
        gdf (gpd.GeoDataFrame): The internal GeoDataFrame for scorable items.
        gdf_ignored (gpd.GeoDataFrame): The internal GeoDataFrame for ignored items.
        stats (list[dict[str, Any]]): A list of dictionaries containing detailed
            statistics from the most recent `classify` run.
    """

    def __init__(self, config: GeoTierConfig, logger: logging.Logger):
        self.config = config
        self.default_tier_id = self.config.default_tier_id
        self.method = self.config.classification
        self.logger = logger
        self.gdf: gpd.GeoDataFrame = None
        self.gdf_ignored: gpd.GeoDataFrame = None
        self.stats: list[dict[str, Any]] = []
        self.idx = 0
        self.score_thresholds: dict[str, float] = {}
        # Convert to a set for fast lookups
        # self.debug_ids = set(config.get('debug_ids', []))
        self.debug_ids = set([6538201028, -6746883])

    def classify(self, scored_dataframe: pd.DataFrame) -> pd.DataFrame:
        """Executes the tiering and (optional) spatial decluttering pipeline."""
        self._prepare_data(scored_dataframe)

        # This always runs, populating the raw score-based tier column
        self._set_score_tier()

        # Use .get() with a default for safety, though the schema should provide one.
        if self.config.get('spatial_separation', True):
            self.logger.info("\n➡️ Starting spatial separation process...")
            sorted_tiers = self._sort_and_validate_tiers()
            spatial_index = SpatialIndex(
                approximate_distance=self.config.approximate_distance, debug_ids=self.debug_ids,
                logger=self.logger
                )

            # The existing spatial processing loop
            for tier_rules in sorted_tiers:
                # NOTE: _process_placement_tier is  only used for spatial placement
                self._process_placement_tier(tier_rules, spatial_index)
        else:
            self.logger.info("\n➡️ Spatial separation is disabled.")
            self.logger.info(
                f"   - Final tier column '{self.config.output_tier_column}' will be a copy of the "
                f"score-based tier."
                )

            # If no separation, the final placement tier is simply the raw score tier.
            if not self.gdf.empty:
                self.gdf[self.config.output_tier_column] = self.gdf[
                    self.config.output_raw_tier_column]

        return self._finalize_results()

    def _prepare_data(self, scored_dataframe: pd.DataFrame) -> None:
        """
        Handles data cleaning, projection, sorting, and pre-calculating
        all necessary score thresholds.
        """
        self.logger.info("➡️ Preparing data for classification...")
        initial_rows = len(scored_dataframe)
        id_col = self.config.id_column
        removed_debug_ids = set()

        if self.config.get('spatial_separation', True):
            if 'lat' not in scored_dataframe.columns or 'lon' not in scored_dataframe.columns:
                raise ValueError(
                    "Input CSV must contain 'lat' and 'lon' columns when spatial_separation is enabled."
                    )

            # 1. Create the boolean mask to identify valid rows
            valid_coords_mask = (
                        scored_dataframe['lat'].notna() & scored_dataframe['lon'].notna() & (
                            scored_dataframe['lat'] != 0))

            # 2. Check if there are any invalid rows to report on
            if not valid_coords_mask.all():
                # Invert the mask to select the *invalid* rows
                invalid_rows_df = scored_dataframe[~valid_coords_mask]
                num_invalid = len(invalid_rows_df)

                # Log the summary warning
                self.logger.warning(
                    f"   - ⚠️  Found {num_invalid} rows with invalid coordinates. These rows will be removed."
                    )

                """                if self.debug_ids:
                    invalid_ids = set(invalid_rows_df[id_col])
                    debug_ids_in_invalid = self.debug_ids.intersection(invalid_ids)
                    if debug_ids_in_invalid:
                        self.logger.error(
                            f"   - ❌ DEBUG: The following debug IDs were REMOVED due to invalid coordinates: "
                            f"{list(debug_ids_in_invalid)}"
                            )
                        removed_debug_ids.update(debug_ids_in_invalid)

                # Log a sample of the first invalid rows for debugging
                self.logger.warning("     --- Sample of invalid rows ---")
                log_columns = ['osm_id', 'lat', 'lon', 'score', 'item_name']
                existing_log_columns = [col for col in log_columns if
                                        col in invalid_rows_df.columns]
                sample_str = invalid_rows_df.head(100)[existing_log_columns].to_string(index=False)
                indented_sample = "\n".join([f"       {line}" for line in sample_str.split('\n')])
                #self.logger.warning(indented_sample)
                self.logger.warning("     ------------------------------")"""
        else:
            valid_coords_mask = pd.Series(True, index=scored_dataframe.index)

        clean_df = scored_dataframe[valid_coords_mask].copy()
        if len(clean_df) < initial_rows:
            self.logger.warning(
            f"   - ⚠️  Removed {initial_rows - len(clean_df)} of {initial_rows} rows due to invalid coordinates."
            )

        if self.config.get('spatial_separation', True):
            gdf = gpd.GeoDataFrame(
                clean_df, geometry=gpd.points_from_xy(clean_df.lon, clean_df.lat), crs="EPSG:4326"
                )
            gdf_proj = gdf.to_crs(PROJECTED_CRS)
        else:
            gdf_proj = clean_df.copy()

        meaningful_mask = gdf_proj[self.config.score_column] > self.config.ignore_scores_below
        self.gdf = gdf_proj[meaningful_mask].copy()
        self.gdf_ignored = gdf_proj[~meaningful_mask].copy()
        if not self.gdf_ignored.empty:
            self.logger.info(
                f"   - Skipping {len(self.gdf_ignored)} items with scores <= {self.config.ignore_scores_below}."
                )

            if self.debug_ids:
                # Check if column exists before accessing
                if id_col in self.gdf_ignored.columns:
                    ignored_ids = set(self.gdf_ignored[id_col])
                    debug_ids_in_ignored = self.debug_ids.intersection(ignored_ids)

                    if debug_ids_in_ignored:
                        self.logger.error(
                            f"   - ❌ DEBUG: The following debug IDs were IGNORED for having a score <= "
                            f"{self.config.ignore_scores_below}: {list(debug_ids_in_ignored)}"
                            )
                        removed_debug_ids.update(debug_ids_in_ignored)
                else:
                    self.logger.warning(
                        f"   - ⚠️ DEBUG SKIPPED: ID column '{id_col}' not found in ignored items dataframe."
                        )

        #if self.debug_ids:
        if True:
            all_processed_ids = set()

            if not self.gdf.empty:
                # Check if column exists before accessing
                if id_col in self.gdf.columns:
                    all_processed_ids = set(self.gdf[id_col])
                else:
                    self.logger.warning(
                        f"   - ⚠️ DEBUG SKIPPED: ID column '{id_col}' not found in processed items dataframe."
                        )

            debug_ids_not_found = self.debug_ids - removed_debug_ids - all_processed_ids

            if debug_ids_not_found:
                self.logger.warning(
                    f"   - ⚠️ DEBUG: The following debug IDs were not found in the dataset at all: "
                    f"{list(debug_ids_not_found)}"
                    )

            if not self.gdf.empty:
                self.gdf.sort_values(by=self.config.score_column, ascending=False, inplace=True)
                self.gdf[self.config.output_tier_column] = self.default_tier_id
                if self.config.output_raw_tier_column:
                    self.gdf[self.config.output_raw_tier_column] = self.default_tier_id

                # Restore the pre-calculation of all score thresholds one time.
                self.logger.debug(f"   - Pre-calculating all score thresholds... Method={self.method}")
                if self.method == 'percentile':
                    all_scores = self.gdf[self.config.score_column].values
                    for tier in self.config.tiers:
                        tier_id = tier['tier_id']
                        percentile = tier['minimum']
                        score_at_percentile = np.percentile(all_scores, percentile)
                        self.score_thresholds[tier_id] = score_at_percentile
                        self.logger.debug(

                                f"     - Tier {tier_id} ({percentile}%): min score = {score_at_percentile:.2f}"
                            )
                else:  # 'score' method
                    for tier in self.config.tiers:
                        self.score_thresholds[tier['tier_id']] = tier['minimum']
            else:
                print("⚠️ WARNING empty gdf")

            self.logger.info("  ✅ Data preparation complete.")

    def _process_placement_tier(self, tier_rules: dict[str, Any], spatial_index) -> None:
        """
        Processes a single tier for SPATIAL PLACEMENT, correctly allowing for
        demotion of rejected items.
        """
        tier_id = tier_rules['tier_id']
        separation_m = tier_rules.get('separation')
        score_threshold = self.score_thresholds[tier_id]
        id_col = self.config.id_column

        unassigned_mask = (self.gdf[self.config.output_tier_column] == self.default_tier_id)
        score_mask = (self.gdf[self.config.score_column] >= score_threshold)
        tier_candidates = self.gdf[unassigned_mask & score_mask]

        num_initial_candidates = len(tier_candidates)
        log_threshold = tier_rules['minimum']
        suffix = "%" if self.method == 'percentile' else " (score)"
        self.logger.info(
            f"➡️Tier {tier_id}, Min: {log_threshold}{suffix}, Sep: {separation_m}m, Eligible Unplaced: "
            f"{num_initial_candidates}"
            )

        if tier_candidates.empty:
            return

        # --- Validate column name ---
        if id_col not in tier_candidates.columns:
            raise ValueError(
                f"⚠️ Warning: ID column '{id_col}' not found in input CSV. Update tiers config"
                f"Available columns: {list(tier_candidates.columns)}"
            )

        # Perform spatial decluttering
        successful_indices = []
        for df_index, candidate in tier_candidates.iterrows():
            candidate_id = candidate[id_col]
            is_debug_id = candidate_id in self.debug_ids

            is_too_close, conflicting_id = spatial_index.is_within_distance(
                candidate.geometry, separation_m, is_debug_id, candidate_id
                )

            if not is_too_close:
                if is_debug_id:
                    self.logger.info(
                        f"   - ✅ DEBUG [{candidate_id}]: PASSED. Placing in Tier {tier_id}."
                        )
                successful_indices.append(df_index)
                spatial_index.add_point(candidate_id, candidate.geometry)
            else:
                if is_debug_id:
                    self.logger.error(
                        f"   - > DEBUG [{candidate_id}]: Conflicts with tier {tier_id} ID: {conflicting_id}."
                        )

        # Assign the final placement tier
        if successful_indices:
            self.gdf.loc[successful_indices, self.config.output_tier_column] = tier_id

        # Statistics collection
        num_placed = len(successful_indices)
        self.stats.append(
            {
                "Tier": tier_id, "Separation (m)": separation_m,
                "Candidates": num_initial_candidates, "Placed": num_placed,
                "Conflict": num_initial_candidates - num_placed,
            }
        )

    def _set_score_tier(self) -> None:
        """
        Assigns the initial score-based tier ('raw_tier_col') to each item,
        independent of spatial considerations.
        """
        raw_tier_col = self.config.output_raw_tier_column
        id_col = self.config.id_column
        if not raw_tier_col or self.gdf.empty:
            return

        self.logger.info(f"   - Assigning initial score tiers based on '{self.method}' method...")
        self.gdf[raw_tier_col] = self.default_tier_id

        # score_thresholds are pre-calculated in _prepare_data
        # and stored in self.score_thresholds

        sorted_tiers = self._sort_and_validate_tiers()
        for tier_rules in sorted_tiers:
            tier_id = tier_rules['tier_id']
            score_threshold = self.score_thresholds[tier_id]

            unassigned_mask = (self.gdf[raw_tier_col] == self.default_tier_id)
            score_mask = (self.gdf[self.config.score_column] >= score_threshold)
            eligible_mask = unassigned_mask & score_mask

            if self.debug_ids and id_col in self.gdf_ignored.columns:
                eligible_indices = self.gdf[eligible_mask].index
                debug_indices_in_eligible = [idx for idx in eligible_indices if
                                             self.gdf.loc[idx, id_col] in self.debug_ids]
                for idx in debug_indices_in_eligible:
                    debug_id = self.gdf.loc[idx, id_col]
                    self.logger.info(
                        f"   - 🔬 DEBUG [{debug_id}]: Preliminary SCORE tier: {tier_id}."
                        )

            self.gdf.loc[eligible_mask, raw_tier_col] = tier_id

        self.logger.info("     - Preliminary Score tiers assigned.")

    def _finalize_results(self) -> pd.DataFrame:
        output_tier_col = self.config.output_tier_column
        raw_tier_col = self.config.output_raw_tier_column

        # Ensure ignored items have the correct columns with default values
        if not self.gdf_ignored.empty:
            self.gdf_ignored[output_tier_col] = self.default_tier_id
            if raw_tier_col:
                self.gdf_ignored[raw_tier_col] = self.default_tier_id

        # Combine scorable and ignored dataframes
        final_scorable_df = self.gdf.drop(columns=['geometry'], errors='ignore')
        if not self.gdf_ignored.empty:
            final_ignored_df = self.gdf_ignored.drop(columns=['geometry'], errors='ignore')
            return pd.concat([final_scorable_df, final_ignored_df], ignore_index=True)
        else:
            return final_scorable_df

    def _sort_and_validate_tiers(self) -> list[dict[str, Any]]:
        """
        Validates the tier configuration for correctness and sorts the tiers
        to ensure the most restrictive (highest minimum) are processed first.
        """
        tiers = self.config.tiers

        # each tier must have a unique threshold.
        minimums = [t.get('minimum') for t in tiers]
        if len(minimums) != len(set(minimums)):
            # Find the duplicates to provide a helpful error message
            seen = set()
            dupes = {x for x in minimums if x in seen or seen.add(x)}
            raise ValueError(
                "FATAL CONFIGURATION ERROR: Duplicate 'minimum' values found in tiers. "
                f"Each tier must have a unique minimum threshold. Duplicates found for: {list(dupes)}"
            )

        sorted_tiers = sorted(
            tiers, key=lambda t: t.get('minimum', -1), reverse=True
        )
        # Validate that separation distances are decreasing (or constant).
        last_separation = float('inf')
        for tier in sorted_tiers:
            current_separation = tier.get('separation', 0)  # Default to 0 if missing
            if current_separation > last_separation:
                self.logger.warning(
                    f"\n   ⚠️ --- CONFIGURATION WARNING ---"
                    f"\n      Tier {tier['tier_id']} has a separation distance ({current_separation}m) "
                    f"that is LARGER than the previous, more important tier ({last_separation}m)."
                )
            last_separation = current_separation

        return sorted_tiers

    def report_stats(self) -> None:
        """Prints formatted summary tables of the classification statistics."""
        if not self.stats:
            self.logger.warning(
                "No statistics were generated. This may happen if all items were ignored."
                )
            return

        stats_df = pd.DataFrame(self.stats)

        # --- GIS STATS TABLE ---
        self.logger.info("\n\n  Summary  ")
        gis_df = stats_df.copy()

        # 1. Calculate the raw float percentage
        gis_df['Placed_Pct_Val'] = (gis_df['Placed'] / gis_df['Candidates'].replace(0, 1) * 100)

        # 2. Generate the warning flag column using numpy
        # We use a space ' ' as the column name so the header is invisible in the log
        gis_df[' '] = np.where(gis_df['Placed_Pct_Val'] < 70, '⚠️', '')

        gis_report_cols = ["Tier", "Separation (m)", "Candidates", "Placed", "Conflict", "Placed %",
            " "]

        # 3. Format columns for display
        gis_df['Placed %'] = gis_df['Placed_Pct_Val'].map('{:.1f}%'.format)

        gis_df_to_print = gis_df[gis_report_cols].copy()

        # Fixed a bug from the original file where Separation (m) was formatted with a % sign
        gis_df_to_print['Separation (m)'] = gis_df_to_print['Separation (m)'].map('{:.1f}'.format)

        self.logger.info(gis_df_to_print.to_string(index=False))

    def report_performance(self) -> None:
        """Prints formatted summary tables of the classification statistics."""
        if not self.stats:
            return

        stats_df = pd.DataFrame(self.stats)

        # --- PERFORMANCE STATS TABLE ---
        self.logger.info("\n--- Performance Summary ---")
        perf_report_cols = ["Tier", "Candidates", "Time (ms)", "Nodes/ms"]

        perf_df_to_print = stats_df[perf_report_cols].copy()
        perf_df_to_print['Time (ms)'] = perf_df_to_print['Time (ms)'].map('{:.2f}'.format)
        perf_df_to_print['Nodes/ms'] = perf_df_to_print['Nodes/ms'].map('{:.2f}'.format)

        self.logger.info(perf_df_to_print.to_string(index=False))
