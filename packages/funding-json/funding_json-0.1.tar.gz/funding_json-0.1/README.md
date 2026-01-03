<!--
SPDX-FileCopyrightText: 2025 Michael Pöhn <michael@poehn.at>
SPDX-License-Identifier: CC0-1.0
-->

# Funding JSON for Python

Python library for parsing, verifying and validating https://fundingjson.org manifests.

## Examples

### Fetch `funding.json` from the web and do a full verification.

```!python
import funding_json

try:
    manifest = funding_json.fetch("https://example.com/funding.json", verify_urls=True)
    print(manifest.entity.name)
except Exception as e:
    print(f"fetching failed: {e}")
```

This will also retreive values for `wellKnown` web-links and verify that the
back-links are correct. To skip that step you can set `verify_urls=False`.

### Load funding json from disk, then run verification:

```!python
import funding_json

try:
    # load manifest from file system
    manifest = funding_json.load(".../local/funding.json")
    # run basic validation checks on well-known urls
    funding_json.validate_well_known_urls("https://example.com/funding.json", manifest)
    # verify link ownership by downloading and checking well-known back-links from the web
    funding_json.verify_well_known_urls("https://example.com/funding.json", manifest)
except AssertionError as e:
    print(f"verificated failed: {e}")
```

## developer notes

run linters, unit tests, etc.:

```
tools/check
```

test fetching, validating and verifying some live funding.json files:

```
tools/integration-test.py
```
