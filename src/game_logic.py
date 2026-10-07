from __future__ import annotations
from datetime import datetime, timezone
from io import StringIO
import json
import uuid

import pandas as pd

from src import github_store
from src.config import AVAILABLE, USED, CARD_STATUS, GAME_STATE, HISTORY, PLAYERS


HISTORY_COLUMNS = [
    "event_id", "game_id", "timestamp", "actor", "action", "house",
    "card_id", "card_name", "details", "undone",
]


def now_iso():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def read_csv(path: str, columns=None) -> pd.DataFrame:
    text = github_store.read_text(path)
    if not text.strip():
        return pd.DataFrame(columns=columns or [])
    return pd.read_csv(StringIO(text))


def write_csv(path: str, df: pd.DataFrame, message: str):
    github_store.write_text(path, df.to_csv(index=False), message)


def load_master() -> pd.DataFrame:
    return read_csv("data/cards_master.csv")


def load_players() -> pd.DataFrame:
    return read_csv(PLAYERS, ["game_id","player_id","player_name","house"])


def load_status() -> pd.DataFrame:
    expected = ["game_id","house","card_id","status","last_used"]
    df = read_csv(CARD_STATUS, expected)
    for column in expected:
        if column not in df.columns:
            df[column] = ""
    df["last_used"] = df["last_used"].fillna("").astype("string")
    return df[expected]


def load_history() -> pd.DataFrame:
    try:
        df = read_csv(HISTORY, HISTORY_COLUMNS)
    except Exception:
        return pd.DataFrame(columns=HISTORY_COLUMNS)
    for column in HISTORY_COLUMNS:
        if column not in df.columns:
            df[column] = ""
    if not df.empty:
        df["undone"] = df["undone"].astype(str).str.lower().eq("true")
    return df[HISTORY_COLUMNS]


def load_game_state() -> dict:
    try:
        return json.loads(github_store.read_text(GAME_STATE))
    except Exception:
        return {"game_id":"","created_at":"","status":"NOT_STARTED"}


def _card_name(card_id: str) -> str:
    master = load_master()
    match = master[master["card_id"].eq(card_id)]
    return match.iloc[0]["display_name"] if not match.empty else card_id


def _snapshot(df: pd.DataFrame, mask) -> list[dict]:
    cols = ["card_id", "status", "last_used"]
    return df.loc[mask, cols].fillna("").to_dict("records")


def _append_history(actor: str, action: str, house: str = "", card_id: str = "",
                    card_name: str = "", details: dict | None = None):
    state = load_game_state()
    history = load_history()
    row = {
        "event_id": uuid.uuid4().hex[:12],
        "game_id": state.get("game_id", ""),
        "timestamp": now_iso(),
        "actor": actor or "",
        "action": action,
        "house": house or "",
        "card_id": card_id or "",
        "card_name": card_name or "",
        "details": json.dumps(details or {}, ensure_ascii=False, separators=(",", ":")),
        "undone": False,
    }
    history = pd.concat([history, pd.DataFrame([row])], ignore_index=True)
    write_csv(HISTORY, history, f"history: {action}")
    return row["event_id"]


def new_game() -> str:
    game_id = datetime.now().strftime("%Y%m%d-%H%M%S") + "-" + uuid.uuid4().hex[:6]
    master = load_master()
    players = pd.DataFrame(columns=["game_id","player_id","player_name","house"])
    status = master[["house","card_id"]].copy()
    status.insert(0, "game_id", game_id)
    status["status"] = AVAILABLE
    status["last_used"] = pd.Series([""] * len(status), dtype="string")
    history = pd.DataFrame(columns=HISTORY_COLUMNS)

    write_csv(PLAYERS, players, f"game: reset players for {game_id}")
    write_csv(CARD_STATUS, status, f"game: reset card status for {game_id}")
    write_csv(HISTORY, history, f"game: reset history for {game_id}")
    state = {"game_id":game_id,"created_at":now_iso(),"status":"ACTIVE"}
    github_store.write_text(GAME_STATE, json.dumps(state, indent=2), f"game: start {game_id}")
    return game_id


def add_player(name: str, house: str):
    name = name.strip()
    if not name:
        raise ValueError("Inserisci il nome del partecipante.")
    state = load_game_state()
    if state.get("status") != "ACTIVE":
        raise ValueError("Avvia prima una nuova partita.")

    df = load_players()
    if not df.empty and house in df["house"].astype(str).tolist():
        raise ValueError(f"La casata {house} è già assegnata.")
    if not df.empty and name.casefold() in df["player_name"].astype(str).str.casefold().tolist():
        raise ValueError("Questo nome è già presente.")

    row = {
        "game_id":state["game_id"],
        "player_id":"P" + uuid.uuid4().hex[:7].upper(),
        "player_name":name,
        "house":house,
    }
    df = pd.concat([df, pd.DataFrame([row])], ignore_index=True)
    write_csv(PLAYERS, df, f"players: add {name} ({house})")


