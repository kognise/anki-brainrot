from .util import migrate_config
migrate_config()

from aqt import mw
mw.addonManager.setWebExports(__name__, r"vendor/.*")

from . import (
    progress_bar,
    sound_effects,
    confetti,
    puppy_reinforcement,
    better_buttons,
    confirmations,
    settings_dialog,
)