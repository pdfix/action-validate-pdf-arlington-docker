# Validation with Arlington PDF Model

A Docker image that automatically checks grammar in PDF using the [Arlington PDF Model](https://github.com/pdf-association/arlington-pdf-model). The verification output is a report containing all of the grammatical errors contained in your PDF.

## Table of Contents

- [Validation with Arlington PDF Model](#validation-with-arlington-pdf-model)
  - [Table of Contents](#table-of-contents)
  - [Getting Started](#getting-started)
  - [Run using Command Line Interface](#run-using-command-line-interface)
  - [Exporting Configuration for Integration](#exporting-configuration-for-integration)
  - [License](#license)
  - [Help \& Support](#help--support)

## Getting Started

To use this Docker application, install the Docker on your system. If Docker is not installed, please follow the instructions on the [official Docker website](https://docs.docker.com/get-docker/) to install it.

## Run using Command Line Interface

To run the Docker container as a CLI, you need to share the folder with the PDF files you wish to validate using the `-v` parameter. In this example, the current folder is used.

First run will pull the docker image, which may take some time. Make your own image for more advanced use.

```bash
docker run -v $(pwd):/data --rm -w /data/ pdfix/validate-pdf-arlington:latest validate -i <input>.pdf
```

Output as HTML

```bash
docker run -v $(pwd):/data --rm -w /data/ pdfix/validate-pdf-arlington:latest validate -i <input>.pdf -o index.html --format html
```

For more detailed information about the available command-line arguments, you can run the following command:

```bash
docker run --rm pdfix/validate-pdf-arlington:latest --help
```

## Exporting Configuration for Integration

To export the configuration JSON file, use the following command:

```bash
docker run -v $(pwd):/data --rm pdfix/validate-pdf-arlington:latest config -o config.json
```

## License

- veraPDF - https://verapdf.org/home/#licensing

## Help & Support

To obtain a PDFix SDK license or report an issue please contact us at support@pdfix.net.
For more information visit https://pdfix.net
