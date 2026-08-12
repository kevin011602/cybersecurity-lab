import requests
import json
import subprocess
import time
import os

def print_json(data):
    print(json.dumps(data, indent=4))

def run_simulation():
    # 1. Avvio del primo nodo sulla porta 8000
    print("[*] Avvio nodo 8000...")
    p8000 = subprocess.Popen(['python3', 'blockchain_8000.py'])
    time.sleep(3)  # Attendiamo l'avvio del server

    # 2. Verifica catena iniziale e invio transazione
    print("\n[*] Catena iniziale nodo 8000:")
    resp = requests.get("http://localhost:8000/chain")
    print_json(resp.json())

    payload_tx = {
        "id": "ID24",
        "canale": "Vendita",
        "dati": "Villa Milano",
        "timestamp": "1689657144"
    }
    
    print("\n[*] Invio transazione a 8000...")
    requests.post("http://127.0.0.1:8000/transactions/new", json=payload_tx)

    # 3. Mining del blocco
    print("\n[*] Mining su nodo 8000...")
    requests.get("http://localhost:8000/mine")

    # 4. Avvio del secondo nodo sulla porta 8001
    print("\n[*] Avvio nodo 8001...")
    p8001 = subprocess.Popen(['python3', 'blockchain_8001.py'])
    time.sleep(3)

    # 5. Registrazione nodo 8000 su 8001
    print("\n[*] Registrazione nodo 8000 presso 8001...")
    requests.post("http://127.0.0.1:8001/nodes/register", json={"node": "http://127.0.0.1:8000"})

    # 6. Nuova transazione su 8001
    payload_tx2 = {
        "id": "ID26",
        "canale": "Vendita",
        "dati": "Appartamento Roma",
        "timestamp": "1689657199"
    }
    print("\n[*] Invio transazione a 8001...")
    requests.post("http://127.0.0.1:8001/transactions/new", json=payload_tx2)

    # 7. Risoluzione dei conflitti (Consenso)
    print("\n[*] Risoluzione conflitti su 8001...")
    requests.get("http://localhost:8001/nodes/resolve")

    # 8. Mining su 8001
    print("\n[*] Mining su nodo 8001...")
    requests.get("http://localhost:8001/mine")

    # 9. Registrazione nodo 8001 su 8000 e sincronizzazione finale
    print("\n[*] Registrazione nodo 8001 presso 8000...")
    requests.post("http://127.0.0.1:8000/nodes/register", json={"node": "http://127.0.0.1:8001"})
    
    print("\n[*] Risoluzione finale conflitti su 8000...")
    requests.get("http://localhost:8000/nodes/resolve")

    # 10. Verifica finale della catena su 8000
    final_chain = requests.get("http://localhost:8000/chain").json()
    print("\n[*] Catena finale sincronizzata (Nodo 8000):")
    print_json(final_chain)

    # Pulizia: chiusura dei server
    p8000.terminate()
    p8001.terminate()

if __name__ == "__main__":
    run_simulation()