from aqt import mw
import os

addon_path = os.path.dirname(__file__)
addon_id = mw.addonManager.addonFromModule(__name__)

def get_cards_done_today(deck_id: int) -> int:
    if not mw.col or not mw.col.db:
        return 0

    try:
        deck_ids = mw.col.decks.deck_and_child_ids(deck_id)
        if not deck_ids:
            return 0

        placeholders = ",".join("?" for _ in deck_ids)
        today_start_ms = int((mw.col.sched.day_cutoff - 86400) * 1000)
        return mw.col.db.scalar(
            f"""
            SELECT COUNT(*)
            FROM revlog
            JOIN cards ON cards.id = revlog.cid
            WHERE revlog.id > ?
              AND (cards.did IN ({placeholders}) OR cards.odid IN ({placeholders}))
            """,
            today_start_ms,
            *deck_ids,
            *deck_ids,
        ) or 0
    except Exception:
        return 0

def get_cards_due_today(deck_id: int) -> int:
    if not mw.col:
        return 0

    deck = mw.col.sched.deck_due_tree(deck_id)
    if not deck:
        return 0
    return deck.review_count + deck.learn_count + deck.new_count * 2