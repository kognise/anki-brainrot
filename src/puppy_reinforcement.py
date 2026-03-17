from aqt import gui_hooks, QLabel, mw, Qt, QFrame
from anki.cards import Card
from .util import addon_path, addon_id
import os

puppy_dir = os.path.join(addon_path, "assets", "puppies")
puppy_paths = []
for file in os.listdir(puppy_dir):
    puppy_paths.append(os.path.join(puppy_dir, file))

def reviewer_did_show_question(card: Card):
    count = 10
    puppy_path = puppy_paths[0]
    encouragement = "UwU"
    html = f"""
        <table cellpadding="10">
            <tr>
                <td>
                    <img height="130" src="{puppy_path}">
                </td>
                <td valign="middle">
                    <center>
                        <b>{count} {'cards' if count > 1 else 'card'} done so far!</b><br>
                        {encouragement}
                    </center>
                </td>
            </tr>
        </table>
    """

    label = QLabel(html, parent=mw)
    label.setFrameStyle(QFrame.Shape.Panel)
    label.setLineWidth(2)
    label.setWindowFlags(Qt.WindowType.ToolTip)
    label.show()

gui_hooks.reviewer_did_show_question.append(reviewer_did_show_question)