.. list-table::
   :widths: 25 25
   :header-rows: 1

   * - `fair-software.nl <https://fair-software.nl>`_ recommendations
     - Badges
   * - \1. Code repository
     - |GitHub Badge|
   * - \2. License
     - |License Badge|
   * - \3. Community Registry
     - |PyPI Badge|
   * - \4. Enable Citation
     - |Zenodo Badge|

.. |GitHub Badge| image:: https://img.shields.io/github/v/release/SS-NES/code-auditor
   :target: https://github.com/SS-NES/code-auditor
   :alt: GitHub Badge

.. |License Badge| image:: https://img.shields.io/badge/license-GPLv3-blue
   :target: https://opensource.org/license/gpl-3-0
   :alt: License Badge

.. |PyPI Badge| image:: https://img.shields.io/pypi/v/code-auditor?colorB=blue
   :target: https://pypi.org/project/code-auditor/
   :alt: PyPI Badge

.. |Zenodo Badge| image:: https://zenodo.org/badge/DOI/10.5281/zenodo.14934232.svg
   :target: https://doi.org/10.5281/zenodo.14934232
   :alt: Zenodo Badge


code-auditor
============

This is a package and command-line utility to audit code quality and compliance
with best practices.


Installation
------------

The package and command-line utility can be installed easily from `PyPI`_ using
``pip``.

.. code:: shell

    pip install code-auditor


To install a specific version, e.g. v0.2.0, use:

.. code:: shell

    pip install code-auditor==0.2.0


To upgrade to the latest version:

.. code:: shell

    pip install --upgrade code-auditor


For the latest development version, you can install directly from the source:

.. code:: shell

    git clone https://github.com/SS-NES/code-auditor.git
    cd code-auditor/
    pip install .


.. _PyPI: https://pypi.org/project/code-auditor/


CLI Usage
---------

.. code:: console

   Usage: codeauditor [OPTIONS] PATH

     Audits the code base, where PATH is the path or URL address of the code base.

   Options:
     --skip-analyser [change_log|citation|code_markdown|code_python|conduct|contributing|dependency_python|documentation|git|jupyter_notebook|license|notice|packaging_python|testing_python]
                                     List of analysers to skip.
     --skip-aggregator [citation|code|community|documentation|license|packaging|repository|testing|version_control|metadata]
                                     List of aggregators to skip.
     --skip-type [citation|code|community|dependency|documentation|license|metadata|packaging|publishing|repository|testing|version_control]
                                     List of processor types to skip.
     -r, --reference FILENAME        Path of the reference metadata for
                                     comparison (e.g. SMP).
     -b, --branch TEXT               Branch or tag of the remote code repository.
     -t, --path-type [zip|tar|tgz|tar.gz|git]
                                     Type of the file located at the path.
     -m, --metadata FILENAME         Path to store the metadata extracted from
                                     the code base.
     -o, --output PATH               Path to store the analysis output.
     -f, --format [plain|html|json|yaml|markdown|rst|rtf|docx]
                                     Output format.  [default: rst]
     -p, --plain                     Enable plain output.
     -l, --message-level INTEGER RANGE
                                     Message level.  [default: 1; 1<=x<=5]
     -d, --debug                     Enable debug mode.
     -v, --version                   Show the version and exit.
     -h, --help                      Show this message and exit.


Examples
~~~~~~~~

Audit the code in the current working directory and display the report in
the terminal:

.. code:: console

   codeauditor .


Audit the code repository of code-auditor and display the report in the
terminal:

.. code:: console

   codeauditor https://github.com/SS-NES/code-auditor


Audit the code repository of code-auditor and save the report as report.docx:

.. code:: console

   codeauditor https://github.com/SS-NES/code-auditor --format docx --output report.docx


Package Usage
-------------

Audit the code in the current working directory and display the report in
the terminal:

.. code:: python

   import codeauditor

   # Generate analysis report
   report = codeauditor.analyse('.')

   # Get report output as Markdown
   out = report.output(format=codeauditor.report.OutputType.MARKDOWN)

   # Display output
   print(out)


Acknowledgements
----------------

This software was developed as part of the TDCC-NES Bottleneck Project "`Best
Practices for Sustainable Software <SS-NES_>`_" funded by the Thematic Digital
Competence Centre (`TDCC`_) for the Natural & Engineering Sciences (`NES`_).

.. _TDCC: https://tdcc.nl/
.. _NES: https://tdcc.nl/about-tddc/nes/
.. _SS-NES: https://tdcc.nl/projects/project-initiatives-nes/tdcc-nes-bottleneck-projects/best-practices-for-sustainable-software/
