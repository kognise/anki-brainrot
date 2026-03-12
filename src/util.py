from aqt import mw
import os

addon_path = os.path.dirname(__file__)
addon_id = mw.addonManager.addonFromModule(__name__)
