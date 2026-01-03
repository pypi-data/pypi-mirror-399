# SPDX-FileCopyrightText: 2025 Michael Pöhn <michael@poehn.at>
# SPDX-License-Identifier: MIT

"""Library for quering and verifying https://fundingjson.org json files."""

import json
import pathlib
import urllib.parse
import urllib.request

from typing import Optional, Union

from . import model


MANIFEST_FILE = "funding.json"
GITHUB_HOST = "github.com"

# see: https://github.com/floss-fund/portal/blob/457be44674f945e3f5d1559d73d39717ed7104a7/internal/models/models.go#L18"""
WELL_KNOWN_URI = "/.well-known/funding-manifest-urls"


def _enable_obnoxious_github_bros_url(
    url: urllib.parse.ParseResult,
) -> urllib.parse.ParseResult:
    """Re-write github.com urls to github "raw" urls.

    floss.fund seems to accept technicaly wrong github.com urls, using this workaround.
    """
    netloc = url.netloc
    if netloc == "github.com":
        netloc = "raw.githubusercontent.com"
    path = url.path
    if url.netloc == "github.com":
        path = path.replace("/blob/", "/", 1)
        path = path.replace("/raw/refs/", "/refs/", 1)
    return urllib.parse.ParseResult(
        url.scheme,
        netloc,
        path,
        url.params,
        url.query,
        url.fragment,
    )


def _enable_obnoxious_github_bros(url: str) -> str:
    return _enable_obnoxious_github_bros_url(urllib.parse.urlparse(url)).geturl()


def fetch(
    manifest_url: str, verify_urls=False, encoding: Optional[str] = None
) -> model.Manifest:
    """Download, parse and verify a funding.json document."""
    d: Optional[dict] = None
    try:
        with urllib.request.urlopen(
            _enable_obnoxious_github_bros(manifest_url)
        ) as response:
            raw = response.read()
            try:
                d = json.loads(raw)
            except Exception as e:
                raise AssertionError(
                    f"Json parser failed to parse manifest '{manifest_url}'"
                ) from e
    except Exception as e:
        raise AssertionError(f"failed to fetch manifest '{manifest_url}'") from e

    manifest = model.Manifest.from_dict(d)

    validate_well_known_urls(manifest_url, manifest)
    if verify_urls:
        verify_well_known_urls(manifest_url, manifest)

    return manifest


def load(path: Union[str, pathlib.Path]) -> model.Manifest:
    """Read and parse funding json file."""
    path = pathlib.Path(path)
    with open(path, "r") as f:
        return model.Manifest.from_dict(json.load(f))


def _verify_well_known_url(
    manifest_url: str,
    link: model.Url,
):
    """
    Download and verfiy well_known link for a single URL.

    Parameters
    ----------
    manifest_url : str
        Web address of the funding json file you'd like to check
        (e.g.: https://example.com/funding.json)

    link : model.Url
        Verifyable web link as specified by funding json.

    Raises
    ------
    AssertionError
        When fundin_json_url or the web address in the Url object aren't using
        'https://'. When the link doesn't match the manifest_url
        domain/path and no well known is set. or when the value stored in well
        known isn't reteivable/matching.
    """
    m_url = urllib.parse.urlparse(manifest_url)

    if m_url.scheme != "https":
        raise AssertionError(
            f"Funding JSON URL '{manifest_url}' not starting with 'https://'"
        )

    if not link.well_known:
        return

    wk_url = urllib.parse.urlparse(link.well_known)
    if wk_url.scheme != "https":
        raise AssertionError(
            f"Well-Known URL '{link.well_known}' not starting with 'https://'"
        )

    try:
        with urllib.request.urlopen(
            _enable_obnoxious_github_bros(link.well_known)
        ) as r:
            wk_from_web = urllib.parse.urlparse(r.read().decode())
    except Exception as e:
        raise AssertionError(f"downloading '{link.well_known}' failed") from e
    if m_url not in [wk_from_web]:
        raise AssertionError(
            f"Content of '{link.well_known}' doesn't contain the expected value '{manifest_url}'"
        )


def verify_well_known_urls(manifest_url: str, manifest: model.Manifest):
    """Donwnload and verify all well-knonw links."""
    _verify_well_known_url(manifest_url, manifest.entity.webpage_url)
    for project in manifest.projects or []:
        _verify_well_known_url(manifest_url, project.repository_url)
        _verify_well_known_url(manifest_url, project.webpage_url)


