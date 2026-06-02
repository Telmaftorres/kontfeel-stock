import io
from datetime import datetime

from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill


def _header_style(cell, bg: str, bold=True):
    cell.font = Font(bold=bold, color="FFFFFF", size=11)
    cell.fill = PatternFill("solid", fgColor=bg)
    cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)


def _row_fill(ws, row: int, cols: int, color: str):
    fill = PatternFill("solid", fgColor=color)
    for col in range(1, cols + 1):
        ws.cell(row=row, column=col).fill = fill


ETAT_COLORS = {
    "bon_etat":    "DCFCE7",
    "usage":       "FEF9C3",
    "abime":       "FED7AA",
    "irreparable": "FEE2E2",
}


def export_articles_xlsx(articles: list) -> bytes:
    wb = Workbook()
    ws = wb.active
    ws.title = "Stock"

    headers = ["Référence", "Nom", "Format", "Zone", "Unité", "Conditionnement", "Stock actuel", "Stock mini", "Modifié le"]
    col_widths = [15, 30, 14, 14, 10, 14, 13, 11, 18]

    for i, (h, w) in enumerate(zip(headers, col_widths), 1):
        cell = ws.cell(row=1, column=i, value=h)
        _header_style(cell, "4F46E5")
        ws.column_dimensions[cell.column_letter].width = w
    ws.row_dimensions[1].height = 28
    ws.freeze_panes = "A2"

    for r, a in enumerate(articles, 2):
        fill_color = "F0F4FF" if r % 2 == 0 else "FFFFFF"
        values = [
            a.ref, a.nom, a.format or "", a.zone, a.unite,
            a.conditionnement, float(a.stock_actuel), float(a.stock_mini),
            a.updated_at.strftime("%d/%m/%Y %H:%M") if a.updated_at else "",
        ]
        for c, v in enumerate(values, 1):
            cell = ws.cell(row=r, column=c, value=v)
            cell.fill = PatternFill("solid", fgColor=fill_color)

    ws.auto_filter.ref = f"A1:I{len(articles) + 1}"

    buf = io.BytesIO()
    wb.save(buf)
    return buf.getvalue()


def export_gollect_xlsx(items: list) -> bytes:
    wb = Workbook()
    ws = wb.active
    ws.title = "Stock Gollect"

    headers = ["Référence", "Nom", "Description", "État", "Stock actuel", "Créé le", "Modifié le"]
    col_widths = [15, 30, 35, 14, 13, 18, 18]

    for i, (h, w) in enumerate(zip(headers, col_widths), 1):
        cell = ws.cell(row=1, column=i, value=h)
        _header_style(cell, "15803D")
        ws.column_dimensions[cell.column_letter].width = w
    ws.row_dimensions[1].height = 28
    ws.freeze_panes = "A2"

    for r, item in enumerate(items, 2):
        etat = item.etat or ""
        fill_color = ETAT_COLORS.get(etat, "FFFFFF")
        values = [
            item.ref, item.nom, item.description or "", etat,
            float(item.stock_actuel),
            item.created_at.strftime("%d/%m/%Y %H:%M") if item.created_at else "",
            item.updated_at.strftime("%d/%m/%Y %H:%M") if item.updated_at else "",
        ]
        for c, v in enumerate(values, 1):
            cell = ws.cell(row=r, column=c, value=v)
            cell.fill = PatternFill("solid", fgColor=fill_color)

    ws.auto_filter.ref = f"A1:G{len(items) + 1}"

    buf = io.BytesIO()
    wb.save(buf)
    return buf.getvalue()
