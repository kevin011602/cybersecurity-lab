# Nmap Cheat Sheet

Una guida essenziale a Nmap da utilizzare nelle attività di penetration testing.

<p align="center">
	<img src="https://nmap.org/images/nmap-logo-256x256.png" alt="Nmap Logo" width="120">
</p>

## Workflow
`Discover ports` → `Enumerate services & scripts` → `Deep analysis / OS` → `Save results`

---

## 1. Discovery (Port Scanning)
Identifica le porte aperte sul target.

```bash
# SYN scan veloce su tutte le 65535 porte
nmap -sS -p- <IP>
```

- `-sS`: Stealth SYN scan (veloce, non completa l'handshake TCP).
- `-p-`: Scansiona tutte le porte (1–65535).

---

## 2. Enumeration & NSE Scripts

Analizza i servizi scoperti ed esegue script di enumeration.

```bash
# Identificazione versioni e script di default su porte specifiche
nmap -sV -sC -p <porte> <IP>

# Enumerazione directory e file su servizi web (porte 80, 443, 5000, etc.)
sudo nmap -sV -p 80,5000 --script http-enum <IP>

# Elencare gli script NSE disponibili nel sistema
ls /usr/share/nmap/scripts/ | grep <servizio>
```

- `-sV`: Identifica la versione dei servizi in esecuzione (es. Apache, OpenSSH).
- `-sC`: Esegue gli script NSE di default per la ricerca di vulnerabilità o info rapide.
- `--script`: Esegue script NSE specifici per arricchire la fase di footprinting.

---

## 3. Deep Analysis & OS Fingerprinting

Analisi approfondita del sistema operativo e della struttura.

```bash
# Rilevamento Operating System e versioni
nmap -sV -O -p <porte> <IP>
```

- `-O`: Tenta di identificare il Sistema Operativo tramite TCP/IP fingerprinting.

---

## 4. UDP Scan

Scansione dei servizi basati su protocollo UDP.

```bash
# Scansione delle 20 porte UDP più comuni
nmap -sU --top-ports 20 <IP>
```

> **Tip:** Aggiungi `-Pn` se il target blocca le richieste ICMP/Ping.

---

## 5. Salvataggio dei Report (Output)

Conservazione dei risultati per analisi successive.

```bash
# Scansione completa salvata in formato standard
nmap -sV -sC -p- -oN scanResults.nmap <IP>
```

- `-oN <filename>`: Salva l'output in formato testo standard.
- `-oX <filename>`: Salva in formato XML (utilissimo per importare in Metasploit o Faraday).
- `-oA <basename>`: Salva contemporaneamente nei 3 formati principali (Normal, XML, Grepable).

---

## 6. Advanced, Timing & Evasion

### Aggressive Scan

```bash
# Scansione completa combinata
nmap -A <IP>
```

- Combina: `-sV`, `-O`, `-sC` e traceroute.
- Richiede privilegi di root. Molto rumorosa e facilmente rilevabile dagli IDS.

### IP Decoy / Evasion

```bash
# Offusca l'IP sorgente mescolandolo con IP civetta
sudo nmap -sV -D <decoy-IP-1,decoy-IP-2,MY-IP,decoy-IP-3> <IP>
```

- `-D`: Invia traffico da più IP falsi per nascondere il vero mittente nei log di sistema.

### Timing Templates (`-T0` - `-T5`)

| Template | Descrizione |
|----------|-------------|
| `-T0 (Paranoid)` | Estremamente lento per eludere gli IDS |
| `-T1 (Sneaky)` | Molto lento |
| `-T2 (Polite)` | Riduce l'impatto sulla banda di rete |
| `-T3 (Normal)` | Velocità predefinita di Nmap |
| `-T4 (Aggressive)` | Veloce e raccomandato nelle CTF o audit interni |
| `-T5 (Insane)` | Estremamente veloce, ad alto rischio di perdita pacchetti |

---

## Note di Sicurezza

> **⚠️ ATTENZIONE**: Nmap è uno strumento potente. Utilizzalo esclusivamente su sistemi di cui si possiede l'autorizzazione scritta. Le scansioni non autorizzate possono essere considerate attività illecite e sono perseguibili per legge.