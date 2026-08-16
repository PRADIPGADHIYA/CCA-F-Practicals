# Testing rules

- Add a test for **every behaviour change** (new function, new branch, or changed return value).
- Use **sentence-style names**: `test_member_discount`, `test_free_shipping_threshold` — they should read like a claim.
- Cover the **boundary and both sides**. Example: free shipping at `$75` means test `$74.99` (just below) and `$75.00` (at the threshold).
- `pytest -q` must pass from the project root before you finish. Config lives in `pytest.ini`.
- Tests live in `src/tests/`. Import the package as `from northpeak.pricing import ...`.
