# CodeScanner Analysis Report

Code quality and conformity for software development best practices analysis
report of {{ metadata.name | metadata(one=True, default='Unnamed Software') }}. The
software is located at `{{ stats.path }}`.

{% for item in notice %}
{{ item | message }}
{% endfor %}

## Issues

{% if issues %}
{% for item in issue %}
{{ item | issue }}
{% endfor %}
{% else %}
No issues found.
{% endif %}

## Metadata

{% if metadata %}
{% for key, item in metadata.items() %}
{{ key }}
: {{ item | metadata(key) }}

{% endfor %}
{% else %}
No metadata found.
{% endif %}

---
Created by [CodeScanner](https://github.com/SS-NES/codescanner) v{{ stats.version }} on {{ stats.date }}.
{{ stats.num_dirs }} directories and {{ stats.num_files }} files are analysed, {{ stats.num_dirs_excluded }} directories were skipped.
Analysis finished in {{ stats.duration }} s.
