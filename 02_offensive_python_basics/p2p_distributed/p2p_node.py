#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import socket
import threading
import sys
import subprocess
import shlex
import os
import time

class P2PNode:
    def __init__(self, listen_host: str, listen_port: int) -> None:
        """Inizializza il nodo con host, porta e strutture dati per i peer."""
        self.listen_host = listen_host
        self.listen_port = listen_port
        self.server_socket: socket.socket | None = None
        # Dizionario per tracciare i peer connessi: {(ip, porta): socket}
        self.peers: dict[tuple[str, int], socket.socket] = {}
        # Lock per gestire l'accesso thread-safe al dizionario dei peer
        self.peers_lock = threading.Lock()
        self.running = True

    def start(self) -> None:
        """Configura il server socket e avvia il thread di ascolto."""
        try:
            # Creazione socket TCP/IP (AF_INET = IPv4, SOCK_STREAM = TCP)
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            # Permette il riutilizzo immediato della porta dopo la chiusura
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind((self.listen_host, self.listen_port))
            self.server_socket.listen(5)
        except OSError as e:
            print(f"[ERRORE] Impossibile avviare il nodo su {self.listen_host}:{self.listen_port} -> {e}")
            sys.exit(1)

        print(f"[INFO] Nodo in ascolto su {self.listen_host}:{self.listen_port}")
        print(f"[INFO] Directory di lavoro: {os.getcwd()}")

        # Avvio del thread listener per accettare nuove connessioni in background
        listener = threading.Thread(target=self._listen_loop, name="ListenerThread", daemon=True)
        listener.start()

    def _listen_loop(self) -> None:
        """Ciclo infinito per accettare connessioni in entrata."""
        while self.running:
            try:
                client_socket, client_address = self.server_socket.accept()
            except OSError:
                break

            print(f"\n[CONNESSIONE IN INGRESSO] da {client_address[0]}:{client_address[1]}")

            # Registrazione del nuovo peer nel dizionario
            with self.peers_lock:
                self.peers[client_address] = client_socket

            # Ogni peer ha un thread dedicato per la gestione dei messaggi ricevuti
            handler = threading.Thread(
                target=self._handle_peer,
                args=(client_socket, client_address),
                name=f"PeerHandler-{client_address}",
                daemon=True,
            )
            handler.start()
            self._prompt()

    def _handle_peer(self, peer_socket: socket.socket, peer_address: tuple[str, int]) -> None:
        """Riceve e smista i messaggi (UPLOAD, EXEC o CHAT) provenienti da un peer."""
        try:
            while self.running:
                data = peer_socket.recv(8192) # Buffer di ricezione da 8KB
                if not data:
                    break

                # Caso 1: Ricezione File (Script)
                if data.startswith(b"UPLOAD:"):
                    try:
                        header = data[:data.find(b"\n")+1].decode("utf-8", errors="ignore")
                        size = int(header.split(":")[-1].strip())
                        file_data = data[data.find(b"\n")+1:]
                        self._receive_file(peer_socket, file_data, size, peer_address)
                        continue
                    except Exception as e:
                        print(f"[ERRORE] Formato UPLOAD non valido: {e}")
                        continue

                raw = data.decode("utf-8", errors="replace").rstrip()

                # Caso 2: Esecuzione Comando Remoto
                if raw.startswith("EXEC:"):
                    # Estrae il comando saltando il prefisso EXEC: o EXEC:all:
                    cmd = raw[5:] if not raw.startswith("EXEC:all:") else raw[9:]
                    print(f"\n[EXEC da {peer_address[0]}:{peer_address[1]}] {cmd}")
                    self._execute_command(cmd, peer_socket, peer_address)

                # Caso 3: Messaggio Chat (con eco in maiuscolo)
                else:
                    print(f"\n[MSG da {peer_address[0]}:{peer_address[1]}] {raw}")
                    if raw != raw.upper():
                        try:
                            peer_socket.sendall(raw.upper().encode("utf-8"))
                        except OSError:
                            break
                self._prompt()

        except (ConnectionResetError, OSError):
            pass
        finally:
            self._remove_peer(peer_address)

    def _execute_command(self, cmd: str, peer_socket: socket.socket, peer_address: tuple[str, int]):
        """Esegue un comando di sistema in una shell sicura (blacklist e timeout)."""
        try:
            # Semplice blacklist per evitare comandi distruttivi immediati
            dangerous = ["rm -rf", "dd if=", "> /dev/", "mkfs", "shutdown", "reboot"]
            if any(kw in cmd.lower() for kw in dangerous):
                output = "[ERRORE DI SICUREZZA] Comando bloccato."
            else:
                # shlex.split gestisce correttamente gli spazi e le virgolette nel comando
                exec_list = shlex.split(cmd)
                result = subprocess.run(
                    exec_list,
                    capture_output=True,
                    text=True,
                    timeout=120, # Timeout per evitare blocchi infiniti
                    cwd="/tmp"   # Esecuzione in directory temporanea isolata
                )
                output = result.stdout + result.stderr
                if not output.strip():
                    output = f"[OK] Eseguito (exit code: {result.returncode})"
                else:
                    output = f"[OUTPUT]\n{output}"
        except subprocess.TimeoutExpired:
            output = "[ERRORE] Timeout 120s"
        except FileNotFoundError:
            output = f"[ERRORE] Comando non trovato: {cmd.split()[0] if cmd else '??'}"
        except Exception as e:
            output = f"[ERRORE] {type(e).__name__}: {e}"

        # Invia l'output del comando al peer richiedente
        try:
            peer_socket.sendall(output.encode("utf-8"))
        except OSError:
            pass

    def _receive_file(self, peer_socket: socket.socket, received_data: bytes, size: int, peer_address: tuple[str, int]):
        """Gestisce il flusso di dati in entrata per ricostruire un file inviato."""
        try:
            data = received_data
            while len(data) < size:
                chunk = peer_socket.recv(min(8192, size - len(data)))
                if not chunk:
                    break
                data += chunk

            save_path = "/tmp/command.sh"
            with open(save_path, "wb") as f:
                f.write(data)

            # Imposta i permessi di esecuzione (rwxr-xr-x)
            os.chmod(save_path, 0o755)

            print(f"[UPLOAD SUCCESS] Script salvato come {save_path} ({len(data)} bytes)")
            peer_socket.sendall(b"[OK] Script salvato in /tmp/command.sh")

        except Exception as e:
            print(f"[ERRORE] Salvataggio file fallito: {e}")

    # ====================== LATO CLIENT ======================
    def connect_to_peer(self, ip: str, port: int) -> None:
        """Inizia una connessione verso un altro nodo P2P."""
        peer_address = (ip, port)
        with self.peers_lock:
            if peer_address in self.peers:
                print(f"[INFO] Già connesso a {ip}:{port}")
                return

        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect(peer_address)
            with self.peers_lock:
                self.peers[peer_address] = sock
            print(f"[INFO] Connesso a {ip}:{port}")

            # Avvio thread di gestione per questo socket appena aperto
            handler = threading.Thread(target=self._handle_peer, args=(sock, peer_address), daemon=True)
            handler.start()
        except Exception as e:
            print(f"[ERRORE] Connessione fallita: {e}")

    def send_script(self, target: str, local_file: str) -> None:
        """Invia un file locale a un peer specifico o a tutti."""
        if not os.path.isfile(local_file):
            print(f"[ERRORE] File non trovato: {local_file}")
            return

        with open(local_file, "rb") as f:
            file_data = f.read()

        # Header del protocollo per informare il ricevente della dimensione del file
        header = f"UPLOAD:command.sh:{len(file_data)}\n".encode("utf-8")

        with self.peers_lock:
            peer_list = list(self.peers.items())

        if target.lower() == "all":
            print(f"[SEND_SCRIPT] Invio '{local_file}' a TUTTI i peer...")
            for addr, sock in peer_list:
                try:
                    sock.sendall(header + file_data)
                except OSError:
                    self._remove_peer(addr)

            time.sleep(1.5) # Attesa per dare tempo ai nodi di scrivere il file su disco
            print("[SEND_SCRIPT] Esecuzione automatica...")
            self._send_to_all("EXEC:all:sh /tmp/command.sh")
            return

        try:
            idx = int(target) - 1
            if idx < 0 or idx >= len(peer_list):
                print(f"[ERRORE] Peer {target} non valido.")
                return
            addr, sock = peer_list[idx]
            print(f"[SEND_SCRIPT] Invio su peer {idx+1}...")
            sock.sendall(header + file_data)
            time.sleep(1.5)
            sock.sendall("EXEC:all:sh /tmp/command.sh".encode("utf-8"))
        except ValueError:
            print("Uso: send_script <numero|all> <file_locale>")

    def status(self, target: str) -> None:
        """Invia una stringa di comandi bash per raccogliere info di sistema dal peer."""
        status_cmd = "echo '=== SYSTEM STATUS ===' && hostname && whoami && uname -a && uptime && free -h | head -n 2 && df -h / | tail -1"

        with self.peers_lock:
            peer_list = list(self.peers.items())

        if target.lower() == "all":
            print("[STATUS] Richiesta su TUTTI i peer...")
            self._send_to_all(f"EXEC:all:{status_cmd}")
            return

        try:
            idx = int(target) - 1
            if idx < 0 or idx >= len(peer_list):
                print(f"[ERRORE] Peer {target} non valido.")
                return
            addr, sock = peer_list[idx]
            print(f"[STATUS] Richiesta sul peer {idx+1}...")
            sock.sendall(f"EXEC:all:{status_cmd}".encode("utf-8"))
        except ValueError:
            print("Uso: status <numero|all>")

    def exec_on_peer(self, target: str, command: str) -> None:
        """Invia una richiesta di esecuzione comando a uno o più peer."""
        with self.peers_lock:
            peer_list = list(self.peers.items())

        if not peer_list:
            print("[INFO] Nessun peer connesso.")
            return

        if target.lower() == "all":
            print(f"[INFO] Esecuzione '{command}' su TUTTI i peer...")
            self._send_to_all(f"EXEC:all:{command}")
            return

        try:
            idx = int(target) - 1
            if idx < 0 or idx >= len(peer_list):
                print(f"[ERRORE] Peer {target} non valido.")
                return
            addr, sock = peer_list[idx]
            print(f"[INFO] Esecuzione sul peer {idx+1} → {addr[0]}:{addr[1]}")
            sock.sendall(f"EXEC:{command}".encode("utf-8"))
        except ValueError:
            print("Uso: exec <numero|all> <comando>")

    def _send_to_all(self, payload: str) -> None:
        """Metodo di utility per inviare una stringa a ogni peer in lista."""
        encoded = payload.encode("utf-8")
        dead = []
        with self.peers_lock:
            for addr, sock in self.peers.items():
                try:
                    sock.sendall(encoded)
                except OSError:
                    dead.append(addr)
        for addr in dead:
            self._remove_peer(addr)

    def list_peers(self) -> None:
        """Mostra a video l'elenco numerato dei peer connessi."""
        with self.peers_lock:
            if not self.peers:
                print("[INFO] Nessun peer connesso.")
                return
            print(f"[INFO] Peer connessi ({len(self.peers)}):")
            for i, (ip, port) in enumerate(self.peers.keys(), 1):
                print(f"  {i}. {ip}:{port}")

    def shutdown(self) -> None:
        """Chiude tutti i socket e arresta i thread del nodo."""
        print("[INFO] Arresto del nodo in corso...")
        self.running = False
        with self.peers_lock:
            for sock in self.peers.values():
                try:
                    sock.close()
                except OSError:
                    pass
            self.peers.clear()

        if self.server_socket:
            try:
                self.server_socket.close()
            except OSError:
                pass
        print("[INFO] Nodo terminato.")

    def _remove_peer(self, peer_address: tuple[str, int]) -> None:
        """Rimuove in modo sicuro un peer dal dizionario e ne chiude il socket."""
        with self.peers_lock:
            sock = self.peers.pop(peer_address, None)
        if sock:
            try:
                sock.close()
            except OSError:
                pass
            print(f"[INFO] Peer {peer_address[0]}:{peer_address[1]} rimosso.")

    @staticmethod
    def _prompt() -> None:
        """Stampa il simbolo del prompt dei comandi."""
        print("> ", end="", flush=True)


