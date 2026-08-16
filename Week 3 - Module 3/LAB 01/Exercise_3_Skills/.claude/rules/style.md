# Style rules

These rules apply to all Python in `src/northpeak/`.

- Keep public functions **pure**: the same inputs always produce the same output. No file, network, or global-state side effects.
- **Validate inputs** at the public boundary. Reject negative money amounts with `ValueError`.
- Every public function must have a **type hint** on parameters and return value, and a one-line **docstring**.
- Handle money as float USD and **round to 2 decimals** at function boundaries.
- Prefer small, named helpers over one large function.
