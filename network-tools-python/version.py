"""Software identity used by the CLI, GUI, documentation, and reports."""

SOFTWARE_NAME = "网络运维工具箱软件"
ENGLISH_NAME = "Network Tools Python"
VERSION = "V1.0"
AUTHOR = "Simpson Liao"
LANGUAGE = "Python"
SUPPORTED_SYSTEMS = "Windows 10/11"


def version_text():
    """Return a concise, user-facing version string."""
    return f"{SOFTWARE_NAME} {VERSION} ({ENGLISH_NAME})"
