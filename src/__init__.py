from aqt import mw

mw.addonManager.setWebExports(__name__, r"vendor/.*js")

from . import progress_bar, sound_effects, confetti