def set_card_status(card_id: str, status: str, actor: str = "") -> dict:
    if status not in (AVAILABLE, USED):
        raise ValueError("Stato carta non valido.")

    df = load_status()
    mask = df["card_id"].eq(card_id)
    if not mask.any():
        raise ValueError("Carta non trovata.")

    house = str(df.loc[mask, "house"].iloc[0])
    card_name = _card_name(card_id)
    house_mask = df["house"].eq(house)
    snapshot = _snapshot(df, house_mask if status == USED else mask)

    df.loc[mask, "status"] = status
    df.loc[mask, "last_used"] = now_iso() if status == USED else ""

    auto_recycled = False
    if status == USED:
        remaining = int((df.loc[house_mask, "status"] == AVAILABLE).sum())
        if remaining == 0:
            # Standard deck cycle: after the seventh card is played, the other
            # six discarded cards return to hand; the just-played card remains discarded.
            other = house_mask & ~mask
            df.loc[other, "status"] = AVAILABLE
            df.loc[other, "last_used"] = ""
            auto_recycled = True

    write_csv(CARD_STATUS, df, f"cards: {card_id} -> {status}")
    action = "USE_CARD_AUTO_RECYCLE" if auto_recycled else ("USE_CARD" if status == USED else "REENABLE_CARD")
    _append_history(
        actor=actor,
        action=action,
        house=house,
        card_id=card_id,
        card_name=card_name,
        details={"before": snapshot, "auto_recycled": auto_recycled},
    )
    return {"auto_recycled": auto_recycled}


def reset_house(house: str, actor: str = ""):
    df = load_status()
    mask = df["house"].eq(house)
    snapshot = _snapshot(df, mask)
    df.loc[mask, "status"] = AVAILABLE
    df.loc[mask, "last_used"] = ""
    write_csv(CARD_STATUS, df, f"cards: reset {house}")
    _append_history(actor, "RESET_HOUSE", house=house, details={"before": snapshot})


def recover_discarded_except(card_id: str, actor: str = "", reason: str = ""):
    df = load_status()
    selected = df["card_id"].eq(card_id)
    if not selected.any():
        raise ValueError("Carta non trovata.")
    house = str(df.loc[selected, "house"].iloc[0])
    house_mask = df["house"].eq(house)
    snapshot = _snapshot(df, house_mask)
    other_used = house_mask & ~selected & df["status"].eq(USED)
    df.loc[other_used, "status"] = AVAILABLE
    df.loc[other_used, "last_used"] = ""
    write_csv(CARD_STATUS, df, f"cards: special recover for {card_id}")
    _append_history(
        actor, "SPECIAL_RECOVER", house=house, card_id=card_id,
        card_name=_card_name(card_id),
        details={"before": snapshot, "reason": reason},
    )


def undo_last_event(actor: str = "") -> dict | None:
    history = load_history()
    state = load_game_state()
    if history.empty:
        return None

    candidates = history[
        history["game_id"].astype(str).eq(str(state.get("game_id", "")))
        & ~history["undone"]
        & history["action"].isin([
            "USE_CARD", "USE_CARD_AUTO_RECYCLE", "REENABLE_CARD",
            "RESET_HOUSE", "SPECIAL_RECOVER",
        ])
    ]
    if candidates.empty:
        return None

    idx = candidates.index[-1]
    event = history.loc[idx]
    try:
        details = json.loads(event["details"]) if isinstance(event["details"], str) else {}
    except Exception:
        details = {}
    before = details.get("before", [])
    if not before:
        return None

    status = load_status()
    for old in before:
        mask = status["card_id"].eq(str(old.get("card_id", "")))
        status.loc[mask, "status"] = old.get("status", AVAILABLE)
        status.loc[mask, "last_used"] = old.get("last_used", "") or ""

    write_csv(CARD_STATUS, status, f"undo: {event['event_id']}")
    history.loc[idx, "undone"] = True
    write_csv(HISTORY, history, f"history: undo {event['event_id']}")
    _append_history(
        actor=actor,
        action="UNDO",
        house=str(event.get("house", "")),
        card_id=str(event.get("card_id", "")),
        card_name=str(event.get("card_name", "")),
        details={"undid_event_id": str(event["event_id"]), "undid_action": str(event["action"])},
    )
    return event.to_dict()


def house_cards(house: str) -> pd.DataFrame:
    master = load_master()
    status = load_status()
    return master[master.house.eq(house)].merge(
        status[status.house.eq(house)], on=["house","card_id"], how="left"
    )
