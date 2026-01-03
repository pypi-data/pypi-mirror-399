# geo_tier.py
""" Places scored items into tiers.

This script acts as the main entry point for the `Geo_tier` tool.
It handles command-line arguments, loads the data and configuration,
and coordinates the `GeoTierEngine` to produce the final tiered output.
"""

import argparse
import logging
from pathlib import Path
import sys

import pandas as pd
from YMLEditor.yaml_reader import ConfigLoader

from GeoTier.geo_tier_config import (GeoTierConfig, GEOTIER_CONFIG_SCHEMA,
                                     GEOTIER_SEPARATION_SCHEMA, merge_configs)
from GeoTier.geo_tier_engine import GeoTierEngine


def main() -> None:
    """Orchestration layer: Handles I/O, config, and calls the engine."""
    parser = argparse.ArgumentParser(
        description="Places scored items into tiers with spatial separation."
    )
    # The arguments are correct from the previous version, just showing the main ones
    parser.add_argument("--input", type=Path, required=True, help="Path to scored CSV.")
    parser.add_argument(
        "--category-config", type=Path, required=True, help="Path to category tier YAML."
        )
    parser.add_argument(
        "--separation-config", type=Path, required=False, help="Path to central separation YAML."
        )
    parser.add_argument("--output", type=Path, required=True, help="Path to save tiered CSV.")
    parser.add_argument("--log-level", type=int, default=4, help="Set log level.")
    args = parser.parse_args()

    logger = _setup_logger(args.log_level)

    logger.info("\n*️⃣ Geo Tier Configuration:")
    logger.info(f"   - Input:             {args.input}")
    logger.info(f"   - Category Config:   {args.category_config}")
    logger.info(f"   - Separation Config: {args.separation_config}")
    logger.info(f"   - Output:            {args.output}")

    try:
        # --- STAGE 1: Load and Merge Configurations ---
        if not args.input.exists():
            raise FileNotFoundError(f"Input file not found: {args.input}")
        if not args.category_config.exists():
            raise FileNotFoundError(f"Category config not found: {args.category_config}")
        if not args.separation_config.exists():
            raise FileNotFoundError(f"Separation config not found: {args.separation_config}")

        category_loader = ConfigLoader(GEOTIER_CONFIG_SCHEMA)
        category_config_dict = category_loader.read(args.category_config)

        separation_loader = ConfigLoader(GEOTIER_SEPARATION_SCHEMA)
        separation_config_dict = separation_loader.read(args.separation_config)

        final_config_dict = merge_configs(category_config_dict, separation_config_dict)
        config = GeoTierConfig(final_config_dict)

        scored_df = pd.read_csv(args.input)

        # --- STAGE 2: Run Classification ---
        geo_tier = GeoTierEngine(config, logger)
        tiered_df = geo_tier.classify(scored_df)

        # --- STAGE 3: Save Results ---
        args.output.parent.mkdir(parents=True, exist_ok=True)
        logger.info(f"\n➡️ Saving {len(tiered_df)} items to {args.output}...")
        tiered_df.to_csv(args.output, index=False)
        logger.info("✅ Classification complete.")

        geo_tier.report_stats()

    except MemoryError as e:
        # This single block now catches any error from any stage
        logger.error(f"\n❌ A fatal error occurred during processing: {e}", exc_info=True)
        sys.exit(1)


def _setup_logger(level: int) -> logging.Logger:
    """Initializes and configures the logger for the script."""
    # Using the script's name is a standard practice for loggers.
    logger = logging.getLogger("geo_tier")
    if level >= 4:
        logger.setLevel(logging.DEBUG)
    if level == 3:
        logger.setLevel(logging.INFO)

    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter("%(message)s")
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    return logger


if __name__ == "__main__":
    main()
