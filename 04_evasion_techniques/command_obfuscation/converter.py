import base64
import sys

def converti_testo(testo):
    # Conversione in byte per Base64 e Hex
    dati_byte = testo.encode('utf-8')
    
    # Base64
    b64 = base64.b64encode(dati_byte).decode('utf-8')
    
    # Esadecimale (Hex)
    hex_val = dati_byte.hex()
    
    # Binario (8-bit)
    binario = ' '.join(format(b, '08b') for b in dati_byte)
    
    # Decimale (Valori ASCII/Unicode)
    decimale = ' '.join(str(b) for b in dati_byte)
    
    # Ottale (Base 8)
    ottale = ' '.join(format(b, 'o') for b in dati_byte)
    
    return b64, hex_val, binario, decimale, ottale

def main():
    print("=" * 40)
    print("   CONVERTITORE MULTI-FORMATO PRO")
    print("=" * 40)
    print("Inserisci il testo e premi Invio.")
    print("Premi CTRL+C per chiudere il programma.\n")
    
    try:
        while True:
            input_utente = input("ASCII > ")
            
            if not input_utente:
                continue
                
            b64, hx, bi, dec, ott = converti_testo(input_utente)
            
            print(f"  [Base64]:  {b64}")
            print(f"  [Hex]:     {hx}")
            print(f"  [Decimale]: {dec}")
            print(f"  [Ottale]:   {ott}")
            print(f"  [Binario]:  {bi}")
            print("-" * 40)
            
    except KeyboardInterrupt:
        print("\n\nSegnale di interruzione ricevuto. Uscita in corso...")
        sys.exit()

if __name__ == "__main__":
    main()