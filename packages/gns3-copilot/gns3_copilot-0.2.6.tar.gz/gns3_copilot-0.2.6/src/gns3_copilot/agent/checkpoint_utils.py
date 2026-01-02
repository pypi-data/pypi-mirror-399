"""
GNS3 Copilot Checkpoint Utilities

This module provides utility functions for interacting with LangGraph checkpoint
database, including thread ID listing and checkpoint management operations.
"""

from typing import Any

from gns3_copilot.log_config import setup_logger

logger = setup_logger("checkpoint_utils")


def list_thread_ids(checkpointer: Any) -> list[str]:
    """
    Get all unique thread IDs from LangGraph checkpoint database.

    Args:
        checkpointer: LangGraph checkpointer instance.

    Returns:
        list: List of unique thread IDs ordered by most recent activity.
              Returns empty list on error or if table doesn't exist.
    """
    try:
        res = checkpointer.conn.execute(
            "SELECT DISTINCT thread_id FROM checkpoints ORDER BY rowid DESC"
        ).fetchall()
        return [r[0] for r in res]
    except Exception as e:
        # Table might not exist yet, return empty list
        logger.debug("Error listing thread IDs (table may not exist): %s", e)
        return []
