#!/usr/bin/env python3
import subprocess
import re
import random
import sys
import signal
import time

"""
Questo script permette di cambiare l'indirizzo fisico (MAC) di una scheda di rete. 

Come si esegue:
1. Modalità Random: sudo python3 stealth_mac.py eth0
2. Modalità Custom: sudo python3 stealth_mac.py eth0 00:11:22:33:44:55

Comandi utili per verifica:
ip link show <interfaccia>
"""

class MACHandler:
    def __init__(self, interface):
        self.interface = interface

    def get_current_mac(self):
        try:
            output = subprocess.check_output(
                ["ip", "link", "show", self.interface],
                text=True
            )
            match = re.search(
                r"link/ether\s+(([0-9a-fA-F]{2}:){5}[0-9a-fA-F]{2})",
                output
            )
            return match.group(1) if match else None
        except Exception:
            return None

    def change_mac(self, new_mac):
        try:
            # stop NetworkManager interference
            subprocess.run(
                ["nmcli", "device", "disconnect", self.interface],
                check=False
            )

            subprocess.run(["ip", "link", "set", self.interface, "down"], check=True)
            subprocess.run(["ip", "link", "set", self.interface, "address", new_mac], check=True)
            subprocess.run(["ip", "link", "set", self.interface, "up"], check=True)

            # reconnect network manager
            subprocess.run(
                ["nmcli", "device", "connect", self.interface],
                check=False
            )

            return True

        except subprocess.CalledProcessError:
            return False


class MACGenerator:
    @staticmethod
    def generate_random_mac():
        first_byte = 0x02  # standard locally administered MAC
        mac = [first_byte] + [random.randint(0x00, 0xff) for _ in range(5)]
        return ':'.join(f"{b:02x}" for b in mac)

    @staticmethod
    def is_valid_mac(mac):
        return re.fullmatch(
            r"[0-9a-fA-F]{2}(:[0-9a-fA-F]{2}){5}",
            mac
        ) is not None


class StealthMACApp:
    def __init__(self, interface):
        self.handler = MACHandler(interface)
        self.interface = interface
        self.original_mac = self.handler.get_current_mac()

        if not self.original_mac:
            print(f"[!] Interfaccia non trovata: {interface}")
            sys.exit(1)

        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)

    def signal_handler(self, sig, frame):
        print(f"\n[!] Interruzione ({sig})")
        self.restore_and_exit()

    def restore_and_exit(self):
        print(f"[*] Ripristino MAC originale: {self.original_mac}")
        self.handler.change_mac(self.original_mac)
        print("[✓] Ripristinato.")
        sys.exit(0)

    def verify_mac(self, expected_mac, retries=5):
        for _ in range(retries):
            current = self.handler.get_current_mac()
            if current and current.lower() == expected_mac.lower():
                return True
            time.sleep(0.2)
        return False

    def run(self, mode="random", custom_mac=None):
        print(f"[i] Interface: {self.interface}")
        print(f"[i] Original MAC: {self.original_mac}")

        target_mac = (
            custom_mac if mode == "custom"
            else MACGenerator.generate_random_mac()
        )

        if not MACGenerator.is_valid_mac(target_mac):
            print("[!] MAC non valido.")
            return

        print(f"[+] Changing MAC → {target_mac}")

        if self.handler.change_mac(target_mac):

            if self.verify_mac(target_mac):
                print("[✓] MAC cambiato e verificato correttamente.")
            else:
                print("[!] MAC cambiato ma non verificato (possibile override sistema).")

            print("\n[!] CTRL+C per ripristinare il MAC originale")

            while True:
                time.sleep(1)

        else:
            print("[!] Errore cambio MAC (permessi root o NetworkManager attivo?)")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: sudo python3 stealth_mac.py <interfaccia> [mac]")
        sys.exit(1)

    iface = sys.argv[1]
    custom = sys.argv[2] if len(sys.argv) > 2 else None

    app = StealthMACApp(iface)

    if custom:
        app.run(mode="custom", custom_mac=custom)
    else:
        app.run(mode="random")