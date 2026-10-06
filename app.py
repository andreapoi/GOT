import streamlit as st
from src.game_logic import load_game_state, load_players

st.set_page_config(page_title="GOT Card Tracker", page_icon="🐺", layout="wide")

st.title("GOT · Card Tracker")
st.caption("Gestione condivisa delle carte casata per la partita in corso.")

state = load_game_state()
players = load_players()

c1, c2, c3 = st.columns(3)
c1.metric("Stato", state.get("status", "NOT_STARTED"))
c2.metric("Game ID", state.get("game_id") or "—")
c3.metric("Giocatori", len(players))

st.info("Usa il menu laterale per Nuova partita, Le mie carte, Avversari e Stato partita.")
