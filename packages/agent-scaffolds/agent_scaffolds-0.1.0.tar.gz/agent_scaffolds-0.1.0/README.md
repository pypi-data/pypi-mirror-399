# Ascender Framework Project

## Overview

This project is built using the **Ascender Framework**, a structured FastAPI-based framework designed for modular and scalable applications.

---

## Getting Started

### Prerequisites

Ensure you have the following dependencies installed:

- **Python 3.11 (recommended)** or higher
- **Poetry** (for dependency management)
- **pip** (Python's package manager)

### Installation

1. **Install Poetry** (if not already installed):

   ```bash
   pip install poetry
   ```

2. **Configure Poetry to use virtual environments**:

   ```bash
   poetry config virtualenvs.create true
   ```

3. **Install project dependencies**:

   ```bash
   poetry install
   ```

   If you prefer a plain virtual environment on Python 3.11:

   ```bash
   python3.11 -m venv .venv
   source .venv/bin/activate
   poetry install
   ```

4. **Run development server**:
    
    ```bash
    ascender run serve
    ```

If everything works, you're done!