from hck2609.pipeline import run_pipeline


def test_pipeline_runs_end_to_end():
    data, insights = run_pipeline()
    assert len(data) > 0
    assert insights