# ======================================================================
def cli_loop(node: P2PNode) -> None:
    """Interfaccia a riga di comando per interagire con il nodo."""
    help_text = (
        "=== ISTRUZIONI PER L'USO DEL NODO P2P ===\n\n"
        "Comandi disponibili:\n"
        "  connect <ip> <porta>\n"
        "  send <messaggio>\n"
        "  exec <numero|all> <comando>\n"
        "  send_script <numero|all> <file_locale>    ← upload + esecuzione automatica\n"
        "  status <numero|all>                       ← info sistema remoto\n"
        "  list\n"
        "  exit / quit\n"
        "  help\n\n"
        "Esempi:\n"
        "  send_script all ./command.sh\n"
        "  status all\n"
        "  exec all whoami\n"
        "  exec 1 ls -la"
    )
    print(help_text)

    while True:
        try:
            line = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if not line:
            continue

        parts = line.split(maxsplit=2)
        cmd = parts[0].lower()

        if cmd == "connect":
            if len(parts) != 3:
                print("Uso: connect <ip> <porta>")
                continue
            try:
                node.connect_to_peer(parts[1], int(parts[2]))
            except ValueError:
                print("Porta non valida.")

        elif cmd == "send":
            if len(parts) < 2:
                print("Uso: send <messaggio>")
                continue
            node._send_to_all("CHAT:" + " ".join(parts[1:]))

        elif cmd == "exec":
            if len(parts) < 3:
                print("Uso: exec <numero|all> <comando>")
                continue
            node.exec_on_peer(parts[1], " ".join(parts[2:]))

        elif cmd == "send_script":
            if len(parts) < 3:
                print("Uso: send_script <numero|all> <file_locale>")
                continue
            node.send_script(parts[1], parts[2])

        elif cmd == "status":
            if len(parts) < 2:
                print("Uso: status <numero|all>")
                continue
            node.status(parts[1])

        elif cmd == "list":
            node.list_peers()

        elif cmd in ("exit", "quit"):
            break

        elif cmd == "help":
            print(help_text)
        else:
            print(f"Comando sconosciuto: {cmd}")

    node.shutdown()

def main() -> None:
    """Punto di ingresso del programma: gestisce gli argomenti CLI e avvia il nodo."""
    if len(sys.argv) != 2:
        print(f"Uso: python3 {sys.argv[0]} <porta>")
        sys.exit(1)

    try:
        port = int(sys.argv[1])
        if not 0 < port < 65536:
            raise ValueError
    except ValueError:
        print("Porta non valida (1-65535).")
        sys.exit(1)

    # In ascolto su tutte le interfacce di rete (0.0.0.0)
    node = P2PNode("0.0.0.0", port)
    node.start()

    try:
        cli_loop(node)
    except Exception as e:
        print(f"[ERRORE FATALE] {e}")
        node.shutdown()

if __name__ == "__main__":
    main()