import streamlit as st

from src.config import HOUSES
from src.game_logic import add_player, load_game_state, load_players, new_game

st.set_page_config(page_title="Nuova partita", page_icon="🎲", layout="wide")
st.title("🎲 Nuova partita")

state = load_game_state()
st.write(f"**Partita attiva:** {state.get('game_id') or 'nessuna'}")

with st.expander("Reset completo partita", expanded=state.get("status") != "ACTIVE"):
    st.warning("Questa operazione azzera giocatori e stato di tutte le carte.")
    confirm = st.checkbox("Confermo di voler iniziare una nuova partita")
    if st.button("NUOVA PARTITA", type="primary", disabled=not confirm, use_container_width=True):
        game_id = new_game()
        st.success(f"Nuova partita creata: {game_id}")
        st.rerun()

st.divider()
st.subheader("Aggiungi partecipante")

players = load_players()
used_houses = set(players["house"].tolist()) if not players.empty else set()
available_houses = [h for h in HOUSES if h not in used_houses]

with st.form("add_player", clear_on_submit=True):
    name = st.text_input("Nome partecipante")
    house = st.selectbox("Casata", available_houses, disabled=not available_houses)
    submitted = st.form_submit_button("Salva associazione", type="primary", use_container_width=True)

if submitted:
    try:
        add_player(name, house)
        st.success(f"{name.strip()} associato a {house}.")
        st.rerun()
    except Exception as exc:
        st.error(str(exc))

st.subheader("Partecipanti")
players = load_players()
if players.empty:
    st.caption("Nessun partecipante inserito.")
else:
    st.dataframe(players[["player_name","house"]].rename(columns={"player_name":"Giocatore","house":"Casata"}), hide_index=True, use_container_width=True)
