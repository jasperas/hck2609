from hck2609.pipeline import run_pipeline


def main() -> None:
    data, insights = run_pipeline()
    print(data)
    for insight in insights:
        print(f"- {insight['title']}: {insight['summary']}")
