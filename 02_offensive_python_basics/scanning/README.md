# SYN Scanner

Scanner di porte TCP basato su pacchetti SYN (half-open scan), realizzato con Scapy per l'analisi e il discovery di servizi di rete.

## Panoramica

Lo script invia pacchetti TCP con flag SYN alle porte target e analizza le risposte per determinare se una porta è:

- **aperta** (risposta SYN-ACK)
- **chiusa** (risposta RST)
- **filtrata** (nessuna risposta o ICMP di errore)

La scansione è **half-open**: la connessione non viene mai completata, il che rende l'attività più veloce e meno invasiva.

## Utilizzo

`sudo python3 syn_scan.py <IP> [opzioni]`

### Opzioni disponibili

| Opzione | Descrizione |
|---------|-------------|
| `--quick` | Scansiona le porte da 1 a 1024 (modalità predefinita) |
| `--common` | Scansiona le 100 porte più comunemente utilizzate |
| `--full` | Scansiona tutte le 65535 porte (più lenta) |

### Esempi

```
# Scansione rapida (1-1024)
sudo python3 syn_scan.py 192.168.188.132

# Scansione delle porte più comuni
sudo python3 syn_scan.py 192.168.188.132 --common

# Scansione completa di tutte le porte
sudo python3 syn_scan.py 192.168.188.132 --full
```

## Funzionamento

1. **ICMP probe** – verifica che l'host target sia raggiungibile (anche in caso di mancata risposta, la scansione prosegue).
2. **Scansione a batch** – le porte vengono analizzate in gruppi per ottimizzare i tempi di esecuzione.
3. **RST packet** – per ogni porta aperta viene inviato un pacchetto RST per chiudere la connessione half-open e ridurre le tracce lasciate.
4. **Riepilogo finale** – al termine viene mostrato il numero di porte aperte, chiuse e filtrate, con il tempo totale impiegato.

## Note

> **⚠️ ATTENZIONE**: Lo script richiede **privilegi di root** per l'invio di pacchetti raw. In alcune reti, firewall o sistemi IDS/IPS possono rilevare e bloccare le scansioni SYN. Utilizzare esclusivamente in ambienti di laboratorio o su sistemi di cui si ha esplicita autorizzazione.