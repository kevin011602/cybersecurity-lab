#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import socket
import sys
import subprocess
import tempfile
import os


def start_client(server_ip: str, server_port: int) -> None:
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            print(f"Connecting to {server_ip}:{server_port}...")
            sock.connect((server_ip, server_port))

            print("Connection established. Receiving script...")

            # Receive script from server (simple stream-based protocol)
            response_data = b''
            while True:
                chunk = sock.recv(4096)
                if not chunk:
                    break
                response_data += chunk
                if len(chunk) < 4096:
                    break

            script_content = response_data.decode('utf-8')

            if script_content.strip() == "SCRIPT_NOT_FOUND":
                print("No script provided by server.")
                return

            # Save received script to temporary file
            with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix=".sh") as script_file:
                script_file.write(script_content)
                temp_script_path = script_file.name

            # Make script executable
            os.chmod(temp_script_path, 0o755)

            print(f"Executing received script: {temp_script_path}\n")
            subprocess.run([temp_script_path], check=False)

            os.remove(temp_script_path)
            print("Script executed and removed.")

    except ConnectionRefusedError:
        print(f"Connection refused. Is the server running on {server_ip}:{server_port}?")
    except socket.gaierror:
        print(f"Invalid server address: {server_ip}")
    except socket.error as e:
        print(f"Socket error: {e}")
    except KeyboardInterrupt:
        print("\nClient interrupted by user.")
    finally:
        print("Client terminated.")


def main():
    if len(sys.argv) != 3:
        print(f"Usage: python3 {sys.argv[0]} <server_ip> <server_port>")
        sys.exit(1)

    server_ip = sys.argv[1]

    try:
        server_port = int(sys.argv[2])
        if not 0 < server_port < 65536:
            raise ValueError
    except ValueError:
        print("Error: port must be between 1 and 65535.")
        sys.exit(1)

    start_client(server_ip, server_port)


if __name__ == "__main__":
    main()