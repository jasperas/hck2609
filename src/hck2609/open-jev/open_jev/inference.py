from typing import Any

import torch

from open_jev.main import Answer, Choice, Jev, JevConfig, Noul, Score

model = Jev(
    JevConfig(
        vocab_size=4096,
        d_model=128,
        n_heads=4,
        d_ff=512,
        n_state_layers=3,
        n_readout_layers=4,
    )
).eval()

questions = [
    Noul("The customer is requesting a refund.", key="wants_refund"),
    Choice(
        "Which team should handle this?",
        options=["billing", "technical", "account"],
        key="route",
    ),
    Score(
        "How frustrated is the customer?",
        labels=["calm", "annoyed", "frustrated", "very frustrated"],
        key="frustration",
    ),
]


def run_inference(message: str) -> list[Answer]:
    state: dict[str, Any] = {
        "customer": {"tier": "enterprise", "tenure_months": 34},
        "message": message,
        "policy": "Duplicate charges are refundable within 60 days.",
    }

    with torch.no_grad():
        return model([state], questions)[0]
