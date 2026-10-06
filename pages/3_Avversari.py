from pathlib import Path
import streamlit as st

from src.config import AVAILABLE
from src.game_logic import house_cards, load_players

st.set_page_config(page_title="Avversari", page_icon="👁️", layout="wide")
st.markdown("""
<style>
.block-container {padding-top: 1.5rem;}
.card-used {opacity:.52; filter: grayscale(1);}
.card-title {font-size:1.08rem;font-weight:700;margin-bottom:.2rem}
.card-meta {opacity:.75;font-size:.9rem;margin-bottom:.35rem}
.effect {min-height:3.8rem;font-size:.93rem;line-height:1.35}
</style>
""", unsafe_allow_html=True)

st.title("👁️ Carte degli avversari")
players = load_players()
if players.empty:
    st.info("Nessun partecipante presente.")
    st.stop()

labels = {f"{r.player_name} — {r.house}": r.house for r in players.itertuples()}
choice = st.selectbox("Visualizza giocatore", list(labels))
house = labels[choice]
cards = house_cards(house)

available_count = int((cards["status"] == AVAILABLE).sum())
used_count = len(cards) - available_count
m1, m2 = st.columns(2)
m1.metric("Disponibili", available_count)
m2.metric("Usate", used_count)

cols = st.columns(3)
for idx, row in enumerate(cards.itertuples()):
    with cols[idx % 3]:
        available = row.status == AVAILABLE
        with st.container(border=True):
            st.markdown(
                f"<div class='card-title'>{'🟢' if available else '🔴'} {row.display_name}</div>"
                f"<div class='card-meta'>Forza {row.strength} · {'DISPONIBILE' if available else 'USATA'}</div>",
                unsafe_allow_html=True,
            )

            img = Path(row.image_path)
            if img.exists():
                st.image(str(img), use_container_width=True)
            else:
                st.caption(f"🖼️ {row.card_id} · immagine da collegare")

            icons = getattr(row, "icons", "")
            if isinstance(icons, str) and icons.strip():
                st.markdown(f"**Icone:** {icons}")

            effect = getattr(row, "effect_summary", "")
            if isinstance(effect, str) and effect.strip():
                st.markdown(f"<div class='effect'><b>Effetto:</b> {effect}</div>", unsafe_allow_html=True)
            else:
                st.markdown("<div class='effect'><b>Effetto:</b> —</div>", unsafe_allow_html=True)

            if not available:
                st.error("USATA")
