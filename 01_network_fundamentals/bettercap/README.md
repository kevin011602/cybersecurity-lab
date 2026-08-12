# Attacco MITM con Bettercap: ARP Spoofing, SSL Stripping e hostname rewriting in presenza di HSTS

Guida didattica per comprendere e sperimentare un attacco Man-In-The-Middle (MITM) in un ambiente di laboratorio controllato, utilizzando Bettercap per intercettare, declassare e analizzare il traffico di rete.

## Indice

- 1. Premessa e limiti dell'attacco
- 2. Prerequisiti
- 3. Installazione di Bettercap
- 4. Guida passo-passo
  - 4.1. Abilitazione dell'IP forwarding
  - 4.2. Avvio di Bettercap e discovery della rete
  - 4.3. ARP Spoofing (posizionamento MITM)
  - 4.4. Sniffing del traffico
  - 4.5. SSL Stripping con il proxy HTTP
  - 4.6. DNS Spoofing (tecnica separata)
  - 4.7. Hostname rewriting in presenza di HSTS con `hstshijack`
- 5. Verifica dell'attacco
- 6. Arresto dell'esperimento
- 7. Disclaimer legale

---

## 1. Premessa e limiti dell'attacco

> **ATTENZIONE:** Questa guida è esclusivamente per scopi didattici e per test in ambienti di laboratorio autorizzati. L'uso non autorizzato di queste tecniche è illegale.

L'attacco MITM con Bettercap è efficace per intercettare il traffico di rete, ma la possibilità di leggere dati sensibili dipende fortemente dal contesto:

- Su servizi che utilizzano HTTP in chiaro, i dati applicativi possono essere osservati direttamente. Su servizi che utilizzano HTTPS ma non HSTS, l'SSL stripping può, in determinate condizioni, impedire il passaggio ad HTTPS e rendere il traffico tra vittima e MITM osservabile in chiaro.
- Su siti moderni che adottano HTTPS con HSTS (inclusi quelli nella lista di preload dei browser), le tecniche di SSL stripping tradizionali sono generalmente inefficaci. Il modulo `hstshijack` tenta di aggirare queste protezioni sfruttando domini alternativi non conosciuti dal browser, ma i browser moderni includono liste HSTS predefinite e possono attivare la modalità "HTTPS-Only" che ne limita ulteriormente l'efficacia.

Questa guida non promette di bypassare la sicurezza di siti reali, ma spiega il funzionamento delle tecniche e come testarle in un ambiente controllato.

---

## 2. Prerequisiti

- Kali Linux (o qualsiasi distribuzione Linux con Bettercap)
- Macchina vittima (Windows, Linux, macOS) sulla stessa rete
- Permessi di root (`sudo`) su Kali
- Bettercap installato (v2.40 o superiore)
- **Opzionale ma consigliato:** pacchetto `bettercap-caplets` per i caplet ufficiali (include `hstshijack`)

---

## 3. Installazione di Bettercap

```
sudo apt update
sudo apt install bettercap -y
```

Verifica la versione:

```
bettercap --version
```

**Nota:** La versione esatta può variare; assicurati che i repository siano aggiornati. Per i caplet aggiuntivi (come `hstshijack`) installa anche:

```
sudo apt install bettercap-caplets
```

I caplet saranno poi disponibili in `/usr/share/bettercap/caplets/`.

---

## 4. Guida passo-passo

### 4.1. Abilitazione dell'IP forwarding

L'IP forwarding permette al sistema di inoltrare i pacchetti tra le interfacce di rete. Bettercap, quando `arp.spoof` è attivo, imposta automaticamente `arp.spoof.forwarding` (default `true`) e abilita il forwarding. Tuttavia, per chiarezza didattica e per facilitare il troubleshooting, è consigliabile abilitarlo manualmente:

```
sudo sysctl -w net.ipv4.ip_forward=1
```

---

### 4.2. Avvio di Bettercap e discovery della rete

```
sudo bettercap -iface eth0
```

**Discovery dei dispositivi sulla rete:**

```
net.probe on
```

`net.probe` invia probe attivi alla subnet (mDNS, NBNS, UPnP, WSD a seconda della configurazione). Il modulo `net.recon` legge periodicamente la tabella ARP e utilizza anche le informazioni di `net.probe` per rilevare gli host. Per questo, `net.recon` deve essere attivo (di solito lo è per default, ma verificalo con `net.recon on` se necessario).

**Visualizza i dispositivi trovati:**

```
net.show
```

