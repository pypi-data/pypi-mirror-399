# NanoFlow

An efficient, low-memory LLM inference engine using Python bindings for GGML.

## Overview

NanoFlow is designed to run GGUF models in constrained memory environments by leveraging a smart streaming architecture and the GGML backend.

## Installation

```bash
pip install .
```

## Dependencies

This project currently links dynamically against pre-built `llama.cpp` shared libraries (`libggml.so`, `libggml-cpu.so`, `libggml-base.so`). 
Ensure these libraries are available in your library path or configured in `setup.py`.
