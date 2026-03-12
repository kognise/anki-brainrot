from aqt.main import MainWindowState
from typing import Literal, Union
from aqt import QUrl, gui_hooks
from PyQt6.QtMultimedia import QSoundEffect
from .util import addon_path
import os
from aqt.reviewer import Reviewer
from anki.cards import Card

sounds_dir = os.path.join(addon_path, "sounds")
sound_names = [
    "again",
    "easy",
    "good",
    "hard",
    "buried",
    "suspended",
]
finish_sound_names = [
    "nyt",
]

sound_effects: dict[str, QSoundEffect] = {}
for sound_name in sound_names:
    path = os.path.join(sounds_dir, sound_name + ".wav")
    effect = QSoundEffect()
    effect.setSource(QUrl.fromLocalFile(path))
    sound_effects[sound_name] = effect

finish_sound_effects: dict[str, QSoundEffect] = {}
for sound_name in finish_sound_names:
    path = os.path.join(sounds_dir, "finish", sound_name + ".wav")
    effect = QSoundEffect()
    effect.setSource(QUrl.fromLocalFile(path))
    finish_sound_effects[sound_name] = effect
sound_effects["finish"] = finish_sound_effects["nyt"]

# Register GUI hooks
def reviewer_did_answer_card(self: Reviewer, card: Card, ease: Literal[1, 2, 3, 4]):
    if ease == 1:
        sound_name = "again"
    elif ease == 2:
        sound_name = "hard"
    elif ease == 3:
        sound_name = "good"
    elif ease >= 4:
        sound_name = "easy"
    else:
        return

    effect = sound_effects[sound_name]
    effect.play()

gui_hooks.reviewer_did_answer_card.append(reviewer_did_answer_card)

def reviewer_will_bury_card(id: int):
    sound_effects["buried"].play()

gui_hooks.reviewer_will_bury_card.append(reviewer_will_bury_card)

def reviewer_will_suspend_card(id: int):
    sound_effects["suspended"].play()

gui_hooks.reviewer_will_suspend_card.append(reviewer_will_suspend_card)

def state_did_change(new_state: MainWindowState, old_state: MainWindowState):
    if new_state == "overview" and old_state == "review":
        sound_effects["finish"].play()

gui_hooks.state_did_change.append(state_did_change)
