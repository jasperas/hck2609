"""The glue: wires the modules together via the contracts. One owner only."""

from hck2609.analysis.insights import analyse
from hck2609.contracts import CleanData, Insight
from hck2609.ingestion.load import load_raw
from hck2609.processing.transform import clean


def run_pipeline(source: str | None = None) -> tuple[CleanData, list[Insight]]:
    data = clean(load_raw(source))
    return data, analyse(data)
