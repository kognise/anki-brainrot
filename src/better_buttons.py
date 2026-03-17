from aqt.overview import Overview
from .util import get_ease_colors
from aqt.theme import theme_manager
from aqt.toolbar import BottomBar
import json
from aqt.reviewer import ReviewerBottomBar
from typing import Union
from aqt.webview import WebContent
from aqt import gui_hooks, mw

STYLE_ID = "dev-kognise-brainrot-styles"

def get_shared_styles() -> str:
    return """
        button {
            box-sizing: border-box;
            padding: 8px 14px;
            height: 36px;
            border-radius: 6px !important;
            margin: 0 6px 10px !important;
            border: none;
            font-size: 14px !important;
        }

        button:hover {
            border: none;
        }

        .nightMode button {
            background: #3a3a3a;
        }

        .nightMode button:hover {
            background: #555555;
        }
    """

def get_answer_bar_styles() -> str:
    return get_shared_styles() + """
        #ansbut {
            width: calc(84px * 4 + 12px * 3);
            margin-top: -2px !important;
        }

        button[onclick*="ease"] {
            color: var(--dev-kognise-brainrot--accent);
            min-width: 84px;
        }

        button[onclick*="ease"]:hover {
            background: var(--dev-kognise-brainrot--accent) !important;
            color: #3a3a3a;
        }

        button[onclick*="ease1"] {
            --dev-kognise-brainrot--accent: %(again_color)s;
        }

        button[onclick*="ease2"] {
            --dev-kognise-brainrot--accent: %(hard_color)s;
        }

        button[onclick*="ease3"] {
            --dev-kognise-brainrot--accent: %(good_color)s;
        }

        button[onclick*="ease4"] {
            --dev-kognise-brainrot--accent: %(easy_color)s;
        }
    """ % get_ease_colors()

def get_main_bar_styles() -> str:
    return get_shared_styles()

def get_overview_styles() -> str:
    return get_shared_styles()

# Style application
def apply_main_bar_styles() -> None:
    BottomBar._centerBody += f"""
        <style>
            {get_main_bar_styles()}
        </style>
    """

apply_main_bar_styles()

def on_webview_will_set_content(web_content: WebContent, context: Union[object, None]):
    if isinstance(context, ReviewerBottomBar):
        web_content.head += f"""
            <style id="{STYLE_ID}">
                {get_answer_bar_styles()}
            </style>
        """
    elif isinstance(context, Overview):
        web_content.head += f"""
            <style id="{STYLE_ID}">
                {get_overview_styles()}
            </style>
        """

gui_hooks.webview_will_set_content.append(on_webview_will_set_content)

def theme_did_change():
    mw.bottomWeb.eval(f"""
        document.querySelector("#{STYLE_ID}").textContent = {json.dumps(get_answer_bar_styles())}
    """)
    mw.overview.web.eval(f"""
        document.querySelector("#{STYLE_ID}").textContent = {json.dumps(get_overview_styles())}
    """)
    apply_main_bar_styles()

gui_hooks.theme_did_change.append(theme_did_change)