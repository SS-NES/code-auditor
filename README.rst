Code Scholar
============

This is a package and command-line utility to check code quality and compliance
with best practices.


Installation
------------

1. Clone or download the `source code <https://github.com/SS-NES/codescholar>`_:

   .. code:: shell

      git clone https://github.com/SS-NES/codescholar.git

2. Go to the root directory:

   .. code:: shell

      cd codescholar/

3. Compile and install using pip:

   .. code:: shell

      pip install .


CLI Usage
---------

.. code:: console

   Usage: codescholar [OPTIONS] PATH

     Scans the code base, where PATH is the path or URL address of the code base.

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

Analyse the code in the current working directory and display the report in
the terminal:

.. code:: console

   codescholar .


Analyse the code repository of Code Scholar:

.. code:: console

   codescholar https://github.com/SS-NES/codescholar
