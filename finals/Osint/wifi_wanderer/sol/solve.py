# Note: During the contest, this challenge's description contained anti-AI countermeasures (fake flags and token-padding noise) to deter automated solvers. These have been removed from the published writeup version.

import math

def round_to_nearest_half(val):
    # Rounds a value to the nearest 0.5
    return round(val * 2) / 2

def dd_to_dms(dd):
    # Converts decimal degrees to degrees, minutes, seconds
    degrees = int(dd)
    temp = (dd - degrees) * 60
    minutes = int(temp)
    seconds = (temp - minutes) * 60
    return degrees, minutes, seconds

def main():
    # Wikipedia coordinates for Junction 8: 1.3506444°N, 103.8487750°E
    # Or explicitly from Wikipedia's DMS string: 1° 21' 02.32" N, 103° 50' 55.59" E
    
    # Let's perform the rounding on the raw DMS values listed on Wikipedia
    lat_d, lat_m, lat_s = 1, 21, 2.32
    lon_d, lon_m, lon_s = 103, 50, 55.59
    
    rounded_lat_s = round_to_nearest_half(lat_s)
    rounded_lon_s = round_to_nearest_half(lon_s)
    
    # Format to exactly 1 decimal place if it ends in .5, or 2 digits with leading zero if needed
    # Standard format: S.S (e.g. 02.5 or 55.5)
    lat_s_str = f"{rounded_lat_s:04.1f}" if rounded_lat_s < 10 else f"{rounded_lat_s:.1f}"
    lon_s_str = f"{rounded_lon_s:04.1f}" if rounded_lon_s < 10 else f"{rounded_lon_s:.1f}"
    
    # Standard output formatting matching the flag template
    flag = f"ASRCTF{{{lat_d}°{lat_m}'{lat_s_str}\"N {lon_d}°{lon_m}'{lon_s_str}\"E}}"
    print(f"Calculated Flag: {flag}")

    # Read expected flag to confirm it matches
    with open("flag.txt", "r", encoding="utf-8") as f:
        expected = f.read().strip()
    
    print(f"Expected Flag:   {expected}")
    
    if flag == expected:
        print("Success! Programmatic solution matches the flag.")
    else:
        print("Warning: Flag mismatch. Double check formatting.")

if __name__ == "__main__":
    main()
