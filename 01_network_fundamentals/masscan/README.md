# Masscan - Massive Port Scanner

## Cos'è Masscan

Masscan è uno scanner di porte progettato per velocità estrema:

- Verifica se una porta è aperta o chiusa
- Usa pacchetti SYN (half-open scan)
- Non analizza i servizi (a differenza di Nmap)
- Può scansionare Internet intero in pochi minuti

## Installazione

```
sudo apt update
sudo apt install masscan -y
```

Verifica installazione:

`masscan --version`

## Comandi Principali

### Scansione Rapida (CLI)

Scansione di una rete con porte 1-1000:

`sudo masscan 192.168.23.0/24 -p1-1000 --rate=1000 --open-only --exclude 192.168.23.2,192.168.23.128`

Output atteso:

```
Starting masscan 1.3.2 (http://bit.ly/14GZzcT) at 2026-08-08 08:53:22 GMT
Initiating SYN Stealth Scan
Scanning 254 hosts [1000 ports/host]
Discovered open port 139/tcp on 192.168.23.134
Discovered open port 22/tcp on 192.168.23.134
Discovered open port 512/tcp on 192.168.23.134
Discovered open port 80/tcp on 192.168.23.134
Discovered open port 21/tcp on 192.168.23.134
Discovered open port 111/tcp on 192.168.23.134
Discovered open port 514/tcp on 192.168.23.134
Discovered open port 53/tcp on 192.168.23.134
Discovered open port 513/tcp on 192.168.23.134
Discovered open port 445/tcp on 192.168.23.134
Discovered open port 23/tcp on 192.168.23.134
Discovered open port 25/tcp on 192.168.23.134
```

Opzioni principali:

- `-p1-1000` → intervallo di porte
- `--rate=1000` → pacchetti al secondo
- `--open-only` → mostra solo porte aperte
- `--exclude` → IP da escludere (es. gateway e scanner)

### Scansione con File di Configurazione

Crea un file `scan.config`:

```
# velocità (pacchetti al secondo)
rate = 10000

# formato output
output-format = xml
output-status = open
output-filename = scan.xml

# porte (tutte)
ports = 0-65535

# rete target
range = 192.168.23.0/24

# IP da escludere
excludefile = exclude.txt
```

Crea un file `exclude.txt`:

```
192.168.23.2    # gateway/router
192.168.23.128  # Kali (scanner)
```

Esegui la scansione:

`sudo masscan -c scan.config`

Output atteso:

```
exclude.txt: excluding 2 ranges from file
Starting masscan 1.3.2 (http://bit.ly/14GZzcT) at 2026-08-08 09:01:45 GMT
Initiating SYN Stealth Scan
Scanning 254 hosts [65536 ports/host]
```

### Visualizzare i Risultati (XML)

`cat scan.xml`

Output atteso:

