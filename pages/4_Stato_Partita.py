import pandas as pd
import streamlit as st

from src.config import AVAILABLE
from src.game_logic import house_cards, load_game_state, load_history, load_players, undo_last_event
from src.ui_helpers import card_pill, current_player

st.set_page_config(page_title="Stato partita", page_icon="📊", layout="wide")
st.title("📊 Stato partita")

players = load_players()
me = current_player(players) if not players.empty else None
actor = str(me["player_name"]) if me is not None else ""

@st.fragment(run_every="7s")
def dashboard():
    state = load_game_state()
    fresh_players = load_players()
    st.caption(f"Game ID: {state.get('game_id') or '—'} · aggiornamento automatico ogni 7 s")

    if fresh_players.empty:
        st.info("Nessun giocatore presente.")
        return

    for p in fresh_players.itertuples():
        cards = house_cards(p.house)
        available = int((cards["status"] == AVAILABLE).sum())
        used = len(cards) - available
        with st.container(border=True):
            c1, c2, c3 = st.columns([2,1,1])
            c1.markdown(f"### {p.player_name} · {p.house}")
            c2.metric("Disponibili", available)
            c3.metric("Usate", used)
            pills = "".join(
                card_pill(str(r.display_name), str(r.status) == AVAILABLE)
                for r in cards.itertuples()
            )
            st.markdown(pills, unsafe_allow_html=True)

dashboard()

st.divider()
st.subheader("🕘 Cronologia")

history = load_history()
state = load_game_state()
if history.empty:
    st.caption("Nessuna azione registrata.")
else:
    current = history[history["game_id"].astype(str).eq(str(state.get("game_id","")))].copy()
    current = current.tail(30).iloc[::-1]
    action_labels = {
        "USE_CARD":"ha usato",
        "USE_CARD_AUTO_RECYCLE":"ha usato (riciclo mazzo)",
        "REENABLE_CARD":"ha riabilitato",
        "RESET_HOUSE":"ha recuperato tutte le carte di",
        "SPECIAL_RECOVER":"ha applicato un recupero speciale con",
        "UNDO":"ha annullato l'ultima modifica su",
    }
    for row in current.itertuples():
        action = action_labels.get(str(row.action), str(row.action))
        target = str(row.card_name) if str(row.card_name) not in ("", "nan") else str(row.house)
        prefix = "↩️ " if str(row.action) == "UNDO" else ""
        if bool(row.undone):
            prefix = "~~"
            suffix = "~~"
        else:
            suffix = ""
        st.markdown(f"{prefix}**{row.actor or 'Sistema'}** {action} **{target}** · {row.timestamp}{suffix}")

    active = current[~current["undone"]] if "undone" in current.columns else current
    can_undo = active["action"].isin([
        "USE_CARD","USE_CARD_AUTO_RECYCLE","REENABLE_CARD","RESET_HOUSE","SPECIAL_RECOVER"
    ]).any() if not active.empty else False

    if st.button("↩️ Annulla ultima modifica", disabled=not can_undo, use_container_width=True):
        event = undo_last_event(actor)
        if event:
            st.success("Ultima modifica annullata.")
            st.rerun()
