# P2P Distributed Lab Node

Un'implementazione Python di un nodo Peer-to-Peer (P2P) simmetrico progettata per scopi didattici e di test in ambienti di rete isolati. Il sistema permette la gestione distribuita di task, l'esecuzione di comandi remoti e il deploy di script su più target simultaneamente.

## Caratteristiche
- **Architettura P2P Simmetrica**: Ogni nodo agisce contemporaneamente come Server (ascolto) e Client (invio).
- **Remote Command Execution (RCE)**: Esecuzione di comandi shell su nodi remoti con gestione dell'output in tempo reale.
- **Script Deployment**: Funzionalità `send_script` per caricare file `.sh` e automatizzarne l'esecuzione su tutta la rete.
- **System Monitoring**: Raccolta centralizzata di informazioni hardware e di sistema dai peer connessi.
- **Sicurezza Integrata**: Blacklist dei comandi pericolosi (es. `rm -rf`, `reboot`) e isolamento dell'esecuzione nella directory `/tmp`.

## 🛠Architettura del Laboratorio
Il progetto è stato testato con successo nella seguente configurazione:
- **Control Node**: Kali Linux (192.168.188.130)
- **Worker Nodes**: 2x Lubuntu (192.168.188.129, 192.168.188.142)
- **Target**: Metasploitable 2 (192.168.188.132)

## Esempio di Utilizzo
1. **Avvio del nodo:**
   ```bash
   python3 p2p_node.py 8080
   ```

2. **Connessione ai peer:**
	```bash
	connect 192.168.188.129 8080
	connect 192.168.188.142 8080
	```

3. **Distribuzione di uno script di simulazione traffico:**
	```bash
   send_script all ./http_traffic_simulation.sh
   ```

## Disclaimer
Questo software è sviluppato esclusivamente per scopi di ricerca e formazione in ambito cybersecurity. L'uso di questo strumento per attaccare infrastrutture senza autorizzazione preventiva è illegale.

---

## Possibili Sviluppi

### 1. Robustezza del Sistema
* **Cifratura Base**: Utilizzo di una chiave condivisa per cifrare il traffico, impedendo la lettura dei comandi in chiaro tramite sniffer di rete (es. Wireshark).
* **Whitelist Comandi**: Sostituzione della blacklist con una lista chiusa di comandi autorizzati (es. `ls`, `whoami`, `sh`) per limitare il raggio d'azione sui peer.
* **Riconnessione Automatica**: Implementazione di un thread dedicato al tentativo di riconnessione ciclica in caso di caduta di un link tra i peer.

### 2. Estensione della Rete (Forwarding)
* **Relay dei Comandi**: Logica di propagazione dove ogni nodo inoltra i messaggi ricevuti ai propri vicini, estendendo la portata della rete oltre la connessione diretta.
* **Gestione Nodi "Nascosti"**: Utilizzo dei peer connessi come bridge/proxy per raggiungere e comandare macchine situate in sottoreti diverse non visibili dal nodo principale.

### 3. Pulizia e Monitoraggio
* **Nomi File Casuali**: Generazione di nomi temporanei univoci per gli script caricati in `/tmp`, evitando sovrascritture o conflitti durante invii multipli.
* **Segnale di Vita (Keep-alive)**: Invio di pacchetti di heartbeat a intervalli regolari per monitorare lo stato (online/offline) di ogni bot nella rete in tempo reale.