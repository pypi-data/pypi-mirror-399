import io
import pathlib
import zipfile
from typing import Any, Optional

import requests

from ..utils.messages import print_verbose


def get(
    url: str,
    path: Optional[str | pathlib.Path] = None,
    verbose: bool = False,
    **kwargs: Any,
) -> Optional[io.BytesIO]:
    """
    Download a ZIP file from a URL and either extract it to a path or return as BytesIO.

    Args:
        url: The URL of the ZIP file to download.
        path: Optional path where the ZIP contents should be extracted.
            If None, returns the ZIP data as a BytesIO object.
            If provided, extracts all files to the specified path.
        verbose: If True, prints progress messages.
        **kwargs: Additional keyword arguments passed to requests.get().

    Returns:
        io.BytesIO containing the ZIP data if path is None,
        otherwise None after extracting files to path.
        Raises on error.

    Raises:
        ValueError: If url is empty or not a string.
        requests.RequestException: If the download fails.
        zipfile.BadZipFile: If the response is not a valid zip.
        Exception: For other unexpected errors while extracting.
    """
    if not isinstance(url, str) or not url.strip():
        raise ValueError("url must be a non-empty string")

    try:
        print_verbose(f"Downloading {url}", verbose=verbose)
        response = requests.get(url, **kwargs)
        response.raise_for_status()  # Raise exception for bad status codes
        data = response.content
        zip_buffer = io.BytesIO(data)

        if path is None:
            return zip_buffer

        print_verbose(f"Saving data to {path}", verbose=verbose)
        zip_buffer.seek(0)
        with zipfile.ZipFile(zip_buffer, "r") as zip_ref:
            # Unlike utils.strings.pathing(), extracting should work even if the
            # destination directory doesn't exist yet.
            extract_root = pathlib.Path(path)
            extract_root.mkdir(parents=True, exist_ok=True)
            for zip_info in zip_ref.infolist():
                extract_path = extract_root / zip_info.filename
                extract_path.parent.mkdir(parents=True, exist_ok=True)
                with open(extract_path, "wb") as f:
                    f.write(zip_ref.read(zip_info.filename))
        return None
    except requests.exceptions.RequestException as e:
        print_verbose(f"Error downloading ZIP from {url}: {e}", verbose=verbose)
        raise
    except zipfile.BadZipFile as e:
        print_verbose(f"Error: Invalid ZIP file from {url}: {e}", verbose=verbose)
        raise
    except Exception as e:
        print_verbose(f"Error processing ZIP file: {e}", verbose=verbose)
        raise
