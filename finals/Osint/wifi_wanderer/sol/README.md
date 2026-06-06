# Wifi Wanderer - Solution (Redacted / Advanced Version)

## Analysis

With all key commercial, F&B, and public SSIDs redacted (blacked out), a simple Google search correlation is no longer possible. Solving this challenge requires advanced wireless geolocation (Wi-Fi triangulation) using OSINT tools.

### 1. Identifying the Country
* The presence of multiple SSIDs matching the format `SINGTEL-xxxx` (e.g., `SINGTEL-6188`, `SINGTEL-TY9G`, `SINGTEL-A57D`, `SINGTEL-CE08_MLO`) points directly to **Singapore**, where **Singtel** is the primary telecommunications provider supplying default router names.
* Other generic router SSIDs like `TP-Link_3C57`, `TP-Link_DFB0`, and `MERCUSYS_22D4` represent common home routers.

### 2. Wi-Fi Geolocation Lookup (Wigle.net)
The intended path is to query a global crowd-sourced Wi-Fi database such as **Wigle.net** using the remaining unique residential/device SSIDs:

1. Solvers look up specific, less common residential/hotspot SSIDs seen in the screenshots:
   * `SINGTEL-6188`
   * `SINGTEL-TY9G`
   * `MERCUSYS_22D4`
   * `TP-Link_3C57`
2. Querying these SSIDs in the Singapore area on Wigle.net yields specific geographic clusters:
   * `SINGTEL-6188` resolves to the vicinity of Block 503, Bishan Street 11.
   * `SINGTEL-TY9G` resolves to the vicinity of Block 501, Bishan Street 11.
   * `MERCUSYS_22D4` resolves to the vicinity of Block 502, Bishan Street 11.
3. Overlapping these coverage areas places the coordinate of the scanner directly at the boundary of these blocks, which sits right next to **Junction 8 Shopping Mall** in Bishan, Singapore.
4. The presence of a commercial smart TV (`[TV] Samsung 6 Series (32)`) and multiple distinct home networks bleeding in confirms the observer is inside the adjacent commercial landmark: **Junction 8**.

### 3. Extracting and Converting Coordinates
* The Wikipedia page for **Junction 8** lists its coordinates as:
  `1°21′02.32″N 103°50′55.59″E`
* Rounding the seconds to the nearest 0.5":
  * Latitude: `02.32"` is closer to `02.5"` than `02.0"`. Rounds to `02.5"`.
  * Longitude: `55.59"` is closer to `55.5"` than `56.0"`. Rounds to `55.5"`.

### 4. Flag
`ASRCTF{1°21'02.5"N 103°50'55.5"E}`