```
<?xml version="1.0"?>
<!-- masscan v1.0 scan -->
<nmaprun scanner="masscan" start="1786179772" version="1.0-BETA"  xmloutputversion="1.03">
<scaninfo type="syn" protocol="tcp" />
<host endtime="1786179772"><address addr="192.168.23.134" addrtype="ipv4"/><ports><port protocol="tcp" portid="1524"><state state="open" reason="syn-ack" reason_ttl="64"/></port></ports></host>
<host endtime="1786179885"><address addr="192.168.23.134" addrtype="ipv4"/><ports><port protocol="tcp" portid="21"><state state="open" reason="syn-ack" reason_ttl="64"/></port></ports></host>
<host endtime="1786179893"><address addr="192.168.23.134" addrtype="ipv4"/><ports><port protocol="tcp" portid="48620"><state state="open" reason="syn-ack" reason_ttl="64"/></port></ports></host>
<host endtime="1786179900"><address addr="192.168.23.134" addrtype="ipv4"/><ports><port protocol="tcp" portid="41205"><state state="open" reason="syn-ack" reason_ttl="64"/></port></ports></host>
<host endtime="1786179968"><address addr="192.168.23.134" addrtype="ipv4"/><ports><port protocol="tcp" portid="46521"><state state="open" reason="syn-ack" reason_ttl="64"/></port></ports></host>
<host endtime="1786180192"><address addr="192.168.23.134" addrtype="ipv4"/><ports><port protocol="tcp" portid="53"><state state="open" reason="syn-ack" reason_ttl="64"/></port></ports></host>
<host endtime="1786180220"><address addr="192.168.23.134" addrtype="ipv4"/><ports><port protocol="tcp" portid="22"><state state="open" reason="syn-ack" reason_ttl="64"/></port></ports></host>
<host endtime="1786180287"><address addr="192.168.23.134" addrtype="ipv4"/><ports><port protocol="tcp" portid="23"><state state="open" reason="syn-ack" reason_ttl="64"/></port></ports></host>
<host endtime="1786180334"><address addr="192.168.23.134" addrtype="ipv4"/><ports><port protocol="tcp" portid="6697"><state state="open" reason="syn-ack" reason_ttl="64"/></port></ports></host>
<host endtime="1786180370"><address addr="192.168.23.134" addrtype="ipv4"/><ports><port protocol="tcp" portid="6000"><state state="open" reason="syn-ack" reason_ttl="64"/></port></ports></host>
<host endtime="1786180459"><address addr="192.168.23.134" addrtype="ipv4"/><ports><port protocol="tcp" portid="25"><state state="open" reason="syn-ack" reason_ttl="64"/></port></ports></host>
<host endtime="1786180477"><address addr="192.168.23.134" addrtype="ipv4"/><ports><port protocol="tcp" portid="54974"><state state="open" reason="syn-ack" reason_ttl="64"/></port></ports></host>
<host endtime="1786180478"><address addr="192.168.23.134" addrtype="ipv4"/><ports><port protocol="tcp" portid="5900"><state state="open" reason="syn-ack" reason_ttl="64"/></port></ports></host>
<host endtime="1786180522"><address addr="192.168.23.134" addrtype="ipv4"/><ports><port protocol="tcp" portid="3306"><state state="open" reason="syn-ack" reason_ttl="64"/></port></ports></host>
<host endtime="1786180534"><address addr="192.168.23.134" addrtype="ipv4"/><ports><port protocol="tcp" portid="1099"><state state="open" reason="syn-ack" reason_ttl="64"/></port></ports></host>
<host endtime="1786180539"><address addr="192.168.23.134" addrtype="ipv4"/><ports><port protocol="tcp" portid="2121"><state state="open" reason="syn-ack" reason_ttl="64"/></port></ports></host>
<host endtime="1786180546"><address addr="192.168.23.134" addrtype="ipv4"/><ports><port protocol="tcp" portid="2049"><state state="open" reason="syn-ack" reason_ttl="64"/></port></ports></host>
<host endtime="1786180737"><address addr="192.168.23.134" addrtype="ipv4"/><ports><port protocol="tcp" portid="512"><state state="open" reason="syn-ack" reason_ttl="64"/></port></ports></host>
<host endtime="1786180769"><address addr="192.168.23.134" addrtype="ipv4"/><ports><port protocol="tcp" portid="8180"><state state="open" reason="syn-ack" reason_ttl="64"/></port></ports></host>
<host endtime="1786180779"><address addr="192.168.23.134" addrtype="ipv4"/><ports><port protocol="tcp" portid="6667"><state state="open" reason="syn-ack" reason_ttl="64"/></port></ports></host>
<host endtime="1786180820"><address addr="192.168.23.134" addrtype="ipv4"/><ports><port protocol="tcp" portid="445"><state state="open" reason="syn-ack" reason_ttl="64"/></port></ports></host>
<host endtime="1786180857"><address addr="192.168.23.134" addrtype="ipv4"/><ports><port protocol="tcp" portid="5432"><state state="open" reason="syn-ack" reason_ttl="64"/></port></ports></host>
<host endtime="1786180979"><address addr="192.168.23.134" addrtype="ipv4"/><ports><port protocol="tcp" portid="514"><state state="open" reason="syn-ack" reason_ttl="64"/></port></ports></host>
<host endtime="1786180993"><address addr="192.168.23.134" addrtype="ipv4"/><ports><port protocol="tcp" portid="139"><state state="open" reason="syn-ack" reason_ttl="64"/></port></ports></host>
<host endtime="1786181184"><address addr="192.168.23.134" addrtype="ipv4"/><ports><port protocol="tcp" portid="513"><state state="open" reason="syn-ack" reason_ttl="64"/></port></ports></host>
<host endtime="1786181200"><address addr="192.168.23.134" addrtype="ipv4"/><ports><port protocol="tcp" portid="3632"><state state="open" reason="syn-ack" reason_ttl="64"/></port></ports></host>
<host endtime="1786181210"><address addr="192.168.23.134" addrtype="ipv4"/><ports><port protocol="tcp" portid="80"><state state="open" reason="syn-ack" reason_ttl="64"/></port></ports></host>
<host endtime="1786181317"><address addr="192.168.23.134" addrtype="ipv4"/><ports><port protocol="tcp" portid="8787"><state state="open" reason="syn-ack" reason_ttl="64"/></port></ports></host>
<host endtime="1786181333"><address addr="192.168.23.134" addrtype="ipv4"/><ports><port protocol="tcp" portid="111"><state state="open" reason="syn-ack" reason_ttl="64"/></port></ports></host>
<host endtime="1786181351"><address addr="192.168.23.134" addrtype="ipv4"/><ports><port protocol="tcp" portid="8009"><state state="open" reason="syn-ack" reason_ttl="64"/></port></ports></host>
<runstats>
<finished time="1786181422" timestr="2026-08-08 04:30:22" elapsed="1717" />
<hosts up="30" down="0" total="30" />
</runstats>
</nmaprun>
```

