Key 1:

Download the audio signal from the Cosmo Connect tab
Use a spectogram viewer to find KEY 1: SPICA_98

Key 2:

Access the web portal. Read through Commander Leo Sterling's microblog feed (@leo_sterling).
You will notice a colleague (@sjenkins_telemetry) reminding him to secure his repository because he committed Wayback URLs and EXIF credentials in the history. Leo replies that he deleted them from the main branch config.
Click on the second commit: Remove test endpoint, staging keys, and old archive url (SHA: d3b10ea).
The commit diff displays the deleted lines:
ARCHIVE_SERVER = "http://archive.cosmoconnect.net/archive/leosterling.astro.old"
EXIF_DECRYPTION_KEY = "HYPERION_X"

Navigate to the [3] AstroArchive tab.
Enter the domain leosterling.astro.old into the browser address bar and search.
At the bottom, click the download link for hyperion_handbook.pdf
Use inspect PDF tool like pdfcrowd to find an object beyond the 3rd page, from there, we can find the KEY2: HYPERION_ALPHA_7

Key 3:

For Key 3, inspect Commander Leo's profile picture on his social posts. The spacecraft pictured is the famous Cassini-Huygens space probe.
Search the web (Wikipedia, NASA) for the official International Designator / COSPAR ID of Cassini-Huygens.
The designator is 1997-061A. We now have Key 3: 1997-061A.

JWT Secret:

In the social feed, download observatory.jpg from Leo's post about his childhood hometown.
Run exiftool observatory.jpg or use an online EXIF viewer (like Jeffrey's Image Metadata Viewer).
Look at the UserComment tag. You will find a hex string: 7b617e71617a7e7c6c74656e696b6a7a76766b6d
The EXIF decryption key is HYPERION_X (found in the Git history commit diff).
Perform an XOR decryption of the hex bytes against the repeated key string HYPERION_X.
Example Python decryption script:
python

hex_str = "7b617e71617a7e7c6c74656e696b6a7a76766b6d"
key = "HYPERION_X" (Found from the github commit in key 2)
ciphertext = bytes.fromhex(hex_str)
key_repeated = (key * (len(ciphertext) // len(key) + 1))[:len(ciphertext)]
plaintext = "".join(chr(c ^ ord(k)) for c, k in zip(ciphertext, key_repeated))
print(plaintext)
# Outputs: 38.433123,-79.839845

OR

You could use online tools such as CyberChef to decrypt this
First, enter the "From Hex" into the recipe, then put in the "XOR" operation under it
Use "HYPERION_X" as the key for the XOR with a "UTF-8" format
Then input the hex_str into the input box, and it should output the same as above

Enter these coordinates (38.433123, -79.839845) into Google Maps or OpenStreetMap.
The coordinates point directly to the Green Bank Telescope in Green Bank, West Virginia.
The childhood observatory town is Green Bank.
The developer comments in app.js hint that the JWT HMAC secret key is the lowercase name of this town: greenbank.


JWT Role change:

Go to the [4] Command Center page.
Notice the Active JWT Session Decoder showing your default session token. It is signed, but has the role "cadet" (unprivileged).
Copy the JWT string from the textarea. It looks like: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VybmFtZSI6ImNhZGV0XzEyIiwicm9sZSI6ImNhZGV0In0.Xk5...
Go to a JWT debugger (like jwt.io) or use a local python script to edit it.
In the Payload block, change "role": "cadet" to "role": "commander", and "username": "cadet_12" to "username": "leo_sterling".
New Payload: {"username": "leo_sterling", "role": "commander"}
Using HMAC-SHA256 with the secret key greenbank.

The forged JWT will be: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VybmFtZSI6Imxlb19zdGVybGluZyIsInJvbGUiOiJjb21tYW5kZXIifQ.4f2c7a2d8a9b3c4d5e...
Paste the forged JWT back into the Command Center textarea.
The session visualizer will immediately light up green and display: VALID SIGNATURE - ROLE: COMMANDER (ACCESS GRANTED)


Submit the 3 keys and the correct JWT and the flag would be displayed, ASRCTF{5t4lk1ng_thr0ugh_th3_c05m05_cf6a2}