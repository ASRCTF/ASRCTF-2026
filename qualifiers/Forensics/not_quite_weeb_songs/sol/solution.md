not_quite_weeb_songs - Solution

The flag is hidden inside a fabricated Spotify streaming history JSON file. Two
anomalies chain together: the first produces a numeric key, the second uses that
key to decode a payload embedded in a clock-tampered listening session.

  Step 1  ->  locate the impossible IP hop within a single session
  Step 2  ->  measure the gap in seconds between the two bordering records (108 s)
  Step 3  ->  treat the gap as an XOR key; find the session where timestamps
              go backwards and every ms_played is a multiple of 1337
  Step 4  ->  apply chr( (ms_played // 1337) XOR 108 ) across all 60 tracks
              in file order, join, Base64-decode -> flag

```bash
python3 solve.py Streaming_History_Audio_2026.json
```

Running the program gives you the flag:
Flag: ASRCTF{h1pp1ty_h0pp1ty_r3w1nd1ty_t3l3p0rt1ty}
