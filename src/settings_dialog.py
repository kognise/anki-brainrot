from typing import Optional
from aqt import QAction, qconnect, mw, QDialog
from PyQt6.QtMultimedia import QSoundEffect
from aqt.qt import (
    QCheckBox,
    QComboBox,
    QDialogButtonBox,
    QGroupBox,
    QHBoxLayout,
    QIcon,
    QLabel,
    QLayout,
    QPainter,
    QPalette,
    QPixmap,
    QPolygonF,
    QRectF,
    QPointF,
    QSize,
    QSizePolicy,
    QToolButton,
    Qt,
    QVBoxLayout,
    QWidget,
)
from .util import get_config, set_config
from .sound_effects import finish_sound_effects

FINISH_SOUND_BY_LABEL = {
    "Crossword": "nyt",
    "Victory": "overwatch",
}

DIALOG_MIN_WIDTH = 500
PREVIEW_ICON_SIZE = 20

class SettingsDialog(QDialog):
    def __init__(self):
        QDialog.__init__(self, mw)
        self.setWindowTitle("Anki Brainrot Settings")
        self._is_loading = True
        self._preview_effect: Optional[QSoundEffect] = None

        root_layout = QVBoxLayout(self)
        root_layout.setSizeConstraint(QLayout.SizeConstraint.SetFixedSize)
        self.setMinimumWidth(DIALOG_MIN_WIDTH)

        root_margins = root_layout.contentsMargins()
        helper_text_min_width = max(0, DIALOG_MIN_WIDTH - root_margins.left() - root_margins.right())
        helper_text = QLabel("""
            <b>Welcome to Anki Brainrot!</b><br>
            <br>
            For the best experience, I recommend disabling "Show remaining card count" and "Show next review time above answer buttons" under the "Review" tab in Anki's settings.<br>
            <br>
            As always, remember to use FSRS, always press "Again" if you get the card wrong, and suspend the cards that make you hate studying!
        """, self)
        helper_text.setWordWrap(True)
        helper_text.setStyleSheet("margin-bottom: 12px;")
        helper_text.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        helper_text.setMinimumWidth(helper_text_min_width)
        helper_text.setSizePolicy(QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.Maximum)
        root_layout.addWidget(helper_text)

        features_group = QGroupBox("Features", self)
        features_layout = QVBoxLayout(features_group)

        self.confetti_checkbox = QCheckBox("🎊 Confetti", self)
        self.progress_bar_checkbox = QCheckBox("➡️ Progress bar", self)
        self.confirmation_popups_checkbox = QCheckBox("✅ Confirmation popups", self)
        self.sound_effects_checkbox = QCheckBox("🔔 Sound effects", self)
        self.puppy_reinforcement_checkbox = QCheckBox("🐶 Puppy reinforcement", self)

        def make_feature_widget(checkbox: QCheckBox, nested_layout: Optional[QHBoxLayout] = None):
            feature_widget = QWidget(self)
            feature_layout = QVBoxLayout(feature_widget)
            feature_layout.setContentsMargins(0, 0, 0, 0)
            feature_layout.addWidget(checkbox)
            if nested_layout is not None:
                nested_layout.setContentsMargins(20, 0, 0, 0)
                feature_layout.addLayout(nested_layout)
            return feature_widget

        sound_layout = QHBoxLayout()
        sound_layout.setSpacing(2)
        self.deck_completion_sound_label = QLabel("Deck completion sound", self)
        self.deck_completion_sound_select = QComboBox(self)
        self.deck_completion_sound_select.addItems(["Crossword", "Victory"])
        self.deck_completion_sound_preview_button = QToolButton(self)
        self.deck_completion_sound_preview_button.setAutoRaise(True)
        self.deck_completion_sound_preview_button.setToolButtonStyle(
            Qt.ToolButtonStyle.ToolButtonIconOnly
        )
        self.deck_completion_sound_preview_button.setStyleSheet(
            "QToolButton { border: none; background: transparent; padding: 0px; margin: 0px; }"
        )
        self.deck_completion_sound_preview_button.setIconSize(
            QSize(PREVIEW_ICON_SIZE, PREVIEW_ICON_SIZE)
        )
        self._preview_play_icon = self._build_preview_icon(is_playing=False)
        self._preview_stop_icon = self._build_preview_icon(is_playing=True)
        self._set_finish_sound_preview_icon(is_playing=False)
        sound_layout.addWidget(self.deck_completion_sound_label)
        sound_layout.addWidget(self.deck_completion_sound_select)
        sound_layout.addWidget(self.deck_completion_sound_preview_button)

        features_layout.addWidget(make_feature_widget(self.confetti_checkbox))
        features_layout.addWidget(make_feature_widget(self.progress_bar_checkbox))
        features_layout.addWidget(make_feature_widget(self.confirmation_popups_checkbox))
        features_layout.addWidget(make_feature_widget(self.sound_effects_checkbox, sound_layout))
        features_layout.addWidget(make_feature_widget(self.puppy_reinforcement_checkbox))
        root_layout.addWidget(features_group)

        close_button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Close, self)
        close_button = close_button_box.button(QDialogButtonBox.StandardButton.Close)
        if not close_button:
            raise Exception("Could not get close button")
        close_button.setAutoDefault(False)
        qconnect(close_button_box.rejected, self.reject)
        root_layout.addWidget(close_button_box)

        self.deck_completion_sound_label.setEnabled(self.sound_effects_checkbox.isChecked())
        self.deck_completion_sound_select.setEnabled(self.sound_effects_checkbox.isChecked())
        self.deck_completion_sound_preview_button.setEnabled(self.sound_effects_checkbox.isChecked())
        qconnect(
            self.sound_effects_checkbox.toggled,
            self.deck_completion_sound_label.setEnabled,
        )
        qconnect(
            self.sound_effects_checkbox.toggled,
            self.deck_completion_sound_select.setEnabled,
        )
        qconnect(
            self.sound_effects_checkbox.toggled,
            self.deck_completion_sound_preview_button.setEnabled,
        )
        qconnect(
            self.sound_effects_checkbox.toggled,
            self._on_sound_effects_toggled,
        )
        qconnect(
            self.deck_completion_sound_preview_button.clicked,
            self._toggle_finish_sound_preview,
        )
        qconnect(
            self.deck_completion_sound_select.currentTextChanged,
            self._on_finish_sound_selection_changed,
        )

        self._load_config()

        qconnect(self.confetti_checkbox.toggled, self._save_config)
        qconnect(self.progress_bar_checkbox.toggled, self._save_config)
        qconnect(self.confirmation_popups_checkbox.toggled, self._save_config)
        qconnect(self.sound_effects_checkbox.toggled, self._save_config)
        qconnect(self.deck_completion_sound_select.currentTextChanged, self._save_config)
        qconnect(self.puppy_reinforcement_checkbox.toggled, self._save_config)

    def _load_config(self):
        config = get_config()

        self.confetti_checkbox.setChecked(config["confetti"]["enabled"])
        self.progress_bar_checkbox.setChecked(config["progress_bar"]["enabled"])
        self.confirmation_popups_checkbox.setChecked(config["confirmation_popups"]["enabled"])
        self.sound_effects_checkbox.setChecked(config["sound_effects"]["enabled"])

        saved_finish_sound = config["sound_effects"]["victory_sound"]
        saved_label = next(
            (label for label, value in FINISH_SOUND_BY_LABEL.items() if value == saved_finish_sound),
            "Crossword",
        )
        self.deck_completion_sound_select.setCurrentText(saved_label)

        self.puppy_reinforcement_checkbox.setChecked(config["puppy_reinforcement"]["enabled"])
        
        self._is_loading = False

    def _save_config(self, *_):
        if self._is_loading:
            return

        finish_sound = FINISH_SOUND_BY_LABEL[self.deck_completion_sound_select.currentText()]
        set_config({
            "confetti": {"enabled": self.confetti_checkbox.isChecked()},
            "progress_bar": {"enabled": self.progress_bar_checkbox.isChecked()},
            "confirmation_popups": {"enabled": self.confirmation_popups_checkbox.isChecked()},
            "sound_effects": {
                "enabled": self.sound_effects_checkbox.isChecked(),
                "victory_sound": finish_sound,
            },
            "puppy_reinforcement": {"enabled": self.puppy_reinforcement_checkbox.isChecked()},
        })

    def _toggle_finish_sound_preview(self):
        if self._preview_effect:
            self._stop_finish_sound_preview()
            return

        selected_sound_key = FINISH_SOUND_BY_LABEL[self.deck_completion_sound_select.currentText()]
        effect = QSoundEffect(self)
        effect.setSource(finish_sound_effects[selected_sound_key].source())
        qconnect(effect.playingChanged, self._on_preview_effect_playing_changed)
        self._preview_effect = effect
        self._set_finish_sound_preview_icon(is_playing=True)
        effect.play()

    def _stop_finish_sound_preview(self):
        effect = self._preview_effect
        if effect is None:
            return

        self._preview_effect = None
        effect.stop()
        effect.deleteLater()
        self._set_finish_sound_preview_icon(is_playing=False)

    def _on_finish_sound_selection_changed(self, *_):
        self._stop_finish_sound_preview()

    def _on_preview_effect_playing_changed(self):
        sender = self.sender()
        if self._preview_effect is None or sender is not self._preview_effect:
            return

        if not self._preview_effect.isPlaying():
            self._preview_effect.deleteLater()
            self._preview_effect = None
            self._set_finish_sound_preview_icon(is_playing=False)

    def _set_finish_sound_preview_icon(self, is_playing: bool):
        if is_playing:
            self.deck_completion_sound_preview_button.setIcon(self._preview_stop_icon)
            self.deck_completion_sound_preview_button.setToolTip("Stop sound preview")
        else:
            self.deck_completion_sound_preview_button.setIcon(self._preview_play_icon)
            self.deck_completion_sound_preview_button.setToolTip("Preview selected sound")

    def _build_preview_icon(self, is_playing: bool) -> QIcon:
        icon = QIcon()
        normal_color = self.palette().color(QPalette.ColorRole.ButtonText)
        disabled_color = self.palette().color(
            QPalette.ColorGroup.Disabled,
            QPalette.ColorRole.ButtonText,
        )
        icon.addPixmap(
            self._build_preview_pixmap(is_playing=is_playing, color=normal_color),
            QIcon.Mode.Normal,
        )
        icon.addPixmap(
            self._build_preview_pixmap(is_playing=is_playing, color=disabled_color),
            QIcon.Mode.Disabled,
        )
        return icon

    # Attention to detail means we need to draw the play/pause icons ourselves LMAO
    def _build_preview_pixmap(self, is_playing: bool, color) -> QPixmap:
        size = PREVIEW_ICON_SIZE
        dpr = self.devicePixelRatioF()
        pixmap = QPixmap(int(size * dpr), int(size * dpr))
        pixmap.setDevicePixelRatio(dpr)
        pixmap.fill(Qt.GlobalColor.transparent)

        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(color)

        if is_playing:
            rect_side = size * 0.48
            rect_offset = (size - rect_side) / 2
            painter.drawRect(QRectF(rect_offset, rect_offset, rect_side, rect_side))
        else:
            left = size * 0.30
            right = size * 0.74
            top = size * 0.23
            bottom = size * 0.77
            painter.drawPolygon(
                QPolygonF(
                    [
                        QPointF(left, top),
                        QPointF(right, size / 2),
                        QPointF(left, bottom),
                    ]
                )
            )

        painter.end()
        return pixmap

    def _on_sound_effects_toggled(self, enabled: bool):
        if not enabled:
            self._stop_finish_sound_preview()

    def reject(self):
        self._stop_finish_sound_preview()
        super().reject()

def open_settings_dialog():
    dialog = SettingsDialog()
    dialog.exec()

action = QAction("Anki Brainrot Settings")
qconnect(action.triggered, open_settings_dialog)
mw.form.menuTools.addAction(action)
mw.addonManager.setConfigAction(__name__, open_settings_dialog)

if get_config().get("is_first_launch", True):
    set_config({**get_config(), "is_first_launch": False})
    open_settings_dialog()