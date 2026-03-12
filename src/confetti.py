from aqt.reviewer import Reviewer
from typing import Literal
from aqt import gui_hooks
from anki.cards import Card

# Register GUI hooks
def reviewer_did_answer_card(reviewer: Reviewer, card: Card, ease: Literal[1, 2, 3, 4]):
    pass

gui_hooks.reviewer_did_answer_card.append(reviewer_did_answer_card)