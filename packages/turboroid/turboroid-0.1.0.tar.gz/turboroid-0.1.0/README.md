<p align="center">
<a href="https://turborg.com/turboroid" target="_blank">
<img src="https://i.postimg.cc/HsL3VD13/logot.png" alt="Turboroid Logo" width="400px">
</a>
</p>

<div align="center">

![Python Versions](https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13%20%7C%203.14-blue?style=flat-square)
![Development Status](https://img.shields.io/badge/status-Alpha-orange?style=flat-square)

</div>

<p align="center">
A blazingly fast, developer-friendly ASGI micro-framework engineered for building high-performance asynchronous APIs and services in Python.
</p>

## About Turboroid

Turboroid is built on the philosophy of maximal throughput with minimal overhead, giving you bare-metal performance while maintaining a clean syntax.

---

## Key Features

* Turbo Speed: Optimized from the ground up to minimize latency and maximize concurrent request handling, rivaling the performance of high-speed servers.
* Python 3.10+ Focused: Explicitly designed for the fastest, most stable versions of Python, leveraging performance gains introduced in 3.10-3.14.
* ASGI Standard: Fully compliant with the Asynchronous Server Gateway Interface (ASGI), ensuring compatibility with high-performance servers like `Granian` and `Uvicorn`.
* Developer-First: Simple, intuitive API and explicit routing that keeps boilerplate code to a minimum.
* Modern Tooling: Out of box tools for turbo development.

## Installation

Turboroid is soon available on PyPI.

### 1. Requirements

Turboroid requires **Python 3.10** or newer.

### 2. Standard Installation

```bash
uv pip install turboroid
```

### 3. Development
```bash
uv pip install -e .[dev]
```
### Branding
Main color of turborg ecosystem is #44a800

## Development Checklist
1. create ControllerAdvice with custom NotFound/Error exceptions which can be overriden
2. Global configuration for configs, so that we configure json camel case or any other naming strategy
3. update more_body so that SSE works and file streaming
4. Integrate in request parsing data from json to objects
5. Add lifespan support
6. Add WS Support
7. Configuration from OS env
8. Add Middleware

---
*Part of the [**Turborg**](https://turborg.com) AI-First Open Source Suite Ecosystem*
