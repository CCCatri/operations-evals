"""Build invoice_match.xlsx: a three-way match (purchase order, receiving count, supplier invoice) with live formulas.

Figures are illustrative (made up). The method is how I checked prize shipments at my booths: the supplier's
invoice against my purchase order and my own count of what came off the truck, line by line; every difference
flagged (no tolerance); price differences back to the sales rep; short cases on the next truck to the same event
before a credit; billing for more than arrived disputed from my count; items never ordered refused or returned;
freight checked against my share of the truck's load by product value. One workbook rule is added for the example,
not claimed as my practice: until the rep confirms a price, approve the lower of the ordered and billed price.
"""
from pathlib import Path
from openpyxl import Workbook
from openpyxl.styles import Font

OUT = Path(__file__).with_name("invoice_match.xlsx")
PURCHASE_ORDER = [  # item code, item, units per case, cases ordered, ordered price per case ($)
    ("PL-101", "Licensed bear, 12 in", 24, 10, 120.00),
    ("PL-102", "Generic bear, 12 in", 36, 12, 90.00),
    ("PL-201", "Jumbo plush, 36 in", 6, 4, 150.00),
    ("PL-301", "Small plush mix", 72, 6, 60.00),
    ("PL-401", "Licensed dog, 12 in", 24, 5, 110.00),
    ("PL-501", "Licensed unicorn, 12 in", 24, 3, 100.00),
]
RECEIVING = [  # item code, cases counted off the truck, later truck to the same event for short cases? (yes/no)
    ("PL-101", 10, "no"), ("PL-102", 10, "yes"), ("PL-201", 4, "no"),
    ("PL-301", 6, "no"), ("PL-401", 3, "no"), ("PL-501", 2, "no"),
]
INVOICE = [  # invoice line, item code, cases billed, billed price per case ($): the supplier's order, not mine
    (1, "PL-201", 4, 165.00),   # price difference (over)
    (2, "PL-101", 10, 120.00),  # match: the control
    (3, "PL-900", 2, 95.00),    # not on the purchase order
    (4, "PL-401", 3, 110.00),   # short, no later truck: credit
    (5, "PL-102", 10, 90.00),   # short, later truck to the same event
    (6, "PL-301", 6, 55.00),    # price difference (under)
    (7, "PL-501", 3, 100.00),   # billed for more than received
    (8, "PL-101", 10, 120.00),  # billed twice
]
TRUCK = [
    ("Truck product value, all vendors ($)", 20000.00),
    ("Total freight for the truck ($)", 1500.00),
    ("Freight billed to me ($)", 300.00),
]
R = "Reconciliation"
REFERENCE = [  # the answer key, stated before the workbook's formulas are checked against it
    ("Goods approved ($)", 3560.00, f"={R}!N10"),
    ("My freight share ($)", 267.00, f"={R}!B15"),
    ("Freight overbilled ($)", 33.00, f"={R}!B17"),
    ("Approved payment ($)", 3827.00, f"={R}!B18"),
    ("Invoice total ($)", 5410.00, f"={R}!B19"),
    ("Invoice minus approved payment ($)", 1583.00, f"={R}!B20"),
    ("Price overcharge not approved ($)", 60.00, f'=SUMIFS({R}!P2:P9,{R}!J2:J9,"price difference")'),
    ("Billed for items not ordered ($)", 190.00, f'=SUMIFS({R}!P2:P9,{R}!J2:J9,"not on purchase order")'),
    ("Billed for more than received ($)", 100.00, f'=SUMIFS({R}!P2:P9,{R}!J2:J9,"billed for more than received")'),
    ("Duplicate line not approved ($)", 1200.00, f'=SUMIFS({R}!P2:P9,{R}!J2:J9,"billed twice")'),
    ("Credit requested ($)", 220.00, f"={R}!Q10"),
    ("Lines matching", 1, f'=COUNTIF({R}!J2:J9,"match")'),
    ("Lines with a price difference", 2, f'=COUNTIF({R}!J2:J9,"price difference")'),
    ("Lines short", 2, f'=COUNTIF({R}!J2:J9,"short")'),
    ("Lines billed for more than received", 1, f'=COUNTIF({R}!J2:J9,"billed for more than received")'),
    ("Lines not on the purchase order", 1, f'=COUNTIF({R}!J2:J9,"not on purchase order")'),
    ("Lines billed twice", 1, f'=COUNTIF({R}!J2:J9,"billed twice")'),
    ("Lines on the next truck", 1, f'=COUNTIF({R}!K2:K9,"next truck to the same event: sales rep")'),
    ("Lines sent to credit", 1, f'=COUNTIF({R}!K2:K9,"credit: sales rep")'),
]
MONEY = "#,##0.00"
BOLD = Font(bold=True)
XL = "_xlfn.XLOOKUP"
PO_CODES = "'Purchase order'!$A$2:$A$7"
RCV_CODES = "Receiving!$A$2:$A$7"

def header(ws, names):
    ws.append(names)
    for c in ws[1]:
        c.font = BOLD

