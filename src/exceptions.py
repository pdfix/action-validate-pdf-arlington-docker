EC_ARG_GENERAL: int = 10
EC_ARG_OUTPUT_NOT_XML: int = 11
EC_ARG_OUTPUT_NOT_HTML: int = 12
EC_ARG_OUTPUT_FOLDER_NOT_EXISTS: int = 13
EC_ARG_INPUT_NOT_PDF: int = 14

EC_VALIDATION_FAILED: int = 30
EC_INPUT_NOT_VALID_PDF: int = 31
EC_INPUT_ENCRYPTED: int = 32

MESSAGE_ARG_GENERAL: str = "Failed to parse arguments. Please check the usage and try again."
MESSAGE_ARG_OUTPUT_NOT_XML: str = "Output file must be XML document."
MESSAGE_ARG_OUTPUT_NOT_HTML: str = "Output file must be HTML document."
MESSAGE_ARG_OUTPUT_FOLDER_NOT_EXISTS: str = "Output folder does not exist."
MESSAGE_ARG_INPUT_NOT_PDF: str = "Input file must be an existing PDF document."

MESSAGE_VALIDATION_FAILED: str = "Validation failed."
MESSAGE_INPUT_NOT_VALID_PDF: str = "Input file is not a valid PDF document."
MESSAGE_INPUT_ENCRYPTED: str = "PDF document is password-protected. Remove the password with another action first."


class ExpectedException(BaseException):
    def __init__(self, error_code: int) -> None:
        self.error_code: int = error_code
        self.message: str = ""

    def _add_note(self, note: str) -> None:
        self.message = note


class ArgumentException(ExpectedException):
    def __init__(self, message: str = MESSAGE_ARG_GENERAL, error_code: int = EC_ARG_GENERAL) -> None:
        super().__init__(error_code)
        self._add_note(message)


class ArgumentOutputNotXmlException(ArgumentException):
    def __init__(self) -> None:
        super().__init__(MESSAGE_ARG_OUTPUT_NOT_XML, EC_ARG_OUTPUT_NOT_XML)


class ArgumentOutputNotHtmlException(ArgumentException):
    def __init__(self) -> None:
        super().__init__(MESSAGE_ARG_OUTPUT_NOT_HTML, EC_ARG_OUTPUT_NOT_HTML)


class ArgumentOutputFolderNotExistsException(ArgumentException):
    def __init__(self, path: str) -> None:
        super().__init__(f"{MESSAGE_ARG_OUTPUT_FOLDER_NOT_EXISTS} {path}", EC_ARG_OUTPUT_FOLDER_NOT_EXISTS)


class ArgumentInputNotPdfException(ArgumentException):
    def __init__(self, path: str) -> None:
        super().__init__(f"{MESSAGE_ARG_INPUT_NOT_PDF} {path}", EC_ARG_INPUT_NOT_PDF)


class ValidationFailed(ExpectedException):
    def __init__(self) -> None:
        super().__init__(EC_VALIDATION_FAILED)
        self._add_note(MESSAGE_VALIDATION_FAILED)


class InputNotValidPdfException(ExpectedException):
    def __init__(self, path: str) -> None:
        super().__init__(EC_INPUT_NOT_VALID_PDF)
        self._add_note(f"{MESSAGE_INPUT_NOT_VALID_PDF} {path}")


class InputEncryptedException(ExpectedException):
    def __init__(self, path: str) -> None:
        super().__init__(EC_INPUT_ENCRYPTED)
        self._add_note(f"{MESSAGE_INPUT_ENCRYPTED} {path}")
