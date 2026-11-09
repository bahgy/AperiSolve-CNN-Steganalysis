# Aperi'Solve

[![Website](https://img.shields.io/website?url=https%3A%2F%2Faperisolve.com)](https://aperisolve.com/)
![CI](https://github.com/Zeecka/AperiSolve/actions/workflows/release.yml/badge.svg)
![Lint](https://github.com/Zeecka/AperiSolve/actions/workflows/lint.yml/badge.svg)
![Docker](https://img.shields.io/badge/docker-compose-blue?logo=docker)
![Python Version](https://img.shields.io/badge/python-3.12%2B-blue)
![Ruff](https://img.shields.io/badge/lint-ruff-30173d)
![uv](https://img.shields.io/badge/package-uv-30173d)
![ty](https://img.shields.io/badge/types-ty-30173d)
![License](https://img.shields.io/github/license/Zeecka/AperiSolve)
![GitHub Issues](https://img.shields.io/github/issues/Zeecka/AperiSolve)
![GitHub Pull Requests](https://img.shields.io/github/issues-pr/Zeecka/AperiSolve)
![Last Commit](https://img.shields.io/github/last-commit/Zeecka/AperiSolve)
![Contributors](https://img.shields.io/github/contributors/Zeecka/AperiSolve)
[![Rawsec's CyberSecurity Inventory](https://inventory.raw.pm/img/badges/Rawsec-inventoried-FF5050_flat.svg)](https://inventory.raw.pm/tools.html#Aperi'Solve)

<p align="center">
  <a href="https://www.aperisolve.com">
    <img src="https://raw.githubusercontent.com/Zeecka/AperiSolve/main/examples/screenshot.png" alt="Aperi'Solve screenshot" />
  </a>
</p>

Try it now: **https://www.aperisolve.com**

Support Aperi'Solve:

<a href="https://github.com/sponsors/Zeecka">
  <img src="https://img.shields.io/badge/Sponsor-Zeecka-ea4aaa?logo=githubsponsors&logoColor=white&style=for-the-badge" alt="Sponsor Aperi'Solve on GitHub" />
</a>

---

Aperi'Solve is an open-source steganalysis web platform that performs automated analysis on images to detect and extract hidden data using common steganography tools and techniques.

## Key features

- Visualize each bit layer (LSB and other layers) per image channel (R/G/B/Alpha).
- Color remapping (random palette remaps with 8 generated variants)
- Runs 16 analyzers in parallel and displays their output, with per-tool
  success/no-result badges and one-click download of extracted files:
  - [binwalk](https://github.com/ReFirmLabs/binwalk) (embedded archives)
  - [exiftool](https://exiftool.org/) (metadata and geolocation)
  - [file](https://manned.org/file.1) (MIME type and format detection)
  - [GraphicsMagick identify](http://www.graphicsmagick.org/identify.html) (image info & properties)
  - [foremost](https://foremost.sourceforge.net/) (carved files)
  - [jsteg](https://github.com/lukechampine/jsteg) (JPEG LSB extraction)
  - [jpseek / jphide](https://github.com/h3xx/jphs) (JPEG steganography extraction, with password)
  - [openstego](https://www.openstego.com/) (extraction with password)
  - [outguess](https://www.rbcafe.com/software/outguess/) (extraction with password, deep analysis)
  - [pcrt](https://github.com/sherlly/PCRT) (PNG check & repair)
  - [pngcheck](https://www.libpng.org/pub/png/apps/pngcheck.html)
  - [steghide](https://steghide.sourceforge.net/) (extraction with password)
  - [strings](https://pubs.opengroup.org/onlinepubs/9799919799/utilities/strings.html)
  - [zsteg](https://github.com/zed-0xff/zsteg) (LSB text/data extraction)
- **In-app wiki** ([`/wiki`](https://www.aperisolve.com/wiki/)): a HackTricks-style
  steganography handbook — a triage methodology, a decision-tree cheatsheet,
  technique pages per medium (image, audio, text, files), and a guide per
  analyzer, all authored as Markdown.
- **Internationalization**: UI available in English, French, Spanish, German,
  Russian, Chinese and Portuguese under language-prefixed URLs (`/fr/`, `/es/`, …).
- Worker queue architecture for offloading heavy/slow analyzers (Redis + background workers).
- Content-addressed result cache, HTTP caching, and per-endpoint rate limiting.
- Results stored temporarily for later browsing and download, then cleaned up
  automatically by a scheduled job.

## Adding an analyzer

Adding an analyzer is a single file: subclass `SubprocessAnalyzer`, set a few
class attributes (`name`, `has_archive`, `needs_password`, `deep_only`,
`display_order`), and install the tool in the `Dockerfile`. The worker run
list, download allow-list, and frontend order are all derived automatically.
See [docs/adding-analyzer.md](docs/adding-analyzer.md).

## Quick start (Docker)

In case you want to host your own version of https://www.aperisolve.com/.

> Required: Docker + Docker Compose.

```bash
git clone https://github.com/Zeecka/AperiSolve.git
cd AperiSolve
cp .env.example .env
docker compose up -d
```

Then browse url: http://localhost:5000/

Ads and analytics are disabled by default; every integration
(`CUSTOM_EXTERNAL_SCRIPT`, `GOOGLE_ADS_TXT`, `SITE_BASE_URL`, Sentry) is
opt-in via environment variables documented in [`.env.example`](.env.example).
The app never injects ad markup itself: `CUSTOM_EXTERNAL_SCRIPT` loads the
AdSense script and placement is left to Auto ads.

## Architecture

The stack runs as Docker Compose services:

- **web** — Flask app served by gunicorn (Jinja templates + vanilla JS frontend).
- **worker** — an RQ worker that runs the analyzers for each submission,
  fanning out to one thread per tool.
- **cron** — an RQ cron scheduler that runs the retention cleanup off the
  request path.
- **initdb** — a one-shot service that creates the tables and pre-fills the
  IHDR CRC recovery database.
- **postgres** — stores image metadata and submission status.
- **redis** — RQ broker (DB 0) and rate-limiter storage (DB 1).
- **rqdashboard** — queue monitoring, bound to localhost:9181.

This separation keeps heavy tools (binwalk, foremost, zsteg, etc.) isolated
and avoids blocking the web worker. Identical submissions are deduplicated by
a content hash, and derived images are cached with long-lived immutable HTTP
headers, so repeat traffic is cheap.

# AperiSolve – CNN Steganalysis

[![Python](https://img.shields.io/badge/Python-3.12-blue.svg)](https://www.python.org/)
[![Docker](https://img.shields.io/badge/Docker-Supported-blue.svg)](https://www.docker.com/)
[![PyTorch](https://img.shields.io/badge/PyTorch-CPU-orange.svg)](https://pytorch.org/)

AperiSolve is an open-source web-based steganalysis platform.
This repository extends the original AperiSolve project with a
Convolutional Neural Network (CNN) analyzer for detecting potential
LSB (Least Significant Bit) steganography in images.

## About This Project

This project builds upon the original AperiSolve platform and adds
a CNN-based image analysis component.

The new analyzer uses a trained deep learning model to classify
images into two categories:

- **Cover:** An image classified as having no detected LSB steganography.
- **Stego:** An image classified as potentially containing LSB steganography.

The analyzer is integrated into the existing AperiSolve analysis
workflow and can be used through its web interface.

## Features

### Original AperiSolve Features

- Analyze images using multiple steganography tools.
- Visualize image bit planes and color channels.
- Generate color-remapped image variations.
- Run multiple analyzers in parallel.
- View analysis results through a web interface.
- Use the built-in documentation and wiki.

### CNN Steganalysis Extension

- CNN-based image classification.
- Detection of potential LSB steganography.
- PyTorch model inference.
- Automatic image preprocessing.
- CPU-based inference.
- Integration with the existing analyzer registry.

## CNN Model

The integrated model is a Convolutional Neural Network implemented
using PyTorch.

Its architecture includes:

- Convolutional layers.
- ReLU activation functions.
- Max pooling layers.
- Fully connected layers.
- Two output classes: Cover and Stego.

### Image Preprocessing

Before inference, images go through the following steps:

1. EXIF orientation correction.
2. Conversion to grayscale.
3. Resizing to 64 × 64 pixels.
4. Least Significant Bit (LSB) extraction.
5. CNN inference.
6. Softmax-based class confidence calculation.

### Important Model Limitations

The current model was trained and evaluated using a small synthetic
dataset generated for LSB steganalysis experiments.

Although it achieved 100% accuracy on its synthetic test set,
this result does not establish real-world detection accuracy.

Performance on real-world images may vary. Confidence scores are
model outputs and should not be considered guarantees.

## Technology Stack

- Python
- Flask
- PyTorch
- NumPy
- OpenCV / Pillow
- PostgreSQL
- Redis
- RQ (Redis Queue)
- Docker and Docker Compose

## Getting Started

### Prerequisites

- Git
- Docker
- Docker Compose

### Clone the Repository

```bash
git clone https://github.com/bahgy/AperiSolve-CNN-Steganalysis.git
# AperiSolve – CNN Steganalysis

[![Python](https://img.shields.io/badge/Python-3.12-blue.svg)](https://www.python.org/)
[![Docker](https://img.shields.io/badge/Docker-Supported-blue.svg)](https://www.docker.com/)
[![PyTorch](https://img.shields.io/badge/PyTorch-CPU-orange.svg)](https://pytorch.org/)

AperiSolve is an open-source web-based steganalysis platform. This repository extends the original AperiSolve project with a Convolutional Neural Network (CNN) analyzer for detecting potential LSB (Least Significant Bit) steganography in images.

## About This Project

This project builds upon the original AperiSolve platform and adds a CNN-based image analysis component.

The new analyzer uses a trained deep learning model to classify images into two categories:

- **Cover:** An image classified as having no detected LSB steganography.
- **Stego:** An image classified as potentially containing LSB steganography.

The analyzer is integrated into the existing AperiSolve analysis workflow and can be used through its web interface.

## Features

### Original AperiSolve Features

- Analyze images using multiple steganography tools.
- Visualize image bit planes and color channels.
- Generate color-remapped image variations.
- Run multiple analyzers in parallel.
- View analysis results through a web interface.
- Use the built-in documentation and wiki.

### CNN Steganalysis Extension

- CNN-based image classification.
- Detection of potential LSB steganography.
- PyTorch model inference.
- Automatic image preprocessing.
- CPU-based inference.
- Integration with the existing analyzer registry.

## CNN Model

The integrated model is a Convolutional Neural Network implemented using PyTorch.

Its architecture includes:

- Convolutional layers.
- ReLU activation functions.
- Max pooling layers.
- Fully connected layers.
- Two output classes: Cover and Stego.

### Image Preprocessing

Before inference, images go through the following steps:

1. EXIF orientation correction.
2. Conversion to grayscale.
3. Resizing to 64 × 64 pixels.
4. Least Significant Bit (LSB) extraction.
5. CNN inference.
6. Softmax-based class confidence calculation.

### Important Model Limitations

The current model was trained and evaluated using a small synthetic dataset generated for LSB steganalysis experiments.

Although it achieved 100% accuracy on its synthetic test set, this result does not establish real-world detection accuracy.

Performance on real-world images may vary. Confidence scores are model outputs and should not be considered guarantees.

## Technology Stack

- Python
- Flask
- PyTorch
- NumPy
- Pillow
- PostgreSQL
- Redis
- RQ (Redis Queue)
- Docker and Docker Compose

## Getting Started

### Prerequisites

- Git
- Docker
- Docker Compose

### Clone the Repository

```bash
git clone https://github.com/bahgy/AperiSolve-CNN-Steganalysis.git
cd AperiSolve-CNN-Steganalysis
```

### Configure Environment

```bash
cp .env.example .env
```

Review the environment variables in `.env` before running the application.

### Build and Run

```bash
docker compose -f compose.dev.yml up -d --build
```

Open the application:

- Web application: http://localhost:5000
- RQ Dashboard: http://localhost:9181

### Stop the Application

```bash
docker compose -f compose.dev.yml down
```

## Project Structure

```text
aperisolve/
├── analyzers/
│   └── cnn_steganalysis.py
│
├── cnn_models/
│   ├── __init__.py
│   ├── residual_model.py
│   └── residual_lsb_hard_100pct.pth
│
└── ...

Dockerfile
pyproject.toml
uv.lock
compose.dev.yml
README.md
```

## Testing

Install development dependencies:

```bash
uv sync --extra dev
```

Run the test suite:

```bash
uv run pytest -q
```

## Original Project and Attribution

This repository is based on the original [AperiSolve](https://github.com/Zeecka/AperiSolve) project.

The original platform was created by **Zeecka** and its contributors.

This repository preserves the original project's attribution and extends it with CNN-based LSB steganalysis integration.

**CNN integration and related modifications:**  
[bahgy](https://github.com/bahgy)

## License

This project retains the original license included in the repository. Please refer to the [LICENSE](LICENSE) file for details.
