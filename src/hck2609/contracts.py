"""Shared data contracts between modules.

Agree on changes here as a team: every module depends on these types.
"""

from typing import TypedDict

import pandas as pd

# ingestion -> processing: one row per raw record, columns are source-specific.
RawData = pd.DataFrame

# processing -> analysis/ui: cleaned, analysis-ready table.
CleanData = pd.DataFrame


class Insight(TypedDict):
    """A single finding produced by the analysis layer and shown by the UI."""

    title: str
    summary: str
