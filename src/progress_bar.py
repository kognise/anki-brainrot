from aqt.main import MainWindowState
from typing import Union, Optional
from aqt import QProgressBar, Qt, QWidget, gui_hooks, mw, QLabel, colors
from aqt.theme import theme_manager
from aqt.toolbar import TopToolbar
from aqt.webview import WebContent
from anki.cards import Card
from anki.collection import OpChanges
from .util import get_cards_done_today, get_cards_due_today, get_config, config_changed_hooks, get_ease_colors

# Create the widget
bar = QProgressBar()
bar.setTextVisible(False)
bar.setOrientation(Qt.Orientation.Horizontal)
bar.setFixedHeight(20)

def update_style():
    if mw.pm.minimalist_mode():
        bg = theme_manager.var(colors.CANVAS)
    elif mw.state == "review":
        c = theme_manager.qcolor(colors.CANVAS_ELEVATED)
        bg = f"rgba({c.red()}, {c.green()}, {c.blue()}, 0.4)"
    else:
        bg = theme_manager.var(colors.CANVAS_ELEVATED)
    fg = get_ease_colors()["easy_color"]
    bar.setStyleSheet(f"""
        QProgressBar {{
            background-color: {bg};
            border: none;
        }}
        QProgressBar::chunk {{
            background-color: {fg};
            margin: 0px;
        }}
    """)

update_style()

mw.mainLayout.insertWidget(0, bar)

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
    
    # Defer the update so we're slightly more in sync with the webview
    mw.toolbarWeb.evalWithCallback("1", lambda _: update_style())
    update_progress_bar()

gui_hooks.state_did_change.append(state_did_change)

def theme_did_change():
    update_style()

gui_hooks.theme_did_change.append(theme_did_change)

def body_classes_need_update():
    update_style()

gui_hooks.body_classes_need_update.append(body_classes_need_update)

def webview_will_set_content(web_content: WebContent, context):
    # Clip the top shadow from the toolbar so it merges with the progress bar
    if isinstance(context, TopToolbar):
        web_content.head += """
            <style>
                .toolbar {
                    clip-path: inset(0 -10px -10px -10px) !important;
                    transition: none !important;
                }
            </style>
        """

gui_hooks.webview_will_set_content.append(webview_will_set_content)

# Config hook
def config_changed():
    global enabled
    enabled = get_config()["progress_bar"]["enabled"]
    bar.setVisible(enabled)
    if enabled:
        update_progress_bar()

config_changed()
config_changed_hooks.append(config_changed)