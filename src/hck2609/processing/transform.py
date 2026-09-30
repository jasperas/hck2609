from hck2609.contracts import CleanData, RawData


def clean(raw: RawData) -> CleanData:
    """Clean and normalise raw data. Stub: strips names, drops missing rows."""
    df = raw.dropna().copy()
    df["name"] = df["name"].str.strip().str.lower()
    return df
