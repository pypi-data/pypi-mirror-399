# spatial_index.py
import logging
from typing import Any

from rtree import index
from shapely.geometry import Point


class SpatialIndex:
    """A wrapper for an R-tree spatial index to manage point placement."""

    def __init__(self, approximate_distance: float, debug_ids: set, logger: logging.Logger):
        """
        Initializes the spatial index.

        Args:
            approximate_distance (float): An initial distance for broad-phase culling.
            debug_ids (set): A set of IDs to provide detailed logging for.
            logger (logging.Logger): The logger instance.
        """
        self.logger = logger
        self.idx = index.Index()
        # Store geometries and their original IDs together
        self.placed_items = {}
        self.next_internal_id = 0
        self.debug_ids = debug_ids

    def add_point(self, item_id: Any, point_geom: Point) -> None:
        """Adds a point with its original ID to the spatial index."""
        internal_id = self.next_internal_id
        self.idx.insert(internal_id, point_geom.bounds)
        # Store the geometry and original ID
        self.placed_items[internal_id] = {'geom': point_geom, 'id': item_id}
        self.next_internal_id += 1

    def is_within_distance(
            self, point_geom: Point, distance: float, is_debug_id: bool = False,
            candidate_id: Any = None
            ) -> tuple[bool, Any]:
        """
        Checks if a point is within a given distance of any existing point in the index.

        Returns:
            A tuple: (is_too_close, conflicting_item_id).
            conflicting_item_id is the original ID of the item it conflicts with, or None.
        """
        if distance is None or distance <= 0:
            return False, None

        # Create a buffer (circle) around the point
        buffer = point_geom.buffer(distance)

        # Find potential neighbors using the fast R-tree index (broad-phase)
        potential_neighbor_ids = list(self.idx.intersection(buffer.bounds))

        if not potential_neighbor_ids:
            return False, None

        # Now, perform the more expensive, precise check on the potential neighbors (narrow-phase)
        for internal_id in potential_neighbor_ids:
            placed_item = self.placed_items[internal_id]
            # Precise intersection check
            if buffer.intersects(placed_item['geom']):
                if is_debug_id:
                    dist = point_geom.distance(placed_item['geom'])
                    self.logger.info(
                        f"   - 🔬 DEBUG [{candidate_id}]: Found potential conflict with ID "
                        f"{placed_item['id']} at {dist:.2f}m (Threshold: {distance}m)."
                        )
                # Precise check passed, it's a conflict
                return True, placed_item['id']

        # No precise conflicts found
        return False, None
