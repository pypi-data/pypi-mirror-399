# CDD Python Adapter

> **Python wrapper for the CDD (Cyberattack-Driven Development) framework.**

This package allows you to run high-performance security audits using the native Rust core of the CDD Framework directly from your Python scripts.

## Installation

Install in editable mode for development:
```bash
pip install -e .
```

## Usage
Python

from cdd_python.engine import CDDEngine

# Initialize the engine
engine = CDDEngine()

# Run an audit against a local or remote target
engine.execute_audit("http://localhost:8080")

Architecture
Engine: Pure Python wrapper using subprocess.

Core: Native Rust binaries for Windows, Linux, and macOS (Alpha 2).

Part of the CDD-Framework organization.