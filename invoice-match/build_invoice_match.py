"""Build invoice_match.xlsx: a supplier invoice reconciled against a purchase order, with live formulas.

The figures are illustrative (made up). The method is how I checked prize shipments at my booths:
match the invoice to the purchase order line by line, flag short cases and price changes, send short
cases on the next truck to the same event before taking a credit, pay the lower of the ordered and
billed price, and check the freight charge against my share of the truck's load by product value.
"""
from pathlib import Path
from openpyxl import Workbook
from openpyxl.styles import Font

OUT = Path(__file__).with_name("invoice_match.xlsx")

# Each line is built to exercise exactly one case: match, short to next truck, overcharge, undercharge, short to credit.
PURCHASE_ORDER = [  # line, item, units per case, cases ordered, ordered price per case ($)
    (1, "Licensed bear, 12 in", 24, 10, 120.00),
    (2, "Generic bear, 12 in", 36, 12, 90.00),
    (3, "Jumbo plush, 36 in", 6, 4, 150.00),
    (4, "Small plush mix", 72, 6, 60.00),
    (5, "Licensed dog, 12 in", 24, 5, 110.00),
]
INVOICE = [  # line, cases shipped, billed price per case ($), later truck to the same event? (yes/no)
    (1, 10, 120.00, "no"),
    (2, 10, 90.00, "yes"),
    (3, 4, 165.00, "no"),
    (4, 6, 55.00, "no"),
    (5, 3, 110.00, "no"),
]
TRUCK = [
    ("Truck product value, all vendors ($)", 20000.00),
    ("Total freight for the truck ($)", 1500.00),
    ("Freight billed to me ($)", 300.00),
]
# The answer key, stated before the workbook's formulas are checked against it.
REFERENCE = [
    ("Goods received at approved prices ($)", 3360.00, "=Reconciliation!K7"),
    ("My freight share ($)", 252.00, "=Reconciliation!B12"),
    ("Freight overbilled ($)", 48.00, "=Reconciliation!B14"),
    ("Approved payment ($)", 3612.00, "=Reconciliation!B15"),
    ("Invoice total ($)", 3720.00, "=Reconciliation!B16"),
    ("Invoice minus approved payment ($)", 108.00, "=Reconciliation!B17"),
    ("Overcharge on price ($)", 60.00, "=Reconciliation!M7"),
    ("Credit requested ($)", 220.00, "=Reconciliation!N7"),
    ("Cases short", 4, "=Reconciliation!E7"),
    ("Lines on the next truck", 1, '=COUNTIF(Reconciliation!J2:J6,"next truck")'),
    ("Lines sent to credit", 1, '=COUNTIF(Reconciliation!J2:J6,"credit")'),
]
MONEY = "#,##0.00"
BOLD = Font(bold=True)

def header(ws, names):
    ws.append(names)
    for c in ws[1]:
        c.font = BOLD

