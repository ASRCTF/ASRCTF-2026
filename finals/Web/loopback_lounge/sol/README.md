# Loopback Lounge Solution

## Intended path

1. Use the sponsor preview endpoint and notice it resolves user input against a base URL.
2. Pass an absolute URL so URL resolution ignores the sponsor base URL.
3. Read the leaked internal mirror port from the page and target IPv6 loopback at `[::1]`.
4. Read the internal response through the preview panel.

## Usage

```bash
python solve.py http://127.0.0.1:5000
```
