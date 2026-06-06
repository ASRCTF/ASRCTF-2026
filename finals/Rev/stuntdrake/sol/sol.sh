#!/bin/bash

while true; do for f in whelp twilight_hatchling_*; do if [ -f "$f" ]; then strings "$f" 2>/dev/null | grep "=" >>equations.txt && echo "[+] Captured from $f" && while [ -f "$f" ]; do sleep 0.1; done; fi; done; done
