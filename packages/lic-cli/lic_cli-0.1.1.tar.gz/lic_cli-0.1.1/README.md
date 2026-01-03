# LIC

<p align="center">
  <img src="./assets/demo.gif" alt="lic demo" />
</p>

<p align="center">
  <img src="https://img.shields.io/github/license/kushvinth/lic" />
</p>

## Overview

A minimal, interactive license generator that fetches licenses from GitHub's official API.

No more going to GitHub, creating a file, typing 'LICENSE', picking a license, pushing and pulling. Just run `lic` and generate your license locally.


## Installation

### Homebrew (recommended)

```bash
brew tap kushvinth/tap
brew install lic
```

This installs `lic` as a globally available CLI.

---

### Install as a uv tool

Requires **Python 3.12+** and **uv**.

```bash
uv tool install git+https://github.com/kushvinth/lic
```

Ensure the uv tool path is on your PATH:

```bash
uv tool ensurepath
```

### From source

```bash
git clone https://github.com/kushvinth/lic.git
cd lic
uv venv
uv pip install -e .
```

## Usage

```bash
lic
```

## Contributing
- Fork the repository
- Create a branch
  ```bash
  git checkout -b contibution/blah-blah-blah
  ```
- Commit your changes and push to your branch
  ```bash
  git commit -m "made an blah-blah-blah"
  git push origin contibution/blah-blah-blah
  ```
- Open a pull request

---

<div align="center">
  Made by <a href="https://github.com/kushvinth">Kushvinth</a>
</div>
