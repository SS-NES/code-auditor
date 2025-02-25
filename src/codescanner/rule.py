"""Rule module."""
import fnmatch

from .analyser import Analyser


class Rule:
    """Rule class.

    Attributes:
        is_dir (bool): True if a directory rule, i.e. ends with ``/``.
        is_nested (bool): True if a nested rule, i.e. contains ``/``.
        val (str): Rule value.
        analysers (list[Analyser]): List of analysers.
    """

    def __init__(self, val: str, analyser: Analyser = None):
        """Initializes rule object.

        Args:
            val (str): Rule value.
            analyser (Analyser): Analyser (optional).
        """
        self.is_dir = val[-1] == '/'
        if self.is_dir:
            val = val[:-1]
        self.is_nested = val[0] == '/'
        if self.is_nested:
            val = val[1:]
        else:
            self.is_nested = '/' in val
        self.val = val
        self.analysers = [analyser] if analyser else []


    def match(self, val: str) -> bool:
        """Check is value matches the rule.

        Args:
            val (str): Value.

        Returns:
            True is value matches the rule, False otherwise.
        """
        return fnmatch.fnmatch(val, self.val)
