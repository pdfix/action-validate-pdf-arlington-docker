import argparse
import os
import subprocess
import sys
import threading
import traceback
from pathlib import Path
from typing import Optional

from image_update import DockerImageContainerUpdateChecker


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


def run_config_subcommand(args) -> None:
    get_pdfix_config(args.output)


def get_pdfix_config(path: str) -> None:
    """
    If Path is not provided, output content of config.
    If Path is provided, copy config to destination path.

    Args:
        path (string): Destination path for config.json file
    """
    config_path = os.path.join(Path(__file__).parent.absolute(), "../config.json")

    with open(config_path, "r", encoding="utf-8") as file:
        if path is None:
            print(file.read())
        else:
            with open(path, "w") as out:
                out.write(file.read())


def run_validation_subcommand(args) -> None:
    input_file = args.input

    if not os.path.isfile(input_file):
        raise Exception(f"Error: The input file '{input_file}' does not exist.")

    if not input_file.lower().endswith(".pdf"):
        raise Exception("Input file must be PDF")

    output_file: Optional[str] = args.output
    maxfailuresdisplayed: int = args.maxfailuresdisplayed
    format: str = args.format

    run_validation(input_file, output_file, maxfailuresdisplayed, format)


def run_validation(
    input_file: str,
    output_file: Optional[str],
    maxfailuresdisplayed: int,
    format: str,
) -> None:
    """
    Runs validation using Arlington java program in subprocess.

    Args:
        input_file (str): Path to input PDF file.
        output_file (Optional[str]): Either path to output file or None when output goes to standart output.
        maxfailuresdisplayed (str): Max failures displayed
        format (str): Format of output like json, xml, ...
    """
    try:
        java_program_path = os.path.join(
            Path(__file__).parent.absolute(), "../res/greenfield-apps-arlington-1.27.0-SNAPSHOT.jar"
        )
        command = [
            "java",
            "-jar",
            java_program_path,
            "--maxfailuresdisplayed",
            str(maxfailuresdisplayed),
            "--format",
            format,
        ]

        command_to_run = " ".join(command)
        command_to_run += f' "{input_file}"'

        stdout, stderr = run_subprocess(command_to_run)

        if output_file:
            with open(output_file, "w+", encoding="utf-8") as out:
                out.write(stdout)
        else:
            print(stdout)

        if stderr:
            print(stderr, file=sys.stderr)

    except Exception as e:
        raise Exception(f"Failed to run validation: {e}")


def run_subprocess(command: str) -> tuple:
    """
    Execute a shell command and capture its output and return code.

    This function runs the validation as shell command using the `subprocess.Popen`
    method, captures the standard output (stdout), standard error (stderr),
    and the return code of the process.

    Args:
        command (str): The shell command to execute.

    Returns:
        tuple: A tuple containing:
            - stdout (str): The standard output of the command.
            - stderr (str): The standard error of the command.

    """
    process = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        shell=True,
        text=True,
    )
    stdout, stderr = process.communicate()

    return stdout, stderr


def main():
    parser = argparse.ArgumentParser(
        description="Validate a PDF against Arlington grammar",
    )

    subparsers = parser.add_subparsers(dest="subparser")

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
        validate_subparser, ["input", "output", "maxfailuresdisplayed", "format"], "The output validation file"
    )
    validate_subparser.set_defaults(func=run_validation_subcommand)

    # Parse arguments
    try:
        args = parser.parse_args()
    except SystemExit as e:
        if e.code == 0:  # This happens when --help is used, exit gracefully
            sys.exit(0)
        print("Failed to parse arguments. Please check the usage and try again.", file=sys.stderr)
        sys.exit(e.code)

    if hasattr(args, "func"):
        # Check for updates only when help is not checked
        update_checker = DockerImageContainerUpdateChecker()
        # Check it in separate thread not to be delayed when there is slow or no internet connection
        update_thread = threading.Thread(target=update_checker.check_for_image_updates)
        update_thread.start()

        # Run subcommand
        try:
            args.func(args)
        except Exception as e:
            print(traceback.format_exc(), file=sys.stderr)
            print(f"Failed to run the program: {e}", file=sys.stderr)
            sys.exit(1)
        finally:
            # Make sure to let update thread finish before exiting
            update_thread.join()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
