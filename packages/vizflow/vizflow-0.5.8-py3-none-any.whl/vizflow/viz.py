"""Visualization utilities for VizFlow."""

import polars as pl


def add_tod(
    df: pl.LazyFrame,
    timestamp_col: str = "ticktime",
) -> pl.LazyFrame:
    """Add time-of-day column for plotting.

    Converts HHMMSSMMM integer timestamp to pl.Time for visualization.
    Note: pl.Time type is not supported by Delta Lake - use this only
    for plotting, not for data that will be written to Delta Lake.

    Args:
        df: Input LazyFrame with HHMMSSMMM timestamp column
        timestamp_col: Column with integer HHMMSSMMM format timestamps
            e.g., 93012145 = 09:30:12.145, 142058425 = 14:20:58.425

    Returns:
        LazyFrame with tod_{timestamp_col} (pl.Time) column added

    Example:
        >>> df = vf.add_tod(df, "ticktime")
        >>> # Creates: tod_ticktime (pl.Time)
    """
    # Parse HHMMSSMMM to nanoseconds since midnight
    tod_ns = (
        (pl.col(timestamp_col) // 10000000) * 3_600_000_000_000
        + (pl.col(timestamp_col) // 100000 % 100) * 60_000_000_000
        + (pl.col(timestamp_col) // 1000 % 100) * 1_000_000_000
        + (pl.col(timestamp_col) % 1000) * 1_000_000
    )
    return df.with_columns(tod_ns.cast(pl.Time).alias(f"tod_{timestamp_col}"))
