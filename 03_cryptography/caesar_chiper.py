#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
import string

# 1. Alfabeto esteso più completo: include punteggiatura comune e spazio
# Usiamo string.ascii_lowercase + string.digits per rapidità
ALFABETO_ESTESO = string.ascii_lowercase + string.digits + " .,!?;:@"

def cifrario_ottimizzato(testo, chiave, modalità):
    """
    Versione ottimizzata:
    - Calcola la chiave totale una volta sola (chiave * passaggi).
    - Usa un dizionario per lookup istantaneo (O(1)).
    """
    risultato = []
    n = len(ALFABETO_ESTESO)
    
    # Normalizziamo la chiave: se decriptiamo, lo spostamento è negativo
    shift = chiave % n
    if modalità == "decript":
        shift = -shift

    # Creiamo una mappatura per velocizzare l'esecuzione su testi lunghi
    mappa = {char: i for i, char in enumerate(ALFABETO_ESTESO)}

    for char in testo:
        lower = char.lower()
        if lower in mappa:
            indice_corrente = mappa[lower]
            nuovo_indice = (indice_corrente + shift) % n
            nuovo_char = ALFABETO_ESTESO[nuovo_indice]
            
            # Ripristino del case
            risultato.append(nuovo_char.upper() if char.isupper() else nuovo_char)
        else:
            risultato.append(char)

    return "".join(risultato)

def chiedi_input(prompt, tipo=int, condizione=None, messaggio_errore="Valore non valido."):
    while True:
        try:
            valore = tipo(input(prompt))
            if condizione and not condizione(valore):
                raise ValueError
            return valore
        except ValueError:
            print(messaggio_errore)

def main():
    print("=== Cifrario di Cesare Pro ===")

    while True:
        print("\n1. Manuale | 2. File | 3. Esci")
        scelta = input("→ ").strip()

        if scelta == "3": break
        
        testo = ""
        if scelta == "1":
            testo = input("Inserisci il testo: ")
        elif scelta == "2":
            percorso = input("Percorso file: ")
            if not os.path.exists(percorso):
                print("Errore: File non trovato.")
                continue
            with open(percorso, "r", encoding="utf-8") as f:
                testo = f.read()
        else: continue

        modalità = input("Modalità (cript/decript): ").lower()
        while modalità not in ["cript", "decript"]:
            modalità = input("Errore. Scrivi 'cript' o 'decript': ").lower()

        chiave_base = chiedi_input("Chiave (intero): ", int)
        passaggi = chiedi_input("Passaggi (>=1): ", int, lambda x: x >= 1)

        # MIGLIORAMENTO LOGICO: 
        # Invece di fare un ciclo for che rallenta il PC, calcoliamo la chiave finale.
        # Spostare di 3 per 10 volte è uguale a spostare di 30.
        chiave_totale = chiave_base * passaggi

        risultato = cifrario_ottimizzato(testo, chiave_totale, modalità)

        print(f"\n--- Risultato ({modalità}) ---\n{risultato}\n---")

        if input("Salvare? (s/n): ").lower() == "s":
            nome_f = input("Nome file: ")
            with open(nome_f, "w", encoding="utf-8") as f:
                f.write(risultato)
            print("Salvato.")

        if input("\nAltra operazione? (s/n): ").lower() != "s":
            break

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(0)