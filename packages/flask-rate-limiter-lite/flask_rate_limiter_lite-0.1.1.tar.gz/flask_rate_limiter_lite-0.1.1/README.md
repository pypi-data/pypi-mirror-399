# 🚦 Rate Limiter – Reusable Flask Decorator Library

A reusable, production-style **rate limiting library** for Flask applications, implemented using multiple industry-standard algorithms and exposed via a **clean decorator-based API**.

The project is designed with **system design principles**, **strategy pattern**, and **real-world API use cases** in mind.

---

## ✨ Features

- Decorator-based rate limiting for Flask routes
- Supports 4 algorithms : 1. Fixed Window 2.Sliding Window 3.Leaky Bucket 4. Token Bucket
- Per-user and per-endpoint enforcement
- Clean, extensible strategy-based architecture
- In-memory state management for simplicity
- Metrics support for observability
- Designed as a reusable Python package

---



## Installation
Clone the repository and install the package in editable mode:

```bash
pip install -e .
    ```
-An example app is created to understand how to use an decorator