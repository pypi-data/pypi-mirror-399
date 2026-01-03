# onfire

A tiny **aafire-style** terminal flame effect in pure Python + `curses`, with optional 256-color gradients and Unicode shading blocks.

## Installation
Simply install with pipx:
```bash
pipx install onfire
```

## Run (dev)

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
onfire
```

Or without installing:

```bash
python -m termsite.onfire
```

## Keys

- `q` / `Esc`: quit
- `s`: cycle character sets (shade → solid → ascii)
- `c`: toggle color on/off
- `[` / `]`: decrease/increase wind (left/right)

## Options

- `--fps`: target render rate (frames per second)
- `--speed`: simulation speed (steps per frame), independent of FPS; fractional values slow things down, larger values accelerate the fire diffusion
- `--special cpu|ram`: scale speed and visible flame height based on live CPU or RAM usage percent
