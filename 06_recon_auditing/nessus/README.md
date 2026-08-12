# 🛡Tenable Nessus - Vulnerability Assessment Lab

![Nessus](https://img.shields.io/badge/Tool-Nessus_Essentials-blue?style=for-the-badge&logo=tenable)
![Environment](https://img.shields.io/badge/Environment-VMware_Workstation-orange?style=for-the-badge&logo=vmware)

Documentazione completa per il deployment, la configurazione e l'esecuzione di un laboratorio di **Vulnerability Assessment** utilizzando **Tenable Core + Nessus Essentials** contro macchine target Linux e Windows.

---

## Architettura di Rete e Ambiente di Test

Tutte le macchine virtuali sono attestate sulla medesima rete NAT locale (`192.168.23.0/24`).

| Ruolo | Hostname / OS | Indirizzo IP | Descrizione / Servizi |
| :--- | :--- | :--- | :--- |
| **Scanner** | Tenable Core (Oracle Linux 8) | `192.168.23.200` | Appliance preconfigurata contenente Nessus Scanner |
| **Target 1** | Metasploitable 2 (Linux) | `192.168.23.134` | VM intenzionalmente vulnerabile (Backdoors, Service Flaws) |
| **Target 2** | Windows 10 x64 | `192.168.23.130` | Workstation target per l'analisi di misconfiguration/patch |

---

## Guida Passo-Passo all'Installazione

```
[1. Import OVA/OVF] ─► [2. Network & Wizard Setup] ─► [3. Tenable Core (8000)]
																										│
[6. Exec Scans & Analysis] ◄─ [5. Plugin Download] ◄─ [4. Nessus Setup (8834)]
```

### 1. Importazione e Prima Configurazione Rete

1. Scaricare Tenable-Core-OL8-Nessus-xxx.ova da https://www.tenable.com/downloads/tenable-appliance?loginAttempted=true#tenablecore-nessus

![](assets/01.png)

2. Importare l'appliance `Tenable-Core-Nessus` su VMware.

![](assets/02.png)

3. Durante la procedura di importazione, lasciare vuoto il campo *User Data (Base64)*

![](assets/03.png)

4. Impostare la scheda di rete della macchina virtuale su `NAT`

![](assets/04.png)

5. Al boot iniziale sul terminale locale, inserire le credenziali temporanee:
   * **Login:** `wizard` | **Password:** `admin`
   
![](assets/05.png)
   
6. Configurare l'indirizzo IP statico (`y`) come segue (`<Edit...>`):
   * **IPv4 Configuration** `Manual`
   * **Addresses:** `192.168.23.200/24` (inserire un IP valido per te)
   * **Gateway:** `192.168.23.2` (inserire un IP valido per te)
   * **DNS servers:** `8.8.8.8` (es.)

![](assets/06.png)
![](assets/07.png)
![](assets/08.png)

7. Creare l'account Amministratore di Sistema principale (`y`), ad es.:
   * **Username:** `admin` | **Password:** `password`
8. Effettuare il login con le medesime credenziali.

---

### 2. Gestione Appliance via Tenable Core (Porta 8000)

* **URL di Accesso:** `https://192.168.23.200:8000`
* **Credenziali:** `admin` / `password`

![](assets/09.png)

> **Nota:** Cliccare su **Turn on administrative access** in alto per abilitare i privilegi completi di gestione del sistema.

![](assets/10.png)

![](assets/11.png)

---

### 3. Attivazione & Setup Nessus Scanner (Porta 8834)

1. Collegarsi alla console di scansione: `https://192.168.23.200:8834`

![](assets/12.png)

2. Selezionare **Nessus Essentials** e cliccare su **Continue**.

![](assets/13.png)

3. Inserire i dati per la registrazione/attivazione, verificare l'e-mail e inserire il proprio **Activation Code**.

![](assets/14.png)

![](assets/15.png)

![](assets/16.png)

![](assets/17.png)

![](assets/18.png)

4. Creare l'account di gestione dello scanner.

![](assets/19.png)

5. Attendere il completamento del download e della compilazione del database dei **Plugin** (operazione che richiede 10-20 minuti).

![](assets/20.png)

![](assets/21.png)

---

## Configurazione ed Esecuzione Scansione

### 1. Creazione Workspace e Scansione

1. Nella sezione **My Scans**, creare una nuova cartella nominata **`Lab_Targets`** e selezionarla.

![](assets/22.png)

![](assets/23.png)

2. Cliccare su **New Scan** → selezionare il template **Basic Network Scan**.

![](assets/24.png)

![](assets/25.png)

3. Compilare le impostazioni della scheda *General*:
   * **Name:** `Metasploitable2 e Win10`
   * **Folder:** `Lab_Targets`
   * **Targets:** `192.168.23.134, 192.168.23.130`
   
4. Cliccare sulla freccia accanto a *Save* e selezionare **Launch**.

![](assets/26.png)

![](assets/27.png)

---

## Risultati dell'Analisi (Vulnerability Assessment)

La scansione completa ha rilevato un totale di **73 vulnerabilità uniche**.

![](assets/28.png)

![](assets/29.png)

### 📈 Distribuzione delle Criticità

| Severità | Punteggio CVSS v3 | Descrizione |
| --- | --- | --- |
| 🔴 **CRITICAL** | `9.0 - 10.0` | Vulnerabilità ad alto impatto (es. Backdoor RCE, Shell remote non autenticate) |
| 🟠 **HIGH** | `7.0 - 8.9` | Rischio elevato di compromissione del servizio o escalation di privilegi |
| 🟡 **MEDIUM** | `4.0 - 6.9` | Misconfiguration e protocolli obsoleti/deboli attivi |
| 🔵 **LOW** | `0.1 - 3.9` | Informazioni utili per attività di footprinting e ricognizione |
| ⚪ **INFO** | `0.0` | Porte aperte, banner dei servizi e dati di sistema |

### Principali Vulnerabilità Critiche Rilevate (Metasploitable 2)

* **UnrealIRCD Backdoor Detection (`CVSS 10.0`):** Presenza di codice malevolo nell`archivio del servizio IRC che permette l'esecuzione remota di comandi arbitrari.
* **Bind Shell Backdoor Detection (`CVSS 9.8`):** Shell root in ascolto su porta TCP aperta senza alcuna autenticazione.
* **VNC Server `password` Password (`CVSS 10.0`):** Servizio di Desktop Remoto protetto da credenziali deboli e facilmente violabili.
* **Samba Badlock Vulnerability (`CVSS 7.5`):** Flaw nel protocollo SMB che espone il sistema ad attacchi Man-In-The-Middle e DoS.

![](assets/30.png)

---

## Note di Sicurezza e Privacy

> **⚠️ AVVERTENZA**: Nessus è uno strumento di sicurezza offensiva/difensiva ad alto impatto. Deve essere utilizzato **esclusivamente** su reti e sistemi di proprietà o previo consenso scritto autorizzato.