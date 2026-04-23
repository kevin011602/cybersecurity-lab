# Hybrid RSA-AES Secure Communication Protocol

Questo progetto implementa un protocollo di comunicazione sicura semplificato che utilizza:
- RSA (OAEP) per lo scambio sicuro delle chiavi
- AES-256-CTR per la cifratura dei dati
- HMAC-SHA256 per la verifica dell'integrità

Il sistema simula uno schema di cifratura ibrida simile ai protocolli come il TLS.

## Architettura

Client:
1. Genera una chiave di sessione AES
2. Cifra i dati usando AES-CTR
3. Calcola l'HMAC per l'integrità
4. Cifra la chiave AES usando la chiave pubblica RSA
5. Invia il payload al server

Server:
1. Riceve la chiave AES cifrata e il testo cifrato
2. Decifra la chiave AES usando la chiave privata RSA
3. Verifica l'integrità tramite HMAC
4. Decifra i dati usando AES

## Utilizzo

### 1. Generazione delle chiavi
Lato Server:
```bash
openssl genpkey -algorithm RSA -out server_private.pem -pkeyopt rsa_keygen_bits:2048
openssl pkey -in server_private.pem -pubout -out server_public.pem
```

Assicurati che il file `server_public.pem` sia disponibile nella directory del client.

Lato Client:
```bash
echo "Top Secret Message" > test.txt
```

### 2. Esecuzione
Server
```bash
python3 hybrid_server.py
```

Client
```bash
python3 hybrid_client.py
```

## Disclaimer

Questo progetto ha scopi puramente didattici e non implementa un protocollo sicuro pronto per l'uso in ambienti di produzione.