# godaddycheck

[![PyPI version](https://img.shields.io/pypi/v/godaddycheck.svg)](https://pypi.org/project/godaddycheck/)
[![Python](https://img.shields.io/pypi/pyversions/godaddycheck.svg)](https://pypi.org/project/godaddycheck/)
[![License](https://img.shields.io/pypi/l/godaddycheck.svg)](https://pypi.org/project/godaddycheck/)
[![Coverage](https://img.shields.io/badge/coverage-100%25-brightgreen.svg)](https://github.com/onlyoneaman/godaddycheck)
[![Downloads](https://img.shields.io/pypi/dm/godaddycheck.svg)](https://pypi.org/project/godaddycheck/)
[![Downloads/week](https://img.shields.io/pypi/dw/godaddycheck.svg)](https://pypi.org/project/godaddycheck/)

> **Built by [aman](https://amankumar.ai) | [@onlyoneaman](https://x.com/onlyoneaman)**

Simple Python package and CLI tool for checking domain availability using the GoDaddy API.

**⭐ If you find this project useful, please consider giving it a star and forking it!**

## Features

- **Check** domain availability
- **Suggest** domain names based on keywords
- **List** available TLDs (top-level domains)
- Built-in retry logic with exponential backoff
- Both library and CLI interface
- Automatic price normalization
- Support for GoDaddy OTE (Operational Test Environment) via `GODADDY_API_URL`

## Installation

```bash
pip install godaddycheck
```

Or install from source:

```bash
git clone https://github.com/onlyoneaman/godaddycheck.git
cd godaddycheck
pip install -e .
```

## Setup

You need GoDaddy API credentials. Get them from [GoDaddy Developer Portal](https://developer.godaddy.com/).

Set environment variables:

```bash
export GODADDY_API_KEY="your_api_key"
export GODADDY_API_SECRET="your_api_secret"
```

For GoDaddy OTE (test environment), also set:

```bash
export GODADDY_API_URL="https://api.ote-godaddy.com"
```

Or create a `.env` file in your project directory (automatically loaded):

```env
GODADDY_API_KEY=your_api_key
GODADDY_API_SECRET=your_api_secret
GODADDY_API_URL=https://api.godaddy.com  # Optional, defaults to production
```

The package automatically loads `.env` files, so you don't need to manually export variables.

## Usage

### Command Line Interface

#### Check domain availability

```bash
# Quick check
godaddycheck check amankumar.ai

# Full check with more details
godaddycheck check amankumar.ai --type FULL

# JSON output
godaddycheck check amankumar.ai --json
```

#### Get domain suggestions

```bash
# Get 10 suggestions (default)
godaddycheck suggest tech

# Get 5 suggestions
godaddycheck suggest startup --limit 5

# JSON output
godaddycheck suggest app --json
```

#### List available TLDs

```bash
# Show first 20 TLDs (default)
godaddycheck tlds

# Show all TLDs
godaddycheck tlds --limit 0

# Show first 50 TLDs
godaddycheck tlds --limit 50

# JSON output
godaddycheck tlds --json
```

### Python Library

#### Basic usage

```python
import godaddycheck

# Check a domain
result = godaddycheck.check('amankumar.ai')
print(f"Available: {result['available']}")
print(f"Price: ${result.get('price', 'N/A')}")

# Get suggestions
suggestions = godaddycheck.suggest('tech', limit=5)
for s in suggestions:
    print(f"{s['domain']}: ${s.get('price', 'N/A')}")

# Get TLDs
tlds = godaddycheck.tlds()
print(f"Found {len(tlds)} TLDs")
```

#### Using the client class

```python
from godaddycheck import GoDaddyClient

# Initialize client (uses environment variables by default)
client = GoDaddyClient()

# Check domain
result = client.check('amankumar.ai', check_type='FAST')
print(result)

# Get suggestions
suggestions = client.suggest('startup', limit=10)
print(suggestions)

# Get TLDs
tlds = client.tlds()
print(tlds)

# Clean up
client.close()
```

#### Using context manager

```python
from godaddycheck import GoDaddyClient

with GoDaddyClient() as client:
    result = client.check('amankumar.ai')
    print(result)
# Client automatically closed
```

#### Custom configuration

```python
from godaddycheck import GoDaddyClient

client = GoDaddyClient(
    api_key='your_key',
    api_secret='your_secret',
    api_url='https://api.ote-godaddy.com',  # Optional
    max_retries=5,
    timeout=60.0
)

result = client.check('amankumar.ai')
```

## API Response Examples

### Check domain

```json
{
  "domain": "amankumar.ai",
  "available": false,
  "currency": "USD"
}
```

### Suggest domains

```json
[
  {
    "domain": "techstartup.com",
    "available": true,
    "price": 12.99,
    "currency": "USD"
  },
  {
    "domain": "mytech.io",
    "available": true,
    "price": 39.99,
    "currency": "USD"
  }
]
```

### List TLDs

```json
[
  {
    "name": "com",
    "type": "GENERIC"
  },
  {
    "name": "io",
    "type": "COUNTRY_CODE"
  }
]
```

## Development

```bash
# Clone the repo
git clone https://github.com/onlyoneaman/godaddycheck.git
cd godaddycheck

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode
pip install -e .

# Install dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run tests with coverage
pytest --cov=godaddycheck --cov-report=html
```

## Requirements

- Python >= 3.7
- httpx >= 0.24.0

## Best Practices

### Virtual Environment

Always use a virtual environment when working with Python packages:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install godaddycheck
```

### Environment Variables

Store sensitive credentials in environment variables or `.env` files (never commit them):

```bash
# .env file (add to .gitignore)
GODADDY_API_KEY=your_key
GODADDY_API_SECRET=your_secret
```

### Resource Management

Use context managers for automatic cleanup:

```python
with GoDaddyClient() as client:
    result = client.check('amankumar.ai')
```

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Support

- **Issues**: [GitHub Issues](https://github.com/onlyoneaman/godaddycheck/issues)
- **Author**: **Aman** - hi@amankumar.ai | [amankumar.ai](https://amankumar.ai) | [@onlyoneaman](https://x.com/onlyoneaman)

---

**⭐ Star this repo if you find it useful!**
