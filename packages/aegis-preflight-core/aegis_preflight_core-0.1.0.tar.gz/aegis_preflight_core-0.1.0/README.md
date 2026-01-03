# aegis-core

Core detection and masking library for Aegis PII protection.

This package provides the shared detection and masking functionality used by both the Aegis API and SDK.

## Installation

```bash
pip install aegis-core
```

## Usage

```python
from aegis_core import detect, mask_text

# Detect sensitive data
items = detect("Contact john@example.com at 555-123-4567")
for item in items:
    print(f"{item.type}: {item.count}")
# EMAIL: 1
# PHONE: 1

# Mask sensitive data
masked = mask_text("Contact john@example.com at 555-123-4567")
print(masked)
# Contact j***@example.com at XXX-XXX-4567
```

## Detection Types

- `EMAIL` - Email addresses
- `PHONE` - Phone numbers
- `CREDIT_CARD` - Credit card numbers (Luhn validated)
- `SSN` - Social Security Numbers
- `API_SECRET` - API keys and secrets
- `IBAN` - International Bank Account Numbers
- `PHI_KEYWORD` - Protected Health Information keywords

## License

Proprietary - Aegis Preflight
