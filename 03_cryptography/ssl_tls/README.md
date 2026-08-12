# SSL/TLS con autenticazione mutua (mTLS)

Questo laboratorio dimostra l'implementazione di una comunicazione sicura tramite **TLS con autenticazione reciproca (mutual TLS)** tra un server e un client, utilizzando Python e la libreria standard `ssl`.

## Scopo

- Generare una **Certificate Authority (CA)** self-signed e certificati firmati per server e client.
- Configurare un server e un client che si autenticano a vicenda tramite certificati.
- Testare due diverse implementazioni:
  1. **Script all-in-one**: scambio singolo di un messaggio (porta 4433).
  2. **Script base**: scambio interattivo di più messaggi con echo in maiuscolo (porta 8080).

## Prerequisiti

- **Python 3.7+** (consigliato 3.10+)
- Libreria `cryptography` (per la generazione dei certificati)

Installa la dipendenza con:

```
pip install cryptography
```

## Struttura dei file

Tutti i file vanno collocati nella **stessa cartella** (ad esempio `~/Desktop/ssl_lab/`).  
Sono presenti i seguenti script:

- `server_client_cert_gen.py` – script all-in-one per generare certificati, avviare server e client.
- `secure_socket_server.py` – server base con echo in maiuscolo.
- `secure_socket_client.py` – client base interattivo.

## Procedura

### 1. Generazione dei certificati (solo sul server)

Sulla macchina che farà da **server** (es. Kali), esegui:

```
python3 server_client_cert_gen.py gen_certs
```

Verranno creati i file:

- `ca_cert.pem`, `ca_key.pem`
- `server_cert.pem`, `server_key.pem`
- `client_cert.pem`, `client_key.pem`

### 2. Trasferimento dei certificati al client

Dal server, avvia un server HTTP temporaneo per condividere i file:

```
python3 -m http.server 8000
```

Sul **client** (es. Lubuntu), scarica i tre file necessari:

```
wget http://<IP_SERVER>:8000/ca_cert.pem
wget http://<IP_SERVER>:8000/client_cert.pem
wget http://<IP_SERVER>:8000/client_key.pem
```

Sostituisci `<IP_SERVER>` con l'IP effettivo del server (es. `192.168.23.128`).

### 3. Test con lo script all-in-one (porta 4433)

**Sul server**:

```
python3 server_client_cert_gen.py server <IP_SERVER>
```

**Sul client**:

```
python3 server_client_cert_gen.py client <IP_SERVER>
```

Il client invia il messaggio `Ciao dal client!` e il server risponde con `Messaggio ricevuto dal server!`.

### 4. Test con gli script base (porta 8080)

**Sul server** (ferma il precedente con `Ctrl+C`):

```
python3 secure_socket_server.py
```

**Sul client**:

```
python3 secure_socket_client.py --host <IP_SERVER>
```

Il client permette di inviare più messaggi; il server li restituisce in **maiuscolo**.  
Per uscire, premi **Invio** senza scrivere nulla.

## Output attesi

### All-in-one
- **Server**: `Connessione accettata... Client autenticato: client.example.com`  
- **Client**: `Connesso al server: server.example.com` e la risposta.

### Script base
- **Server**: `handshake TLS OK - versione: TLSv1.3` e i messaggi ricevuti.
- **Client**: `TLS ok - versione: TLSv1.3`, prompt per i messaggi e risposte in maiuscolo.