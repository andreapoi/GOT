from __future__ import annotations
import base64
import html
import mimetypes
from pathlib import Path

import streamlit as st


def current_player(players):
    if players.empty:
        return None

    ids = players["player_id"].astype(str).tolist()
    saved = st.session_state.get("my_player_id")
    default_index = ids.index(saved) if saved in ids else 0

    labels = {
        str(r.player_id): f"{r.player_name} — {r.house}"
        for r in players.itertuples()
    }
    chosen = st.selectbox(
        "Io sono",
        ids,
        index=default_index,
        format_func=lambda x: labels[x],
        key="identity_selector",
    )
    st.session_state["my_player_id"] = chosen
    row = players[players["player_id"].astype(str).eq(str(chosen))]
    return row.iloc[0] if not row.empty else None


def render_card_image(image_path: str, used: bool = False):
    path = Path(image_path)
    if not path.exists():
        st.caption(f"🖼️ {image_path} · immagine non disponibile")
        return

    mime = mimetypes.guess_type(path.name)[0] or "image/png"
    data = base64.b64encode(path.read_bytes()).decode("ascii")
    filter_css = "grayscale(100%) brightness(45%);" if used else "none;"
    overlay = (
        "<div style='position:absolute;inset:0;display:flex;align-items:center;"
        "justify-content:center;font-size:2rem;font-weight:900;color:white;"
        "text-shadow:0 2px 8px black;letter-spacing:.08em;'>USATA</div>"
        if used else ""
    )
    st.markdown(
        f"""
        <div style="position:relative;width:100%;margin:.35rem 0 .65rem 0;">
          <img src="data:{mime};base64,{data}"
               style="width:100%;display:block;border-radius:12px;filter:{filter_css}">
          {overlay}
        </div>
        """,
        unsafe_allow_html=True,
    )


def card_pill(name: str, available: bool) -> str:
    bg = "rgba(46,160,67,.16)" if available else "rgba(220,53,69,.18)"
    border = "rgba(46,160,67,.55)" if available else "rgba(220,53,69,.6)"
    dot = "🟢" if available else "🔴"
    return (
        f"<span title='{html.escape(name)}' style='display:inline-block;margin:3px;"
        f"padding:5px 8px;border-radius:999px;background:{bg};border:1px solid {border};"
        f"font-size:.82rem'>{dot} {html.escape(name)}</span>"
    )
