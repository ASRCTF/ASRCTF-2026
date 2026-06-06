# Receipt Runner Solution

## Intended path

1. Fetch the public key from the `/public_key` endpoint.
2. Forge a JWT by signing it with the public key as the secret, but specifying the symmetric algorithm `HS256` (JWT Algorithm Confusion).
3. Access the administrative organizer endpoint at `/organizer/receipts/8421` using the forged token.
4. Extract the flag from the response.

## Usage

```bash
python solve.py http://127.0.0.1:5000
```
