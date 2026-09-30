import torch
from open_jev.main import (
    Jev,
    JevConfig,
    Noul,
    Choice,
    Score,
    NoulAnswer,
    ChoiceAnswer,
    Question,
    RLCDLoss,
)


def _demo() -> None:
    torch.manual_seed(0)

    cfg = JevConfig(
        vocab_size=4096,
        d_model=128,
        n_heads=4,
        d_ff=512,
        n_state_layers=3,
        n_readout_layers=4,
        n_slots=8,
    )
    model = Jev(cfg).eval()
    n_params = sum(p.numel() for p in model.parameters())
    print(f"Jev reference model: {n_params/1e6:.1f}M params (random weights)\n")

    state = {
        "customer": {"name": "Ada", "tier": "enterprise", "tenure_months": 34},
        "message": "This is the third time I've been charged for the same order. Fix it now.",
        "transactions": [
            {"id": "t_1", "amount": 89.0, "status": "captured"},
            {"id": "t_2", "amount": 89.0, "status": "captured"},
        ],
        "policy": "Duplicate charges are refundable within 60 days without review.",
    }

    questions: list[Question] = [
        Noul("The customer is requesting a refund.", key="wants_refund"),
        Noul("The transactions show a duplicate charge.", key="is_duplicate"),
        Choice(
            "Which team should handle this ticket?",
            options=["billing", "technical", "account"],
            key="route",
        ),
        Score(
            "How frustrated is this customer?",
            labels=["calm", "annoyed", "frustrated", "very frustrated"],
            key="frustration",
        ),
    ]

    with torch.no_grad():
        answers = model([state], questions)[0]

    print("--- Answers (one forward pass, 4 questions) ---")
    for a in answers:
        if isinstance(a, NoulAnswer):
            print(f"  {a.key:12s} noul={a.noul:.3f}")
        elif isinstance(a, ChoiceAnswer):
            dist = " ".join(f"{k}={v:.2f}" for k, v in a.probabilities.items())
            print(
                f"  {a.key:12s} choice={a.choice!r} conf={a.confidence:.3f}  [{dist}]"
            )
        else:
            dist = " ".join(f"{k}={v:.2f}" for k, v in a.probabilities.items())
            print(
                f"  {a.key:12s} score={a.score:.2f} conf={a.confidence:.3f}  [{dist}]"
            )

    # Type safety is structural: every Choice answer is a declared option.
    route = next(a for a in answers if a.key == "route")
    assert isinstance(route, ChoiceAnswer) and route.choice in (
        "billing",
        "technical",
        "account",
    )
    print("\n  [ok] choice is always a declared option -- unrepresentable otherwise")

    # Key-order invariance: shuffled dict, identical structural encoding.
    shuffled = {k: state[k] for k in reversed(list(state.keys()))}
    with torch.no_grad():
        alt = model([shuffled], questions)[0]
    drift = max(
        abs(x.noul - y.noul)
        for x, y in zip(answers, alt)
        if isinstance(x, NoulAnswer) and isinstance(y, NoulAnswer)
    )
    print(f"  [ok] key-shuffle drift on Noul: {drift:.4f} (untrained; trained -> ~0)")

    # One RLCD step against SOFT targets.
    print("\n--- One RLCD training step (soft targets, not one-hots) ---")
    model.train()
    targets = [
        torch.tensor([[0.08, 0.92]]),  # wants_refund: 11/12 teachers say yes
        torch.tensor([[0.15, 0.85]]),  # is_duplicate
        torch.tensor([[0.80, 0.05, 0.15]]),  # route -> billing
        torch.tensor([[0.02, 0.10, 0.48, 0.40]]),  # frustration, genuinely ambiguous
    ]
    loss_fn = RLCDLoss()
    opt = torch.optim.AdamW(model.parameters(), lr=1e-4)
    loss = loss_fn(model, [state], questions, targets, augmented_states=[shuffled])
    loss.backward()
    opt.step()
    print("  " + "  ".join(f"{k}={v:.4f}" for k, v in loss_fn.parts.items()))

    print("\n  Note the frustration target: 0.48/0.40 is not a mistake to be")
    print("  trained away. The situation really is ambiguous, and a calibrated")
    print("  model should say so rather than manufacture a confident answer.")


if __name__ == "__main__":
    _demo()
