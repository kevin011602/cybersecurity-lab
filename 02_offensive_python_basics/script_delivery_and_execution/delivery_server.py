#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import socketserver
import threading
import os


class ScriptRequestHandler(socketserver.BaseRequestHandler):
    def handle(self):
        client_ip = self.client_address[0]
        thread_name = threading.current_thread().name

        print(f"[{thread_name}] Client connected: {client_ip}")

        try:
            # Load payload script if available
            payload_path = "payloads/http_flood_sim.sh"

            if os.path.exists(payload_path):
                with open(payload_path, "r") as f:
                    script_content = f.read()

                print(f"[{thread_name}] Sending payload to client...")
                self.request.sendall(script_content.encode("utf-8"))

            else:
                error_message = "SCRIPT_NOT_FOUND"
                print(f"[{thread_name}] Payload not found: {payload_path}")
                self.request.sendall(error_message.encode("utf-8"))

        except Exception as e:
            print(f"[{thread_name}] Error while sending payload: {e}")

        finally:
            print(f"[{thread_name}] Connection closed: {client_ip}")


def main():
    HOST, PORT = "0.0.0.0", 8000

    socketserver.ThreadingTCPServer.allow_reuse_address = True

    try:
        with socketserver.ThreadingTCPServer((HOST, PORT), ScriptRequestHandler) as server:
            print(f"[+] Script delivery server running on {HOST}:{PORT}")
            print("[*] Press CTRL+C to stop.")

            server.serve_forever()

    except KeyboardInterrupt:
        print("\n[!] Server shutdown requested.")

    finally:
        print("Server stopped.")


if __name__ == "__main__":
    main()