import json
from dataclasses import asdict

from open_jev.inference import run_inference

if __name__ == "__main__":
    sample_message = "This is the third duplicate charge. Please fix it."
    print(
        json.dumps(
            [asdict(answer) for answer in run_inference(sample_message)], indent=2
        )
    )
