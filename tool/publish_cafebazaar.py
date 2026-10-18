#!/usr/bin/env python3
"""Submit a signed PixelHub APK using Cafe Bazaar's app-scoped Pishkhan API.

Intended ONLY for the dedicated manual production workflow. It deliberately
refuses to replace or commit another uncommitted draft release.
"""

from __future__ import annotations

import argparse
import hashlib
import html
import json
import os
from pathlib import Path
import sys
import urllib.error
import urllib.request
import uuid


API_ROOT = "https://api.pishkhan.cafebazaar.ir/v1/apps/releases"
EXPECTED_PACKAGE = "io.github.abolfazl2600.pixelhub"
MAX_ERROR_LENGTH = 300


class PublishError(Exception):
    """A publication precondition or API response failed."""


def call_api(
    method: str,
    endpoint: str,
    secret: str,
    *,
    json_data: dict | None = None,
    apk_file: Path | None = None,
) -> dict:
    if json_data is not None and apk_file is not None:
        raise PublishError("JSON and multipart uploads must be separate requests.")

    headers = {
        "CAFEBAZAAR-PISHKHAN-API-SECRET": secret,
        "Accept": "application/json",
        "User-Agent": "PixelHub-manual-release/1.0",
    }
    body = None
    if json_data is not None:
        body = json.dumps(json_data, ensure_ascii=False).encode("utf-8")
        headers["Content-Type"] = "application/json"
    elif apk_file is not None:
        # The APK is an intentionally bounded release artifact; encoding the
        # multipart form in memory avoids a third-party runtime dependency.
        boundary = "pixelhub-" + uuid.uuid4().hex
        head = (
            f"--{boundary}\r\n"
            'Content-Disposition: form-data; name="architecture"\r\n\r\n'
            "all\r\n"
            f"--{boundary}\r\n"
            'Content-Disposition: form-data; name="apk"; filename="app-release.apk"\r\n'
            "Content-Type: application/vnd.android.package-archive\r\n\r\n"
        ).encode("ascii")
        tail = f"\r\n--{boundary}--\r\n".encode("ascii")
        body = head + apk_file.read_bytes() + tail
        headers["Content-Type"] = f"multipart/form-data; boundary={boundary}"

    request = urllib.request.Request(
        f"{API_ROOT}/{endpoint.lstrip('/')}",
        data=body,
        headers=headers,
        method=method,
    )
    try:
        with urllib.request.urlopen(request, timeout=300) as response:
            payload = response.read()
    except urllib.error.HTTPError as error:
        # Do not echo the HTTP response body; it may contain account data.
        raise PublishError(
            f"Pishkhan {endpoint} returned HTTP {error.code}. "
            "Check the app-scoped token and release state in Pishkhan."
        ) from None
    except urllib.error.URLError as error:
        raise PublishError(f"Pishkhan {endpoint} request failed: network error.") from error

    try:
        result = json.loads(payload)
    except (ValueError, UnicodeDecodeError) as error:
        raise PublishError(f"Pishkhan {endpoint} returned non-JSON data.") from error
    if not isinstance(result, dict):
        raise PublishError(f"Pishkhan {endpoint} returned an invalid response.")
    return result


def require_success(endpoint: str, result: dict) -> None:
    if result.get("type") != "success":
        message = str(result.get("message") or "Unknown API response")
        # Never print raw provider text long enough to include tokens/headers.
        raise PublishError(f"Pishkhan {endpoint} rejected the request: {message[:MAX_ERROR_LENGTH]}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apk", type=Path, required=True, help="Signed APK from this workflow")
    arguments = parser.parse_args()

    secret = os.environ.get("CAFEBAZAAR_PISHKHAN_API_SECRET", "").strip()
    changelog_fa = os.environ.get("CAFEBAZAAR_CHANGELOG_FA", "")
    changelog_en = os.environ.get("CAFEBAZAAR_CHANGELOG_EN", "")
    developer_note = os.environ.get("CAFEBAZAAR_DEVELOPER_NOTE", "")
    version = os.environ.get("RELEASE_VERSION", "")

    if not secret:
        raise PublishError("Missing CAFEBAZAAR_PISHKHAN_API_SECRET secret.")
    if not changelog_fa.strip():
        raise PublishError("Persian release notes must be entered manually.")
    if not arguments.apk.is_file() or arguments.apk.stat().st_size == 0:
        raise PublishError("Signed APK is missing or empty.")
    if arguments.apk.name != "app-release.apk":
        raise PublishError("Only the signed app-release.apk produced by this workflow is supported.")

    sha256 = hashlib.sha256(arguments.apk.read_bytes()).hexdigest()
    print(f"Prepared release {version or '(unknown version)'} for {EXPECTED_PACKAGE}")
    print(f"Signed APK SHA-256: {sha256}")

    # A previous failed run or a manual draft must never be silently mutated.
    pending = call_api("GET", "last-uncommitted/", secret)
    if pending.get("type") != "not-exists":
        raise PublishError(
            "Cafe Bazaar already has an uncommitted release (or its state is unclear). "
            "Review/resolve that draft in Pishkhan before starting a new publication."
        )
    print("No uncommitted release found.")

    require_success("create release", call_api("POST", "", secret, json_data={}))
    print("Created a new Cafe Bazaar draft release.")
    # Do not retry POST operations automatically: the server may have accepted
    # one even when a client-side timeout occurred.
    require_success("upload APK", call_api("POST", "upload/", secret, apk_file=arguments.apk))
    print("Uploaded release APK.")

    commit = {
        "auto_publish": True,
        "staged_rollout_percentage": 100,
        "changelog_fa": changelog_fa,
        "changelog_en": changelog_en,
        "developer_note": developer_note,
    }
    require_success("commit release", call_api("POST", "commit/", secret, json_data=commit))
    print("Cafe Bazaar accepted the release submission. Auto-publish was requested after approval.")

    summary_path = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary_path:
        with open(summary_path, "a", encoding="utf-8") as summary:
            summary.write(
                "## Cafe Bazaar release submitted\n\n"
                f"- App: `{EXPECTED_PACKAGE}`\n"
                f"- Version: `{html.escape(version)}`\n"
                f"- APK SHA-256: `{sha256}`\n"
                "- Rollout requested: **100% after Bazaar approval**\n"
                "- Status: **Submitted** (not proof of live store publication)\n"
                "- [Open Cafe Bazaar Pishkhan](https://pishkhan.cafebazaar.ir/)\n\n"
                f"**Persian notes:** {html.escape(changelog_fa)}\n\n"
                f"**English notes:** {html.escape(changelog_en) or '—'}\n"
            )
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except PublishError as error:
        print(f"::error::{error}", file=sys.stderr)
        sys.exit(1)