Prendi nota dell'IP della vittima (es. `192.168.23.133`) e del gateway (es. `192.168.23.2`).

**Disabilita `net.probe` per ridurre il traffico di discovery** (in alcune configurazioni può interferire con lo spoofing):

```
net.probe off
```

---

### 4.3. ARP Spoofing (posizionamento MITM)

L'ARP spoofing consiste nell'inviare pacchetti ARP falsificati per far credere alla vittima che il nostro computer sia il gateway, e al gateway che il nostro computer sia la vittima. In questo modo tutto il traffico bidirezionale passa attraverso la nostra macchina.

```
set arp.spoof.fullduplex true
```

Abilita lo spoofing bidirezionale: attacca sia la vittima che il router.

```
set arp.spoof.targets 192.168.23.133
```

Imposta l'IP della vittima.

```
arp.spoof on
```

Avvia l'attacco ARP spoofing.

**Output atteso:**

```
[war] arp.spoof full duplex spoofing enabled, if the router has ARP spoofing mechanisms, the attack will fail.
[inf] arp.spoof arp spoofer started, probing 1 targets.
```

> **⚠️ Il warning è normale** e indica che lo spoofing bidirezionale è attivo. Se il router ha protezioni ARP, l'attacco potrebbe fallire.

---

### 4.4. Sniffing del traffico

Lo sniffer cattura tutto il traffico che attraversa la nostra macchina. **Importante:** lo sniffing non decritta il contenuto delle connessioni HTTPS. Il traffico TLS può permettere di osservare metadati di rete e di protocollo, dimensioni e temporizzazione dei pacchetti, ma il contenuto applicativo rimane cifrato. Per leggere dati in chiaro occorre un downgrade a HTTP (vedi SSL Stripping).

```
set net.sniff.local true
```

Include anche il traffico generato dal nostro stesso computer.

```
set net.sniff.verbose true
```

Aumenta il livello di dettaglio dell'output.

```
net.sniff on
```

Avvia lo sniffer. In questa fase vedrai le richieste HTTP in chiaro; il traffico HTTPS apparirà come traffico TLS cifrato, di cui non è possibile leggere il contenuto applicativo.

---

### 4.5. SSL Stripping con il proxy HTTP

**Cos'è l'SSL stripping?**  
La tecnica fa sì che la connessione tra vittima e attaccante avvenga in HTTP, mentre l'attaccante mantiene una connessione HTTPS con il server reale. Il proxy HTTP di Bettercap intercetta le richieste e tenta di impedire che il browser della vittima venga portato dalla navigazione HTTP ad HTTPS, quando le condizioni lo consentono. In questo modo i dati viaggiano in chiaro tra vittima e attaccante.

**Importante:** in una configurazione trasparente correttamente predisposta, la macchina vittima non deve essere configurata manualmente per utilizzare il proxy HTTP; il traffico HTTP intercettato può essere inoltrato al proxy.

```
set http.proxy.sslstrip true
```

Abilita la funzionalità di SSL stripping nel proxy HTTP.

```
http.proxy on
```

Avvia il proxy HTTP.

**Output atteso:**

```
[inf] http.proxy started on 192.168.23.128:8080 (sslstrip enabled)
```

Lo stripping funziona **solo se il browser della vittima accetta di navigare in HTTP** (nessun HSTS pregresso, nessun "HTTPS-Only mode" attivato). Molti siti moderni e browser forzano HTTPS, rendendo questa tecnica inefficace senza ulteriori stratagemmi.

---

### 4.6. DNS Spoofing (tecnica separata)

Il DNS spoofing non è richiesto per il MITM di base con ARP spoofing + SSL stripping; si tratta di una tecnica distinta che può essere utilizzata per reindirizzare le richieste DNS della vittima verso un IP scelto dall'attaccante.

**Scenario tipico:** rispondere a richieste per un dominio controllato o inesistente, reindirizzando la vittima a un server malevolo (o al nostro Kali).

```
set dns.spoof.domains example.corn
set dns.spoof.address 192.168.23.128
dns.spoof on
```

- `dns.spoof.domains`: elenco di domini da spoofare, separati da virgole (es. `example.corn,malware.net`). Nel presente scenario `arp.spoof` è già attivo, quindi Bettercap può ricevere le richieste DNS della vittima.
- `dns.spoof.address`: IP a cui reindirizzare (il nostro Kali).

**Verifica:** sulla vittima, `nslookup example.corn` dovrebbe restituire `192.168.23.128`.

---

### 4.7. Hostname rewriting in presenza di HSTS con `hstshijack`

