# tests/test_tier_engine.py
"""Unit tests for the ClassificationEngine.

This module uses pytest to validate the core tiering and spatial
decluttering logic of GeoTiers, with a focus on the
percentile-based selection method.
"""

import logging
from typing import Any

import geopandas as gpd
import pandas as pd
import pytest
from pytest_mock import MockerFixture

from GeoTier.geo_tier_config import GeoTierConfig
from GeoTier.geo_tier_engine import GeoTierEngine

# --- Test Setup  ---

@pytest.fixture
def mock_logger() -> logging.Logger:
    """Provides a basic logger for testing purposes."""
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    return logger

class MockGeoTierConfig(GeoTierConfig):
    """A mock config object for testing purposes."""
    def __init__(
            self,
            tiers: list[dict[str, Any]],
            score_column: str = 'score',
            ignore_scores_below: int = -1
    ):
        self.tiers = tiers
        self.score_column = score_column
        self.output_tier_column = 'resolved_tier'
        self.output_style_tier_column = 'style_tier'
        self.ignore_scores_below = ignore_scores_below
        self.default_tier_id = 0
        self.approximate_distance = False

def setup_geospatial_data(points_in_meters: dict, scores: dict) -> pd.DataFrame:
    """
    Creates a GeoDataFrame from meter-based coordinates and converts it to
    a standard lat/lon pandas DataFrame for testing.
    """
    df = pd.DataFrame([
        {'id': pid, 'x': coords[0], 'y': coords[1], 'score': scores[pid]}
        for pid, coords in points_in_meters.items()
    ])

    gdf = gpd.GeoDataFrame(
        df, geometry=gpd.points_from_xy(df.x, df.y), crs="EPSG:32612" # UTM Zone 12N
    )

    gdf_wgs84 = gdf.to_crs("EPSG:4326")

    return pd.DataFrame({
        'id': gdf_wgs84['id'],
        'lon': gdf_wgs84.geometry.x,
        'lat': gdf_wgs84.geometry.y,
        'score': gdf_wgs84['score']
    })

# --- Test Data Generation  ---

# Base 4-point dataset
FOUR_POINT_SCORES = {'A': 100, 'B': 99, 'C': 40, 'D': 10}

# No conflict data (points are far apart)
no_conflict_data = setup_geospatial_data({
    'A': (10000, 10000), 'B': (20000, 20000), 'C': (30000, 30000), 'D': (40000, 40000),
}, FOUR_POINT_SCORES)

# Conflict data (A and B are 500m apart)
conflict_data = setup_geospatial_data({
    'A': (10000, 10000), 'B': (10500, 10000), 'C': (20000, 20000), 'D': (30000, 30000),
}, FOUR_POINT_SCORES)

# --- more complex dataset for advanced tests ---
# E is close to A, F is close to B. A > E > B > F in score.
# This setup will test intra-tier conflict resolution.
MULTI_CONFLICT_SCORES = {'A': 100, 'E': 99.5, 'B': 99, 'F': 98.5, 'C': 40, 'D': 10}
multi_conflict_data = setup_geospatial_data({
    'A': (10000, 10000), 'E': (10500, 10000), # A and E are 500m apart
    'B': (20000, 20000), 'F': (20500, 20000), # B and F are 500m apart
    'C': (30000, 30000), 'D': (40000, 40000),
}, MULTI_CONFLICT_SCORES)

# --- Test Data for the ignore_scores_below case ---
PERCENTILE_IGNORE_SCORES = {
    'Ignored1': 1, 'Ignored2': 2, 'Ignored3': 3, 'Ignored4': 4,       # 4 items <= 10
    'Low1': 20, 'Low2': 30, 'Low3': 40, 'Low4': 50,                   # 4 items > 10 and <= 50
    'High1': 60, 'High2': 70, 'High3': 80, 'High4': 90,               # 4 items > 50
}

percentile_with_ignored_data = setup_geospatial_data({
    # Place points far apart to avoid any spatial conflicts
    'Ignored1': (1000, 1000), 'Ignored2': (2000, 2000), 'Ignored3': (3000, 3000), 'Ignored4': (4000, 4000),
    'Low1': (5000, 5000), 'Low2': (6000, 6000), 'Low3': (7000, 7000), 'Low4': (8000, 8000),
    'High1': (9000, 9000), 'High2': (10000, 10000), 'High3': (11000, 11000), 'High4': (12000, 12000),
}, PERCENTILE_IGNORE_SCORES)


