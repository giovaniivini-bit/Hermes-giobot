# Spreadsheets Reference — GT App Ecosystem

## Access Credentials
- Token: `/opt/data/google_token.json`
- Python: `/opt/data/venv_google/bin/python`
- API: Google Sheets v4

```python
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

creds = Credentials.from_authorized_user_file('/opt/data/google_token.json')
service = build('sheets', 'v4', credentials=creds)
```

---

## 1. PENDÊNCIA AVIAMENTOS
**ID:** `1aAsiicOY0vu5MgQjeeBCsqcAZwGn3JQmj8drYrVaZtc`
**Title:** PENDÊNCIA AVIAMENTOS

### Abas: PENDENTES | RESOLVIDOS | Tabela dinâmica 1 | Detalhe1-HI

### PENDENTES — Column Schema
| Index | Column | Example |
|-------|--------|---------|
| 0 | TIPO AVIAMENTO | BOTÃO, CADARÇO, ETIQUETA |
| 1 | FORNECEDOR | BRASIL BOTÕES, AL, QUALITA, HI |
| 2 | RESPONSÁVEL | ANA, NATHALIA |
| 3 | COLEÇÃO | HERING INVERNO 27, SUMMER II 2026, WINTER I 2026 |
| 4 | PEDIDO OU FEIRA | FEIRA, PEDIDO |
| 5 | PRODUTO | 13.15.00.0631, 01.14.00.7855 |
| 6 | DESCRIÇÃO | BOTÃO, AL26/10, ETIQUETA |
| 7 | SOLICITADO | 25/06/2026 |
| 8 | PREVISÃO | 17/07/2026 *(NULLABLE — '-' = sem data)* |
| 9 | DIAS | dias corridos desde solicitação |
| 10 | DIAS 2 | "dias 2" (úteis ou outro cálculo) |
| 11 | OBSERVAÇÃO | texto livre, pode conter status |

**Data quality:** Rows 12-13 have PREVISÃO = '-' (no date). ~12 active rows (Jul 2026).

### RESOLVIDOS — Same columns + same data quality issues
~183 resolved items. Some rows incomplete (missing PREVISÃO, empty OBS).

### Tabela dinâmica 1 — Fornecedor ranking
| Col | Content |
|-----|---------|
| 0 | FORNECEDOR (AL, LINEAR, HI, FERRETE...) |
| 1 | Qtde ref |
| 2 | % |
Top suppliers: AL (46/25%), LINEAR (40/22%), HI (19/10%), FERRETE (13/7%)

### Detalhe1-HI — Filtered view
All rows: TIPO AVIAMENTO=ETIQUETA, FORNECEDOR=HI (~14 rows)

---

## 2. PENDENCIA DE CORES - TINTURARIA
**ID:** `1j7k8WWvE9m4YZrw7qadANIcx_XtOzAlwYfWnm0AC5sA`
**Title:** PENDENCIA DE CORES - TINTURARIA

### Abas: ESTILO | CORES APROVADAS | PPCP | Tabela dinâmica 1 | Atrasos por Responsável

### ESTILO — Column Schema (15 cols)
| Index | Column | Notes |
|-------|--------|-------|
| 0 | TINTURARIA | MULTICOLOR (sempre) |
| 1 | RESPONSÁVEL | ANA, NATHALIA, JOYCE, C&A |
| 2 | COLEÇÃO | CENTAURO, HERING, C&A, LICOS RENNER... |
| 3 | SITUAÇÃO | DESENVOLVIMENTO, REBATENDO, AMOSTRA, PEÇA FOTO, BUFFER |
| 4 | PANTONE | código Pantone |
| 5 | COR | nome da cor |
| 6 | BASE | composição (100%CO, 50%CO50%PES...) |
| 7 | SOLICITAÇÃO | número de solicitação |
| 8 | ENVIO AMOST | data de envio da amostra |
| 9 | PREVISÃO | **data prevista entrega** — chave para análise de atraso |
| 10 | DIAS | dias desde solicitação |
| 11 | DIAS 2 | dias 2 |
| 12 | RECEBIDO | data de recebimento físico |
| 13 | ENV CLIENTE | data de envio ao cliente |
| 14 | OBS | texto livre — "RECEBIDO", "PENDENTE...", "Reprovado" |

**Parsing pitfalls:**
- Date format: `dd/mm/yyyy`
- Typos in raw data: `19/062026` (6-digit year), `20262026` need cleanup before parsing
- Value `'33007'` appears as garbage in date columns — treat as no-data
- `'#VALUE!'` appears in calculated cells — treat as no-data
- Check OBS for "RECEBIDO" string when date fields are empty
- ENV CLIENTE can have a date even when RECEBIDO is empty (sent but not physically received)

### CORES APROVADAS — Column Schema (12 cols)
| Index | Column | Notes |
|-------|--------|-------|
| 0 | TINTURARIA | MULTICOLOR, LANCASTER |
| 1 | RESPONSÁVEL | ANA, NATHALIA, JOYCE |
| 2 | COLEÇÃO | SUMMER I 2026, ALTO VERÃO (H9A), OUTONO 2027... |
| 3 | SITUAÇÃO | DESENVOLVIMENTO, AMOSTRA DE COR, REBATENDO |
| 4 | PANTONE | código Pantone |
| 5 | COR | nome da cor |
| 6 | BASE | composição |
| 7 | SOLICITAÇÃO | número ou "PENDENTE C&A" |
| 8 | ENVIO AMOST | data |
| 9 | PREVISÃO | **data prevista** |
| 10 | DIAS | dias |
| 11 | OBS | texto livre |

**IMPORTANT:** No RECEBIDO or ENV CLIENTE columns. "APROVADAS" suggests archived/approved workflow stage.
~94 rows. Many items have PREVISÃO dates in Mar-May 2026 (very old — likely batch-imported historical data).

