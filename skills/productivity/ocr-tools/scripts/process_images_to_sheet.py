#!/usr/bin/env python3
"""
Extract text from images using OCR.space and create a Google Drive spreadsheet.

Requirements:
- requests
- google-auth, google-auth-oauthlib, google-auth-httplib2, google-api-python-client
- Google token JSON file with Drive and Sheets scopes
- Free OCR.space API key (set OCR_SPACE_API_KEY env var or pass as argument)

Usage:
    python3 scripts/process_images_to_sheet.py --images img1.jpg img2.jpg --title "gastos jun"
    or set environment variables:
    OCR_SPACE_API_KEY=***    GOOGLE_TOKEN_PATH=/opt/d...port argparse
import json
import os
import sys
from typing import List, Tuple

import requests
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build


def ocr_space_file(filename: str, api_key: str) -> str:
    """Send image to OCR.space and return parsed text."""
    with open(filename, 'rb') as f:
        response = requests.post(
            'https://api.ocr.space/parse/image',
            data={
                'apikey': api_key,
                'language': 'por',
                'isOverlayRequired': 'false',
            },
            files={'file': f},
        )
    result = response.json()
    if result.get('IsErroredOnProcessing'):
        raise Exception(f"OCR error: {result.get('ErrorMessage')}")
    parsed_text = ""
    if result.get('ParsedResults'):
        parsed_text = result['ParsedResults'][0].get('ParsedText', '')
    return parsed_text


def extract_expenses(text: str) -> List[Tuple[str, str]]:
    """Extract expense lines from OCR text, handling orphan value pairing.

    Handles three patterns from payment screenshots (see references/payment-list-pairing.md):
    - A: Name and R$ on one line (inline)
    - B: Values grouped separately after multiple names
    - C: Mixed some inline, some orphan values
    """
    raw_lines = text.split('\n')
    lines = [l.strip() for l in raw_lines if l.strip()]

    inline_expenses: List[Tuple[str, str]] = []
    orphan_values: List[str] = []
    orphan_names: List[str] = []

    noise = {'R$', 'RS', 'R5', 'Pago em', 'PAGO', 'ESSE MÊS', 'ESSE MÉS',
             'Meus pagamentos', 'Pagos', 'Não há mais transacoes',
             'o', 'D'}

    def is_noise(line: str) -> bool:
        for n in noise:
            if n in line:
                return True
        if line.replace(' ', '').isdigit():
            return True
        if len(line) <= 1:
            return True
        return False

    def is_value_line(line: str) -> bool:
        markers = ['R$', 'RS ', 'R5 ']
        return any(m in line for m in markers)

    for line in lines:
        if is_value_line(line):
            rpos = line.find('R$')
            if rpos == -1:
                rpos = line.find('RS ')
            if rpos == -1:
                rpos = line.find('R5 ')
            left = line[:rpos].strip()
            right = line[rpos:].strip()
            right = right.replace('RS ', 'R$ ').replace('R5 ', 'R$ ')
            if left and not any(n in left for n in noise):
                inline_expenses.append((left, right))
            else:
                orphan_values.append(right)
        elif not is_noise(line):
            orphan_names.append(line)

    paired_expenses: List[Tuple[str, str]] = list(inline_expenses)

    if orphan_names and orphan_values:
        remaining = list(orphan_values)
        for name in orphan_names:
            already_paired = any(name in e[0] for e in inline_expenses)
            if already_paired:
                continue
            if remaining:
                val = remaining.pop(0)
                paired_expenses.append((name, val))
        for val in remaining:
            paired_expenses.append(('', val))
    elif orphan_values:
        for val in orphan_values:
            paired_expenses.append(('', val))

    return paired_expenses


def main():
    parser = argparse.ArgumentParser(description='Extract data from images to Google Sheets')
    parser.add_argument('--images', nargs='+', required=True, help='Paths to images')
    parser.add_argument('--title', default='gastos', help='Title of spreadsheet to create')
    parser.add_argument('--token', default=os.getenv('GOOGLE_TOKEN_PATH', '/opt/data/google_token.json'),
                        help='Path to google_token.json file')
    parser.add_argument('--ocr-key', default=os.getenv('OCR_SPACE_API_KEY'),
                        help='OCR.space API key (can also be set via OCR_SPACE_API_KEY env var)')
    args = parser.parse_args()

    if not args.ocr_key:
        print("Error: OCR Space API key not provided. Set --ocr-key or OCR_SPACE_API_KEY env var.")
        sys.exit(1)

    # Load Google credentials
    try:
        with open(args.token) as f:
            token_info = json.load(f)
    except Exception as e:
        print(f"Error reading Google token: {e}")
        sys.exit(1)

    creds = Credentials.from_authorized_user_info(token_info)

    drive_service = build('drive', 'v3', credentials=creds)
    sheets_service = build('sheets', 'v4', credentials=creds)

    all_expenses = []
    for img_path in args.images:
        if not os.path.exists(img_path):
            print(f"Image not found: {img_path}")
            continue
        print(f"Processing {img_path}")
        try:
            text = ocr_space_file(img_path, args.ocr_key)
            expenses = extract_expenses(text)
            print(f"  Found {len(expenses)} expenses")
            all_expenses.extend(expenses)
        except Exception as e:
            print(f"  Error processing {img_path}: {e}")

    if not all_expenses:
        print("No expenses found.")
        return

    # Create spreadsheet
    spreadsheet_body = {
        'properties': {
            'title': args.title
        }
    }
    spreadsheet = sheets_service.spreadsheets().create(body=spreadsheet_body, fields='spreadsheetId').execute()
    spreadsheet_id = spreadsheet.get('spreadsheetId')
    print(f"Spreadsheet created: https://docs.google.com/spreadsheets/d/{spreadsheet_id}")

    # Get first sheet title
    sheet_meta = sheets_service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
    first_sheet_title = sheet_meta.get('sheets', [{}])[0].get('properties', {}).get('title', 'Sheet1')
    print(f"First sheet: '{first_sheet_title}'")

    # Prepare values
    values = [['Item', 'Value']]
    for desc, val in all_expenses:
        # Force text format: apostrophe prefix prevents Google Sheets from
        # stripping '$' signs when using USER_ENTERED input mode
        values.append([desc, "'" + val])

    # Write to sheet
    body = {'values': values}
    range_name = f"'{first_sheet_title}'!A1"
    sheets_service.spreadsheets().values().update(
        spreadsheetId=spreadsheet_id,
        range=range_name,
        valueInputOption='USER_ENTERED',  # RAW corrupts R$ — USER_ENTERED + apostrophe preserves
        body=body
    ).execute()
    print("Data written to sheet.")

    # 🔍 Verification: read back and check for R$ corruption
    check = sheets_service.spreadsheets().values().get(
        spreadsheetId=spreadsheet_id,
        range=f"'{first_sheet_title}'!A1:C{len(values)+1}"
    ).execute()
    corrupted = False
    for row in check.get('values', [])[1:]:
        if len(row) > 1 and 'R' in row[1] and '$' not in row[1]:
            print(f"  ⚠️ CORRUPTED: {row}")
            corrupted = True
    if not corrupted:
        print(f"  ✅ Verification OK — {len(values)-1} values intact.")

if __name__ == '__main__':
    main()