# --- Main Test Cases for the Engine  ---
TEST_CASES = [
    # --- Test Case 1: Base Test Case  ---
    pytest.param(
        no_conflict_data,
        [{'tier_id': 2, 'method': 'percentile', 'min_pctl': 74, 'separation': 0},
         {'tier_id': 1, 'method': 'percentile', 'min_pctl': 0, 'separation': 0}],
        { 'A': 2, 'B': 2, 'C': 1, 'D': 1 },
        -1,
        id="no_conflict_establishes_ground_truth"
    ),

    # --- Test Case 2: Base Test Case  ---
    pytest.param(
        conflict_data,
        [{'tier_id': 2, 'method': 'percentile', 'min_pctl': 75, 'separation': 1000},
         {'tier_id': 1, 'method': 'percentile', 'min_pctl': 0, 'separation': 100}],
        { 'A': 2, 'B': 1, 'C': 1, 'D': 1 },
        -1,
        id="downgrade_when_distance_is_between_separations"
    ),

    # --- Test Case 3: Multi-Tier Downgrade ---
    # B is 500m from A.
    # Tier 3 (sep: 1000m) -> CONFLICT with A
    # Tier 2 (sep: 600m) -> CONFLICT with A
    # Tier 1 (sep: 400m) -> NO CONFLICT
    # This tests that B is correctly rejected from two tiers before being placed.
    pytest.param(
        conflict_data,
        [
            {'tier_id': 3, 'method': 'percentile', 'min_pctl': 74, 'separation': 1000},
            {'tier_id': 2, 'method': 'percentile', 'min_pctl': 49, 'separation': 600},
            {'tier_id': 1, 'method': 'percentile', 'min_pctl': 0, 'separation': 400}
        ],
        { 'A': 3, 'B': 1, 'C': 2, 'D': 1 },
        -1,
        id="multi_tier_downgrade"
    ),

    # --- Test Case 4: Intra-Tier Conflict Resolution ---
    # A, E, B, F are all candidates for Tier 3 (>66th percentile).
    # Tier 3 separation is 1000m.
    # A conflicts with E. B conflicts with F.
    # The engine must correctly select A (score 100) and B (score 99) because they
    # have higher scores than their respective conflicting neighbors E and F.
    pytest.param(
        multi_conflict_data,
        [
            {'tier_id': 3, 'method': 'percentile', 'min_pctl': 66, 'separation': 1000},
            {'tier_id': 2, 'method': 'percentile', 'min_pctl': 33, 'separation': 100},
            {'tier_id': 1, 'method': 'percentile', 'min_pctl': 0, 'separation': 10}
        ],
        { 'A': 3, 'B': 3, 'E': 2, 'F': 2, 'C': 2, 'D': 1 },
        -1,
        id="intra_tier_conflict_prioritizes_by_score"
    ),

    # ---  Test Case 5: Empty Candidate Set ---
    # The first tier rule is designed to place ALL points.
    # Therefore, when the engine proceeds to the second tier rule, the set of
    # unassigned candidates will be empty, triggering the target code block.
    pytest.param(
        no_conflict_data,
        [
            # This first tier will successfully place ALL points.
            {'tier_id': 5, 'method': 'percentile', 'min_pctl': 0, 'separation': 0},
            # This second tier will have no unassigned candidates to process.
            {'tier_id': 1, 'method': 'percentile', 'min_pctl': 0, 'separation': 0}
        ],
        { 'A': 5, 'B': 5, 'C': 5, 'D': 5 }, # The expected final state
        -1,
        id="all_points_placed_in_first_tier_triggers_empty_candidate_path"
    ),

    # ---  Test Case 6: Empty Tier-Specific Candidate Set ---
    # We use the 'range' method to create an impossible-to-satisfy rule.
    pytest.param(
        no_conflict_data,
        [
            # Tier 3 will place point A (score 100).
            {'tier_id': 3, 'method': 'percentile', 'min_pctl': 99, 'separation': 0},

            # Tier 2 looks for scores between 50 and 60. The remaining
            # candidates (B=99, C=40, D=10) do not fall in this range.
            # This will result in an empty `tier_candidates` DataFrame.
            {'tier_id': 2, 'method': 'range', 'above_score': 50, 'below_score': 60, 'separation': 0},

            # Tier 1 will then place the remaining points B, C, and D.
            {'tier_id': 1, 'method': 'percentile', 'min_pctl': 0, 'separation': 0},
        ],
        { 'A': 3, 'B': 1, 'C': 1, 'D': 1 }, # The expected final state
        -1,
        id="impossible_range_rule_triggers_empty_tier_candidate_path"
    ),

    # --- Test ignored values ---
    pytest.param(
        percentile_with_ignored_data,
        [
            # This tier should select the top 50% of the 8 SCORABLE items.
            {'tier_id': 5, 'method': 'percentile', 'min_pctl': 50, 'separation': 0},
            # This tier is a catch-all for the remaining scorable items.
            {'tier_id': 1, 'method': 'percentile', 'min_pctl': 0, 'separation': 0}
        ],
        {
            # Ignored items (score <= 10) should remain in the default tier 0.
            'Ignored1': 0, 'Ignored2': 0, 'Ignored3': 0, 'Ignored4': 0,
            # Lower 50% of scorable items should be placed in the catch-all tier 1.
            'Low1': 1, 'Low2': 1, 'Low3': 1, 'Low4': 1,
            # Top 50% of scorable items (High1-4) should be placed in tier 5.
            'High1': 5, 'High2': 5, 'High3': 5, 'High4': 5,
        },
        10, # ignore_threshold
        id="ignored_items_are_excluded_from_percentile_ranking"
    ),
]
@pytest.mark.parametrize(
    "input_data, tier_rules, expected_tiers, ignore_threshold",
    TEST_CASES
)
def test_classification_engine(
        input_data: pd.DataFrame,
        tier_rules: list[dict[str, Any]],
        expected_tiers: dict[str, int],
        ignore_threshold: int,
        mock_logger: logging.Logger,
        mocker: MockerFixture # mocker is no longer used, but we can leave it
):
    """
    Tests the GeoTierEngine with various data and rule configurations.
    """
    # 1. Arrange: Create the mock configuration object directly.
    mock_config = MockGeoTierConfig(
        tiers=tier_rules,
        ignore_scores_below=ignore_threshold
    )

    # 2. Act: Instantiate the engine by injecting the mock config.
    #    There is no more need for patching.
    engine = GeoTierEngine(config=mock_config, logger=mock_logger)
    result_df = engine.classify(input_data.copy())

    # 3. Assert: Verify the results.
    result_tiers = pd.Series(
        result_df['resolved_tier'].values, index=result_df['id']
    ).to_dict()

    sorted_result = dict(sorted(result_tiers.items()))
    sorted_expected = dict(sorted(expected_tiers.items()))

    assert sorted_result == sorted_expected
