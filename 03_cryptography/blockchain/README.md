# Blockchain - Implementazione in Python

## Obiettivo

Implementare una blockchain semplificata in Python con Flask per dimostrare i concetti fondamentali delle tecnologie distribuite:

- **Proof of Work** per il consenso distribuito
- **Transazioni** memorizzate in blocchi
- **Consenso distribuito** tra nodi di una rete
- **API REST** per interagire con la blockchain

--

## Prerequisiti

- Python 3.6+
- Librerie: `flask`, `requests` (installabili con `pip install flask requests`)

---

## Cos'è una Blockchain

Una blockchain è un registro distribuito e immutabile composto da una catena di blocchi. Ogni blocco contiene:

- Un indice (posizione nella catena)
- Un timestamp (data e ora di creazione)
- Una lista di transazioni
- Una prova (proof) generata tramite Proof of Work
- L'hash del blocco precedente (che lega i blocchi tra loro)

L'immutabilità è garantita dal fatto che modificare un blocco richiederebbe di ricalcolare tutti i blocchi successivi.

---

## Come Funziona

```
1. Un nodo crea una transazione
         |
         v
2. La transazione viene aggiunta al pool di transazioni in sospeso
         |
         v
3. Un miner esegue il Proof of Work (trova un numero che soddisfa la difficoltà)
         |
         v
4. Viene creato un nuovo blocco contenente le transazioni
         |
         v
5. Il blocco viene aggiunto alla catena
         |
         v
6. I nodi della rete sincronizzano la catena tramite consenso
```

---

## Architettura del Progetto

| File | Descrizione | Porta |
|------|-------------|-------|
| `01_node_8000.py` | Nodo blockchain sulla porta 8000 | 8000 |
| `02_node_8001.py` | Nodo blockchain sulla porta 8001 | 8001 |
| `03_node_8003.py` | Nodo blockchain sulla porta 8003 | 8003 |
| `04_main_blockchain.py` | Script di simulazione che orchesta i nodi | - |

---

## Struttura del Blocco

Ogni blocco è un dizionario con i seguenti campi:

```
{
    `index`: 1,                    # Posizione nella catena
    `timestamp`: 1689657144.0,     # Data/ora di creazione
    `transazioni`: [...],          # Lista di transazioni
    `proof`: 100,                  # Prova generata
    `hash_precedente`: `1`         # Hash del blocco precedente
}
```

## Struttura della Transazione

Ogni transazione contiene:

```
{
    `id`: `ID24`,                  # Identificatore del mittente
    `canale`: `Vendita`,           # Canale di comunicazione
    `dati`: `Villa Milano`,        # Contenuto del messaggio
    `timestamp`: `1689657144`      # Data/ora dell`operazione
}
```

---

## Endpoints API

### 1. Visualizzare la Catena

**GET /chain**

Restituisce l'intera blockchain e la sua lunghezza.

**Esempio:**

`curl http://localhost:8000/chain`

**Risposta:**

```
{
    "catena": [...],
    "lunghezza": 2
}
```

### 2. Creare una Nuova Transazione

**POST /transactions/new**

Aggiunge una nuova transazione al pool di transazioni in sospeso.

**Corpo della richiesta (JSON):**

```
{
    "id": "ID24",
    "canale": "Vendita",
    "dati": "Villa Milano",
    "timestamp": "1689657144"
}
```

**Esempio:**

```
curl -X POST http://localhost:8000/transactions/new \
    -H "Content-Type: application/json" \
    -d `{"id":"ID24","canale":"Vendita","dati":"Villa Milano","timestamp":"1689657144"}`
```

### 3. Mining di un Nuovo Blocco

**GET /mine**

Esegue il Proof of Work e crea un nuovo blocco con le transazioni in sospeso.

**Esempio:**

`curl http://localhost:8000/mine`

**Risposta:**

```
{
    "risposta": "Nuovo blocco creato",
    "index": 3,
    "transazioni": [...],
    "proof": 12345,
    "hash_precedente": "abc123..."
}
```

### 4. Registrare un Nuovo Nodo

**POST /nodes/register**

Aggiunge un nuovo nodo alla rete.

**Corpo della richiesta (JSON):**

```
{
    "node": "http://127.0.0.1:8001"
}
```

**Esempio:**

```
curl -X POST http://localhost:8000/nodes/register \
    -H "Content-Type: application/json" \
    -d `{"node":"http://127.0.0.1:8001"}`
```

### 5. Risolvere Conflitti (Consenso)

**GET /nodes/resolve**

