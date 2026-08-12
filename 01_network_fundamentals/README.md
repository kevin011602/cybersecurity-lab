# Network Fundamentals

## Struttura

| Cartella | Contenuto |
|----------|-----------|
| `arp/` | ARP spoofing, poisoning e scansione di rete. |
| `bettercap/` | Automazione di attacchi MITM con Bettercap (ARP spoofing, SSL stripping, HSTS hijack). |
| `icmp/` | Generazione e analisi di pacchetti ICMP (ping). |
| `mac/` | Modifica dell'indirizzo MAC su interfacce Linux. |
| `masscan/` | Cheat sheet e note per l'utilizzo di Masscan. |
| `netdiscover/` | Scansione ARP per il discovery di host attivi sulla rete locale. |
| `nmap/` | Cheat sheet e note per l'utilizzo di Nmap. |
| `packet_analysis/` | Ispezione di pacchetti IP con Scapy (senza invio). |

## Script principali

- **`arp_mitm_tool.py`** – Strumento completo per ARP poisoning con discovery automatica dei MAC e ripristino della rete.
- **`arp/arp_spoofing.py`** – Versione base di spoofing ARP con indirizzi hardcoded.
- **`arp/network_arp_scan.py`** – ARP sweep per scoprire host attivi su una rete.
- **`arp/leaving_quietly.py`** – Ripristino delle tabelle ARP dopo uno spoofing.
- **`icmp/icmp_request.py`** – Invio di un ping con IP sorgente personalizzato.
- **`icmp/icmp2_request.py`** – Ping con analisi dettagliata dei campi IP e ICMP.
- **`mac/mac_change.py`** – Cambio MAC con parametri fissi.
- **`mac/mac_change_advanced.py`** – Cambio MAC con supporto a indirizzo casuale e ripristino su interrupt.
- **`bettercap/bettercap_sslstrip.py`** – Automazione dell'attacco MITM via Bettercap.
- **`packet_analysis/ip_packet_inspector.py`** – Creazione e ispezione di un pacchetto IP in memoria.