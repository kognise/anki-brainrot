from typing import Optional
from aqt import QAction, qconnect, mw, QDialog
from aqt.qt import QCheckBox, QComboBox, QGroupBox, QHBoxLayout, QLabel, QVBoxLayout, QWidget
from .util import get_config, set_config

FINISH_SOUND_BY_LABEL = {
    "Crossword": "nyt",
    "Victory": "overwatch",
}

class SettingsDialog(QDialog):
    def __init__(self):
        QDialog.__init__(self, mw)
        self.setWindowTitle("Anki Brainrot Settings")
        self.setFixedWidth(500)
        self._is_loading = True

        root_layout = QVBoxLayout(self)
        helper_text = QLabel("""
            <b>Welcome to Anki Brainrot!</b><br>
            <br>
            For the best experience, I recommend disabling "Show remaining card count" and "Show next review time above answer buttons" under the "Review" tab in Anki's settings.
        """, self)
        helper_text.setWordWrap(True)
        helper_text.setStyleSheet("margin-bottom: 12px;")
        root_layout.addWidget(helper_text)

        features_group = QGroupBox("Features", self)
        features_layout = QVBoxLayout(features_group)

        self.confetti_checkbox = QCheckBox("🎊 Confetti", self)
        self.progress_bar_checkbox = QCheckBox("➡️ Progress bar", self)
        self.confirmation_popups_checkbox = QCheckBox("✅ Confirmation popups", self)
        self.puppy_reinforcement_checkbox = QCheckBox("🐶 Puppy reinforcement", self)
        self.sound_effects_checkbox = QCheckBox("🔔 Sound effects", self)

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
        self.deck_completion_sound_label = QLabel("Deck completion sound", self)
        self.deck_completion_sound_select = QComboBox(self)
        self.deck_completion_sound_select.addItems(["Crossword", "Victory"])
        sound_layout.addWidget(self.deck_completion_sound_label)
        sound_layout.addWidget(self.deck_completion_sound_select)

        features_layout.addWidget(make_feature_widget(self.confetti_checkbox))
        features_layout.addWidget(make_feature_widget(self.progress_bar_checkbox))
        features_layout.addWidget(make_feature_widget(self.confirmation_popups_checkbox))
        features_layout.addWidget(make_feature_widget(self.puppy_reinforcement_checkbox))
        features_layout.addWidget(make_feature_widget(self.sound_effects_checkbox, sound_layout))
        root_layout.addWidget(features_group)

        self.deck_completion_sound_label.setEnabled(self.sound_effects_checkbox.isChecked())
        self.deck_completion_sound_select.setEnabled(self.sound_effects_checkbox.isChecked())
        qconnect(
            self.sound_effects_checkbox.toggled,
            self.deck_completion_sound_label.setEnabled,
        )
        qconnect(
            self.sound_effects_checkbox.toggled,
            self.deck_completion_sound_select.setEnabled,
        )

        self._load_config()

        qconnect(self.confetti_checkbox.toggled, self._save_config)
        qconnect(self.progress_bar_checkbox.toggled, self._save_config)
        qconnect(self.confirmation_popups_checkbox.toggled, self._save_config)
        qconnect(self.puppy_reinforcement_checkbox.toggled, self._save_config)
        qconnect(self.sound_effects_checkbox.toggled, self._save_config)
        qconnect(self.deck_completion_sound_select.currentTextChanged, self._save_config)

    def _load_config(self):
        config = get_config()

        self.confetti_checkbox.setChecked(config["confetti"]["enabled"])
        self.progress_bar_checkbox.setChecked(config["progress_bar"]["enabled"])
        self.confirmation_popups_checkbox.setChecked(config["confirmation_popups"]["enabled"])
        self.puppy_reinforcement_checkbox.setChecked(config["puppy_reinforcement"]["enabled"])
        self.sound_effects_checkbox.setChecked(config["sound_effects"]["enabled"])

        saved_finish_sound = config["sound_effects"]["victory_sound"]
        saved_label = next(
            (label for label, value in FINISH_SOUND_BY_LABEL.items() if value == saved_finish_sound),
            "Crossword",
        )
        self.deck_completion_sound_select.setCurrentText(saved_label)
        
        self._is_loading = False

    def _save_config(self, *_):
        if self._is_loading:
            return

        finish_sound = FINISH_SOUND_BY_LABEL[self.deck_completion_sound_select.currentText()]
        set_config({
            "confetti": {"enabled": self.confetti_checkbox.isChecked()},
            "progress_bar": {"enabled": self.progress_bar_checkbox.isChecked()},
            "confirmation_popups": {"enabled": self.confirmation_popups_checkbox.isChecked()},
            "puppy_reinforcement": {"enabled": self.puppy_reinforcement_checkbox.isChecked()},
            "sound_effects": {
                "enabled": self.sound_effects_checkbox.isChecked(),
                "victory_sound": finish_sound,
            },
        })

def open_settings_dialog():
    dialog = SettingsDialog()
    dialog.exec()

action = QAction("Anki Brainrot Settings")
qconnect(action.triggered, open_settings_dialog)
mw.form.menuTools.addAction(action)
mw.addonManager.setConfigAction(__name__, open_settings_dialog)
