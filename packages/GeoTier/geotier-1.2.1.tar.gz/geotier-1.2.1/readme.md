# GeoTier: Intelligent Map Decluttering

**GeoTier** takes a list of scored geographic features and assigns them to hierarchical tiers based on score and
spatial separation. Items are assigned to tiers based on the percentile rank of their score. This is further
refined by enforcing that every item in a tier meets a specified separation distance for that tier.

The output is a dataset ready for multi-scale map rendering, with two distinct assignments for each feature:

* **`score_tier`**: The tier a feature qualifies for based its scores percentile rank. This is ideal for **styling**,
  allowing features to be styled by their importance tier.
* **`resolved_tier`**: The tier a feature is placed in after enforcing separation. This is
  ideal for **visibility filtering** at different zoom levels. Using the resolved_tier for zoom filtering ensures
  that each zoom level has features with the specified separation distance.

### Example: Tiering Mountain Peaks

Imagine you have a list of mountain peaks, and your configuration defines two tiers: Tier 10 for globally significant
peaks,
and Tier 9 for regionally significant ones. (_Note for the example: Lhotse is the 4th tallest peak in the world but
close to
Everest_)

**Input Data:**

| Name          | Score  | Lon  | Lat  |
|:--------------|:-------|:-----|:-----|
| Mount Everest | 100    | ...  | ...  |
| Lhotse        | 99     | ...  | ...  |

**Configuration:**

* **Tier 4:** Requires a score in the top 1% and a **1000km** separation.
* **Tier 5:** Requires a score in the top 5% and a **200km** separation.

**GeoTier Output:**

| Name              | Score | score_tier | resolved_tier | Comment                                                                     |
|:------------------|:------|:-----------|:--------------|:----------------------------------------------------------------------------|
| **Mount Everest** | 100   | 4          | 4             | Highest score, placed in Tier 4.                                            |
| **Lhotse**        | 99    | 4          | 6             | **Downgraded.** Qualifies for Tier 4 by score, but is too close to Everest. |
|                   |       |            |               | Placed in the next tier where it meets separation.                          |

The score tier can be used to style based on importance, while the resolved_tier can be used to filter to prevent
clutter.
As the example shows, **GeoTier** ensures your most important features are always preserved while intelligently
managing the visual density of your map. At a low zoom, Lhotse could be filtered out and then shown as the zoom
increases. However, in both cases it could be displayed with the same bold labelling for the top mountains in the world.

### Key Benefits  :

* **Automated Decluttering:** Eliminates the cumbersome process of selecting which labels to show at different
  map scales.
* **Data-Driven Generalization:** Uses a quantitative, repeatable process based on an importance score, leading to more
  objective and consistent maps.
* **Guaranteed Separation:** Enforces a minimum separation distance for each `resolved_tier`, ensuring labels meet the
  distance you specify.
* **Dual-Tier Output:** By separating the `score_tier` (for styling) from the `resolved_tier` (for visibility), you can
  correctly style a downgraded item with the prominence it deserves.
* **Hierarchy-Aware:** The algorithm is designed to be "hierarchy-aware." If two points are in conflict, the point with
  the **higher importance score always wins**, ensuring your most significant features are always preserved.
* **Configuration-Driven:** All tiering and separation rules are defined in a simple, human-readable YAML file, making
  your workflow transparent, versionable, and easy to modify.

Any points that do not meet the criteria for any defined tier will be assigned the `default_tier_id`.
Note that you choose the tier names. You could name them to match the expected zoom level for the tier.

---

## Distance Measurement and Performance

> **Input Data:** The input CSV file must contain point coordinates in WGS84 (EPSG:4326).

To ensure both accuracy and speed, **GeoTier** uses a two-phase process for spatial calculations:

1. **Coordinate Projection:** All geographic coordinates are projected once into a meter-based system (EPSG:3395) for
   fast
   Euclidean distance checks.
2. **Conflict Detection:** An **R-tree spatial index** is used to find nearby points efficiently. The engine supports
   two
   modes, controlled by the `approximate_distance` config setting:
    * **Accurate (Default):** A fast bounding box search finds potential neighbors, then a precise radial distance check
      is
      performed on that small subset.
    * **Approximate (Faster):** Skips the second precise check and uses only the initial bounding box search. This should only 
   be needed for extremely large datasets.

---

## Configuration Example

All tiering rules are defined in a single YAML file (e.g., `config/geysers_classification.yml`).

```yaml
# Defines the input and output column names
id_column: id
score_column: score
output_resolved_tier_column: tier      # For zoom filtering
output_score_tier_column: style_tier # For styling
default_tier_id: 0  # For items not meeting any tier criteria

# Any item with a score below this will be ignored by percentile calculations
# and automatically placed in the default tier.
ignore_scores_below: 0.01
approximate_distance: false   # If true then a bounding box is used (faster) otherwise true distance is used

# Defines the tiering rules, processed from most restrictive to least.
# `separation` is in meters.
tiers:
  - tier_id: 9
    method: percentile
    min_pctl: 98
    separation: 4000

  - tier_id: 7
    method: percentile
    min_pctl: 95
    separation: 1000

  - tier_id: 1
    method: score
    min_score: 10
    separation: 50
```

---

## Usage with Multiple Datasets (Cross-Category Ranking)

A key challenge in cartography is creating a single, coherent map from multiple feature types (e.g., peaks,
waterfalls, points of interest, etc). **GeoTier** is designed to support this through a deliberate, two-stage workflow
that
relies on its companion
tool, `ImportanceScore`.

This approach is called **Thematic Scaling**, which allows you, the domain expert, to define the relative importance
*between*
different categories.

### The Recommended Workflow

**Stage 1: Generate Thematically Scaled Scores with `ImportanceScore`**

Before using `GeoTier`, process each category independently using `ImportanceScore`. ImportanceScore uses Machine
Learning to create a score based on the item's attributes.

The key is to use ImportanceScore's `scaling`
configuration block to assign each category its own "importance ceiling."

* **Example:** You decide that the most important mountain peaks are globally significant, while even the most important
  man-made points of interest are only regionally significant.

    * `config/peaks_model.yml`:
      ```yaml
      scaling:
        min: 0
        max: 100 # Peaks can achieve the maximum possible score.
      ```
    * `config/poi_model.yml`:
      ```yaml
      scaling:
        min: 0
        max: 70 # POIs are capped; they can never be more important than a 70.
      ```

1. Run Importance score on peaks and then on POI's.

**Stage 2: Merge and Classify with `GeoTier`**

1. **Merge Data:** Combine all the scored output files from Stage 1 into a single CSV file. The `score` column in this
   file now reflects your expert-defined cross-category hierarchy.
2. **Run `GeoTier`:** Run `GeoTier` **once** on this single, merged file.

**Why this works:** `GeoTier`'s percentile ranking will now operate on the pre-weighted distribution. The top tiers will
naturally be filled by peaks (as only they can have scores above 70), and the spatial separation will be correctly
resolved **between all feature types simultaneously**.
This ensures a globally consistent and cartographically sound map.