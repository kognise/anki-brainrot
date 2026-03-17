from aqt.main import MainWindowState
from typing import Union, Optional
from aqt import QProgressBar, Qt, QWidget, QDockWidget, gui_hooks, mw, QLabel
from anki.cards import Card
from anki.collection import OpChanges
from .util import get_cards_done_today, get_cards_due_today, get_config, config_changed_hooks

# Create the widget
bar = QProgressBar()
bar.setTextVisible(False)
bar.setOrientation(Qt.Orientation.Horizontal)
bar.setFixedHeight(20)
bar.setStyleSheet("""
    QProgressBar {
        background-color: transparent;
    }
                    
    QProgressBar::chunk {
        background-color: #3399cc;
        margin: 0px;
    }
""")

widget = QDockWidget()
widget.setWidget(bar)
widget.setTitleBarWidget(QWidget())
mw.addDockWidget(Qt.DockWidgetArea.TopDockWidgetArea, widget)

enabled = False

def update_progress_bar():
    deck = mw.col.decks.current() if mw.col else None
    if not deck:
        bar.setRange(0, 0)
        bar.setValue(0)
        return
    deck_id = deck["id"]

    done_count = get_cards_done_today(deck_id)
    due_count = get_cards_due_today(deck_id)
    total = done_count + due_count

    bar.setRange(0, total + 1)
    bar.setValue(min(done_count, total) + 1)

# Register GUI hooks
def reviewer_did_show_question(card: Card):
    if not enabled:
        return
    update_progress_bar()

gui_hooks.reviewer_did_show_question.append(reviewer_did_show_question)

def operation_did_execute(changes: OpChanges, handler: Optional[object]):
    if not enabled:
        return
    if changes.study_queues:
        update_progress_bar()

gui_hooks.operation_did_execute.append(operation_did_execute)

def state_did_change(new_state: MainWindowState, old_state: MainWindowState):
    if not enabled:
        return
    update_progress_bar()

gui_hooks.state_did_change.append(state_did_change)

# Config hook
def config_changed():
    global enabled
    enabled = get_config()["progress_bar"]["enabled"]
    widget.setVisible(enabled)
    if enabled:
        update_progress_bar()

config_changed()
config_changed_hooks.append(config_changed)