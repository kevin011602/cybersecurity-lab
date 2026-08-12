# Netdiscover - ARP Scanner

## Cos'è Netdiscover

Netdiscover è uno strumento di ricognizione di rete che utilizza il protocollo ARP (Address Resolution Protocol) per scoprire gli host attivi su una rete locale. È particolarmente utile quando:

- Si vuole una **scansione veloce** senza bisogno di privilegi avanzati (usa solo ARP).
- Si è in una rete locale e si vogliono mappare gli IP e i MAC dei dispositivi connessi.
- Si vuole operare in **modalità passiva** per non generare traffico sospetto (ascolta le risposte ARP già in circolazione).

A differenza di `nmap -sn` (ping sweep), `netdiscover` lavora a livello 2 (Link Layer), risultando più affidabile in reti dove i ping ICMP sono bloccati.

---

## Installazione

Su Kali Linux è preinstallato. Su altre distribuzioni:

```
sudo apt update
sudo apt install netdiscover -y
```

## Comandi Principali

### Scansione Attiva (Range IP)

Invia richieste ARP a tutti gli IP del range specificato.

```
sudo netdiscover -r 192.168.1.0/24
```

**Output atteso:**

```
 192.168.1.1        aa:bb:cc:11:22:33      1      60  Router
 192.168.1.10       dd:ee:ff:44:55:66      1      60  Desktop
 192.168.1.15       00:11:22:33:44:55      1      60  Laptop
```

### Scansione da File

Se hai un file di testo con una lista di IP o subnet (uno per riga):

```
sudo netdiscover -f targets.txt
```

### Scansione Passiva

Non invia pacchetti, ma rimane in ascolto per catturare i pacchetti ARP che transitano sulla rete. È molto più silenzioso e difficile da rilevare.

```
sudo netdiscover -p
```

### Selezionare un'interfaccia specifica

```
sudo netdiscover -i eth0 -r 192.168.1.0/24
```

### Salvare i risultati

```
sudo netdiscover -r 192.168.1.0/24 -o scan_netdiscover.txt
```

---

## Opzioni Utili

| Opzione | Descrizione |
|---------|-------------|
| `-r <range>` | Scansiona un range di rete (es. 192.168.1.0/24) |
| `-p` | Modalità passiva (non invia pacchetti) |
| `-i <interfaccia>` | Specifica l'interfaccia di rete (es. eth0, wlan0) |
| `-f <file>` | Legge i target da un file |
| `-n <node>` | Range di IP in notazione inversa (es. -n 192.168.1.0/24) |
| `-o <file>` | Salva l'output in un file di testo |
| `-c` | Mostra l'output con colori (utile per leggibilità) |

---

## Differenze con altri strumenti

| Strumento | Protocollo | Velocità | Rilevabilità | Scopo |
|-----------|------------|----------|--------------|-------|
| Netdiscover | ARP (L2) | Altissima | Media (attivo) / Bassa (passivo) | Mappatura LAN |
| Nmap (`-sn`) | ICMP/TCP (L3) | Media | Alta | Ping sweep |
| Masscan | SYN (L3) | Estrema | Altissima | Scansione porte massiva |

---

## Note

> **⚠️ ATTENZIONE:** L'uso di `netdiscover` in modalità attiva genera traffico di rete ARP che può essere rilevato da sistemi di sicurezza (IDS/IPS) o da switch con protezioni ARP (es. Dynamic ARP Inspection). Utilizza la modalità passiva (`-p`) se vuoi operare in silenzio.