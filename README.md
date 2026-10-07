# GOT Card Tracker

Companion Streamlit condiviso per gestire le carte Casa durante una partita a **Il Trono di Spade – Il Gioco da Tavolo**.

## V1

La V1 aggiunge alla base funzionante:

- identità del giocatore memorizzata nella sessione;
- carte usate mostrate in scala di grigi con overlay **USATA**;
- conferma prima di usare una carta;
- riabilitazione manuale di ogni singola carta;
- reset dell'intera mano con conferma;
- avversari organizzati in tab giocatore/casata;
- aggiornamento automatico ogni 7 secondi nelle viste condivise;
- cronologia persistente delle azioni;
- **Undo** dell'ultima modifica di stato;
- dashboard globale compatta con tutte le carte;
- riciclo automatico standard: quando viene usata la settima carta, le altre sei tornano disponibili;
- supporto a Roose Bolton: in caso di sconfitta recupera le altre carte Stark scartate.

## Struttura

- `app.py`: home e selezione identità.
- `pages/1_Nuova_Partita.py`: nuova partita e giocatori.
- `pages/2_Le_Mie_Carte.py`: gestione della propria mano.
- `pages/3_Avversari.py`: stato live degli avversari.
- `pages/4_Stato_Partita.py`: dashboard, cronologia e undo.
- `src/game_logic.py`: logica di gioco, history e automazioni.
- `src/github_store.py`: persistenza su GitHub.
- `src/ui_helpers.py`: rendering e componenti UI condivisi.
- `data/cards_master.csv`: anagrafica delle 42 carte.
- `data/players.csv`: giocatori della partita corrente.
- `data/card_status.csv`: stato corrente delle carte.
- `data/history.csv`: cronologia delle azioni.
- `data/game_state.json`: stato della partita.
- `assets/cards/`: immagini delle carte.

## Configurazione Streamlit Cloud

Nei Secrets dell'app:

```toml
GITHUB_TOKEN = "github_pat_..."
GITHUB_REPO = "andreapoi/GOT"
GITHUB_BRANCH = "main"
```

Il token deve avere permesso **Contents: Read and write** sulla repository.

## Avvio locale

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Storage

La V1 usa GitHub come storage condiviso. È adatto al volume limitato di aggiornamenti di una partita da tavolo. Se in futuro serviranno più partite contemporanee o maggiore concorrenza, lo strato storage può essere sostituito con Supabase/Postgres mantenendo quasi invariata la UI.
