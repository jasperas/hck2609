from hck2609.pipeline import run_pipeline


def test_pipeline_runs_end_to_end():
    data, insights = run_pipeline()
    assert len(data) > 0
    assert insights


def test_convert_raw_writes_flat_json(tmp_path):
    import json
    from pathlib import Path

    from hck2609.processing.transform import convert_raw

    raw = Path("data/raw")
    if not (raw / "01_emails").exists():
        return
    out = convert_raw(raw, tmp_path)
    assert len(out) == 40
    doc = json.loads(out[0].read_text())
    assert set(doc) == {"type", "metadata", "body"}
