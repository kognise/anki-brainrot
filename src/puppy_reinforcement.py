from aqt import gui_hooks, QLabel, mw, Qt, QFrame, QPalette, QColor, QTimer, QPropertyAnimation, QPoint
from anki.cards import Card
from .util import addon_path, get_cards_done_today
import os
import random

puppy_dir = os.path.join(addon_path, "assets", "puppies")
puppy_paths = [os.path.join(puppy_dir, file) for file in os.listdir(puppy_dir)]

DURATION_MS = 3000
ENCOURAGE_EVERY = 10
MAX_SPREAD = 5
TOOLTIP_BG = "#AFFFC5"
TOOLTIP_FG = "#000000"
ENCOURAGEMENTS = {
    "low": ["Great job!", "Keep it up!", "Way to go!", "Keep up the good work!"],
    "middle": ["You're on a streak!", "You're crushing it!", "Don't stop now!", "You're doing great!"],
    "high": ["Fantastic job!", "Wow!", "Beautiful!", "Awesome!", "I'm proud of you!"],
    "max": ["Incredible!", "You're on fire!", "Bravo!", "So many cards..."],
}

last_message = None
next_popup_at = None

def next_interval() -> int:
    return 1
    return max(1, ENCOURAGE_EVERY + random.randint(-MAX_SPREAD, MAX_SPREAD))

def random_encouragement(card_count: int) -> str:
    global last_message
    if card_count >= 100:
        options = list(ENCOURAGEMENTS["max"])
    elif card_count >= 50:
        options = list(ENCOURAGEMENTS["high"])
    elif card_count >= 25:
        options = list(ENCOURAGEMENTS["middle"])
    else:
        options = list(ENCOURAGEMENTS["low"])
    if last_message in options and len(options) > 1:
        options.remove(last_message)
    last_message = random.choice(options)
    return last_message

def reviewer_did_show_question(card: Card):
    global next_popup_at

    deck = mw.col.decks.current() if mw.col else None
    if not deck:
        return
    deck_id = deck["id"]

    done_count = get_cards_done_today(deck_id)
    if next_popup_at is None:
        next_popup_at = done_count + next_interval()
    if done_count < next_popup_at:
        return

    puppy_path = random.choice(puppy_paths)
    encouragement = random_encouragement(done_count)
    html = f"""
        <table cellpadding="10">
            <tr>
                <td>
                    <img height="130" src="{puppy_path}">
                </td>
                <td valign="middle">
                    <center>
                        <b>{done_count} {'cards' if done_count != 1 else 'card'} done so far!</b><br>
                        {encouragement}
                    </center>
                </td>
            </tr>
        </table>
    """

    label = QLabel(html, parent=mw)
    label.setFrameStyle(QFrame.Shape.Panel)
    label.setLineWidth(2)
    label.setWindowFlags(Qt.WindowType.ToolTip)
    palette = QPalette()
    palette.setColor(QPalette.ColorRole.Window, QColor(TOOLTIP_BG))
    palette.setColor(QPalette.ColorRole.WindowText, QColor(TOOLTIP_FG))
    label.setPalette(palette)
    label.setAutoFillBackground(True)
    label.setStyleSheet(f"font-size: 16px; line-height: 1.5;")
    label.adjustSize()
    
    parent = mw.app.activeWindow() or mw
    x = 0
    y = parent.height() - label.height() - 100
    label.move(parent.mapToGlobal(parent.rect().topLeft()) + QPoint(x, y))
    label.show()
    animation = QPropertyAnimation(label, b"windowOpacity")
    animation.setStartValue(1.0)
    animation.setEndValue(0.0)
    animation.setDuration(250)
    QTimer.singleShot(DURATION_MS - 250, animation.start)
    QTimer.singleShot(DURATION_MS, label.deleteLater)

    next_popup_at = done_count + next_interval()

gui_hooks.reviewer_did_show_question.append(reviewer_did_show_question)