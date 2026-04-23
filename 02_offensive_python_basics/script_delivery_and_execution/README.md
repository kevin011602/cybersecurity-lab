# Script Delivery Simulation Module

Questo modulo simula un meccanismo di consegna script controllato tra un server e un client all'interno di un ambiente di laboratorio isolato.

---

## Panoramica

L'architettura consiste in un server che invia un payload (lo script predefinito) e un client che lo riceve, lo archivia e lo esegue localmente. Questa configurazione fornisce una base pratica per comprendere come funzionano i deployment automatizzati e le esecuzioni remote in un ambiente di rete.

## Componenti

### `delivery_server.py`
Un server TCP responsabile dell'invio del payload dello script predefinito. Resta in ascolto di connessioni in entrata e trasmette i dati dello script a qualsiasi client autenticato o connesso.

### `delivery_client.py`
Il componente lato client che gestisce il ciclo di vita dello script ricevuto:
1. Connessione: Stabilisce un collegamento con il server di consegna.
2. Ricezione: Scarica il payload dello script.
3. Archiviazione: Salva temporaneamente lo script sul file system locale.
4. Esecuzione: Avvia lo script localmente.
5. Pulizia: Rimuove automaticamente lo script dopo l'esecuzione per mantenere l'integrità dell'ambiente.

### `payloads/http_traffic_simulation.sh`
Uno script Bash utilizzato come payload predefinito. Simula la generazione di traffico HTTP a scopo didattico, consentendo agli utenti di osservare i pattern di rete in un ambiente controllato.