def build():
    wb = Workbook()
    ws = wb.active
    ws.title = "Purchase order"
    header(ws, ["Item code", "Item", "Units per case", "Cases ordered", "Ordered price per case ($)"])
    for row in PURCHASE_ORDER:
        ws.append(list(row))
    for r in range(2, 8):
        ws[f"E{r}"].number_format = MONEY

    ws = wb.create_sheet("Receiving")
    header(ws, ["Item code", "Cases counted off the truck", "Later truck to the same event for short cases? (yes/no)"])
    for row in RECEIVING:
        ws.append(list(row))

    ws = wb.create_sheet("Invoice")
    header(ws, ["Invoice line", "Item code", "Cases billed", "Billed price per case ($)"])
    for row in INVOICE:
        ws.append(list(row))
    for r in range(2, 10):
        ws[f"D{r}"].number_format = MONEY

    ws = wb.create_sheet("Truck")
    header(ws, ["Input", "Value"])
    for label, value in TRUCK:
        ws.append([label, value])
    for r in range(2, 5):
        ws[f"B{r}"].number_format = MONEY

    ws = wb.create_sheet(R)
    header(ws, ["Invoice line", "Item code", "Item", "Cases ordered", "Cases received (my count)", "Cases billed",
                "Ordered price ($)", "Billed price ($)", "Billed earlier on this invoice?", "Exception",
                "Action: owner", "Cases approved", "Approved price ($)", "Approved amount ($)", "Billed amount ($)",
                "Not approved ($)", "Credit requested ($)"])
    for r in range(2, 10):
        ws.append([
            f"=Invoice!A{r}", f"=Invoice!B{r}",
            f'={XL}(B{r},{PO_CODES},\'Purchase order\'!$B$2:$B$7,"not on purchase order")',
            f"={XL}(B{r},{PO_CODES},'Purchase order'!$D$2:$D$7,0)",
            f"={XL}(B{r},{RCV_CODES},Receiving!$B$2:$B$7,0)",
            f"=Invoice!C{r}",
            f"={XL}(B{r},{PO_CODES},'Purchase order'!$E$2:$E$7,0)",
            f"=Invoice!D{r}",
            f"=COUNTIF(Invoice!$B$2:$B{r},B{r})>1",
            f'=IF(C{r}="not on purchase order","not on purchase order",IF(I{r},"billed twice",'
            f'IF(F{r}>E{r},"billed for more than received",IF(E{r}<D{r},"short",'
            f'IF(H{r}<>G{r},"price difference","match")))))',
            f'=IF(J{r}="not on purchase order","refuse or return: supplier",IF(J{r}="billed twice","reject the duplicate line: me",'
            f'IF(J{r}="billed for more than received","dispute from my count: me",IF(J{r}="short",'
            f'IF({XL}(B{r},{RCV_CODES},Receiving!$C$2:$C$7,"no")="yes","next truck to the same event: sales rep","credit: sales rep"),'
            f'IF(J{r}="price difference","price back to the sales rep","approve")))))',
            f'=IF(OR(J{r}="not on purchase order",J{r}="billed twice"),0,MIN(E{r},F{r}))',
            f"=IF(L{r}=0,0,MIN(G{r},H{r}))",
            f"=L{r}*M{r}", f"=F{r}*H{r}", f"=O{r}-N{r}",
            f'=IF(K{r}="credit: sales rep",(D{r}-E{r})*G{r},0)',
        ])
    ws.append(["Total"] + [None] * 12 + ["=SUM(N2:N9)", "=SUM(O2:O9)", "=SUM(P2:P9)", "=SUM(Q2:Q9)"])
    ws.append([])
    for label, formula in [
        ("My product value ($)", "=N10"),
        ("Truck product value, all vendors ($)", "=Truck!B2"),
        ("Total freight for the truck ($)", "=Truck!B3"),
        ("My freight share ($)", "=ROUND(B12/B13*B14,2)"),
        ("Freight billed to me ($)", "=Truck!B4"),
        ("Freight overbilled ($)", "=B16-B15"),
        ("Approved payment ($)", "=N10+B15"),
        ("Invoice total ($)", "=O10+B16"),
        ("Invoice minus approved payment ($)", "=B19-B18"),
    ]:
        ws.append([label, formula])
    for r in range(2, 11):
        for col in "GHMNOPQ":
            ws[f"{col}{r}"].number_format = MONEY
    for r in range(12, 21):
        ws[f"B{r}"].number_format = MONEY
    ws["A10"].font = BOLD

    ws = wb.create_sheet("Reference answers")
    header(ws, ["Result", "Reference answer"])
    for label, value, _ in REFERENCE:
        ws.append([label, value])

    ws = wb.create_sheet("Checks")
    header(ws, ["Check", "Workbook value", "Reference answer", "Result"])
    for i, (label, _, formula) in enumerate(REFERENCE, start=2):
        ws.append([label, formula, f"='Reference answers'!B{i}", f'=IF(ABS(B{i}-C{i})<0.005,"PASS","FAIL")'])
    n = len(REFERENCE) + 2
    ws.append(["Every invoice line has an exception category and an owner",
               f"=SUMPRODUCT(--(LEN({R}!J2:J9)>0),--(LEN({R}!K2:K9)>0))", f"=ROWS({R}!A2:A9)",
               f'=IF(B{n}=C{n},"PASS","FAIL")'])
    ws.append(["Difference explained (amounts not approved + freight overbilled)", f"={R}!B20",
               f"={R}!P10+{R}!B17", f'=IF(ABS(B{n+1}-C{n+1})<0.005,"PASS","FAIL")'])
    ws.append(["All checks", None, None, f'=IF(COUNTIF(D2:D{n+1},"FAIL")=0,"ALL PASS","FAIL")'])
    ws[f"A{n+2}"].font = BOLD
    ws[f"D{n+2}"].font = BOLD

    wb.save(OUT)
    print(f"built {OUT.name}: three-way match, 8 invoice lines (one case each), every result a live formula")

if __name__ == "__main__":
    build()
