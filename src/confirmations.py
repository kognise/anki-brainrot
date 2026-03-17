from .util import get_ease_colors, get_config
from typing import Literal
from aqt import gui_hooks, QParallelAnimationGroup
from aqt.reviewer import Reviewer
from anki.cards import Card
from aqt import QLabel, QPropertyAnimation, QSequentialAnimationGroup, QPauseAnimation, Qt, QPoint, QRect, mw

CONFIRMATION_TEXT = {
    1: "Again!",
    2: "Hard!",
    3: "Good!",
    4: "Easy!",
}
CONFIRMATION_X_OFFSETS = {
    1: -160,
    2: -55,
    3: 55,
    4: 160,
}

DURATION_MS = 900
BOTTOM_OFFSET = 120

def show_confirmation_label(
    text: str,
    color: str,
    x_offset: int,
) -> None:
    # Create a temp label to render to a pixmap that we can animate the scale of
    temp_label = QLabel(text)
    temp_label.setStyleSheet(f"""
        color: {color};
        font-size: 25px;
        background-color: transparent;
    """)
    temp_label.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
    temp_label.adjustSize()
    pixmap = temp_label.grab()

    # Create the actual label
    label = QLabel(parent=mw)
    label.setPixmap(pixmap)
    label.setScaledContents(True)
    label.setWindowFlags(Qt.WindowType.ToolTip | Qt.WindowType.FramelessWindowHint)
    label.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
    label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)

    # Calculate the size and position
    base_w = pixmap.width()
    base_h = pixmap.height()

    x = (mw.width() - base_w) // 2 + x_offset
    y = mw.height() - base_h - BOTTOM_OFFSET
    base_pos = mw.mapToGlobal(mw.rect().topLeft()) + QPoint(x, y)

    # Helper to keep the label centered when animating the scale
    def get_rect_for_scale(scale: float) -> QRect:
        w = int(base_w * scale)
        h = int(base_h * scale)
        rx = base_pos.x() + (base_w - w) // 2
        ry = base_pos.y() + (base_h - h) // 2
        return QRect(rx, ry, w, h)

    # Animations time!

    # Animation 1: zoom the label in
    scale_anim = QPropertyAnimation(label, b"geometry", label)
    scale_anim.setDuration(DURATION_MS)
    scale_anim.setStartValue(get_rect_for_scale(0.6))
    scale_anim.setEndValue(get_rect_for_scale(1))

    # Animation 2: fade out after a delay
    fade_out = QPropertyAnimation(label, b"windowOpacity", label)
    fade_out.setDuration(int(DURATION_MS * 0.4))
    fade_out.setStartValue(1.0)
    fade_out.setEndValue(0.0)

    fade_seq = QSequentialAnimationGroup(label)
    fade_seq.addAnimation(QPauseAnimation(int(DURATION_MS * 0.6)))
    fade_seq.addAnimation(fade_out)

    # Run those two in parallel
    main_group = QParallelAnimationGroup(label)
    main_group.addAnimation(scale_anim)
    main_group.addAnimation(fade_seq)

    label.show()
    main_group.finished.connect(label.deleteLater)
    main_group.start()

def reviewer_did_answer_card(reviewer: Reviewer, card: Card, ease: Literal[1, 2, 3, 4]):
    if not get_config()["confirmation_popups"]["enabled"]:
        return
    
    ease_colors = get_ease_colors()
    color = {
        1: ease_colors["again_color"],
        2: ease_colors["hard_color"],
        3: ease_colors["good_color"], 
        4: ease_colors["easy_color"],
    }[ease]
    show_confirmation_label(
        text=CONFIRMATION_TEXT[ease],
        color=color,
        x_offset=CONFIRMATION_X_OFFSETS[ease],
    )

gui_hooks.reviewer_did_answer_card.append(reviewer_did_answer_card)