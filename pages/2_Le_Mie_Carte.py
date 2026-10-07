from pathlib import Path
import streamlit as st

from src.config import AVAILABLE, USED
from src.game_logic import (
    house_cards, load_history, load_players, recover_discarded_except,
    reset_house, set_card_status, undo_last_event,
)
from src.ui_helpers import current_player, render_card_image

st.set_page_config(page_title="Le mie carte", page_icon="🃏", layout="wide")
st.markdown("""
<style>
.block-container {padding-top: 1.2rem;}
[data-testid="stMetric"] {border:1px solid rgba(128,128,128,.25);border-radius:14px;padding:10px;}
.card-title {font-size:1.08rem;font-weight:700;margin-bottom:.2rem}
.card-meta {opacity:.75;font-size:.9rem;margin-bottom:.35rem}
.effect {min-height:3.5rem;font-size:.93rem;line-height:1.35}
</style>
""", unsafe_allow_html=True)

st.title("🃏 Le mie carte")
players = load_players()
if players.empty:
    st.info("Aggiungi prima almeno un giocatore.")
    st.stop()

me = current_player(players)
if me is None:
    st.stop()
actor = str(me["player_name"])
house = str(me["house"])
cards = house_cards(house)

st.caption(f"Casata: **{house}**")

available_count = int((cards["status"] == AVAILABLE).sum())
used_count = int((cards["status"] == USED).sum())
m1, m2, m3 = st.columns(3)
m1.metric("Disponibili", available_count)
m2.metric("Usate", used_count)
m3.metric("Totale", len(cards))

history = load_history()
active_events = history[~history["undone"]] if not history.empty else history
undoable = active_events["action"].isin([
    "USE_CARD","USE_CARD_AUTO_RECYCLE","REENABLE_CARD","RESET_HOUSE","SPECIAL_RECOVER"
]).any() if not active_events.empty else False

uc1, uc2 = st.columns(2)
with uc1:
    if st.button("↩️ Annulla ultima modifica", disabled=not undoable, use_container_width=True):
        event = undo_last_event(actor)
        if event:
            st.success("Ultima modifica annullata.")
            st.rerun()
with uc2:
    if st.button("♻️ Recupera tutte le carte", use_container_width=True):
        st.session_state["confirm_reset_house"] = True

if st.session_state.get("confirm_reset_house"):
    st.warning(f"Confermi il recupero di tutte le carte {house}?")
    a, b = st.columns(2)
    if a.button("Conferma recupero", type="primary", use_container_width=True):
        reset_house(house, actor)
        st.session_state.pop("confirm_reset_house", None)
        st.rerun()
    if b.button("Annulla", use_container_width=True):
        st.session_state.pop("confirm_reset_house", None)
        st.rerun()

if st.session_state.get("pending_card"):
    pending = st.session_state["pending_card"]
    st.warning(f"Vuoi davvero usare **{pending['name']}**?")
    a, b = st.columns(2)
    if a.button("Sì, usa la carta", type="primary", use_container_width=True):
        result = set_card_status(pending["id"], USED, actor)
        st.session_state.pop("pending_card", None)
        if result.get("auto_recycled"):
            st.success("Carta usata. Era la settima: le altre 6 carte sono tornate disponibili.")
        st.rerun()
    if b.button("Annulla", use_container_width=True):
        st.session_state.pop("pending_card", None)
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
            render_card_image(row.image_path, used=not available)

            icons = getattr(row, "icons", "")
            if isinstance(icons, str) and icons.strip():
                st.markdown(f"**Icone:** {icons}")

            effect = getattr(row, "effect_summary", "")
            if isinstance(effect, str) and effect.strip():
                st.markdown(f"<div class='effect'><b>Effetto:</b> {effect}</div>", unsafe_allow_html=True)
            else:
                st.markdown("<div class='effect'><b>Effetto:</b> —</div>", unsafe_allow_html=True)

            if available:
                if st.button("Usa carta", key=f"use_{row.card_id}", type="primary", use_container_width=True):
                    st.session_state["pending_card"] = {"id": row.card_id, "name": row.display_name}
                    st.rerun()
            else:
                if st.button("♻️ Riabilita questa carta", key=f"recover_{row.card_id}", use_container_width=True):
                    set_card_status(row.card_id, AVAILABLE, actor)
                    st.rerun()

            if row.card_id == "STARK_03" and not available:
                if st.button("🐺 Roose: ho perso il combattimento", key="roose_lost", use_container_width=True):
                    recover_discarded_except(
                        row.card_id, actor,
                        reason="Roose Bolton: sconfitta, recupera le altre carte Casa scartate",
                    )
                    st.success("Le altre carte Stark scartate sono state recuperate.")
                    st.rerun()
