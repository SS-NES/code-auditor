"""Metadata module."""
import re
from pathlib import Path


REGEXP_DOI = re.compile(r"10\.\d{4,9}/[-._;()/:a-z\d]+", re.IGNORECASE)
"""Regular expression for DOI validation."""

REGEXP_URL = re.compile(r"((http|ftp)(s)?):\/\/(www\.)?[a-z\d@:%._\+~#=-]{2,256}\.[a-z]{2,6}\b([-a-z\d@:%_\+.~#?&//=]*)", re.IGNORECASE)
"""Regular expression for URL validation."""

METADATA = [
    # Authors of the software.
    'authors',
    # Date the software has been released (YYYY-MM-DD).
    'date_released',
    # Description of the software.
    'description',
    # DOI of the software.
    'doi',
    # Keywords that describe the software.
    'keywords',
    # SPDX license identifier of the software.
    'license',
    # Name of the software license.
    'license_name',
    # File name of the software license.
    'license_file',
    # URL address of the software license.
    'license_url',
    # Long description of the software.
    'long_description',
    # Maintainers of the software.
    'maintainers',
    # Name of the software.
    'name',
    # List of dependency packages of the software (Python).
    'python_dependencies',
    # Readme of the software.
    'readme',
    # Readme file of the software.
    'readme_file',
    # URL address of the source code repository of the software.
    'repository_code',
    # Version of the software.
    'version',
    # Version control system of the software.
    'version_control',
]
"""Metadata attributes."""


def is_empty(val) -> bool:
    """Checks if value is empty.

    Args:
        val: Value

    Returns:
        True if value is empty, False otherwise.
    """
    if val is None:
        return True

    if isinstance(val, str) and val.strip() == '':
        return True

    if isinstance(val, dict) or isinstance(val, list):
        for item in val:
            if not is_empty(item):
                return False
        return True

    return False


class Metadata:
    """Metadata class.

    Attributes:
        uid (int): Unique identifier counter.
        metadata (dict): Metadata dictionary.
        lists (dict): List attributes.
    """
    def __init__(self):
        """Initializes metadata object."""
        self.uid = 0
        self.metadata = {}
        self.lists = {}


    def keys(self) -> list[str]:
        """Returns metadata attribute keys."""
        return self.metadata.keys()


    def has(self, key: str) -> bool:
        """Checks is metadata attribute value exists.

        Args:
            key (str): Metadata attribute key.

        Returns:
            True if metadata attribute value exists, False otherwise.
        """
        return True if key in self.metadata else False


    def get(self, key: str, plain: bool=False, first: bool=False, default=None):
        """Returns metadata attribute values.

        Args:
            key (str): Metadata attribute key.
            plain (bool): Set True to return value(s) only (default = False).
            first (bool): Set True to return the firsy value (default = False).
            default: Default value is no attribute value (optional).

        Returns:
            Metadata attribute values.
        """
        if key not in self.metadata:
            return default

        if first:

            item = self.metadata[key][0]

            if self.is_list(key):
                out = []
                id = item['id']

                for item in self.metadata[key]:
                    if item['id'] != id:
                        break
                    out.append(item['val'] if plain else item)

                return out

            elif not plain:
                return item

            else:
                return item['val']

        if not plain:
            return self.metadata[key]

        out = []
        for item in self.metadata[key]:
            if item['val'] not in out:
                out.append(item['val'])

        if not self.is_list(key) and len(out) < 2:
            return out[0]

        return out


    def add(self, analyser, key: str, val, path: Path=None):
        """Adds a metadata attribute.

        Args:
            analyser (Analyser): Analyser class.
            key (str): Metadata attribute key.
            val: Metadata attribute value(s).
            path (Path): Path of the source file (optional).
        """
        # Return if empty value
        if is_empty(val):
            return

        # Initialize metadata list if required
        if key not in self.metadata:
            self.metadata[key] = []

        # Increase id counter
        self.uid += 1

        # Check if value is a list
        if isinstance(val, list):
            vals = val
            self.lists[key] = True

        else:
            vals = [val]

        # For each value
        for val in vals:

            # Skip if empty value
            if is_empty(val):
                continue

            # Add value to metadata list
            item = {
                'val': val,
                'analyser': analyser,
                'path': Path(path) if isinstance(path, str) else path,
                'id': self.uid,
            }

            if item not in self.metadata[key]:
                self.metadata[key].append(item)


    def is_list(self, key: str) -> bool:
        """Checks if metadata attribute is a list.

        Args:
            key (str): Metadata attribute key

        Returns:
            True if metadata attribute is a list, False otherwise.
        """
        return self.lists.get(key) == True


    def validate(self, key: str, val):
        """Validates metadata attribute value.

        Args:
            key (str): Metadata attribute key.
            val: Metadata attribute value.

        Raises:
            ValueError: If metadata value is invalid.
        """
        # Digital Object Identifier (DOI)
        if key == 'doi':
            if not re.fullmatch(REGEXP_DOI, val):
                raise ValueError("Invalid DOI.")

        elif key in ['repository_code', 'license_url']:
            if not re.fullmatch(REGEXP_URL, val):
                raise ValueError("Invalid URL address.")
