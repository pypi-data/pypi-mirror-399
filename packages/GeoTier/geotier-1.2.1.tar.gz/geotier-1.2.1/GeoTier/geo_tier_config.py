# geo_tier_config.py
"""Handles the loading and validation of the geo tier YAML configuration.

This module provides a flexible GeoTierConfig class that holds validated
configuration settings, making them accessible via object attributes. The structure
is defined by a single schema, ensuring there is a single source of truth.
"""
import logging
from pathlib import Path
from typing import Any

from YMLEditor.yaml_reader import ConfigLoader

# --- Schema for the per-category config (e.g., peaks_tier.yml) ---
CATEGORY_TIER_SCHEMA = {
    'type': 'dict', 'required': True, 'schema': {
        'tier_id': {'type': 'integer', 'required': True},
        'minimum': {'type': 'number', 'required': True},
    }
}

GEOTIER_CONFIG_SCHEMA = {
    'config_type': {'type': 'string', 'required': True, 'allowed': ["GeoTierConfig"]},
    'id_column': {'type': 'string', 'required': True},
    'score_column': {'type': 'string', 'required': True}, 'classification': {
        'type': 'string', 'required': False, 'default': 'percentile',
        'allowed': ['percentile', 'score']
    }, 'output_tier_column': {'type': 'string', 'required': True},
    'output_raw_tier_column': {'type': 'string', 'required': True},
    'spatial_separation': {'type': 'boolean', 'required': False, 'default': True},
    'default_tier_id': {'type': 'integer', 'required': False, 'default': 0},
    'ignore_scores_below': {'type': 'float', 'required': False, 'default': 0.0},
    'approximate_distance': {'type': 'boolean', 'required': False, 'default': False},
    'density_modifier': {'type': 'float', 'required': False, 'default': 1.0},
    'tiers': {'type': 'list', 'required': True, 'schema': CATEGORY_TIER_SCHEMA},
}

# --- Schema for the central separation config (tier_separation.yml) ---
SEPARATION_TIER_SCHEMA = {
    'type': 'dict', 'required': True, 'schema': {
        'tier_id': {'type': 'integer', 'required': True},
        'separation': {'type': 'number', 'required': True, 'min': 0},
    }
}

GEOTIER_SEPARATION_SCHEMA = {
    'config_type': {'type': 'string', 'required': True, 'allowed': ["GeoTierSeparation"]},
    'tiers': {'type': 'list', 'required': True, 'schema': SEPARATION_TIER_SCHEMA},
}


def merge_configs(category_config: dict, separation_config: dict) -> dict:
    """
    Merges a category-specific config with a central separation config.

    This function is the core of the configuration logic. It builds a final,
    unified tier list by calculating and injecting the correct separation
    distance for each tier, including interpolation for intermediate tiers.

    Returns:
        A new dictionary representing the final, merged configuration.
    """
    logger = logging.getLogger("geo_tier")
    logger.info("   - Merging category and separation configurations...")

    # Build the separation lookup table
    separation_lookup = {tier['tier_id']: tier['separation'] for tier in separation_config['tiers']}
    sep_min_tier = min(separation_lookup.keys())
    sep_max_tier = max(separation_lookup.keys())

    # Validate that all category tiers are within the defined separation bounds
    for tier in category_config['tiers']:
        if not (sep_min_tier <= tier['tier_id'] <= sep_max_tier):
            raise ValueError(
                f"FATAL ERROR: Tier '{tier['tier_id']}' in category config is outside the "
                f"range defined in the separation config ({sep_min_tier}-{sep_max_tier})."
            )

    density_modifier = category_config.get('density_modifier', 1.0)
    final_tiers = []

    for tier in category_config['tiers']:
        tier_id = tier['tier_id']
        base_separation = 0.0

        if tier_id in separation_lookup:
            base_separation = separation_lookup[tier_id]
        else:  # Interpolate
            sorted_sep_tiers = sorted(separation_lookup.keys())
            lower_tier_id = max(t for t in sorted_sep_tiers if t < tier_id)
            upper_tier_id = min(t for t in sorted_sep_tiers if t > tier_id)

            lower_sep = separation_lookup[lower_tier_id]
            upper_sep = separation_lookup[upper_tier_id]

            interval_range = upper_tier_id - lower_tier_id
            position_in_interval = tier_id - lower_tier_id
            t = position_in_interval / interval_range

            base_separation = lower_sep * (upper_sep / lower_sep) ** t
            logger.info(
                f"     - Interpolated separation for tier {tier_id}: {base_separation:.2f}m"
                )

        modified_separation = base_separation / density_modifier

        final_tiers.append(
            {
                'tier_id': tier_id, 'minimum': tier['minimum'], 'separation': modified_separation
            }
        )

    # Create the final, unified config dictionary
    merged_config_dict = category_config.copy()
    merged_config_dict['tiers'] = final_tiers

    logger.info("   - ✅ Configurations successfully merged.")
    print(merged_config_dict)
    return merged_config_dict


class GeoTierConfig:
    """A flexible container for validated configuration settings."""

    def __init__(self, config_dict: dict[str, Any]):
        """
        Initializes the config object with a pre-validated dictionary.
        """
        self._data = config_dict

    def __getattr__(self, name: str) -> Any:
        """
        Enables attribute-style access to the configuration dictionary.
        e.g., `config.score_column` instead of `config['score_column']`.
        """
        if name in self._data:
            return self._data[name]
        raise AttributeError(f"Configuration has no attribute '{name}'")

    def get(self, key: str, default: Any = None) -> Any:
        """Provides dictionary-style .get() access with a default value."""
        return self._data.get(key, default)

    @classmethod
    def from_yaml(cls, path: Path) -> "GeoTierConfig":
        """
        Loads and validates the configuration from a YAML file.
        """
        loader = ConfigLoader(GEOTIER_SCHEMA)
        config_dict = loader.read(path)
        return cls(config_dict)
