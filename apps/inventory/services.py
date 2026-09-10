"""
QB Item import service.

Accepted file formats:
  CSV  — must have columns: Code, Description, UOM  (case-insensitive, order doesn't matter)
  XLSX — same column requirements, reads first sheet

Column aliases accepted:
  Code        → code, item code, item no, item number, sku, part no, part number
  Description → description, desc, item name, name
  UOM         → uom, unit, unit of measure, um
"""
import csv
import io
from django.db import transaction
from .models import QBItem, QBUploadLog


ALIASES = {
    'code':        {'code', 'item code', 'item no', 'item number', 'sku', 'part no', 'part number'},
    'description': {'description', 'desc', 'item name', 'name'},
    'uom':         {'uom', 'unit', 'unit of measure', 'um'},
}


class UploadError(Exception):
    pass


def _normalise_headers(headers):
    """Map raw header names to canonical keys (code, description, uom)."""
    mapping = {}
    for idx, h in enumerate(headers):
        key = h.strip().lower()
        for canonical, aliases in ALIASES.items():
            if key in aliases:
                mapping[canonical] = idx
    missing = [k for k in ('code', 'description', 'uom') if k not in mapping]
    if missing:
        raise UploadError(
            f'Missing required column(s): {", ".join(missing)}. '
            f'Expected headers: Code, Description, UOM.'
        )
    return mapping


def _rows_from_csv(file_obj):
    text = file_obj.read().decode('utf-8-sig')  # handles BOM from Excel CSV export
    reader = csv.reader(io.StringIO(text))
    rows = list(reader)
    if not rows:
        raise UploadError('File is empty.')
    mapping = _normalise_headers(rows[0])
    return mapping, rows[1:]


def _rows_from_xlsx(file_obj):
    try:
        import openpyxl
    except ImportError:
        raise UploadError('openpyxl is required for Excel uploads. Run: pip install openpyxl')
    wb = openpyxl.load_workbook(file_obj, read_only=True, data_only=True)
    ws = wb.active
    rows = [[str(c.value or '').strip() for c in row] for row in ws.iter_rows()]
    wb.close()
    if not rows:
        raise UploadError('Spreadsheet is empty.')
    mapping = _normalise_headers(rows[0])
    return mapping, rows[1:]


@transaction.atomic
def import_qb_items(file_obj, filename, user):
    """
    Parse and upsert QB items from an uploaded file.
    Returns a QBUploadLog instance.
    """
    ext = filename.rsplit('.', 1)[-1].lower()
    if ext == 'csv':
        mapping, data_rows = _rows_from_csv(file_obj)
    elif ext in ('xlsx', 'xls'):
        mapping, data_rows = _rows_from_xlsx(file_obj)
    else:
        raise UploadError(f'Unsupported file type ".{ext}". Upload a CSV or XLSX file.')

    created = updated = skipped = 0

    for row_num, row in enumerate(data_rows, start=2):
        if not any(row):           # skip blank rows
            skipped += 1
            continue
        try:
            code = row[mapping['code']].strip()
            name = row[mapping['description']].strip()
            uom  = row[mapping['uom']].strip()
        except IndexError:
            skipped += 1
            continue

        if not code:
            skipped += 1
            continue

        obj, was_created = QBItem.objects.update_or_create(
            code=code,
            defaults={'name': name, 'uom': uom, 'is_active': True, 'uploaded_by': user},
        )
        if was_created:
            created += 1
        else:
            updated += 1

    log = QBUploadLog.objects.create(
        uploaded_by=user,
        filename=filename,
        rows_total=len(data_rows),
        rows_created=created,
        rows_updated=updated,
        rows_skipped=skipped,
    )
    return log
