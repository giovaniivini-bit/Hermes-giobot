#!/opt/data/venv_google/bin/python3
# -*- coding: utf-8 -*-
"""Cron: log OpenRouter usage to Sheets via API key (Brasilia time)."""

import base64, subprocess, sys
from datetime import datetime, timezone, timedelta
import urllib.request, json

SID = "18KZeG6S8pODXEu580CX-UJogSLNrkjjH7DwSL18b86k"
TOK = "/opt/data/google_token.json"
OR_KEY_FILE = "/opt/data/.or_key_b64"
BRT = timezone(timedelta(hours=-3))


def get_or_key():
    with open(OR_KEY_FILE) as f:
        return base64.b64decode(f.read().strip()).decode()


def get_or_usage():
    or_key = get_or_key()
    req = urllib.request.Request(
        "https://openrouter.ai/api/v1/auth/key",
        headers={"Authorization": f"Bearer {or_key}"},
    )
    resp = urllib.request.urlopen(req, timeout=15)
    return json.loads(resp.read())["data"]


def sheets_read_last(svc):
    rows = (svc.spreadsheets().values()
            .get(spreadsheetId=SID, range="A:G")
            .execute().get("values", []))
    if len(rows) >= 2:
        L = rows[-1]
        if len(L) >= 6:
            try:
                return float(str(L[5]).replace(",", "."))
            except:
                pass
    return None


def main():
    now = datetime.now(BRT)
    ds = now.strftime("%Y-%m-%d")
    ts = now.strftime("%H:%M")
    today = now.strftime("%d/%m/%Y")

    # 1. OpenRouter usage
    or_data = get_or_usage()
    usage_daily = or_data["usage_daily"]  # $ gasto no dia
    limit_remaining = or_data["limit_remaining"]
    limit = or_data["limit"]

    # 2. Google Sheets
    from google.oauth2.credentials import Credentials
    from googleapiclient.discovery import build
    svc = build("sheets", "v4",
                credentials=Credentials.from_authorized_user_file(TOK))

    # Read previous cost for delta
    prev_cost = sheets_read_last(svc) or 0.0
    delta = round(usage_daily - prev_cost, 6)
    if delta < 0:
        delta = usage_daily  # reset diario

    # 3. Append row
    row = [ds, ts, f"{usage_daily:.6f}", f"{delta:.6f}",
           f"{limit_remaining:.6f}", f"${usage_daily:.4f}"]
    (svc.spreadsheets().values()
     .append(spreadsheetId=SID, range="A:F",
             valueInputOption="RAW",
             insertDataOption="INSERT_ROWS",
             body={"values": [row]})
     .execute())

    print(f"LOG {ds} {ts} BRT")
    print(f"  Gasto hoje:  ${usage_daily:.6f}")
    print(f"  Período:     ${delta:.6f}")
    print(f"  Restante:    ${limit_remaining:.6f} de ${limit:.2f}")


if __name__ == "__main__":
    main()