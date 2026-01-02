<header>
<p align="center">
    <img src="res/logo/rite_logo.svg" width="20%" height="20%" alt="rite Logo">
</p>

<h3 align='center'>Python Utility Package</h3>
<p align="center"><code>rites to write py right</code></p>

</header>

<br/>

---

<div align="center">
  <a href="https://github.com/scape-agency/rite/issues/new?assignees=&labels=Needs%3A+Triage+%3Amag%3A%2Ctype%3Abug-suspected&template=bug_report.yml">Report a Bug</a>
  |
  <a href="https://github.com/scape-agency/rite/issues/new?assignees=&labels=Needs%3A+Triage+%3Amag%3A%2Ctype%3Afeature-request%2CHelp+wanted+%F0%9F%AA%A7&template=feature_request.yml">Request a Feature</a>
  |
  <a href="https://github.com/scape-agency/rite/issues/new?assignees=&labels=Needs%3A+Triage+%3Amag%3A%2Ctype%3Aquestion&template=question.yml">Ask a Question</a>
  |
  <a href="https://github.com/scape-agency/rite/issues/new?assignees=&labels=Needs%3A+Triage+%3Amag%3A%2Ctype%3Aenhancement&template=suggestion.yml">Make a Suggestion</a>
  |
  <a href="https://github.com/scape-agency/rite/discussions">Start a Discussion</a>
</div>

<br/>

<div align="center">

