import torch

from open_jev.main import Choice, Jev, JevConfig, Noul, Score

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

state = {
    "customer": {"tier": "enterprise", "tenure_months": 34},
    "message": "This is the third duplicate charge. Please fix it.",
    "policy": "Duplicate charges are refundable within 60 days.",
}

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

with torch.no_grad():
    answers = model([state], questions)[0]

for answer in answers:
    print(answer)
