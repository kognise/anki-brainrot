from aqt.main import MainWindowState
from typing import Union
from aqt import QProgressBar, Qt, QWidget, QDockWidget, gui_hooks, mw, QLabel
from anki.cards import Card
from anki.collection import OpChanges
from .util import get_cards_done_today, get_cards_due_today

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

    bar.setRange(0, total)
    bar.setValue(min(done_count, total))

# Register GUI hooks
def reviewer_did_show_question(card: Card):
    update_progress_bar()

gui_hooks.reviewer_did_show_question.append(reviewer_did_show_question)

def operation_did_execute(changes: OpChanges, handler: Union[object, None]):
    if changes.study_queues:
        update_progress_bar()

gui_hooks.operation_did_execute.append(operation_did_execute)

def state_did_change(new_state: MainWindowState, old_state: MainWindowState):
    update_progress_bar()

gui_hooks.state_did_change.append(state_did_change)