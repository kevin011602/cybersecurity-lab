# Diffie-Hellman Key Exchange

## Cos'è

**Diffie-Hellman (DH)** è un protocollo crittografico che permette a due parti (Alice e Bob) di generare un **segreto condiviso** su un canale insicuro, senza aver mai scambiato una chiave segreta in precedenza.

Questo segreto può poi essere usato come chiave per un algoritmo simmetrico (es. AES) per cifrare la comunicazione successiva.

## Come funziona

1. Alice e Bob concordano pubblicamente su due parametri: un numero primo 'p' e un generatore 'g'.
2. Alice sceglie un numero segreto 'a' e calcola 'A = g^a mod p'. Invia 'A' a Bob.
3. Bob sceglie un numero segreto 'b' e calcola 'B = g^b mod p'. Invia 'B' a Alice.
4. Alice calcola 's = B^a mod p'.
5. Bob calcola 's = A^b mod p'.
6. I due valori 's' coincidono: è il **segreto condiviso**.

## Lo script

Questo script implementa il protocollo DH in Python usando la libreria 'cryptography':

```
pip install cryptography
python3 dh_key_exchange.py
```

Eseguendolo, lo script:

- Genera parametri DH (2048-bit).
- Genera chiavi per Alice e Bob.
- Deriva il segreto condiviso da entrambe le parti.
- Verifica che i segreti coincidano.

## Output atteso

```
1. Generazione parametri DH 2048-bit (attendere...)
2. Alice: Generazione chiavi...
3. Bob: Generazione chiavi...
4. Derivazione segreti condivisi...
5. Verifica finale...
--------------------------------------------------
SUCCESSO: I segreti corrispondono!
Impronta (Alice): 8180c426ea39ddabf5d7b62d2afdd9e05144cfa279e2d4708f0a0d93ff283acc
Impronta (Bob):   8180c426ea39ddabf5d7b62d2afdd9e05144cfa279e2d4708f0a0d93ff283acc
--------------------------------------------------
```

## File generati

| File | Contenuto |
|------|-----------|
| 'parametersPG.pem' | Parametri DH condivisi (p, g) |
| 'Alice_KeyPair.pem' | Chiave privata di Alice |
| 'Alice_Public.pem' | Chiave pubblica di Alice |
| 'Bob_KeyPair.pem' | Chiave privata di Bob |
| 'Bob_Public.pem' | Chiave pubblica di Bob |
| 'AliceSharedSecret.bin' | Segreto condiviso (derivato da Alice) |
| 'BobSharedSecret.bin' | Segreto condiviso (derivato da Bob) |

> **Nota:** I file vengono generati localmente e possono essere rimossi dopo l'esecuzione.