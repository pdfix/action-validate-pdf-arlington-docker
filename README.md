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
| `--output`, `-o` | for `xml` and `html` | Path for report file in an existing folder; omit to print `raw`, `text` or `json` to stdout | Output file |
| `--format` | no | One of: `raw`, `xml`, `html`, `text`, `json` (default: `xml`) | Report format |
| `--maxfailuresdisplayed` | no | Integer (default **-1**) | Max failures shown |
| `--profile` | no | One of the profile ids below | Arlington grammar profile |

Profiles:

| Desktop name | `--profile` value |
|---|---|
| Autodetect | `auto` |
| PDF 1.0 | `arlington1.0` |
| PDF 1.1 | `arlington1.1` |
| PDF 1.2 | `arlington1.2` |
| PDF 1.3 | `arlington1.3` |
| PDF 1.4 | `arlington1.4` |
| PDF 1.5 | `arlington1.5` |
| PDF 1.6 | `arlington1.6` |
| PDF 1.7 | `arlington1.7` |
| PDF 2.0 | `arlington2.0` |

Notes:

- For `--format xml` (the default), `--output` is required and must end with `.xml`.
- For `--format html`, `--output` is required and must end with `.html`.
- Exit code 0 means the PDF is compliant, 1 means it is not compliant (see the report). Other codes are errors listed in `config.json`.
- Omit `--profile` and the flag is not passed to the Arlington jar.
- PDFix Desktop always passes `--profile`. Autodetect is the default, so a Desktop run sends at least `--profile auto`.

## Examples

Validate and print a text report to stdout:

```bash
docker run --rm -v "$(pwd)":/data -w /data pdfix/validate-pdf-arlington:latest validate -i /data/input.pdf --format text
```

Validate and write HTML:

```bash
docker run --rm -v "$(pwd)":/data -w /data pdfix/validate-pdf-arlington:latest \
  validate -i /data/input.pdf -o /data/report.html --format html
```

Validate against the PDF 1.7 profile:

```bash
docker run --rm -v "$(pwd)":/data -w /data pdfix/validate-pdf-arlington:latest \
  validate -i /data/input.pdf -o /data/report.xml --profile arlington1.7
```

## Help & support

To report an issue, contact `support@pdfix.net`.

## Licenses

- [veraPDF licensing](https://verapdf.org/home/#licensing) (GPLv3+ / MPLv2+): the Arlington PDF Model checker `res/cli-arlington-1.30.3.jar`
- [Arlington PDF Model](https://github.com/pdf-association/arlington-pdf-model) (Apache-2.0)
- [OpenJDK](https://openjdk.org/legal/gplv2+ce.html) (GPLv2 with the Classpath Exception): Java runtime in the image

