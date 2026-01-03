# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['funding_json']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'funding-json',
    'version': '0.1',
    'description': 'python library for querying and verifying funding.json',
    'long_description': '<!--\nSPDX-FileCopyrightText: 2025 Michael Pöhn <michael@poehn.at>\nSPDX-License-Identifier: CC0-1.0\n-->\n\n# Funding JSON for Python\n\nPython library for parsing, verifying and validating https://fundingjson.org manifests.\n\n## Examples\n\n### Fetch `funding.json` from the web and do a full verification.\n\n```!python\nimport funding_json\n\ntry:\n    manifest = funding_json.fetch("https://example.com/funding.json", verify_urls=True)\n    print(manifest.entity.name)\nexcept Exception as e:\n    print(f"fetching failed: {e}")\n```\n\nThis will also retreive values for `wellKnown` web-links and verify that the\nback-links are correct. To skip that step you can set `verify_urls=False`.\n\n### Load funding json from disk, then run verification:\n\n```!python\nimport funding_json\n\ntry:\n    # load manifest from file system\n    manifest = funding_json.load(".../local/funding.json")\n    # run basic validation checks on well-known urls\n    funding_json.validate_well_known_urls("https://example.com/funding.json", manifest)\n    # verify link ownership by downloading and checking well-known back-links from the web\n    funding_json.verify_well_known_urls("https://example.com/funding.json", manifest)\nexcept AssertionError as e:\n    print(f"verificated failed: {e}")\n```\n\n## developer notes\n\nrun linters, unit tests, etc.:\n\n```\ntools/check\n```\n\ntest fetching, validating and verifying some live funding.json files:\n\n```\ntools/integration-test.py\n```\n',
    'author': 'Michael Pöhn',
    'author_email': 'michael@poehn.at',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'https://codeberg.org/uniqx/funding-json-py',
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
