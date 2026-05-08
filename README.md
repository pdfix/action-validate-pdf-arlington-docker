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

Notes:

- For `--format xml`, if `--output` is set it must end with `.xml`.
- For `--format html`, if `--output` is set it must end with `.html`.

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

## Help & support

To report an issue, contact `support@pdfix.net`.

## Licenses

- [Arlington PDF Model](https://github.com/pdf-association/arlington-pdf-model)
