Event Horizon - Solution
---

## Part 1: Timestamps

Every record's FILETIME timestamp has its millisecond field set to the ASCII value of one flag character, in record order. FILETIME is a 64-bit count of 100-nanosecond intervals since 1601-01-01.

Reading all 27 millisecond values as ASCII bytes in record order gives Part 1. The tell is that every millisecond value falls in the printable ASCII range (49–123) rather than the sub-millisecond noise present in real event logs.

```python
ft = struct.unpack_from('<Q', rec._buf, rec._offset + 16)[0]
ms = (ft % 10_000_000) // 10_000
```

Part 1: `ASRCTF{t1m3_4nd_3v3nt5_c4n_`

---

## Part 2: ScriptBlockText Base64

Parsing the log reveals record 14 of 27 contains an anomalous ScriptBlockText, the only record with a FromBase64String call:

```powershell
$b=[System.Convert]::FromBase64String('YjB0aF9iM191NTNkX3QwX2gxZDNfdGgxbmc1fQ==');Invoke-Expression(...)
```

Decoding the payload directly gives Part 2 as plaintext ASCII:

```bash
echo 'YjB0aF9iM191NTNkX3QwX2gxZDNfdGgxbmc1fQ==' | base64 -d
```

Part 2: `b0th_b3_u53d_t0_h1d3_th1ng5}`

---

## Flag

Concatenate Part 1 + Part 2:

ASRCTF{t1m3_4nd_3v3nt5_c4n_b0th_b3_u53d_t0_h1d3_th1ng5}
