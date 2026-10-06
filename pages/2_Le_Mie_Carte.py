from pathlib import Path
import streamlit as st

from src.config import AVAILABLE, USED
from src.game_logic import house_cards, load_players, reset_house, set_card_status, set_mandatory

st.set_page_config(page_title="Le mie carte", page_icon="🃏", layout="wide")
st.markdown("""
<style>
.block-container {padding-top: 1.5rem;}
[data-testid="stMetric"] {border: 1px solid rgba(128,128,128,.25); border-radius: 14px; padding: 10px;}
.card-title {font-size:1.08rem;font-weight:700;margin-bottom:.2rem}
.card-meta {opacity:.75;font-size:.9rem;margin-bottom:.35rem}
.effect {min-height:3.8rem;font-size:.93rem;line-height:1.35}
</style>
""", unsafe_allow_html=True)

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

m1, m2, m3 = st.columns(3)
m1.metric("Disponibili", available_count)
m2.metric("Usate", used_count)
m3.metric("Totale", len(cards))

if used_count == len(cards) and len(cards):
    st.success("Tutte le carte sono state utilizzate: il mazzo può essere recuperato.")

if st.button("♻️ Recupera tutte le carte della casata", use_container_width=True):
    reset_house(house)
    st.success("Carte ripristinate.")
    st.rerun()

st.divider()

cols = st.columns(3)
for idx, row in enumerate(cards.itertuples()):
    with cols[idx % 3]:
        status = row.status if isinstance(row.status, str) else AVAILABLE
        available = status == AVAILABLE
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

            mandatory = bool(row.mandatory) if str(row.mandatory) != "nan" else False
            new_mandatory = st.checkbox("Mandatory", value=mandatory, key=f"mandatory_{row.card_id}")
            if new_mandatory != mandatory:
                set_mandatory(row.card_id, new_mandatory)
                st.rerun()

            if available:
                if st.button("Usa carta", key=f"use_{row.card_id}", type="primary", use_container_width=True):
                    set_card_status(row.card_id, USED)
                    st.rerun()
            else:
                if st.button("♻️ Recupera carta", key=f"recover_{row.card_id}", use_container_width=True):
                    set_card_status(row.card_id, AVAILABLE)
                    st.rerun()
