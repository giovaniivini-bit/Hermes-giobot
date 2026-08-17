#!/opt/data/venv_google/bin/python3
# -*- coding: utf-8 -*-
"""Cron: log OpenRouter token usage to Google Sheets (Brasilia time UTC-3).

Opções:
1. Método atual (legado): Parse de `hermes insights` (input/output tokens + cálculo de custo)
2. Método preferido (OpenRouter API direta): Consulta `/api/v1/auth/key` → `usage_daily` já calculado.
   Veja exemplo completo em `references/log-usage-openrouter.py`.
"""

import re, subprocess, sys
from datetime import datetime, timezone, timedelta

SID = "SPREADSHEET_ID"
HERM = "/opt/hermes/bin/hermes"
TOK = "/opt/data/google_token.json"
PIN, POUT = 0.00000009, 0.00000018  # DeepSeek V4 Flash (OpenRouter)
BRT = timezone(timedelta(hours=-3))


def parse_ins(out):
    d = {}
    for k, p in [("i", r"Input tokens:\s+([\d,]+)"),
                 ("o", r"Output tokens:\s+([\d,]+)"),
                 ("t", r"Total tokens:\s+([\d,]+)")]:
        m = re.search(p, out)
        d[k] = int(m.group(1).replace(",", "")) if m else 0
    return d


def main():
    now = datetime.now(BRT)
    ds, ts = now.strftime("%Y-%m-%d"), now.strftime("%H:%M")

    # 1. Hermes insights
    r = subprocess.run([HERM, "insights", "--days", "1"],
                       capture_output=True, text=True, timeout=60)
    if r.returncode != 0:
        print(f"ERRO insights: {r.stderr}")
        sys.exit(1)
    cur = parse_ins(r.stdout)

    # 2. Read previous cumulative from Sheets
    from google.oauth2.credentials import Credentials
    from googleapiclient.discovery import build
    svc = build("sheets", "v4",
                credentials=Credentials.from_authorized_user_file(TOK))
    prev_in = prev_out = 0
    prev_cost = 0.0
    rows = (svc.spreadsheets().values()
            .get(spreadsheetId=SID, range="A:G")
            .execute().get("values", []))
    if len(rows) >= 2:
        L = rows[-1]
        if len(L) >= 7:
            def pv(i):
                try:
                    return float(str(L[i]).replace(",", "."))
                except:
                    return 0.0
            prev_in = int(pv(2))
            prev_out = int(pv(3))
            prev_cost = pv(6)

    # 3. Delta & cost
    din = cur["i"] - prev_in
    dout = cur["o"] - prev_out
    dtotal = din + dout
    dcost = round(din * PIN + dout * POUT, 6)
    ccost = round(prev_cost + dcost, 6)

    # 4. Append (RAW mode — critical for pt_BR locale)
    (svc.spreadsheets().values()
     .append(spreadsheetId=SID, range="A:G",
             valueInputOption="RAW",  # ← RAW, NÃO USER_ENTERED!
             insertDataOption="INSERT_ROWS",
             body={"values": [[ds, ts, str(cur["i"]), str(cur["o"]),
                               str(dtotal), f"{dcost:.6f}", f"{ccost:.6f}"]]})
     .execute())

    print(f"LOG {ds} {ts} BRT")
    print(f"  Periodo: +{din} in / +{dout} out = {dtotal} tok | Custo: ${dcost:.6f}")
    print(f"  Total:   {cur['i']} in / {cur['o']} out = {cur['t']} tok | Custo total: ${ccost:.6f}")


if __name__ == "__main__":
    main()

# NOTA: Para uso com OpenRouter API direta (recomendado), veja:
#   references/log-usage-openrouter.py
# 
# Vantagens:
# - Dados em tempo real (sem delay até próximo `insights`)
# - Custo já calculado pela OpenRouter (não precisa calcular input*preço + output*preço)
# - Funciona independente do Hermes estar rodando
# 
# Setup:
# 1. Criar chave OpenRouter API (Workspace Settings → API Keys)
# 2. Codificar em base64: `echo -n "sk-or-v1-..." | base64 > ~/.hermes/.or_key_b64`
# 3. Atualizar script para usar OR_KEY_FILE = "/opt/data/.or_key_b64"
# 4. Substituir parse_insights por get_or_usage() (ver exemplo)