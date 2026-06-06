# Union Station Solution

## Intended path

1. Register or log in to reach the archive search.
2. Notice the advanced JSON search endpoint and its `_connector` field.
3. Inject a connector that changes the structured filter into a compatible `UNION SELECT`.
4. Pull the flag from the hidden `secrets` table.

## Usage

```bash
python solve.py http://127.0.0.1:5000
```
