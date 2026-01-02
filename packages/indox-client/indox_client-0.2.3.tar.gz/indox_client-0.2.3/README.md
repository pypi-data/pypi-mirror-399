# indox-client

Python SDK for the Indox media and document conversion services.

## Installation

```bash
pip install indox-client
```

## Quick Start

```python
from indox_client import Indox

# Initialize with API key
client = Indox(api_key="your-api-key")

# Or use environment variable (INDOX_API_KEY)
client = Indox()

# Convert a font file (all-in-one)
path = client.fonts.convert_and_download(
    "./font.ttf",
    target_format="woff2",
    output_path="./font.woff2"
)
print(f"Downloaded: {path}")
```

## Features

- **Font Conversion**: Convert between TTF, OTF, WOFF, WOFF2, EOT, SVG, and 13+ other formats
- **Media Conversion**: Convert images and videos (coming soon)
- **Simple API**: OpenAI-style client pattern
- **Multiple Input Sources**: Local files, S3 keys

## Font Conversion

### List Supported Formats

```python
from indox_client import Indox

client = Indox(api_key="your-api-key")

# Get all engines and formats
formats = client.fonts.formats.list()
print(f"Total formats: {formats['total_formats']}")
print(f"Engines: {list(formats['engines'].keys())}")

# Get outputs for specific input format
outputs = client.fonts.formats.get("ttf")
for out in outputs["outputs"]:
    print(f"  ttf -> {out['output']} ({out['engine']})")
```

### Convert Font File

**Option 1: All-in-one (recommended)**

```python
path = client.fonts.convert_and_download(
    "./font.ttf",
    target_format="woff2",
    output_path="./font.woff2",
    timeout=60.0
)
```

**Option 2: Step-by-step**

```python
# Upload
upload = client.fonts.upload("./font.ttf")
print(f"Uploaded: {upload['s3_key']}")

# Convert
job = client.fonts.convert(upload["s3_key"], target_format="woff2")
print(f"Job ID: {job['id']}")

# Wait for completion
result = client.fonts.conversions.wait(job["id"], timeout=60.0)
print(f"Status: {result['status']}")

# Download
path = client.fonts.conversions.download(job["id"], "./font.woff2")
print(f"Downloaded: {path}")
```

### Validate Before Converting

```python
validation = client.fonts.validate("./font.ttf", target_format="woff2")

if validation["valid"]:
    print(f"Engine: {validation['engine']}")
    print(f"Credits: {validation['credits']}")
else:
    print("Conversion not supported")
```

## Context Manager

```python
from indox_client import Indox

with Indox(api_key="your-api-key") as client:
    path = client.fonts.convert_and_download(
        "./font.ttf",
        target_format="woff2",
        output_path="./font.woff2"
    )
```

## Configuration

| Environment Variable | Description | Default |
|---------------------|-------------|---------|
| `INDOX_API_KEY` | Your API key | Required |
| `INDOX_BASE_URL` | Base URL | `https://indox.org` |

```python
# Custom base URL
client = Indox(
    api_key="your-api-key",
    base_url="http://localhost:4800"
)
```

## Error Handling

```python
from indox_client import (
    Indox,
    IndoxError,
    APIStatusError,
    AuthenticationError,
    PaymentRequiredError,
    NotFoundError,
    RateLimitError,
    ConversionError,
    ConversionTimeoutError,
)

client = Indox(api_key="your-api-key")

try:
    path = client.fonts.convert_and_download(
        "./font.ttf",
        target_format="woff2",
        output_path="./font.woff2"
    )
except AuthenticationError:
    print("Invalid API key")
except PaymentRequiredError:
    print("Insufficient credits")
except NotFoundError:
    print("Endpoint or resource not found")
except RateLimitError:
    print("Too many requests")
except ConversionError as e:
    print(f"Conversion failed: {e.message}")
except ConversionTimeoutError:
    print("Conversion timed out")
except APIStatusError as e:
    print(f"API error {e.status_code}: {e.message}")
except IndoxError as e:
    print(f"Error: {e.message}")
```

## Supported Font Formats

| Engine | Formats |
|--------|---------|
| fonttools | ttf, otf, woff, woff2 |
| fontforge | ttf, otf, woff, woff2, eot, svg, pfa, pfb, ufo, dfont, ttc, bdf, pt3, t42, cff, sfd, fon, fnt, otb |

## License

Proprietary - see LICENSE for details.