#### Cos'è HSTS?

HTTP Strict Transport Security (HSTS) è un meccanismo di sicurezza web con cui un server può dichiarare al browser di comunicare solo in HTTPS per un certo dominio (ed eventualmente per tutti i sottodomini). Se il browser ha memorizzato una policy HSTS per un dominio, anche se l'utente digita `http://...` la richiesta viene automaticamente aggiornata ad HTTPS prima di effettuare la connessione.

Il browser può conoscere una policy HSTS in due modi principali:
- **HSTS dinamico:** il server invia l'header `Strict-Transport-Security` in una rispostad HTTPS valida.
- **HSTS preload:** il dominio è incluso nella preload list utilizzata dal browser, che consente di applicare la policy HSTS già alla prima connessione.

**Attenzione:** Molti browser moderni offrono anche una modalità "HTTPS-Only" (o "HTTPS-First") che tenta di usare HTTPS per tutti i siti, indipendentemente da HSTS. Questa protezione lato client può impedire l'SSL stripping anche su siti privi di HSTS.

#### Cosa fa hstshijack?

`hstshijack` **non rompe HSTS**, ma tenta di evitare la policy cambiando l'hostname a cui la vittima si collega. Il principio è:
1. Si sceglie un dominio fittizio (es. `facebook.corn`) che **non** sia mai stato visitato e per il quale il browser non possiede alcuna policy HSTS.
2. Tramite DNS spoofing si fa in modo che la vittima risolva `facebook.corn` con l'IP dell'attaccante.
3. Quando è possibile intercettare una risposta HTTP del dominio originale, `hstshijack` modifica i riferimenti (link, redirect) iniettando codice JavaScript o alterando il contenuto HTML, sostituendo i riferimenti al dominio originale con il dominio fittizio (es. `facebook.com` → `facebook.corn`).
4. Il browser viene quindi dirottato su `facebook.corn` via HTTP, dove non c'è protezione HSTS e lo stripping può funzionare.

`facebook.corn` è un hostname distinto da `facebook.com`; pertanto una policy HSTS associata a `facebook.com` non viene applicata automaticamente a `facebook.corn`. L'header `includeSubDomains` estende invece la policy agli hostname che sono effettivamente sottodomini del dominio protetto, ma non a hostname completamente diversi come `facebook.corn`.

#### Utilizzo pratico del caplet ufficiale (Kali)

Su Kali, il caplet `hstshijack` è preinstallato con il pacchetto `bettercap-caplets`. **Il caplet configura non solo `targets` e `replacements`, ma anche `http.proxy.script` (puntando a `hstshijack.js`), payload, whitelist, domini SSL e le regole DNS.** Per questo motivo, limitarsi a impostare manualmente poche variabili non è sufficiente: è necessario caricare l'intero caplet.

Per usarlo:

1. Verifica che il caplet sia disponibile:

```
caplets.show
```

2. Assicurati che il DNS spoofing e il proxy HTTP siano configurati come richiesto dal caplet (di solito ci pensa lui stesso).
3. Carica il caplet:

```
hstshijack/hstshijack
```

Il caplet ufficiale contiene le impostazioni e gli script necessari al proprio funzionamento; il contenuto esatto può variare a seconda della versione dei caplets installata.

#### Esempio di test in laboratorio

Per osservare il meccanismo di hostname rewriting, crea un ambiente di test isolato. **Nota:** l'esempio seguente dimostra la riscrittura dei domini e il DNS spoofing, ma **non** un vero bypass di HSTS, perché il dominio di partenza `lab.test` non ha HSTS. Per una dimostrazione didattica completa si dovrebbe confrontare il comportamento con un dominio protetto da HSTS.

**Preparazione:** Configura il DNS o il file hosts della rete di laboratorio in modo che `lab.test` risolva verso il server web di test. Imposta un dominio di test come `lab.test` su un server web in una rete virtuale (evita `.local`, che può interferire con mDNS).

Procedi quindi in due fasi:

**Fase 1 – Test senza HSTS (hostname rewriting di base)**
1. Sul server web, non configurare HSTS (solo HTTP).
2. In Bettercap, prima di caricare il caplet, imposta le variabili per il tuo dominio (modifica il caplet o crea un caplet personalizzato):

```
set hstshijack.targets lab.test,*.lab.test
set hstshijack.replacements lab.corn,*.lab.corn
set dns.spoof.domains lab.corn
set dns.spoof.address 192.168.23.128
```