Esegue l'algoritmo di consenso per risolvere conflitti tra nodi. Sostituisce la catena corrente con quella più lunga e valida trovata nella rete.

**Esempio:**

`curl http://localhost:8000/nodes/resolve`

---

## Proof of Work (PoW)

L'algoritmo di Proof of Work trova un numero `n` tale che l'hash di `(ultima_prova + n + ultimo_hash)` inizi con 4 zeri.

```
def validazione_prova(ultima_prova, prova, ultimo_hash):
    supposizione = f`{ultima_prova}{prova}{ultimo_hash}`.encode()
    hash_della_supposizione = hashlib.sha256(supposizione).hexdigest()
    return hash_della_supposizione[:4] == "0000"
```

La difficoltà è impostata su 4 zeri, ma può essere modificata per rendere il mining più o meno difficile.

---

## Algoritmo di Consenso

Quando un nodo si unisce alla rete o rileva un conflitto, esegue l'algoritmo di consenso:

1. Richiede la catena a tutti i nodi vicini
2. Verifica la validità di ogni catena ricevuta
3. Sceglie la catena più lunga e valida
4. Sostituisce la propria catena con quella scelta

```
def algoritmo_per_consenso(self):
    vicini = self.nodi
    nuova_blockchain = None
    max_len = len(self.catena)

    for node in vicini:
        response = requests.get(f'http://{node}/chain')
        if response.status_code == 200:
            lunghezza = response.json()['lunghezza']
            catena = response.json()['catena']
            if lunghezza > max_len and self.validazione_catena(catena):
                max_len = lunghezza
                nuova_blockchain = catena

    if nuova_blockchain:
        self.catena = nuova_blockchain
        return True
    return False
```

---

## Procedura di Simulazione

Lo script `04_main_blockchain.py` esegue automaticamente una simulazione completa:

### Step 1: Avvio del Primo Nodo

`[*] Avvio nodo 8000...`

### Step 2: Verifica Catena Iniziale

```
[*] Catena iniziale nodo 8000:
{
    "catena": [...],
    "lunghezza": 1
}
```

### Step 3: Creazione di una Transazione

`[*] Invio transazione a 8000...`

### Step 4: Mining del Blocco

`[*] Mining su nodo 8000...`

### Step 5: Avvio del Secondo Nodo

`[*] Avvio nodo 8001...`

### Step 6: Registrazione dei Nodi

`[*] Registrazione nodo 8000 presso 8001...`

### Step 7: Nuova Transazione

`[*] Invio transazione a 8001...`

### Step 8: Risoluzione Conflitti

`[*] Risoluzione conflitti su 8001...`

### Step 9: Mining sul Secondo Nodo

`[*] Mining su nodo 8001...`

### Step 10: Sincronizzazione Finale

```
[*] Registrazione nodo 8001 presso 8000...
[*] Risoluzione finale conflitti su 8000...
```

### Step 11: Verifica Finale

```
[*] Catena finale sincronizzata (Nodo 8000):
{
    "catena": [...],
    "lunghezza": 3
}
```

---

## Esecuzione Manuale

### Avviare un Singolo Nodo

`python3 01_node_8000.py`

### Avviare un Nodo su una Porta Specifica

`python3 01_node_8000.py -p 8000`

### Eseguire la Simulazione Completa

`python3 04_main_blockchain.py`

---

## Comandi Chiave

### Verifica della Catena

`curl http://localhost:8000/chain`

### Creazione di una Transazione

```
curl -X POST http://localhost:8000/transactions/new \
    -H "Content-Type: application/json" \
    -d `{"id":"ID24","canale":"Vendita","dati":"Villa Milano","timestamp":"1689657144"}`
```

### Mining

`curl http://localhost:8000/mine`

### Registrazione di un Nodo

```
curl -X POST http://localhost:8000/nodes/register \
    -H "Content-Type: application/json" \
    -d `{"node":"http://127.0.0.1:8001"}`
```

### Consenso

`curl http://localhost:8000/nodes/resolve`

---

## Note di Implementazione

- **Flask**: Framework web utilizzato per esporre le API REST
- **Requests**: Libreria per comunicare tra nodi
- **Hashlib**: Generazione hash SHA-256
- **UUID**: Identificatori univoci per i nodi

---

## Personalizzazione

### Modificare la Difficoltà del PoW

Cambiare il numero di zeri in `validazione_prova`:

```
return hash_della_supposizione[:6] == "000000"  # Più difficile
```

### Aggiungere Più Nodi

Modificare `04_main_blockchain.py` per avviare nodi su porte aggiuntive:

`p8003 = subprocess.Popen(['python3', 'blockchain_8003.py'])`