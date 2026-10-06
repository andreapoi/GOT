# GOT Card Tracker

Applicazione Streamlit condivisa per gestire le carte casata durante una partita a **Il Trono di Spade – Il Gioco da Tavolo**.

## Funzioni V0

- Avvio di una nuova partita con reset completo dello stato.
- Associazione univoca giocatore ↔ casata.
- Visualizzazione delle proprie carte.
- Stato carta `AVAILABLE` / `USED`.
- Flag `mandatory`.
- Recupero di una singola carta.
- Reset completo delle carte di una casata.
- Visualizzazione delle carte avversarie.
- Dashboard generale dello stato partita.
- Persistenza condivisa su GitHub.

## Struttura

- `app.py`: home.
- `pages/`: quattro pagine operative.
- `src/game_logic.py`: logica di gioco.
- `src/github_store.py`: persistenza GitHub con controllo SHA/retry.
- `data/cards_master.csv`: anagrafica permanente carte.
- `data/players.csv`: associazioni della partita corrente.
- `data/card_status.csv`: stato corrente delle carte.
- `data/game_state.json`: identificativo/stato partita.
- `assets/cards/`: immagini.

## Configurazione Streamlit Cloud

Aggiungere nei Secrets dell'app:

```toml
GITHUB_TOKEN = "github_pat_..."
GITHUB_REPO = "andreapoi/GOT"
GITHUB_BRANCH = "main"
```

Il token deve avere permesso di scrittura sul repository.

In locale, se i Secrets non sono configurati, l'app legge e scrive direttamente i file locali del clone.

## Avvio locale

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Immagini delle carte

I 42 record del master sono già predisposti per le sei casate. I nomi carta sono placeholder intenzionali finché non colleghiamo definitivamente le immagini generate.

Path attesi, ad esempio:

- `assets/cards/stark/STARK_01.png`
- `assets/cards/lannister/LANNISTER_01.png`

La V0 funziona anche senza immagini, mostrando un placeholder.

## Nota tecnica

GitHub viene usato come storage della V0. È sufficiente per gli aggiornamenti sporadici tipici di un gioco da tavolo; in una V1 lo storage può essere sostituito da Supabase/Postgres senza cambiare sostanzialmente l'interfaccia.
