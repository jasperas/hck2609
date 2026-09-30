from hck2609.contracts import CleanData, Insight


def analyse(data: CleanData) -> list[Insight]:
    """Turn clean data into findings (stats, model output, LLM summaries). Stub."""
    return [Insight(title="Row count", summary=f"{len(data)} clean rows")]
