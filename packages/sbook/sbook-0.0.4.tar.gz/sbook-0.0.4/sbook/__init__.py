from importlib.metadata import version, PackageNotFoundError


def get_version() -> str:
    try:
        return version("sbook")
    except PackageNotFoundError:
        return "0.0.0"
