# Validate Arlington PDF Model

Validates PDF structure using local Arlington PDF Model grammar rules. Fully offline and open-source; no license required for the validator itself.

## Table of Contents

- [Validate Arlington PDF Model](#validate-arlington-pdf-model)
  - [Getting started](#getting-started)
  - [Usage](#usage)
  - [Commands](#commands)
  - [Arguments](#arguments)
  - [How it works](#how-it-works)
  - [Exit codes](#exit-codes)
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
| `--password` | no | String (default: empty) | Password to open a password-protected PDF |
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
- Autodetect (`auto`) takes the higher of the PDF versions in the file header and in the document catalog and checks PDF 1.0–1.4 with the PDF 1.4 rules, PDF 1.5–1.7 with the PDF 1.7 rules and PDF 2.0 with the PDF 2.0 rules. Select a profile to check the rules of an exact version.
- Omit `--profile` and the flag is not passed to the Arlington jar.
- PDFix Desktop always passes `--profile`. Autodetect is the default, so a Desktop run sends at least `--profile auto`.

## How it works

- The Arlington validator (Java) checks every object of the PDF against the Arlington PDF Model grammar of the profile and writes the report (deviations with the object, key and rule) in the selected format.
- **Autodetect** uses only three rule sets: PDF 1.0–1.4 → PDF 1.4 rules, PDF 1.5–1.7 → PDF 1.7 rules, PDF 2.0 → PDF 2.0 rules (the version is the higher of the file header and the document catalog).
- The PDF is only read. The report is written also when the PDF cannot be parsed or is password-protected (errors 31 and 32).
- Messages of the validator are logged as warnings. A run takes a few seconds.
- **Checks before validation:** output extension (11 / 12) and folder (13), input (14).

## Exit codes

| Code | Meaning |
|---|---|
| 0 | The PDF is compliant with the Arlington PDF Model |
| 1 | The PDF is not compliant; see the report |
| 2 | Unexpected error (`Failed to run the program:` + traceback) |
| 10 | Invalid arguments or no command |
| 11 | Output file must be an XML document (`--format xml`) |
| 12 | Output file must be an HTML document (`--format html`) |
| 13 | Output folder does not exist |
| 14 | Input file is not an existing PDF |
| 30 | Validation failed (the validator ended with another error, the log shows its code) |
| 31 | Input file is not a valid PDF document (cannot be parsed) |
| 32 | Input file is password-protected |

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

