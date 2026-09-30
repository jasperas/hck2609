"""Dash interface. Run with: uv run python src/hck2609/ui/app.py"""

import json
from dataclasses import asdict
from typing import Any

from dash import Dash, Input, Output, State, dcc, html
from open_jev.inference import run_inference

app = Dash(__name__)
app.title = "Open Jev"

field_style = {
    "boxSizing": "border-box",
    "width": "100%",
    "minHeight": "320px",
    "padding": "16px",
    "border": "1px solid #c8d6d3",
    "borderRadius": "4px",
    "backgroundColor": "#fffefa",
    "color": "#183c39",
    "fontSize": "15px",
    "lineHeight": "1.5",
    "resize": "vertical",
}

app.layout = html.Main(
    [
        html.Header(
            [
                html.P(
                    "OPEN JEV / INFERENCE",
                    style={"color": "#28756b", "fontSize": "12px", "fontWeight": 700},
                ),
                html.H1(
                    "Typed decisions from text",
                    style={"margin": "8px 0", "fontSize": "36px"},
                ),
                html.P(
                    "Enter a customer message and inspect the model's structured response.",
                    style={"color": "#526663"},
                ),
            ],
            style={"marginBottom": "32px"},
        ),
        html.Div(
            [
                html.Section(
                    [
                        html.Label(
                            "Message",
                            htmlFor="input-text",
                            style={
                                "display": "block",
                                "fontWeight": 700,
                                "marginBottom": "8px",
                            },
                        ),
                        dcc.Textarea(
                            id="input-text",
                            placeholder="Type a customer message...",
                            style=field_style,
                        ),
                        html.Button(
                            "run",
                            id="run-button",
                            n_clicks=0,
                            style={
                                "marginTop": "14px",
                                "padding": "10px 24px",
                                "border": 0,
                                "borderRadius": "4px",
                                "backgroundColor": "#cf5b3b",
                                "color": "white",
                                "fontSize": "15px",
                                "fontWeight": 700,
                                "cursor": "pointer",
                            },
                        ),
                    ],
                    style={"minWidth": 0},
                ),
                html.Section(
                    [
                        html.Label(
                            "JSON output",
                            htmlFor="json-output",
                            style={
                                "display": "block",
                                "fontWeight": 700,
                                "marginBottom": "8px",
                            },
                        ),
                        dcc.Textarea(
                            id="json-output",
                            readOnly=True,
                            placeholder="Inference results will appear here.",
                            style={
                                **field_style,
                                "fontFamily": "monospace",
                                "backgroundColor": "#f0f5f2",
                            },
                        ),
                    ],
                    style={"minWidth": 0},
                ),
            ],
            style={
                "display": "grid",
                "gridTemplateColumns": "repeat(auto-fit, minmax(min(100%, 360px), 1fr))",
                "gap": "24px",
            },
        ),
        html.Section(
            [
                html.H2(
                    "Inference details",
                    style={"margin": "36px 0 16px", "fontSize": "22px"},
                ),
                html.Div(
                    id="answer-cards",
                    style={
                        "display": "grid",
                        "gridTemplateColumns": "repeat(auto-fit, minmax(min(100%, 280px), 1fr))",
                        "gap": "16px",
                    },
                ),
            ]
        ),
    ],
    style={
        "maxWidth": "1120px",
        "margin": "0 auto",
        "padding": "48px 24px",
        "fontFamily": "Georgia, serif",
        "color": "#183c39",
    },
)

app.layout.style = {
    **app.layout.style,
    "minHeight": "100vh",
    "backgroundColor": "#e7efeb",
}


@app.callback(
    Output("json-output", "value"),
    Output("answer-cards", "children"),
    Input("run-button", "n_clicks"),
    State("input-text", "value"),
    prevent_initial_call=True,
)
def infer_message(
    _n_clicks: int, message: str | None
) -> tuple[str, list[html.Article] | list[html.Div]]:
    if not message or not message.strip():
        return (
            json.dumps(
                {"error": "Enter a message before running inference."}, indent=2
            ),
            [],
        )

    try:
        answers = run_inference(message.strip())
    except (RuntimeError, TypeError, ValueError) as error:
        return json.dumps({"error": str(error)}, indent=2), []

    result = [asdict(answer) for answer in answers]
    return json.dumps(result, indent=2), [
        render_answer_card(answer) for answer in result
    ]


