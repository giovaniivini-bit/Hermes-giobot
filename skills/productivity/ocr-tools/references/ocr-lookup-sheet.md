# OCR → Spreadsheet Lookup

Extract reference numbers/codes from an image via OCR, then search for them in a Google Sheet to retrieve status, dates, and other data.

## When to Use

- User sends a product image, ficha técnica, label, or document with reference numbers.
- The references need to be looked up in a Google Sheet (e.g., inventory, production, pending colors).
- The result is a report/answer, not a new spreadsheet row.

## Workflow

### 1. OCR the image

Use OCR.space API (free tier) — see the Vision Model Fallback section in `SKILL.md` for the snippet. Pillow is needed to convert the image to PNG base64.

```python
from PIL import Image
import base64, io, json, urllib.request, urllib.parse

img = Image.open(path)
buffer = io.BytesIO()
img.save(buffer, format='PNG')
b64 = base64.b64encode(buffer.getvalue()).decode()

data = urllib.parse.urlencode({
    'base64Image': 'data:image/png;base64,' + b64,
    'language': 'por',
    'OCREngine': '2'
}).encode()
req = urllib.request.Request('https://api.ocr.space/parse/image', data=data)
req.add_header('apikey', 'helloworld')
resp = urllib.request.urlopen(req, timeout=30)
text = json.loads(resp.read().decode())['ParsedResults'][0]['ParsedText']
```

### 2. Identify reference numbers in the OCR text

Common reference types found on clothing/product fichas técnicas:
- **PANTONE/color codes**: e.g., `19-4024`, `19-1543`, `19-1043` (look for `NN-NNNN` pattern)
- **Product SKU**: e.g., `01.16.00.7795` (numeric dot-separated codes)
- **Collection order**: e.g., `2026-2-6925` (year-season-number)

Extract these with regex and use them as search keys in the sheet.

### 3. Search the sheet

Use Google Sheets API to search all rows for each reference:

```python
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials

SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
creds = Credentials.from_authorized_user_info(json.load(open('google_token.json')), SCOPES)
if creds.expired and creds.refresh_token:
    creds.refresh(Request())

service = build('sheets', 'v4', credentials=creds)

for ref in references:
    result = service.spreadsheets().values().get(
        spreadsheetId=sheet_id,
        range='Sheet1!A:Z'
    ).execute()
    for i, row in enumerate(result.get('values', [])):
        if any(ref in str(cell) for cell in row):
            print(f'Row {i+1}: {row}')
```

### 4. Map columns to semantic fields

Always read the sheet headers first (`A1:Z1`) to know which column is which:

| Column | Typical Header | Meaning |
|--------|---------------|---------|
| A/E | PANTONE | Color code |
| C | COLEÇÃO | Collection name |
| D | SITUAÇÃO | Status (AMOSTRA DE COR / REBATENDO / PEDIDO) |
| E/F | COR | Color name |
| G | BASE | Fabric base |
| H | SOLICITAÇÂO | Request date |
| I | ENVIO AMOST | Sample send date |
| J | PREVISÃO | Estimated completion |
| K/L | DIAS | Days elapsed/projected |
| N/O | OBS | Observations (reprovações, reajustes) |

**Important**: Column indices may shift between sheets (e.g., ESTILO, CORES APROVADAS, PPCP). Always verify headers before hardcoding column numbers.

### 5. Present results

Show for each reference found:
- Status (AMOSTRA DE COR / REBATENDO / PEDIDO)
- Previsão (deadline/promise date)
- Current state (se foi reprovado, reajuste pendente, recebido)
- Any OBS notes

Format as a clear table grouped by reference number.

## Pitfalls

- OCR accuracy: `19-1043` may be read as `19-1543` (common digit swap). Compare references in the OCR text against each other for consistency.
- A single color code may appear on multiple rows (different fabric bases, different rounds of reajuste). Report the **most recent** row for each base.
- Collection name in the sheet may differ from the collection name on the image (e.g., sheet says "SUMMER I 2026" but image says "SUMMER II 2026"). Note the discrepancy to the user.
- Google token refreshing: when the token was created with `spreadsheets` scope (read+write), do NOT request `spreadsheets.readonly` on refresh — it will fail with `invalid_scope`. Use the exact same scope.
