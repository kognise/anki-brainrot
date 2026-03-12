from aqt.main import MainWindowState
from typing import Union
from aqt import QProgressBar, Qt, QWidget, QDockWidget, gui_hooks, mw
from anki.decks import DeckTreeNode
from anki.cards import Card
from anki.collection import OpChanges

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

# Define update functions
total_by_deck_id: dict[int, int] = {}

def update_progress_bar_with_deck(deck: Union[DeckTreeNode, None]):
    global total_by_deck_id

    if deck is None:
        bar.setRange(0, 1)
        bar.setValue(1)
        return
    
    remaining = deck.review_count + deck.learn_count + deck.new_count * 2
    total = total_by_deck_id[deck.deck_id] = max(total_by_deck_id.get(deck.deck_id, remaining), remaining)
    progress = total - remaining

    bar.setRange(0, total + 1)
    bar.setValue(progress + 1)

def update_progress_bar():
    deck = mw.col.decks.current()
    if deck is None:
        update_progress_bar_with_deck(None)
        return
    deck = mw.col.sched.deck_due_tree(deck["id"])
    update_progress_bar_with_deck(deck)

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