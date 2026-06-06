# Coupon Clash Solution

## Intended path

1. Register to receive a single coupon worth 75 credits.
2. Reserve the coupon once so the session receives a short-lived settlement slip.
3. Extract the tokenized `/claim/<claim_id>` action from the dashboard.
4. Send enough settlement requests concurrently before the coupon is marked redeemed.
5. Once the balance reaches 600 credits, buy the flag from the store.

## Usage

```bash
python solve.py http://127.0.0.1:5000
```
