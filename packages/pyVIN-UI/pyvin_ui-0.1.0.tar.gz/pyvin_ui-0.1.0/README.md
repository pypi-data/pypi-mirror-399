# pyVIN - Vehicle Identification Number Decoder

[![CI](https://github.com/bmj2728/pyVIN/actions/workflows/ci.yml/badge.svg)](https://github.com/bmj2728/pyVIN/actions/workflows/ci.yml)
[![Docker Build](https://github.com/bmj2728/pyVIN/actions/workflows/docker.yml/badge.svg)](https://github.com/bmj2728/pyVIN/actions/workflows/docker.yml)
[![codecov](https://codecov.io/gh/bmj2728/pyVIN/branch/main/graph/badge.svg)](https://codecov.io/gh/bmj2728/pyVIN)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Code style: ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit)](https://github.com/pre-commit/pre-commit)

A Python-based Vehicle Identification Number (VIN) decoder that provides comprehensive vehicle information using the NHTSA vPIC (Vehicle Product Information Catalog) API.

## Table of Contents

- [Features](#features)
- [Demo](#demo)
- [Installation](#installation)
- [Usage](#usage)
  - [Web Interface](#web-interface)
  - [Python API](#python-api)
- [Deployment](#deployment)
  - [Streamlit Cloud](#streamlit-cloud)
  - [Docker](#docker)
  - [Self-Hosted](#self-hosted)
- [Development](#development)
  - [Setup](#setup)
  - [Running Tests](#running-tests)
  - [Code Quality](#code-quality)
  - [Project Structure](#project-structure)
- [API Reference](#api-reference)
- [Contributing](#contributing)
- [License](#license)
- [Acknowledgments](#acknowledgments)

## Features

- 🔍 **Decode 17-character VINs** - Full or partial VINs with wildcard support
- 📊 **Comprehensive Data** - Make, model, year, specifications, and safety features
- 🏭 **Manufacturing Details** - Plant location and manufacturer information
- ⚠️ **Smart Error Handling** - Distinguishes warnings from critical errors
- ✨ **Clean UI** - Responsive Streamlit interface with tooltips
- 🎯 **Filtered Results** - Shows only available data with clean field labels
- 🚀 **High Performance** - LRU caching for faster repeated queries
- 🧪 **Well Tested** - 97%+ code coverage with 100 passing tests

## Demo

**Example VINs to try:**

- `5UXWX7C50BA123456` - Full VIN (BMW X3)
- `5UXWX7C*5*B*A******` - Partial VIN with wildcards
- `JHL**77813C002328` - Partial VIN (shows suggestions)

## Installation

### Prerequisites

- Python 3.10 or higher
- pip package manager

### Quick Install

```bash
# Clone the repository
git clone https://github.com/bmj2728/pyVIN.git
cd pyVIN

# Install dependencies
pip install -e .

# For development (includes testing tools)
pip install -e ".[dev]"
```

## Usage

### Web Interface

Launch the Streamlit web application:

```bash
streamlit run src/ui/app.py
```

The app will open in your browser at `http://localhost:8501`

**Navigation:**

- **Home** - Information about pyVIN and VIN basics
- **VIN Decoder** - Enter a VIN to decode vehicle information

**Tips:**

- VIN must be exactly 17 characters
- Use `*` as a wildcard for unknown positions
- Copy/paste VINs directly into the input field

### Python API

Use pyVIN programmatically in your Python code:

```python
from src.api.client import decode_vin_values_extended
from src.exceptions import VINDecoderError

try:
    # Decode a full VIN
    result = decode_vin_values_extended("5UXWX7C50BA123456")

    print(f"Make: {result.make}")
    print(f"Model: {result.model}")
    print(f"Year: {result.model_year}")
    print(f"Body: {result.body_class}")

    # Check for warnings
    if result.error_text and result.error_code != "0":
        print(f"Warning: {result.error_text}")
        if result.suggested_vin:
            print(f"Suggested VIN: {result.suggested_vin}")

except VINDecoderError as e:
    print(f"Error: {e}")
```

**Using wildcards for partial VINs:**

```python
# Partial VIN with wildcards
result = decode_vin_values_extended("5UXWX7C*5*B*A******")

# Filter to only populated fields
from src.formatting.response import filter_non_null
filtered_data = filter_non_null(result)

for field, value in filtered_data.items():
    print(f"{field}: {value}")
```

## Deployment

### Streamlit Cloud

Deploy to Streamlit Cloud for free hosting:

1. **Push to GitHub**

   ```bash
   git add .
   git commit -m "Ready for deployment"
   git push origin main
   ```

2. **Deploy on Streamlit Cloud**
   - Go to [share.streamlit.io](https://share.streamlit.io)
   - Click "New app"
   - Select your repository: `bmj2728/pyVIN`
   - Main file path: `src/ui/app.py`
   - Click "Deploy"

3. **Configure (Optional)**
   - Add custom domain in settings
   - Set environment variables if needed

### Docker

Build and run with Docker:

```bash
# Build the image
docker build -t pyvin .

# Run the container
docker run -p 8501:8501 pyvin
```

**Docker Compose:**

```yaml
version: '3.8'
services:
  pyvin:
    build: .
    ports:
      - "8501:8501"
    environment:
      - NHTSA_BASE_URL=https://vpic.nhtsa.dot.gov/api/vehicles
    restart: unless-stopped
```

### Self-Hosted

Deploy on your own server:

```bash
# Install dependencies
pip install -e .

# Run with production settings
streamlit run src/ui/app.py \
  --server.port 8501 \
  --server.address 0.0.0.0 \
  --server.headless true
```

**Using systemd (Linux):**

Create `/etc/systemd/system/pyvin.service`:

```ini
[Unit]
Description=pyVIN VIN Decoder
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/opt/pyvin
ExecStart=/usr/bin/streamlit run src/ui/app.py --server.port 8501
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start:

```bash
sudo systemctl enable pyvin
sudo systemctl start pyvin
```

## Development

### Setup

Set up your development environment:

```bash
# Clone and install
git clone https://github.com/bmj2728/pyVIN.git
cd pyVIN
pip install -e ".[dev]"

# Verify installation
python -c "from src.api.client import decode_vin_values_extended; print('OK')"
```

### Running Tests

Run the test suite with coverage:

```bash
# Run all tests
pytest

# Run with coverage report
pytest --cov=src --cov-report=term-missing

# Generate HTML coverage report
pytest --cov=src --cov-report=html
open htmlcov/index.html

# Run specific test file
pytest tests/test_api/test_client.py -v

# Run with fuzzing (longer tests)
pytest --hypothesis-profile=default
```

**Current Test Stats:**

- 100 tests passing
- 97.5% code coverage
- Includes property-based testing with Hypothesis

### Code Quality

Check and format code:

```bash
# Run linter
ruff check src/ tests/

# Auto-fix issues
ruff check --fix src/ tests/

# Format code
ruff format src/ tests/
```

### Pre-commit Hooks

Set up pre-commit hooks to automatically check code before commits:

```bash
# Install pre-commit
pip install pre-commit

# Install the git hooks
pre-commit install

# Run manually on all files
pre-commit run --all-files
```

**Hooks included:**

- Trailing whitespace removal
- YAML/TOML validation
- **Gitleaks** - Secret scanning
- **Ruff** - Linting and formatting
- Markdown linting
- Python syntax checking

### Continuous Integration

The project uses GitHub Actions for CI/CD:

**CI Pipeline** (`.github/workflows/ci.yml`):

- Runs on push to `main`/`dev` and all PRs
- Multi-version testing (Python 3.10, 3.12, 3.14)
- Linting with Ruff
- Security scanning with Gitleaks
- Test suite with coverage reporting
- Uploads coverage to Codecov

**Docker Build** (`.github/workflows/docker.yml`):

- Builds multi-platform images (amd64, arm64)
- Pushes to GitHub Container Registry

**Release** (`.github/workflows/release.yml`):

- Triggered by version tags (`v*.*.*`)
- Creates GitHub Release with changelog
- Builds and tags Docker images to GHCR

**Required Secrets:**

- `CODECOV_TOKEN` - For coverage reporting

### Project Structure

```text
pyVIN/
├── src/
│   ├── api/                 # NHTSA API client and models
│   │   ├── client.py        # API interaction with caching
│   │   └── models.py        # Pydantic models for responses
│   ├── validation/          # VIN validation logic
│   │   └── vin.py           # VIN format validation
│   ├── formatting/          # Response formatting utilities
│   │   ├── fields.py        # Field labels and descriptions
│   │   └── response.py      # Response filtering
│   ├── ui/                  # Streamlit web interface
│   │   ├── app.py           # Home page
│   │   ├── pages/
│   │   │   └── VIN_Decoder.py  # VIN decoder page
│   │   └── components/
│   │       └── results_table.py  # Results display component
│   ├── logs/                # Logging configuration
│   ├── config.py            # Application configuration
│   └── exceptions.py        # Custom exceptions
├── tests/                   # Test suite
│   ├── conftest.py          # Shared test fixtures
│   ├── test_api/            # API tests
│   ├── test_validation/     # Validation tests
│   ├── test_formatting/     # Formatting tests
│   └── test_logs/           # Logging tests
├── pyproject.toml           # Project metadata and dependencies
├── LICENSE                  # MIT License
└── README.md               # This file
```

## API Reference

### Main Functions

#### `decode_vin_values_extended(vin: str) -> VINDecodeResult`

Decode a VIN using the NHTSA API.

**Parameters:**

- `vin` (str): 17-character VIN (use `*` for wildcards)

**Returns:**

- `VINDecodeResult`: Pydantic model with decoded data

**Raises:**

- `InvalidVINError`: Invalid VIN format
- `NetworkError`: Network/connection error
- `APIError`: Critical API error (400+ error codes)

**Example:**

```python
result = decode_vin_values_extended("5UXWX7C50BA123456")
print(result.make)  # "BMW"
```

#### `validate_and_normalize_vin(vin: str) -> str`

Validate and normalize a VIN string.

**Parameters:**

- `vin` (str): VIN to validate

**Returns:**

- `str`: Normalized VIN (uppercase, stripped)

**Raises:**

- `InvalidVINError`: Invalid VIN format

#### `filter_non_null(result: VINDecodeResult) -> Dict[str, Any]`

Filter out null/empty fields from a decode result.

**Parameters:**

- `result` (VINDecodeResult): Decode result to filter

**Returns:**

- `dict`: Dictionary with only populated fields

## Contributing

Contributions are welcome! Please follow these guidelines:

1. **Fork the repository**
2. **Create a feature branch** (`git checkout -b feature/amazing-feature`)
3. **Make your changes**
   - Add tests for new functionality
   - Ensure all tests pass (`pytest`)
   - Follow code style (`ruff check`)
4. **Commit your changes** (`git commit -m 'Add amazing feature'`)
5. **Push to the branch** (`git push origin feature/amazing-feature`)
6. **Open a Pull Request**

### Development Guidelines

- Maintain 90%+ test coverage
- Add docstrings to all public functions
- Use type hints
- Follow existing code style
- Update README for new features

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

Copyright (c) 2025 NovelGit LLC

## Acknowledgments

- **NHTSA vPIC API** - Vehicle data provided by the National Highway Traffic Safety Administration
- **Streamlit** - Web framework for the user interface
- **Pydantic** - Data validation and settings management
- **Hypothesis** - Property-based testing framework

---

**Disclaimer:** This tool is for informational purposes only. Always verify vehicle information through official sources. NHTSA data may not be complete or fully accurate for all vehicles.

**Questions or Issues?** Open an issue on [GitHub](https://github.com/bmj2728/pyVIN/issues)