def render_answer_card(answer: dict[str, Any], subtitle: str = "") -> html.Article:
    key = answer["key"]
    emoji = {
        "wants_refund": "💸",
        "route": "🧭",
        "frustration": "😤",
    }.get(key, "🔎")
    confidence = answer.get("confidence")
    if confidence is None:
        confidence = abs(float(answer["noul"]) - 0.5) * 2
    confidence = max(0.0, min(1.0, float(confidence)))
    hue = round(confidence * 125)
    color = f"hsl({hue}, 55%, 38%)"
    title = "Yes/No decision" if "noul" in answer else key

    details = []
    for name, value in answer.items():
        if name in {"key", "confidence"}:
            continue
        if name == "probabilities" and isinstance(value, dict):
            label = name.replace("_", " ").title()
            display = html.Div(
                [
                    html.Div(
                        [
                            html.Div(
                                [
                                    html.Span(option),
                                    html.Span(f"{probability:.0%}"),
                                ],
                                style={
                                    "display": "flex",
                                    "justifyContent": "space-between",
                                    "gap": "8px",
                                    "fontSize": "13px",
                                },
                            ),
                            html.Div(
                                html.Div(
                                    style={
                                        "width": f"{max(0.0, min(1.0, float(probability))) * 100:.1f}%",
                                        "height": "100%",
                                        "backgroundColor": "#2878b5",
                                    }
                                ),
                                style={
                                    "height": "7px",
                                    "marginTop": "5px",
                                    "overflow": "hidden",
                                    "borderRadius": "4px",
                                    "backgroundColor": "#dce5e1",
                                },
                            ),
                        ],
                        style={"marginTop": "10px"},
                    )
                    for option, probability in value.items()
                ]
            )
        elif isinstance(value, dict):
            label = name.replace("_", " ").title()
            display = json.dumps(value, indent=2)
        elif name == "noul":
            if value < 0.2:
                noul_text = "Definitely no"
            elif 0.2 <= value <= 0.3:
                noul_text = "Leaning towards no"
            elif 0.3 <= value <= 0.5:
                noul_text = "Undecided between yes/no"
            elif 0.5 <= value <= 0.7:
                noul_text = "Leaning towards yes"
            elif 0.7 <= value:
                noul_text = "Definitely yes"

            display = noul_text
            label = ""
        elif isinstance(value, float):
            label = name.replace("_", " ").title()
            display = f"{value:.3f}"
        else:
            label = name.replace("_", " ").title()
            display = str(value)

        if name in {"choice", "score", "noul"}:
            value_display = html.Div(
                display,
                style={
                    "marginTop": "4px",
                    "fontSize": "26px",
                    "fontWeight": 700,
                    "lineHeight": 1.2,
                    "color": "#183c39",
                    "overflowWrap": "anywhere",
                },
            )
        elif isinstance(display, str):
            value_display = html.Pre(
                display,
                style={
                    "margin": "4px 0 0",
                    "whiteSpace": "pre-wrap",
                    "overflowWrap": "anywhere",
                    "fontFamily": "monospace" if isinstance(value, dict) else "inherit",
                    "fontSize": "13px",
                },
            )
        else:
            value_display = display

        details.append(
            html.Div(
                (
                    [html.Span(label, style={"fontWeight": 700, "color": "#526663"})]
                    if label
                    else []
                )
                + [value_display],
                style={"padding": "10px 0", "borderTop": "1px solid #dce5e1"},
            )
        )

    return html.Article(
        [
            html.Header(
                [
                    html.H3(
                        f"{emoji}  {title}",
                        style={"margin": 0, "fontSize": "17px"},
                    ),
                    html.Span(
                        f"{confidence:.0%} confidence",
                        style={
                            "padding": "5px 8px",
                            "borderRadius": "3px",
                            "backgroundColor": f"hsl({hue}, 55%, 90%)",
                            "color": color,
                            "fontSize": "12px",
                            "fontWeight": 700,
                            "whiteSpace": "nowrap",
                        },
                    ),
                ],
                style={
                    "display": "flex",
                    "justifyContent": "space-between",
                    "alignItems": "center",
                    "gap": "12px",
                    "marginBottom": "8px",
                },
            ),
            *(
                [
                    html.P(
                        subtitle,
                        style={
                            "margin": "0 0 8px",
                            "color": "#526663",
                            "fontSize": "14px",
                            "lineHeight": 1.5,
                        },
                    )
                ]
                if "noul" in answer and subtitle
                else []
            ),
            *details,
        ],
        style={
            "minWidth": 0,
            "padding": "16px",
            "border": f"1px solid hsl({hue}, 40%, 78%)",
            "borderLeft": f"5px solid {color}",
            "borderRadius": "4px",
            "backgroundColor": f"hsl({hue}, 50%, 97%)",
            "boxShadow": "0 2px 8px rgb(24 60 57 / 6%)",
        },
    )


if __name__ == "__main__":
    app.run(debug=True)