def validate_well_known_urls(manifest_url: str, manifest: model.Manifest):
    """Check validity for well_known urls in given Funding JSON Manifest object."""
    _well_known_url(manifest_url, manifest.entity.webpage_url)
    for project in manifest.projects or []:
        _well_known_url(manifest_url, project.repository_url)
        _well_known_url(manifest_url, project.webpage_url)


def _trim_suffix(text: Optional[str], suffix: str):
    """One-time strip suffix string from text string."""
    if text and text.endswith(suffix):
        return text[: -len(suffix)]
    return text


def _is_well_known_required(
    manifest_url: urllib.parse.ParseResult,
    target_url: urllib.parse.ParseResult,
    mf_path,
    tg_path,
):
    """Check whether target url needs a funding json style well-known url to be valid.

    ported from: https://github.com/floss-fund/go-funding-json/blob/master/common/validations.go
    """
    # Parse URLs
    # manifest_parsed = urlparse(manifest_url)
    # target_parsed = urlparse(target_url)

    # Different hosts always require wellKnown
    if manifest_url.netloc != target_url.netloc:
        return True

    # Check if the manifest is in the root of the domain
    # if mf_path == "/":
    if manifest_url.path == "/":
        return False

    # Check if the manifest path can be in a subpath of the target URL or vice versa
    if tg_path.startswith(mf_path) or mf_path.startswith(tg_path):
        return False

    # Special case for github.com where certain conditions apply
    if manifest_url.netloc == GITHUB_HOST and target_url.netloc == GITHUB_HOST:
        parts = manifest_url.path.lstrip("/").split("/")
        if len(parts) > 2 and parts[0] == parts[1]:
            # Check if the target URI is a subpath of the /$user URI
            if target_url.path.startswith(f"/{parts[0]}/"):
                return False

    return True


def _well_known_url(
    manifest_url: str,
    link: model.Url,
    # target, well_known <- encapsuleate in link arg
    # well_known_uri <- we're using WELL_KNOWN_URI constant instead
):
    """Verify whether link is valid or not.

    ported from: https://github.com/floss-fund/go-funding-json/blob/master/common/validations.go

    Parameters
    ----------
    manifest_url : str
        Web address of the funding json file you'd like to check
        (e.g.: https://example.com/funding.json)

    link : model.Url
        Verifyable web link as specified by funding json.
    """
    _manifest_url = urllib.parse.urlparse(manifest_url)
    target_url = urllib.parse.urlparse(link.url)
    wk_url = urllib.parse.urlparse(link.well_known)

    # Get the paths and suffix them with "/" for checking with str.startswith later.
    mf_path = _trim_suffix(_trim_suffix(_manifest_url.path, MANIFEST_FILE), "/") + "/"
    tg_path = target_url.path.rstrip("/") + "/"
    # Check if wellKnown is required based on host and path matching.
    is_required = _is_well_known_required(_manifest_url, target_url, mf_path, tg_path)

    # If wellKnown is not required.
    if not is_required:
        # WellKnownNotRequired
        return

    # wellKnown is required but not provided.
    if not link.well_known:
        raise AssertionError("WellKnownRequired: `wellKnown` required but not provided")

    # Validate the provided wellKnown URL.
    if not str(wk_url.path).endswith(WELL_KNOWN_URI):
        raise AssertionError(
            f"WellKnownInvalid: `wellKnown` should end in '{WELL_KNOWN_URI}'"
        )

    # wellKnown URL should match the main URL.
    if wk_url.netloc != target_url.netloc:
        raise AssertionError(
            f"WellKnownInvalid: url '{target_url.geturl()}' and "
            "`wellKnown` '{wk_url.geturl()}' hostnames do not match"
        )

    wk_path = str(wk_url.path).rstrip("/")
    # is_wk_root = os.path.dirname(wk_path) == ""
    is_wk_root = "/".join(wk_path.split("/")[-1]) == ""

    # If wellKnown is at the root of the host, then all sub-paths are acceptable.
    if is_wk_root:
        return

    # If it's not at the root, then tg_path should be a prefix of the wellKnown path.
    if tg_path != "/" and not wk_path.startswith(tg_path):
        raise AssertionError(
            (
                f"WellKnownInvalid: url and manifest URL host and paths do not match. "
                f"Expected wellKnown for provenance check at "
                f"{target_url.scheme}://{target_url.netloc}{target_url.path}/*{WELL_KNOWN_URI}"
            )
        )
