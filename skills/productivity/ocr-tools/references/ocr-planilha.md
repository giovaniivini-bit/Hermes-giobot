---
name: ocr-planilha
description: "Extracts text from images using OCR and creates a spreadsheet in Google Drive."
version: 2.0.0
author: Hermes Agent (adapted from obra/superpowers + MorAlekss)
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [OCR, Image, Spreadsheet, Google-Drive]
    related_skills: []
---

# OCR for Spreadsheet

Extract text from images using OCR and create a spreadsheet in Google Drive.

## When to Use

- When you have images containing tabular data (e.g., expenses, payments) and want to insert them into a spreadsheet.
- When you have images containing general text (e.g., product labels, ficha técnica, reference numbers) and need to search that data in a spreadsheet.
- Supports images with monetary values in the format R$ xxx,xx.

## Steps

### 1. Configure Google Credentials
- Have the `google_token.json` file available (generated via OAuth2 authentication).
- The token must have scopes for Google Drive and Google Sheets.

### 2. Install Dependencies (once)
- Use `uv` or `pip` to install: `requests`, `google-auth`, `google-auth-oauthlib`, `google-auth-httplib2`, `google-api-python-client`.
- If `--user` doesn't work (PEP 668), use `uv pip install --target /tmp/packages <pkgs>` and add `sys.path.insert(0, '/tmp/packages')` before imports in the script.

### 3. Run the Script
- Provide image paths in an array.
- The script sends each image to OCR.space (requires a free API key).
- Extracts lines containing "R$" and splits them into description and value.
- Creates a new spreadsheet named "expenses [month]" (or specified name) in the root of Drive.
- Writes header "Item, Value" (and optionally "Date") and the data in subsequent rows.

### 4. Extract Payment Dates
- Bank app screenshots often show "Paid on DD/MM/YYYY" below each name.
- In OCR, these lines appear right after the name (or after the value if inline).
- To pair: after processing names and values, scan lines for `Paid on (\d{2}/\d{2}/\d{4})` and associate with the corresponding expense in order.
- Include a third column "Date" column and sort rows by ascending date (paid first).

### 5. Update Existing Spreadsheet (instead of creating new)
- Use `sheets_service.spreadvalues().clear()` first, then `.update()`.
- Find the spreadsheet ID of the existing one via `sheets_service.spreadsheets().get()`.
- The sheet title (tab) may be "Sheet1" in Portuguese accounts — always read dynamically.

## Pitfalls

- **Google token scope mismatch**: If the token was issued with `https://www.googleapis.com/auth/spreadsheets` (read+write), requesting `spreadsheets.readonly` on refresh will fail with `invalid_scope`. Always use the exact scope the token was originally granted:
  ```python
  SCOPES = ['https://www.googleapis.com/auth/spreadsheets']  # ✅ read+write
  # NOT:
  SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']  # ❌ refresh fails
  ```
  Check the token's original scopes: `python3 -c "import json; print(json.load(open('google_token.json'))['scopes'])"`

- OCR.space free tier limit: 500 requests/day with key "helloworld".
- Ensure images are legible; blurry photos reduce accuracy.
- Script assumes the monetary value is the last occurrence of "R$" on the line.
- If multiple values per line, adjust extraction logic.
- **⚠️ R$ symbol corrupted by Google Sheets API**: using `valueInputOption="RAW"` writes `R$1.460,00` as `R00,00` — the `$` and digits are interpreted as numeric formatting and stripped.
  **Fix**: use `valueInputOption="USER_ENTERED"` and prefix value with apostrophe to force text: `'R$1.460,00`.
  ```python
  # Instead of:
  valueInputOption='RAW'     # ❌ corrupts R$1.460,00 → R00,00
  # Use:
  valueInputOption='USER_ENTERED'  # ✅ preserves R$1.460,00
  # And in data: "'" + "R$1.460,00" → "'R$1.460,00"
  ```
- **Always verify the spreadsheet after writing**: read back with `.values().get()` and check that `$` symbols are intact. Example:
  ```python
  result = sheets_service.spreadsheets().values().get(
      spreadsheetId=id, range='Sheet1!A1:C20'
  ).execute()
  for row in result.get('values', []):
      if 'R' in row[1] and '$' not in row[1]:
          print(f"CORRUPTED: {row}")
  ```

## References

- OCR.space API: https://ocr.space/ocrapi
- Google Sheets API: https://developers.google.com/sheets/api

## Use Case: Monthly Expense Tracking

Use this skill when the user sends screenshots of payments/bank apps with names and amounts (R$) and asks to create/update a monthly expense spreadsheet.

### Extra Steps for This Use Case

1. Extract **3 columns**: Item (name), Value (R$), Date (DD/MM/YYYY).
2. **Dates**: each payment block has "Paid on DD/MM/YYYY" right below the name — extract and associate per heuristic in `references/payment-list-pairing.md` (Pattern D).
3. **Sort by date ascending** (paid first).
4. **Confirm with user** before writing to spreadsheet:
   - Show extracted Name → Value → Date pairs.
   - Ask if order is correct (especially with stray/orphan R$).
   - Only write after user confirms ("ok to insert").
5. **Force text in value cell** with `'R$1.460,00` (apostrophe prefix, `USER_ENTERED` mode) to avoid Google Sheets interpreting as number and stripping `$` and digits.
6. **Verify** by reading back the sheet and confirming all `$` symbols are present.

## Cron Integration

To create a daily check that updates the spreadsheet with new prints:

```
cronjob action=create schedule="0 9 * * *" \
  name="expenses-daily-jun" \
  skills='["ocr-planilha"]' \
  prompt="Check spreadsheet 'expenses jun' (ID: <ID>) in Google Drive for new images in /opt/data/image_cache/. If found, extract expenses, compare with existing, and add missing ones."
```

The `ocr-planilha` skill is automatically loaded by the cron, granting access to its references and scripts.

## User Responses

- Always respond in PT-BR directly, without pleasantries.
- Use tables or bullet points to show extracted pairs.
- Responses in maximum token economy.

## References

- `references/payment-list-pairing.md` — Patterns for name↔value association in bank screenshots
- `scripts/process_images_to_sheet.py` — Functional script implementing the entire flow