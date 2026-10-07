import streamlit as st
from src.game_logic import load_game_state, load_players
from src.ui_helpers import current_player

st.set_page_config(page_title="GOT Card Tracker", page_icon="🐺", layout="wide")
st.title("GOT · Card Tracker")
st.caption("Companion condiviso per le carte Casa.")

state = load_game_state()
players = load_players()

c1, c2, c3 = st.columns(3)
c1.metric("Stato", state.get("status", "NOT_STARTED"))
c2.metric("Game ID", state.get("game_id") or "—")
c3.metric("Giocatori", len(players))

if not players.empty:
    me = current_player(players)
    if me is not None:
        st.success(f"Sessione impostata su **{me['player_name']} · {me['house']}**")
else:
    st.info("Avvia una partita e registra i partecipanti dalla pagina Nuova partita.")

st.markdown("""
### Uso rapido
- **Le mie carte**: usa, riabilita o recupera le tue carte.
- **Avversari**: vista live delle carte degli altri giocatori.
- **Stato partita**: riepilogo globale, cronologia e undo.
""")
