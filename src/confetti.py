from aqt.webview import WebContent
import json
from .util import addon_path, addon_id, get_config
import os
from aqt.reviewer import Reviewer
from typing import Literal, Callable, Union, Optional
from aqt import gui_hooks, QWebEngineScript, QWebEnginePage
from anki.cards import Card

base_confetti_options = {
    "particleCount": 200,
    "spread": 100,
    "startVelocity": 70,
    "decay": 0.8,
}
confetti_origins = [
    { "x": 0.1, "y": 1.1 },
    { "x": 0.9, "y": 1.1 },
]

def confetti(reviewer: Reviewer, additional_options: dict = {}):
    for origin in confetti_origins:
        options_json = json.dumps({**base_confetti_options, **additional_options, "origin": origin})
        reviewer.web.eval(f"confetti({options_json})")

def on_webview_will_set_content(web_content: WebContent, context: Optional[object]):
    if context and isinstance(context, Reviewer):
        web_content.js.append(f"/_addons/{addon_id}/vendor/canvas-confetti.min.js")

gui_hooks.webview_will_set_content.append(on_webview_will_set_content)

def reviewer_did_answer_card(reviewer: Reviewer, card: Card, ease: Literal[1, 2, 3, 4]):
    if not get_config()["confetti"]["enabled"]:
        return

    if ease == 3: # Good
        confetti(reviewer, { "ticks": 150 })
    elif ease == 4: # Easy
        confetti(reviewer, { "ticks": 400 })

gui_hooks.reviewer_did_answer_card.append(reviewer_did_answer_card)