### Banner Grabbing

Scansiona porte specifiche e recupera i banner dei servizi:

`sudo masscan 192.168.23.134 -p21,22,25,53,80,111,139,445,512,513,514,23,3306,5432,5900,6667,8009,8180,8787 --banners --rate=1000 -oL banner.txt`

Output atteso:

```
cat banner.txt
#masscan
open tcp 111 192.168.23.134 1786181686
open tcp 80 192.168.23.134 1786181686
open tcp 53 192.168.23.134 1786181686
open tcp 5432 192.168.23.134 1786181686
open tcp 22 192.168.23.134 1786181686
open tcp 514 192.168.23.134 1786181686
open tcp 512 192.168.23.134 1786181686
open tcp 139 192.168.23.134 1786181686
open tcp 5900 192.168.23.134 1786181686
open tcp 6667 192.168.23.134 1786181686
open tcp 8009 192.168.23.134 1786181686
open tcp 23 192.168.23.134 1786181686
open tcp 25 192.168.23.134 1786181686
open tcp 8787 192.168.23.134 1786181686
open tcp 3306 192.168.23.134 1786181686
open tcp 21 192.168.23.134 1786181686
open tcp 8180 192.168.23.134 1786181686
open tcp 445 192.168.23.134 1786181686
open tcp 513 192.168.23.134 1786181686
# end
```

Opzioni per Banner Grabbing:

- `--banners` → tenta di leggere info servizio
- `-oL` → output leggibile (one-line)
- `/32` → singolo host

### Banner Grabbing su IP esterno

Scansiona un IP pubblico su porte specifiche:

`sudo masscan 37.119.209.207/32 -p22,5000 --banners --source-ip 192.168.58.200 -oL banner.txt`

Output atteso:

```
cat banner.txt
#masscan
open tcp 22 37.119.209.207 1776785112
open tcp 5000 37.119.209.207 1776785112
banner tcp 22 37.119.209.207 1776785117 ssh SSH-2.0-OpenSSH_10.0p2 Debian-7
# end
```

### Differenza tra virgola e trattino

| Sintassi | Significato | Numero di porte |
|----------|-------------|-----------------|
| `-p22,5000` | Scansiona solo la porta 22 e la 5000 | 2 porte |
| `-p22-5000` | Scansiona tutto l`intervallo dalla 22 alla 5000 | 4979 porte |

## Opzioni Utili

| Opzione | Descrizione |
|---------|-------------|
| `-p<porte>` | Specifica le porte da scansionare |
| `--rate=<n>` | Pacchetti al secondo |
| `--open-only` | Mostra solo porte aperte |
| `--exclude <IP>` | Esclude IP dalla scansione |
| `--banners` | Recupera i banner dei servizi |
| `--source-ip <IP>` | Spoofing dell`IP sorgente |
| `-oL` | Output leggibile (one-line) |
| `-oX` | Output XML |

## Note

> **⚠️ ATTENZIONE**: Masscan è uno strumento potente da utilizzare solo su sistemi autorizzati

- Masscan è più veloce di Nmap ma non analizza i servizi
- È progettato per scansioni su larga scala
- Richiede privilegi di root per l'invio di pacchetti raw
- Usa `--rate` con cautela per non sovraccaricare la rete