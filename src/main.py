import argparse
import logging
import subprocess
import sys
import threading
import time
from datetime import datetime
from pathlib import Path
from typing import Optional

from tqdm import tqdm

from constants import CONFIG_FILE
from exceptions import (
    EC_ARG_GENERAL,
    MESSAGE_ARG_GENERAL,
    ArgumentInputNotPdfException,
    ArgumentOutputFolderNotExistsException,
    ArgumentOutputNotHtmlException,
    ArgumentOutputNotXmlException,
    ExpectedException,
    InputEncryptedException,
    InputNotValidPdfException,
    ValidationFailed,
)
from image_update import DockerImageContainerUpdateChecker
from logger import get_logger

logger: logging.Logger = get_logger("app_logger")

DEFAULT_PROFILE: str = "auto"

# Exit codes of the Arlington jar (veraPDF CliConstants.ExitCodes)
JAR_EXIT_FAILED_PARSING: int = 7
JAR_EXIT_ENCRYPTED: int = 8

# CLI ids passed to the Arlington jar as --profile. Desktop labels are the matching
# config.json "set" entries. Keep the two lists in sync.
# Desktop always sends --profile (default auto). Omitting the flag here does not
# forward --profile to the jar.
PROFILES: list[str] = [
    DEFAULT_PROFILE,
    "arlington1.0",
    "arlington1.1",
    "arlington1.2",
    "arlington1.3",
    "arlington1.4",
    "arlington1.5",
    "arlington1.6",
    "arlington1.7",
    "arlington2.0",
]


def set_arguments(
    parser: argparse.ArgumentParser,
    names: list,
    output_help: str = "",
) -> None:
    """
    Set arguments for the parser based on the provided names and options.

    Args:
        parser (argparse.ArgumentParser): The argument parser to set arguments for.
        names (list): List of argument names to set.
        output_help (str): Help shown for output argument. Defaults to "".
    """
    for name in names:
        match name:
            case "format":
                parser.add_argument(
                    "--format",
                    type=str,
                    default="xml",
                    choices=["raw", "xml", "html", "text", "json"],
                    help="Format of output",
                )
            case "input":
                parser.add_argument("--input", "-i", type=str, required=True, help="The input PDF file")
            case "maxfailuresdisplayed":
                parser.add_argument("--maxfailuresdisplayed", type=int, default=-1, help="Max failures displayed")
            case "output":
                parser.add_argument("--output", "-o", type=str, help=output_help)
            case "profile":
                parser.add_argument(
                    "--profile",
                    type=str,
                    choices=PROFILES,
                    help="Arlington grammar profile. Omit to leave profile selection to the Arlington jar.",
                )


def run_config_subcommand(args) -> None:
    get_pdfix_config(args.output)


def get_pdfix_config(path: str) -> None:
    """
    If Path is not provided, output content of config.
    If Path is provided, copy config to destination path.

    Args:
        path (string): Destination path for config.json file
    """
    config_path: Path = Path(__file__).parent.parent.joinpath(CONFIG_FILE).resolve()

    with open(config_path, "r", encoding="utf-8") as file:
        if path is None:
            print(file.read())
        else:
            with open(path, "w") as out:
                out.write(file.read())


def check_output_file(output_path: Optional[str], format: str) -> None:
    """
    Check the output file extension and that its folder exists before validation.

    Args:
        output_path (Optional[str]): Path to the report file, or None to print the report.
        format (str): Format of the report.
    """
    suffix: str = Path(output_path).suffix.lower() if output_path else ""
    if format == "xml" and suffix != ".xml":
        raise ArgumentOutputNotXmlException()
    if format == "html" and suffix != ".html":
        raise ArgumentOutputNotHtmlException()
    if output_path:
        output_folder: Path = Path(output_path).resolve().parent
        if not output_folder.is_dir():
            raise ArgumentOutputFolderNotExistsException(output_folder.as_posix())


def check_input_file(input_path: str) -> None:
    """
    Check that the input is an existing PDF file.

    Args:
        input_path (str): Path to the input PDF file.
    """
    path: Path = Path(input_path)
    if path.suffix.lower() != ".pdf" or not path.is_file():
        raise ArgumentInputNotPdfException(input_path)


def run_validation_subcommand(args) -> None:
    check_output_file(args.output, args.format)
    check_input_file(args.input)

    returncode: int = run_validation(args.input, args.output, args.maxfailuresdisplayed, args.format, args.profile)
    sys.exit(returncode)