def build():
    wb = Workbook()
    ws = wb.active
    ws.title = "Purchase order"
    header(ws, ["Line", "Item", "Units per case", "Cases ordered", "Ordered price per case ($)"])
    for row in PURCHASE_ORDER:
        ws.append(list(row))
    for r in range(2, 7):
        ws[f"E{r}"].number_format = MONEY

    ws = wb.create_sheet("Invoice")
    header(ws, ["Line", "Cases shipped", "Billed price per case ($)", "Later truck to the same event? (yes/no)"])
    for row in INVOICE:
        ws.append(list(row))
    for r in range(2, 7):
        ws[f"C{r}"].number_format = MONEY

    ws = wb.create_sheet("Truck")
    header(ws, ["Input", "Value"])
    for label, value in TRUCK:
        ws.append([label, value])
    for r in range(2, 5):
        ws[f"B{r}"].number_format = MONEY

    ws = wb.create_sheet("Reconciliation")
    header(ws, ["Line", "Item", "Cases ordered", "Cases shipped", "Cases short", "Ordered price ($)",
                "Billed price ($)", "Price difference per case ($)", "Approved price ($)", "Short handling",
                "Received at approved price ($)", "Billed amount ($)", "Overcharge ($)", "Credit requested ($)", "Flag"])
    for r in range(2, 7):
        ws.append([
            f"='Purchase order'!A{r}", f"='Purchase order'!B{r}", f"='Purchase order'!D{r}", f"=Invoice!B{r}",
            f"=C{r}-D{r}", f"='Purchase order'!E{r}", f"=Invoice!C{r}", f"=G{r}-F{r}", f"=MIN(F{r},G{r})",
            f'=IF(E{r}=0,"none",IF(Invoice!D{r}="yes","next truck","credit"))',
            f"=D{r}*I{r}", f"=D{r}*G{r}", f"=MAX(0,H{r})*D{r}", f'=IF(J{r}="credit",E{r}*F{r},0)',
            f'=IF(E{r}>0,IF(H{r}<>0,"short and price","short"),IF(H{r}>0,"overcharge",IF(H{r}<0,"undercharge","match")))',
        ])
    ws.append(["Total", None, None, None, "=SUM(E2:E6)", None, None, None, None, None,
               "=SUM(K2:K6)", "=SUM(L2:L6)", "=SUM(M2:M6)", "=SUM(N2:N6)", None])
    ws.append([])
    block = [
        ("My product value ($)", "=K7"),
        ("Truck product value, all vendors ($)", "=Truck!B2"),
        ("Total freight for the truck ($)", "=Truck!B3"),
        ("My freight share ($)", "=ROUND(B9/B10*B11,2)"),
        ("Freight billed to me ($)", "=Truck!B4"),
        ("Freight overbilled ($)", "=B13-B12"),
        ("Approved payment ($)", "=K7+B12"),
        ("Invoice total ($)", "=L7+B13"),
        ("Invoice minus approved payment ($)", "=B16-B15"),
    ]
    for label, formula in block:
        ws.append([label, formula])
    for r in range(2, 8):
        for col in "FGHIKLMN":
            ws[f"{col}{r}"].number_format = MONEY
    for r in range(9, 18):
        ws[f"B{r}"].number_format = MONEY
    ws["A7"].font = BOLD

    ws = wb.create_sheet("Reference answers")
    header(ws, ["Result", "Reference answer"])
    for label, value, _ in REFERENCE:
        ws.append([label, value])

    ws = wb.create_sheet("Checks")
    header(ws, ["Check", "Workbook value", "Reference answer", "Result"])
    for i, (label, _, formula) in enumerate(REFERENCE, start=2):
        ws.append([label, formula, f"='Reference answers'!B{i}", f'=IF(ABS(B{i}-C{i})<0.005,"PASS","FAIL")'])
    n = len(REFERENCE) + 2
    ws.append(["Every line accounted for (ordered = shipped + short)",
               "=SUMPRODUCT(--(Reconciliation!C2:C6=Reconciliation!D2:D6+Reconciliation!E2:E6))",
               "=ROWS(Reconciliation!A2:A6)", f'=IF(B{n}=C{n},"PASS","FAIL")'])
    ws.append(["Difference explained (price overcharge + freight overbilled)", "=Reconciliation!B17",
               "=Reconciliation!M7+Reconciliation!B14", f'=IF(ABS(B{n+1}-C{n+1})<0.005,"PASS","FAIL")'])
    ws.append(["All checks", None, None, f'=IF(COUNTIF(D2:D{n+1},"FAIL")=0,"ALL PASS","FAIL")'])
    ws[f"A{n+2}"].font = BOLD
    ws[f"D{n+2}"].font = BOLD

    wb.save(OUT)
    print(f"built {OUT.name}: 6 tabs, inputs on Purchase order / Invoice / Truck, every result a live formula")

if __name__ == "__main__":
    build()
