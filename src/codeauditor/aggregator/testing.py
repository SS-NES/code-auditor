"""Testing aggregator module."""
from . import Aggregator
from ..processor import ProcessorType
from ..report import Report


URLS = {
    'pytest': 'https://docs.pytest.org/en/stable/',
    'test-outside': 'https://docs.pytest.org/en/stable/explanation/goodpractices.html#tests-outside-application-code',
    'test-inside': 'https://docs.pytest.org/en/stable/explanation/goodpractices.html#tests-as-part-of-application-code',
}


class Testing(Aggregator):
    """Testing aggregator class."""

    @classmethod
    def get_type(cls) -> ProcessorType:
        """Returns analyser type of the aggregator."""
        return ProcessorType.TESTING


    @classmethod
    def aggregate(cls, report: Report, results: dict):
        """Aggregates available analysis results.

        Args:
            report (Report): Analysis report.
            results (dict): Analyser results.
        """
        paths = set()
        num_tests = 0
        num_files = 0

        for analyser, items in results.items():

            for path, result in items.items():

                if not result:
                    continue

                report.metadata.add(cls, 'testing_framework', result['framework'], path)
                paths.add(path.parents[0].relative_to(report.path))

                num_tests += result['num_tests']
                num_files += 1

        if not num_tests:
            report.add_issue(cls, "No unit testing.")
            return

        report.add_notice(cls, "Testing exists.")

        layout = None
        for path in paths:
            val = "inside" if len(path.parents) > 2 else "outside"
            if val != layout:
                layout = "mixed" if layout else val
            if layout == "mixed":
                break

        report.metadata.add(cls, 'test_layout', layout)

        result = {
            'num_tests': num_tests,
            'num_files': num_files,
            'paths': list(paths),
        }

        return result


    @classmethod
    def output(cls, report: Report, results: dict) -> str:
        """Generates output from the analysis report and results.

        Args:
            report (Report): Analysis report.
            results (dict): Analysis results.

        Returns:
            Analysis output.
        """
        out = ''
        notes = ''

        out += report.output_heading("Testing", 2)

        val = report.metadata.get('testing_framework', plain=True)

        if isinstance(val, list):
            out += "Testing frameworks are {}.\n".format(
                ", ".join(val)
            )

        else:
            out += "Testing framework is {}.\n".format(
                f"`{val} <{URLS[val]}>`_" if val in URLS else val
            )

        val = report.metadata.get('test_layout', plain=True)

        if val == 'outside':
            out += "Tests are outside the application code [#test-outside].\n"
            notes += f".. [#test-outside] {URLS['test-outside']}\n"

        elif val == 'inside':
            out += "Tests are part of the application code [#test-inside].\n"
            notes += f".. [#test-inside] {URLS['test-inside']}\n"

        elif val == 'mixed':
            out += "Tests have a mixed layout; they are located both inside and outside the application code.\n"

        out += "Tests are located in ``{}`` {}.\n".format(
            "``, ``".join([str(path) for path in results['paths']]),
            "directories" if len(results['paths']) > 1 else "directory"
        )

        out += "There {} {} {} in {} {}.\n".format(
            "are" if results['num_tests'] > 1 else "is",
            results['num_tests'],
            "tests" if results['num_tests'] > 1 else "test",
            results['num_files'],
            "files" if results['num_files'] > 1 else 'file'
        )

        if notes:
            out += "\n\n" + notes

        out += "\n\n"

        return out
