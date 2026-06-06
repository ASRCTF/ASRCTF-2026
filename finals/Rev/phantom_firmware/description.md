Challenge Title: Phantom Firmware<br>
Author: Chthonic Cream<br>
Description:<br>
*Stardate 2487.3 - Kepler-442b Orbital Corridor*<br>
<br>
A deep space probe's firmware update relay has been compromised.<br>
<br>
During a routine memory dump from **Orbital Relay Station 7** - one of the automated firmware distribution nodes along the Kepler-442b survey corridor - something anomalous was captured. The relay was in the middle of pushing a firmware update to the Kepler-442b deep-field survey probe when the dump was taken.<br>
<br>
The incident packet classifies the image as a Linux memory-forensics case. Parse the LiME header, recover the kernel symbol table, identify the hidden rootkit module, then carve the module's encrypted config block to obtain the command string.<br>
<br>
The clock is ticking. The next firmware push is in 6 hours, and whatever is hiding in that payload will propagate to every probe in the corridor.