3. Carica il caplet `hstshijack/hstshijack` (se il caplet ufficiale sovrascrive queste variabili, modifica direttamente il file `.cap`).
4. Dalla macchina vittima, visita `http://lab.test`. Dovresti osservare la sostituzione dell'hostname con `lab.corn` e, se la configurazione è corretta, la successiva navigazione tramite il dominio alternativo.

**Fase 2 – Confronto con HSTS**
5. Configura ora il server `lab.test` con HSTS (imposta l'header `Strict-Transport-Security`).
6. Assicurati che il browser abbia appreso la policy HSTS (visita prima `https://lab.test` in modo sicuro).
7. Ripeti il tentativo di visitare `http://lab.test`: il browser non dovrebbe effettuare direttamente una connessione HTTP, ma passare subito ad HTTPS. L'hostname alternativo `lab.corn`, se non possiede una propria policy HSTS e non è soggetto ad altre policy del browser, non eredita automaticamente la policy HSTS di `lab.test` e può quindi accettare HTTP. Questo confronto mostra la differenza tra i due hostname.

**Limitazioni importanti:**
- I browser con **HSTS preload** per il dominio target bloccano la connessione HTTP all'origine, quindi non si arriva nemmeno allo step di rewriting.
- La **modalità HTTPS-Only** del browser può forzare HTTPS per tutti i siti, vanificando lo stripping anche su domini sconosciuti.
- Content Security Policy (CSP) e altre difese lato client possono impedire l'esecuzione del JavaScript iniettato.
- La procedura descritta si concentra sul traffico HTTP intercettabile dal proxy HTTP di Bettercap. Il traffico HTTP/3 (QUIC) non viene intercettato da questo tipo di proxy; l'esperimento presuppone pertanto l'uso di HTTP/1.1 o HTTP/2 su TCP.

---

## 5. Verifica dell'attacco

### Sulla vittima

1. Utilizza un browser di test con un profilo pulito, creato appositamente per gli esperimenti. In questo modo eviti interferenze dovute a cache, cookie o stato HSTS preesistente.
2. Disattiva temporaneamente eventuali modalità "HTTPS-Only" del browser.
3. Visita un sito HTTP noto (es. `http://neverssl.com`) per verificare il semplice sniffing del traffico in chiaro.
4. Per testare lo stripping o il comportamento dell'hostname rewriting in presenza di HSTS, visita manualmente la versione `http://` del dominio target.

### Sull'attaccante (Kali)

Nel terminale di Bettercap, con `net.sniff` attivo, vedrai le richieste HTTP in chiaro:

```
[net.sniff.http.request] http 192.168.23.133 GET neverssl.com/
[net.sniff.http.response] http 200 OK -> 192.168.23.133
```

Se la vittima invia credenziali su un sito declassato, potresti vedere una richiesta POST (attenzione: non è garantito, molti form moderni inviano dati viad HTTPS o utilizzano JavaScript che ostacola il semplice stripping):

```
POST /login HTTP/1.1
Host: example.test
user=test&pass=password123
```

**Nota:** per il traffico HTTPS senza stripping, lo sniffing mostrerà solo pacchetti cifrati; il contenuto non è leggibile.

---

## 6. Arresto dell'esperimento

Per terminare correttamente l'esperimento e ripristinare le condizioni di rete originali, esegui in Bettercap:

```
net.sniff off
http.proxy off
dns.spoof off
arp.spoof off
```

Quindi disabilita manualmente l'IP forwarding se desideri:

```
sudo sysctl -w net.ipv4.ip_forward=0
```

> **Nota:** `arp.spoof off` attiva il ripristino automatico delle tabelle ARP originali. Attendi il completamento di questa operazione prima di scollegare le macchine dal laboratorio. Se durante il test sono state modificate configurazioni persistenti del sistema o del browser (es. proxy manuali, file hosts), ripristinarle manualmente al termine dell'esperimento.

---

## 7. Disclaimer legale

> **⚠️ ATTENZIONE:** Questa guida è esclusivamente per scopi educativi e per test in ambienti di laboratorio controllati di cui si possiede la proprietà o l'autorizzazione esplicita.

> **È ILLEGALE** utilizzare queste tecniche su reti o dispositivi di cui non si ha la proprietà o il permesso scritto. L'autore non si assume alcuna responsabilità per usi impropri.

**Prima di eseguire qualsiasi attacco:**

- Ottieni il consenso scritto dal proprietario della rete.
- Utilizza solo ambienti di test isolati (es. macchine virtuali in una rete privata).
- Rispetta le leggi locali e internazionali sulla cybersecurity