know_it_all - Solution

Each challenge exposes one fragment. Concatenate all six in order to
assemble the flag: ASRCTF{<1><2><3><4><5><6>}.

---

## 1. Forensics — calibration.png

Inspecting the PNG metadata with exiftool or PIL reveals several tEXt
chunks. Most are plausible camera fields; the CameraSerial entry
stands out as it contains no serial-number formatting.

Fragment: th3_5k

---

## 2. Rev — vault

Strings on the binary surfaces a short ciphertext embedded in .rodata.
The curly-brace structure signals a Caesar-family cipher; ROT13 resolves
it in one step. Running the binary directly also works.

Fragment: 1ll5_y

---

## 3. Crypto — message.txt

The transmission header states both the cipher (Vigenere) and the key
(NEXUS). Non-alphabetic characters pass through unchanged. Any standard
Vigenere decoder or a short hand-decryption recovers the fragment.

Fragment: 0u_l34

---

## 4. OSINT — report.pdf

Running pdfinfo or exiftool on the PDF dumps its document properties.
The Author and Keywords fields each hold half of the fragment;
concatenating them in that order gives the full piece.

Fragment: rn_4l0

---

## 5. Web — live service

Fetching the portal with curl -v shows the raw response headers. A
non-standard header carries the fragment; the browser renders the HTML
body only, so this goes unnoticed without inspecting the headers.

Fragment: ng_th3

---

## 6. Pwn — door

The binary prints the address of win() on startup, eliminating the need
for disassembly. A 32-byte overflow reaches the return address; a single
ret gadget handles stack alignment before jumping to win().

Fragment: _w4y
