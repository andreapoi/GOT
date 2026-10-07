import streamlit as st

from src.config import AVAILABLE
from src.game_logic import house_cards, load_players
from src.ui_helpers import current_player, render_card_image

st.set_page_config(page_title="Avversari", page_icon="👁️", layout="wide")
st.markdown("""
<style>
.block-container {padding-top:1.2rem;}
.card-title {font-size:1.05rem;font-weight:700;margin-bottom:.2rem}
.card-meta {opacity:.75;font-size:.88rem;margin-bottom:.3rem}
.effect {min-height:3.3rem;font-size:.91rem;line-height:1.32}
</style>
""", unsafe_allow_html=True)

st.title("👁️ Carte degli avversari")
players = load_players()
if players.empty:
    st.info("Nessun partecipante presente.")
    st.stop()

me = current_player(players)
my_id = str(me["player_id"]) if me is not None else ""
opponents = players[~players["player_id"].astype(str).eq(my_id)]

if opponents.empty:
    st.info("Non ci sono ancora avversari registrati.")
    st.stop()

@st.fragment(run_every="7s")
def opponent_view():
    fresh_players = load_players()
    fresh_opponents = fresh_players[~fresh_players["player_id"].astype(str).eq(my_id)]
    labels = [f"{r.player_name} · {r.house}" for r in fresh_opponents.itertuples()]
    tabs = st.tabs(labels)

    for tab, p in zip(tabs, fresh_opponents.itertuples()):
        with tab:
            cards = house_cards(p.house)
            available_count = int((cards["status"] == AVAILABLE).sum())
            used_count = len(cards) - available_count
            a, b = st.columns(2)
            a.metric("Disponibili", available_count)
            b.metric("Usate", used_count)

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
                        render_card_image(row.image_path, used=not available)
                        icons = getattr(row, "icons", "")
                        if isinstance(icons, str) and icons.strip():
                            st.markdown(f"**Icone:** {icons}")
                        effect = getattr(row, "effect_summary", "")
                        if isinstance(effect, str) and effect.strip():
                            st.markdown(f"<div class='effect'><b>Effetto:</b> {effect}</div>", unsafe_allow_html=True)
                        if not available:
                            st.error("USATA")

opponent_view()
st.caption("↻ Lo stato degli avversari si aggiorna automaticamente ogni 7 secondi.")
