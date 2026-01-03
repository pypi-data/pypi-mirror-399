# godaddycheck

Simple Python package and CLI tool for checking domain availability using the GoDaddy API.

## Features

- **Check** domain availability
- **Suggest** domain names based on keywords
- **List** available TLDs (top-level domains)
- Built-in retry logic with exponential backoff
- Both library and CLI interface
- Automatic price normalization

## Installation

```bash
pip install godaddycheck
```

Or install from source:

```bash
git clone https://github.com/yourusername/godaddycheck.git
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

Or create a `.env` file:

```
GODADDY_API_KEY=your_api_key
GODADDY_API_SECRET=your_api_secret
```

## Usage

### Command Line Interface

#### Check domain availability

```bash
# Quick check
godaddycheck check example.com

# Full check with more details
godaddycheck check example.com --type FULL

# JSON output
godaddycheck check example.com --json
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
result = godaddycheck.check('example.com')
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

# Initialize client
client = GoDaddyClient()

# Check domain
result = client.check('example.com', check_type='FAST')
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
    result = client.check('example.com')
    print(result)
# Client automatically closed
```

#### Custom configuration

```python
from godaddycheck import GoDaddyClient

client = GoDaddyClient(
    api_key='your_key',
    api_secret='your_secret',
    max_retries=5,
    timeout=60.0
)

result = client.check('example.com')
```

## API Response Examples

### Check domain

```json
{
  "domain": "example.com",
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

## Error Handling

The package automatically retries failed requests with exponential backoff for:
- Network errors
- Timeouts
- Rate limiting (429)
- Server errors (5xx)

```python
from godaddycheck import GoDaddyClient
import httpx

try:
    client = GoDaddyClient()
    result = client.check('example.com')
except ValueError as e:
    print(f"Configuration error: {e}")
except httpx.HTTPStatusError as e:
    print(f"API error: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

## Development

```bash
# Clone the repo
git clone https://github.com/yourusername/godaddycheck.git
cd godaddycheck

# Install in development mode
pip install -e .

# Install dev dependencies
pip install -e ".[dev]"

# Run tests
pytest
```

## Requirements

- Python >= 3.7
- httpx >= 0.24.0

## License

MIT License - see LICENSE file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Credits

Inspired by the bella project's GoDaddy service implementation.