[![license](https://img.shields.io/github/license/scape-agency/rite?color=green&label=license&style=flat-square)](LICENSE.txt)
[![website](https://img.shields.io/website?color=blue&down_color=red&down_message=offline&label=website&style=flat-square&up_color=green&up_message=online&url=https%3A%2F%2Fwww.pyrites.dev)](https://www.pyrites.dev)
![python](https://img.shields.io/pypi/pyversions/rite?color=blue&label=python&style=flat-square)
![wheel](https://img.shields.io/pypi/wheel/rite?color=green&label=wheel&style=flat-square)

![stars](https://img.shields.io/github/stars/scape-agency/rite?color=blue&label=stars&style=flat-square)
![forks](https://img.shields.io/github/forks/scape-agency/rite?color=blue&label=forks&style=flat-square)
![downloads](https://img.shields.io/github/downloads/scape-agency/rite/total?color=blue&label=downloads&style=flat-square)
![issues](https://img.shields.io/github/issues/scape-agency/rite?label=issues&style=flat-square)
![sponsors](https://img.shields.io/github/sponsors/scape-agency?color=blue&label=sponsors&style=flat-square)
![contributors](https://img.shields.io/github/contributors/scape-agency/rite?color=blue&label=contributors&style=flat-square)

</div>

---

<br/>

<details open="open">
<summary>Table of Contents</summary>

-   [About](#about)
-   [Features](#features)
-   [Quick Start](#quick-start)
    -   [Installation](#installation)
    -   [Basic Usage](#basic-usage)
-   [Documentation](#documentation)
-   [Contributing](#contributing)
-   [Authors](#authors)
-   [License](#license)
-   [Disclaimer](#disclaimer)

</details>

---

## About

**rite** is a modern Python utility library with zero external runtime dependencies. Built with Python 3.12+ in mind, it provides a comprehensive collection of utilities for cryptography, filesystem operations, text processing, collections, conversions, networking, and more.

### Key Features

-   **Zero Dependencies**: No external runtime dependencies
-   **Type Safe**: Comprehensive type hints with Python 3.12+ syntax
-   **Well Tested**: >99% code coverage with extensive test suite
-   **Modern Python**: Supports Python 3.12, 3.13
-   **Modular Design**: Clear module organization with consistent structure
-   **Fully Documented**: Extensive documentation and practical examples

### Module Overview

| Module | Description |
|--------|-------------|
| **collections** | Buffers, caches (LRU/LFU/TTL), dict/list/set utilities, queues, trees |
| **conversion** | Type conversions, format transformations, unit conversions |
| **crypto** | UUID generation, hashing (SHA-256, MD5, BLAKE2), ciphers, random |
| **diagnostics** | Debugging, error handling, logging, metrics, profiling |
| **filesystem** | File/folder operations, compression, path utilities, MIME types |
| **functional** | Composition, currying, decorators, memoization, predicates |
| **markup** | HTML/XML/Markdown processing, entity encoding, sanitization |
| **net** | HTTP utilities, MIME types, URL encoding, request helpers |
| **numeric** | Math operations, statistics, number formatting |
| **reflection** | Attributes, inspection, signatures, type checking |
| **serialization** | JSON, CSV, INI, TOML, pickle serialization |
| **system** | Environment, platform detection, process management, shell |
| **temporal** | Date/time utilities, timestamp operations, formatting |
| **text** | Slug generation, case conversion, sanitization, analysis, search |

---

## Quick Start

### Installation

**From PyPI:**

```sh
pip install rite
```

**Using Poetry:**

```sh
poetry add rite
```

**From Source:**

```sh
git clone https://github.com/scape-agency/rite.git
cd rite
poetry install
```

[View on PyPI](https://pypi.org/project/rite/)

### Basic Usage

```python
# Cryptography
from rite.crypto.uuid import uuid_hex
from rite.crypto.hash import hash_sha256

user_id = uuid_hex()
password_hash = hash_sha256("secure_password")

# Filesystem
from rite.filesystem.file import file_copy, file_exists

if file_exists("config.json"):
    file_copy("config.json", "config.backup.json")

# Text Processing
from rite.text.slug import slug_generate
from rite.text.case import case_to_snake

slug = slug_generate("Hello World!")  # 'hello-world'
snake = case_to_snake("helloWorld")   # 'hello_world'

# Collections
from rite.collections.list import list_unique, list_flatten

unique = list_unique([1, 2, 2, 3])    # [1, 2, 3]
flat = list_flatten([[1, 2], [3, 4]]) # [1, 2, 3, 4]

# Serialization
from rite.serialization.json import json_load, json_dump

data = json_load("config.json")
json_dump(data, "output.json", indent=2)

# Functional
from rite.functional.composition import composition_pipe

pipeline = composition_pipe(str.strip, str.lower, str.title)
result = pipeline("  hello world  ")  # 'Hello World'

# System
from rite.system.platform import platform_is_linux, platform_name

if platform_is_linux():
    print(f"Running on {platform_name()}")

# Diagnostics
from rite.diagnostics.profiling import profiling_stopwatch

with profiling_stopwatch() as timer:
    # ... your code ...
    pass
print(f"Elapsed: {timer.elapsed:.3f}s")
```

---

## Documentation

### User Documentation

-   **[Getting Started](doc/getting-started.md)** - Quick introduction and module overview
-   **[Installation Guide](doc/installation.md)** - Detailed installation instructions
-   **[Usage Examples](doc/examples.md)** - Practical examples for all modules
-   **[API Reference](https://www.pyrites.dev)** - Complete API documentation

### Developer Documentation

-   **[Contributing Guide](doc/contributing.md)** - How to contribute to Rite
-   **[Development Setup](doc/development/setup.md)** - Set up your development environment
-   **[Code Style Guide](doc/development/code-style.md)** - Code standards and conventions
-   **[Testing Guide](doc/development/testing.md)** - Testing practices and patterns
-   **[Configuration Reference](doc/development/configuration.md)** - Configuration files and settings

### AI Agent Documentation

-   **[AI Instructions](doc/development/ai-instructions.md)** - Guidelines for AI agents and GitHub Copilot

### Additional Resources

-   **[Changelog](CHANGELOG.md)** - Version history and release notes
-   **[Architecture](ARCHITECTURE.txt)** - System architecture overview
-   **[Security Policy](SECURITY.md)** - Security guidelines and reporting
-   **[License](LICENSE)** - MIT License details

---

## Authors

**rite** is an open-source project by **[Scape Agency](https://www.scape.agency "Scape Agency website")**.

Scape Agency is a spatial innovation collective that dreams, discovers and designs the everyday of tomorrow. We blend design thinking with emerging technologies to create a brighter perspective for people and planet. Our products and services naturalise technology in liveable and sustainable –scapes that spark the imagination and inspire future generations.

-   website: [scape.agency](https://www.scape.agency "Scape Agency website")
-   github: [github.com/scape-agency](https://github.com/scape-agency "Scape Agency Github")

---

## Contributing

We'd love for you to contribute and to make **rite** even better than it is today!
Please refer to the [contribution guidelines](CONTRIBUTING.md) for details on:

-   Code of conduct
-   Development workflow
-   Code standards
-   Testing requirements
-   Pull request process

> Quick start for contributors:

```bash
# Clone the repository
git clone https://github.com/scape-agency/rite.git
cd rite

# Install dependencies
poetry install --with dev

# Install pre-commit hooks
poetry run pre-commit install

# Run tests
make test

# Run all checks
make check
```

---

## License

Except where otherwise noted, **rite** is licensed under the terms of the [MIT License](https://opensource.org/licenses/MIT "MIT License").

---

## Disclaimer

**THIS SOFTWARE IS PROVIDED AS IS WITHOUT WARRANTY OF ANY KIND, EITHER EXPRESS OR IMPLIED, INCLUDING ANY IMPLIED WARRANTIES OF FITNESS FOR A PARTICULAR PURPOSE, MERCHANTABILITY, OR NON-INFRINGEMENT.**

---

<p align="center">
    <b>Made with ♥ by <a href="https://www.scape.agency" target="blank">Scape Agency</a></b><br/>
    <sub>Copyright 2025 Scape Agency. All Rights Reserved</sub>
</p>
