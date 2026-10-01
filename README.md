# Validate Arlington PDF Model

Validates PDF structure using local Arlington PDF Model grammar rules. Fully offline and open-source; no license required for the validator itself.

## Table of Contents

- [Validate Arlington PDF Model](#validate-arlington-pdf-model)
  - [Getting started](#getting-started)
  - [Usage](#usage)
  - [Commands](#commands)
  - [Arguments](#arguments)
  - [Examples](#examples)
  - [Help \& support](#help--support)
  - [Licenses](#licenses)

## Getting started

You need Docker installed. The first run downloads the image and may take longer than later runs.

## Usage

Mount a folder into the container and run a subcommand:

```bash
docker run --rm -v "$(pwd)":/data -w /data pdfix/validate-pdf-arlington:latest <command> [options]
```

## Commands

- `validate`: Validate a PDF and write or print a report

## Arguments

### `validate`

| Option | Required | Type / expected value | Description |
|---|:---:|---|---|
| `--input`, `-i` | yes | Path to an existing `.pdf` file | Input PDF |
| `--output`, `-o` | no | Path for report file; omit to print to stdout | Output file |
| `--format` | no | One of: `raw`, `xml`, `html`, `text`, `json` (default: `xml`) | Report format |
| `--maxfailuresdisplayed` | no | Integer (default **-1**) | Max failures shown |
| `--profile` | no | One of the profile ids below | Arlington grammar profile |

Profiles:

| Desktop name | `--profile` value |
|---|---|
| Autodetect | `auto` |
| Arlington 1.0 | `arlington1.0` |
| Arlington 1.1 | `arlington1.1` |
| Arlington 1.2 | `arlington1.2` |
| Arlington 1.3 | `arlington1.3` |
| Arlington 1.4 | `arlington1.4` |
| Arlington 1.5 | `arlington1.5` |
| Arlington 1.6 | `arlington1.6` |
| Arlington 1.7 | `arlington1.7` |
| Arlington 2.0 | `arlington2.0` |

Notes:

- For `--format xml`, if `--output` is set it must end with `.xml`.
- For `--format html`, if `--output` is set it must end with `.html`.
- Omit `--profile` and the flag is not passed to the Arlington jar.
- PDFix Desktop always passes `--profile`. Autodetect is the default, so a Desktop run sends at least `--profile auto`.

## Examples

Validate and print XML to stdout:

```bash
docker run --rm -v "$(pwd)":/data -w /data pdfix/validate-pdf-arlington:latest validate -i /data/input.pdf
```

Validate and write HTML:

```bash
docker run --rm -v "$(pwd)":/data -w /data pdfix/validate-pdf-arlington:latest \
  validate -i /data/input.pdf -o /data/report.html --format html
```

Validate against Arlington 1.7:

```bash
docker run --rm -v "$(pwd)":/data -w /data pdfix/validate-pdf-arlington:latest \
  validate -i /data/input.pdf --profile arlington1.7
```

## Help & support

To report an issue, contact `support@pdfix.net`.

## Licenses

- [Arlington PDF Model](https://github.com/pdf-association/arlington-pdf-model)

