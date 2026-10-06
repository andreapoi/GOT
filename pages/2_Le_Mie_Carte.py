from pathlib import Path
import streamlit as st

from src.config import AVAILABLE, USED
from src.game_logic import house_cards, load_players, reset_house, set_card_status, set_mandatory

st.set_page_config(page_title="Le mie carte", page_icon="🃏", layout="wide")
st.title("🃏 Le mie carte")

players = load_players()
if players.empty:
    st.info("Aggiungi prima almeno un giocatore.")
    st.stop()

labels = {f"{r.player_name} — {r.house}": r.house for r in players.itertuples()}
choice = st.selectbox("Giocatore / casata", list(labels))
house = labels[choice]
cards = house_cards(house)

available_count = int((cards["status"] == AVAILABLE).sum())
used_count = int((cards["status"] == USED).sum())
m1, m2 = st.columns(2)
m1.metric("Disponibili", available_count)
m2.metric("Usate", used_count)

if st.button("♻️ Recupera tutte le carte della casata", use_container_width=True):
    reset_house(house)
    st.success("Carte ripristinate.")
    st.rerun()

st.divider()

cols = st.columns(3)
for idx, row in enumerate(cards.itertuples()):
    with cols[idx % 3]:
        status = row.status if isinstance(row.status, str) else AVAILABLE
        icon = "🟢" if status == AVAILABLE else "🔴"
        st.subheader(f"{icon} {row.display_name}")
        st.caption(f"Valore {row.strength} · {status}")

        img = Path(row.image_path)
        if img.exists():
            st.image(str(img), use_container_width=True)
        else:
            st.info(f"Immagine non ancora caricata: {row.image_path}")

        mandatory = bool(row.mandatory) if str(row.mandatory) != "nan" else False
        new_mandatory = st.checkbox("Mandatory", value=mandatory, key=f"mandatory_{row.card_id}")
        if new_mandatory != mandatory:
            set_mandatory(row.card_id, new_mandatory)
            st.rerun()

        if status == AVAILABLE:
            if st.button("Segna come utilizzata", key=f"use_{row.card_id}", use_container_width=True):
                set_card_status(row.card_id, USED)
                st.rerun()
        else:
            if st.button("♻️ Recupera questa carta", key=f"recover_{row.card_id}", use_container_width=True):
                set_card_status(row.card_id, AVAILABLE)
                st.rerun()
