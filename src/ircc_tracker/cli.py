"""Command-line interface for querying the user's own tracker account."""

from __future__ import annotations

import argparse
import getpass
import json
import sys
from typing import Any, Optional, Sequence

from .client import (
    IrccClient,
    IrccError,
    application_number,
    extract_applications,
    normalize_uci,
)


def build_parser() -> argparse.ArgumentParser:
    return argparse.ArgumentParser(
        prog="ircc-tracker",
        description="Query your own IRCC Application Status Tracker data locally.",
    )


def main(argv: Optional[Sequence[str]] = None) -> int:
    build_parser().parse_args(argv)

    try:
        uci = normalize_uci(input("UCI: "))
        password = getpass.getpass("Tracker password: ")
        if not password:
            raise ValueError("Tracker password cannot be empty.")

        client = IrccClient()
        print("Connecting to IRCC…", file=sys.stderr)

        client.authenticate(uci, password)
        password = ""
        profile = client.get_profile_summary()
        apps = extract_applications(profile)

        if not apps:
            raise IrccError("No applications were returned for this account.")
        app_number = choose_application(apps)

        details = client.get_application_details(
            application_number=app_number,
            uci=uci,
        )
        result: dict[str, Any] = {
            "applicationNumber": app_number,
            "details": details,
        }
        print(json.dumps(result, ensure_ascii=False, indent=2))
        client.clear_tokens()
        return 0

    except (IrccError, ValueError, KeyboardInterrupt, EOFError) as exc:
        if isinstance(exc, KeyboardInterrupt):
            print("\nCancelled.", file=sys.stderr)
        else:
            print(f"Error: {exc}", file=sys.stderr)
        return 1


def choose_application(apps: list[dict[str, Any]]) -> str:
    print("\nApplications:")
    for index, app in enumerate(apps, start=1):
        number = application_number(app) or "unknown"
        app_type = _first_value(app, "appType", "lob", "type") or "—"
        status = _first_value(app, "status", "appStatus") or "—"
        updated = _first_value(app, "lastUpdated", "lastUpdatedTime") or "—"
        print(f"  {index}. {number}  {app_type}  {status}  {updated}")

    while True:
        selection = input("Select application number: ").strip()
        try:
            selected = int(selection)
        except ValueError:
            print("Enter a number from the list.", file=sys.stderr)
            continue
        if 1 <= selected <= len(apps):
            number = application_number(apps[selected - 1])
            if number:
                return number
            raise IrccError("The selected application has no application number.")
        print("Selection is outside the list.", file=sys.stderr)


def _first_value(app: dict[str, Any], *keys: str) -> str:
    for key in keys:
        value = app.get(key)
        if value is not None and value != "":
            return str(value)
    return ""


if __name__ == "__main__":
    raise SystemExit(main())
