# Offensive Python Basics

## Struttura

| Cartella | Contenuto |
|----------|-----------|
| `p2p_distributed/` | Nodo peer-to-peer simmetrico per esecuzione di comandi remoti e distribuzione di script. |
| `reverse_shell/` | Client e server per shell inversa con protocollo length-prefix. |
| `scanning/` | Scanner di porte SYN (half-open) ad alte prestazioni con Scapy. |
| `script_delivery_and_execution/` | Server e client per consegna ed esecuzione automatica di script su macchine remote. |

## Script principali

- **`p2p_distributed/p2p_node.py`**  
  Nodo P2P che agisce sia come server che come client. Supporta connessione a peer remoti, invio di messaggi, esecuzione di comandi (con blacklist), invio/esecuzione di script e recupero di informazioni di sistema.

- **`reverse_shell/reverse_shell_server.py`**  
  Server multi-thread in ascolto su una porta, che accetta connessioni da client e fornisce una shell interattiva remota.

- **`reverse_shell/reverse_shell_client.py`**  
  Client che si connette al server e fornisce una shell. Supporta riconnessione automatica con backoff esponenziale e comando `cd`.

- **`scanning/syn_scan.py`**  
  Scanner di porte basato su pacchetti SYN. Offre modalità di scansione (veloce, comune, completa), verifica dell’host tramite ICMP e output colorato con riepilogo.

- **`script_delivery_and_execution/delivery_server.py`**  
  Server che attende connessioni e invia un payload predefinito (script Bash) a ogni client connesso.

- **`script_delivery_and_execution/delivery_client.py`**  
  Client che riceve lo script dal server, lo salva in `/tmp/`, lo rende eseguibile, lo esegue e lo rimuove automaticamente.