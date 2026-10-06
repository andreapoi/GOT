import streamlit as st
import pandas as pd

from src.config import AVAILABLE
from src.game_logic import house_cards, load_game_state, load_players

st.set_page_config(page_title="Stato partita", page_icon="📊", layout="wide")
st.title("📊 Stato partita")

state = load_game_state()
players = load_players()

st.caption(f"Game ID: {state.get('game_id') or '—'}")

if players.empty:
    st.info("Nessun giocatore presente.")
    st.stop()

rows = []
for p in players.itertuples():
    cards = house_cards(p.house)
    available = int((cards["status"] == AVAILABLE).sum())
    used = len(cards) - available
    status_icons = "".join("🟢" if s == AVAILABLE else "🔴" for s in cards["status"].tolist())
    rows.append({
        "Giocatore": p.player_name,
        "Casata": p.house,
        "Disponibili": available,
        "Usate": used,
        "Carte": status_icons,
    })

df = pd.DataFrame(rows)
st.dataframe(df, hide_index=True, use_container_width=True)

st.subheader("Riepilogo rapido")
for row in rows:
    st.write(f"**{row['Casata']} · {row['Giocatore']}** — {row['Carte']}")