### PPCP — Column Schema (16+ cols)
| Index | Column |
|-------|--------|
| 0 | RESPONSÁVEL |
| 1 | COLEÇÃO |
| 2 | SITUAÇÃO |
| 3 | PANTONE |
| 4 | COR |
| 5 | BASE |
| 6 | ENTREGUE PPCP |
| 7 | ON |
| 8 | MULTICOLOR |
| 9 | PREÇO |
| 10 | A.J |
| 11 | PREÇO |
| 12 | HJ |
| 13 | PREÇO |
| 14 | CRISTINA |
| 15 | PREÇO |

**No PREVISÃO column** — this is a price/production planning sheet, not for date-based queries. ~147 rows.

### Tabela dinâmica 1 — Responsibility summary
| Resp | Qtde |
|------|------|
| ANA | 17 |
| C&A | 1 |
| NATHALIA | 1 |
| **Total** | **19** |

### Atrasos por Responsável — Overdue count
| Resp | Atrasos |
|------|---------|
| ANA | 9 |

---

## 3. PENDÊNCIA ROTATIVOS
**ID:** `1uQGFBQjMI4Gnyq8eIMxRqFArmr00bEazGQVrHRD9vlY`
**Title:** PENDÊNCIA ROTATIVOS

### Abas: PENDENTES | RESOLVIDOS

### PENDENTES — Column Schema (11 cols)
| Index | Column | Notes |
|-------|--------|-------|
| 0 | PRODUTO | código do produto |
| 1 | ARQUIVO APROV | data de aprovação do arquivo |
| 2 | FID | código FID |
| 3 | PREV. ENT. CILINDRO | previsão de entrega do cilindro |
| 4 | SOLICITAÇÃO | número de solicitação |
| 5 | MESA ENVIADA | data de envio da mesa |
| 6 | PREV. MESA | previsão da mesa — **queriable** |
| 7 | DIAS | dias corridos |
| 8 | RECEBIDO | data de recebimento |
| 9 | ENV. CLIENTE | data de envio ao cliente |
| 10 | OBS | texto livre |

~10 active rows. Rows 13-39 are garbage (repeated '33007') — skip them.

### RESOLVIDOS — Column Schema (13 cols)
Same as PENDENTES + 2 extra columns:
| 11 | APROVADO | data de aprovação |
| 12 | Preço | valor |
| 13 | OBS | texto (may shift depending on row — sometimes OBS is at index 10+2) |

~20 resolved items.

---

## Helpers

### Date Parsing (Python)
```python
from datetime import datetime, date

TODAY = date(2026, 7, 8)  # update when needed

def parse_br_date(s):
    if not s or str(s).strip() in ("-", "", "N/A", "#VALUE!"):
        return None
    s = str(s).strip().replace("20262026", "2026")
    try:
        return datetime.strptime(s, "%d/%m/%Y").date()
    except:
        return None
```

### Overdue Check Pattern
```python
def is_overdue(row, prev_col_idx, rec_col_idx=None, env_col_idx=None, obs_col_idx=None):
    prev = parse_br_date(row[prev_col_idx] if len(row) > prev_col_idx else None)
    if not prev or prev >= TODAY:
        return False
    if rec_col_idx is not None and parse_br_date(row[rec_col_idx]):
        return False
    if env_col_idx is not None and parse_br_date(row[env_col_idx]):
        return False
    if obs_col_idx is not None and "RECEBIDO" in (row[obs_col_idx] or "").upper():
        return False
    return True
```

### Previstos para data específica
```python
target = date(2026, 7, 9)  # amanhã / data alvo

# CORES (ESTILO, col 9 = PREVISÃO)
rows = svc.spreadsheets().values().get(
    spreadsheetId="1j7k8WWvE9m4YZrw7qadANIcx_XtOzAlwYfWnm0AC5sA",
    range="ESTILO!A1:O"
).execute().get("values", [])
for row in rows[1:]:
    prev = parse_br_date(row[9] if len(row) > 9 else None)
    if prev == target:
        print(f"{row[1]} | {row[5]} | Pantone {row[4]} | {row[2]}")

# AVIAMENTOS (PENDENTES, col 8 = PREVISÃO)
rows = svc.spreadsheets().values().get(
    spreadsheetId="1aAsiicOY0vu5MgQjeeBCsqcAZwGn3JQmj8drYrVaZtc",
    range="PENDENTES!A1:L"
).execute().get("values", [])
for row in rows[1:]:
    prev = parse_br_date(row[8] if len(row) > 8 else None)
    if prev == target:
        print(f"{row[0]} | Prod {row[5]} | Forn {row[1]} | {row[3]}")
```

### Previstos para intervalo de datas (esta semana)
```python
start, end = date(2026, 7, 6), date(2026, 7, 10)

# ROTATIVOS (PENDENTES, col 6 = PREV. MESA)
rows = svc.spreadsheets().values().get(
    spreadsheetId="1uQGFBQjMI4Gnyq8eIMxRqFArmr00bEazGQVrHRD9vlY",
    range="PENDENTES!A1:K"
).execute().get("values", [])
for row in rows[1:]:
    prev = parse_br_date(row[6] if len(row) > 6 else None)
    if prev and start <= prev <= end:
        print(f"Prod {row[0]} | FID {row[2]} | Prev mesa: {prev.day:02d}/{prev.month:02d}")
```

### Skip garbage rows
```python
def is_real_row(row):
    """Filter out rows with garbage values (33007, all empty, etc.)"""
    if not row or not any(cell.strip() for cell in row):
        return False
    if row[0] and row[0].strip() == "33007":
        return False
    return True
```
