from hck2609.contracts import RawData
import pandas as pd


def load_raw(source: str | None = None) -> RawData:
    """Fetch/parse the messy source data. Stub: returns a dummy table."""
    return pd.DataFrame({"id": [1, 2, 3], "name": [" a ", "B", None], "value": [1.0, 2.5, 4.0]})
