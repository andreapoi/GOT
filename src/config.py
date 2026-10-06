from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
CARDS_MASTER = DATA / "cards_master.csv"
PLAYERS = "data/players.csv"
CARD_STATUS = "data/card_status.csv"
GAME_STATE = "data/game_state.json"

HOUSES = ["Stark", "Lannister", "Baratheon", "Greyjoy", "Tyrell", "Martell"]
AVAILABLE = "AVAILABLE"
USED = "USED"
