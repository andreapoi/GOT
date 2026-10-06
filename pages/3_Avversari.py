from pathlib import Path
import streamlit as st

from src.config import AVAILABLE
from src.game_logic import house_cards, load_players

st.set_page_config(page_title="Avversari", page_icon="👁️", layout="wide")
st.title("👁️ Carte degli avversari")

players = load_players()
if players.empty:
    st.info("Nessun partecipante presente.")
    st.stop()

labels = {f"{r.player_name} — {r.house}": r.house for r in players.itertuples()}
choice = st.selectbox("Visualizza giocatore", list(labels))
house = labels[choice]
cards = house_cards(house)

cols = st.columns(3)
for idx, row in enumerate(cards.itertuples()):
    with cols[idx % 3]:
        available = row.status == AVAILABLE
        st.subheader(("🟢 " if available else "🔴 ") + row.display_name)
        st.caption(f"Valore {row.strength} · {'DISPONIBILE' if available else 'USATA'}")
        if bool(row.mandatory) if str(row.mandatory) != "nan" else False:
            st.warning("⚠️ Mandatory")

        img = Path(row.image_path)
        if img.exists():
            st.image(str(img), use_container_width=True)
        else:
            st.markdown(f"**{row.card_id}**")
            st.caption("Immagine non ancora caricata")

        if not available:
            st.error("USATA")