def run_validation(
    input_file: str,
    output_file: Optional[str],
    maxfailuresdisplayed: int,
    format: str,
    profile: Optional[str],
) -> int:
    """
    Runs validation using Arlington java program in subprocess.

    Args:
        input_file (str): Path to input PDF file.
        output_file (Optional[str]): Either path to output file or None when output goes to standart output.
        maxfailuresdisplayed (str): Max failures displayed
        format (str): Format of output like json, xml, ...
        profile (Optional[str]): Arlington profile id, for example auto or arlington1.7.

    Return:
        Return code of validation process.
    """
    with tqdm(total=100) as progress_bar:
        progress_bar.set_description("Validating")

        java_program_path: str = Path(__file__).parent.parent.joinpath("res/cli-arlington-1.30.3.jar").as_posix()
        command: list[str] = [
            "java",
            "-jar",
            java_program_path,
            "--maxfailuresdisplayed",
            str(maxfailuresdisplayed),
            "--format",
            format,
        ]
        if profile and profile != DEFAULT_PROFILE:
            command.append("--flavour")
            command.append(profile)

        command_to_run: str = " ".join(command)
        command_to_run += f' "{input_file}"'

        returncode, stdout, stderr = run_subprocess(command_to_run)

        if output_file:
            with open(output_file, "w+", encoding="utf-8") as out:
                out.write(stdout)
        else:
            print(stdout)

        progress_bar.n = 100
        progress_bar.set_description("Done")
        progress_bar.refresh()

    # Log only after the progress bar is closed, so log lines are not glued to it
    for line in stderr.splitlines():
        if line.strip():
            logger.warning(line)

    # arlington returns 0 (no validation errors) or 1 (some validation errors)
    if returncode == JAR_EXIT_FAILED_PARSING:
        raise InputNotValidPdfException(input_file)
    if returncode == JAR_EXIT_ENCRYPTED:
        raise InputEncryptedException(input_file)
    if returncode > 1:
        logger.error(f"Validation exited with code {returncode}")
        raise ValidationFailed()

    if returncode == 0:
        logger.info("PDF document is compliant with the Arlington PDF Model.")
    else:
        logger.info("PDF document is not compliant with the Arlington PDF Model. See the report for details.")
    return returncode


def run_subprocess(command: str) -> tuple[int, str, str]:
    """
    Execute a shell command and capture its output and return code.

    This function runs the validation as shell command using the `subprocess.Popen`
    method, captures the standard output (stdout), standard error (stderr),
    and the return code of the process.

    Args:
        command (str): The shell command to execute.

    Returns:
        tuple: A tuple containing:
            - returncode (int): The return code of the command.
            - stdout (str): The standard output of the command.
            - stderr (str): The standard error of the command.

    """
    process: subprocess.Popen = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        shell=True,
        text=True,
    )
    stdout, stderr = process.communicate()

    return process.returncode, stdout, stderr


def main():
    parser = argparse.ArgumentParser(
        description="Validate a PDF against Arlington grammar",
    )

    subparsers = parser.add_subparsers(title="Commands", dest="command", required=True)

    # Config subcommand
    config_subparser = subparsers.add_parser(
        "config",
        help="Extract config file for integration",
    )
    set_arguments(
        config_subparser, ["output"], "Output to save the config JSON file. Application output is used if not provided."
    )
    config_subparser.set_defaults(func=run_config_subcommand)

    # Validate subcommand
    validate_subparser = subparsers.add_parser(
        "validate",
        help="Run validation of PDF document",
    )
    set_arguments(
        validate_subparser,
        ["input", "output", "maxfailuresdisplayed", "format", "profile"],
        "The output validation file",
    )
    validate_subparser.set_defaults(func=run_validation_subcommand)

    # Parse arguments
    try:
        args = parser.parse_args()
    except ExpectedException as e:
        logger.error(e.message)
        sys.exit(e.error_code)
    except SystemExit as e:
        if e.code != 0:
            logger.error(MESSAGE_ARG_GENERAL)
            sys.exit(EC_ARG_GENERAL)
        # This happens when --help is used, exit gracefully
        sys.exit(0)
    except Exception as e:
        logger.error("Failed to run the program:")
        logger.exception(e)
        sys.exit(2)

    if hasattr(args, "func"):
        # Check for updates only when help is not checked
        update_checker = DockerImageContainerUpdateChecker()
        # Check it in separate thread not to be delayed when there is slow or no internet connection
        update_thread = threading.Thread(target=update_checker.check_for_image_updates)
        update_thread.start()

        # Measure the time it takes to process the input
        start_time: float = time.time()
        current_time: str = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        logger.info(f"Processing started at: {current_time}")

        # Run subcommand
        try:
            args.func(args)
        except ExpectedException as e:
            logger.error(e.message)
            sys.exit(e.error_code)
        except Exception as e:
            # not expected exception -> print stack trace and what exception happened
            logger.error("Failed to run the program:")
            logger.exception(e)
            sys.exit(2)
        finally:
            elapsed_time: float = time.time() - start_time
            current_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            logger.info(f"Processing finished at: {current_time}. Elapsed time: {elapsed_time:.2f} seconds")

            # Make sure to let update thread finish before exiting
            update_thread.join()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
