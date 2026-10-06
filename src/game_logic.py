from __future__ import annotations
from datetime import datetime, timezone
from io import StringIO
import json
import uuid

import pandas as pd

from src import github_store
from src.config import AVAILABLE, USED, CARD_STATUS, GAME_STATE, PLAYERS


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
    df = read_csv(
        CARD_STATUS,
        ["game_id","house","card_id","status","mandatory","last_used"],
    )

    # An empty CSV column is otherwise inferred by pandas as float64 (NaN).
    # Keep last_used explicitly textual because it later stores ISO timestamps.
    if "last_used" not in df.columns:
        df["last_used"] = pd.Series(dtype="string")
    else:
        df["last_used"] = df["last_used"].fillna("").astype("string")

    return df


def load_game_state() -> dict:
    try:
        return json.loads(github_store.read_text(GAME_STATE))
    except Exception:
        return {"game_id":"","created_at":"","status":"NOT_STARTED"}


def new_game() -> str:
    game_id = datetime.now().strftime("%Y%m%d-%H%M%S") + "-" + uuid.uuid4().hex[:6]
    master = load_master()
    players = pd.DataFrame(columns=["game_id","player_id","player_name","house"])
    status = master[["house","card_id"]].copy()
    status.insert(0, "game_id", game_id)
    status["status"] = AVAILABLE
    status["mandatory"] = False
    status["last_used"] = pd.Series([""] * len(status), dtype="string")

    write_csv(PLAYERS, players, f"game: reset players for {game_id}")
    write_csv(CARD_STATUS, status, f"game: reset card status for {game_id}")
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


def set_card_status(card_id: str, status: str):
    if status not in (AVAILABLE, USED):
        raise ValueError("Stato carta non valido.")
    df = load_status()
    mask = df["card_id"].eq(card_id)
    if not mask.any():
        raise ValueError("Carta non trovata.")
    df.loc[mask, "status"] = status
    df.loc[mask, "last_used"] = now_iso() if status == USED else ""
    write_csv(CARD_STATUS, df, f"cards: {card_id} -> {status}")


def set_mandatory(card_id: str, mandatory: bool):
    df = load_status()
    mask = df["card_id"].eq(card_id)
    if not mask.any():
        raise ValueError("Carta non trovata.")
    df.loc[mask, "mandatory"] = bool(mandatory)
    write_csv(CARD_STATUS, df, f"cards: mandatory {card_id} -> {mandatory}")


def reset_house(house: str):
    df = load_status()
    mask = df["house"].eq(house)
    df.loc[mask, "status"] = AVAILABLE
    df.loc[mask, "mandatory"] = False
    df.loc[mask, "last_used"] = ""
    write_csv(CARD_STATUS, df, f"cards: reset {house}")


def house_cards(house: str) -> pd.DataFrame:
    master = load_master()
    status = load_status()
    return master[master.house.eq(house)].merge(
        status[status.house.eq(house)], on=["house","card_id"], how="left"
    )
