# 🔍 Shodan e FOFA - Motori di ricerca OSINT

> Shodan e FOFA non indicizzano il testo delle pagine web come Google o Bing, ma scansionano direttamente gli indirizzi IP e i servizi connessi a Internet (server, router, telecamere IoT, database, ecc.).

---

## ⚙️ Come funzionano: Banner Grabbing

A differenza dei normali crawler, questi motori utilizzano la tecnica del **Banner Grabbing**: inviano richieste agli indirizzi IP e salvano le risposte grezze (*banner*) dei servizi esposti (porte aperte, versioni del software, intestazioni HTTP, certificati SSL).

Servono per effettuare **ricognizioni passive**: permettono di raccogliere informazioni su un bersaglio analizzando i dati già archiviati dai motori, senza inviare pacchetti direttamente dalla propria rete.

---

## [Shodan](https://www.shodan.io/)

È il motore di ricerca di riferimento a livello globale per l'IoT e le infrastrutture di rete. Permette di individuare dispositivi connessi, software obsoleti e vulnerabilità note (CVE).

### 🛠️ Filtri di ricerca utili

| Comando / Filtro | Descrizione |
| :--- | :--- |
| `port:22` | Filtra per porta aperta (es. SSH, RDP). |
| `net:192.168.1.0/24` | Limita la ricerca a una sottorete o a un intervallo di IP. |
| `org:"Nome Azienda"` | Cerca dispositivi registrati a una specifica organizzazione. |
| `product:"Apache"` | Cerca un software o un servizio specifico. |
| `vuln:CVE-2021-44228` | Identifica i sistemi esposti a una specifica vulnerabilità. |

---

## [FOFA](https://fofa.info/)

Motore di ricerca OSINT di origine cinese. Simile a Shodan, vanta una copertura molto più profonda sulle infrastrutture asiatiche e una spiccata specializzazione nel *web fingerprinting* (identificazione di framework web, CMS e certificati SSL).

### 🛠️ Filtri di ricerca utili

| Comando / Filtro | Descrizione |
| :--- | :--- |
| `title="Dashboard"` | Cerca parole chiave nel titolo della pagina web. |
| `cert="dominio.com"` | Cerca i sistemi collegati a uno specifico certificato SSL (ottimo per scovare server o sottodomini nascosti). |
| `body="index of/"` | Cerca directory con elencazione dei contenuti attiva (*directory listing*). |
| `protocol="ssh"` | Filtra per protocollo di rete. |