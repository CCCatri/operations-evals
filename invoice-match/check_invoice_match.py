"""Check invoice_match.xlsx without trusting its formulas.

1. Every calculated cell on Reconciliation and Checks must be a live formula, not a typed number.
2. Every reference answer is recomputed in Python from the input tabs alone and must match.
With --self-test, two faults are injected (a changed billed price; a formula replaced by a typed number)
and each must be caught before any PASS counts.
"""
import sys
from pathlib import Path
from openpyxl import load_workbook

BOOK = Path(__file__).with_name("invoice_match.xlsx")
FORMULA_RANGES = [("Reconciliation", [f"{c}{r}" for r in range(2, 7) for c in "ABCDEFGHIJKLMNO"]
                   + [f"{c}7" for c in "EKLMN"] + [f"B{r}" for r in range(9, 18)]),
                  ("Checks", [f"{c}{r}" for r in range(2, 15) for c in "BCD"] + ["D15"])]

def inputs(wb):
    po = {r[0]: {"ordered": r[3], "price": r[4]} for r in wb["Purchase order"].iter_rows(min_row=2, max_row=6, values_only=True)}
    inv = {r[0]: {"shipped": r[1], "billed": r[2], "later": r[3]} for r in wb["Invoice"].iter_rows(min_row=2, max_row=6, values_only=True)}
    t = [wb["Truck"][f"B{r}"].value for r in (2, 3, 4)]
    return po, inv, t

def recompute(po, inv, truck):
    truck_value, freight, freight_billed = truck
    goods = billed = over = credit = short_total = 0.0
    next_lines = credit_lines = 0
    for line, p in po.items():
        i = inv[line]
        short = p["ordered"] - i["shipped"]
        goods += i["shipped"] * min(p["price"], i["billed"])
        billed += i["shipped"] * i["billed"]
        over += max(0.0, i["billed"] - p["price"]) * i["shipped"]
        short_total += short
        if short > 0 and i["later"] == "yes":
            next_lines += 1
        elif short > 0:
            credit_lines += 1
            credit += short * p["price"]
    share = round(goods / truck_value * freight, 2)
    approved = goods + share
    invoice = billed + freight_billed
    return {
        "Goods received at approved prices ($)": goods,
        "My freight share ($)": share,
        "Freight overbilled ($)": freight_billed - share,
        "Approved payment ($)": approved,
        "Invoice total ($)": invoice,
        "Invoice minus approved payment ($)": invoice - approved,
        "Overcharge on price ($)": over,
        "Credit requested ($)": credit,
        "Cases short": short_total,
        "Lines on the next truck": next_lines,
        "Lines sent to credit": credit_lines,
    }

def failures(wb):
    found = []
    for sheet, cells in FORMULA_RANGES:
        for c in cells:
            v = wb[sheet][c].value
            if not (isinstance(v, str) and v.startswith("=")):
                found.append(f"{sheet}!{c} is not a live formula ({v!r})")
    reference = {r[0]: r[1] for r in wb["Reference answers"].iter_rows(min_row=2, values_only=True) if r[0]}
    for label, value in reference.items():
        if isinstance(value, str):
            found.append(f"reference answer '{label}' is a formula, not a stated value")
    got = recompute(*inputs(wb))
    for label, want in reference.items():
        if abs(got[label] - want) > 0.005:
            found.append(f"'{label}': recomputed {got[label]:.2f}, reference answer {want:.2f}")
    return found

def main():
    wb = load_workbook(BOOK)
    bad = failures(wb)
    print(f"check {BOOK.name}: {'PASS' if not bad else 'FAIL'} ({len(bad)} problems)")
    for b in bad:
        print("  " + b)
    if "--self-test" in sys.argv:
        if bad:
            print("self-test refused: the workbook must pass before an injected fault can count as caught")
            sys.exit(1)
        caught = 0
        wb1 = load_workbook(BOOK); wb1["Invoice"]["C4"] = 150.00
        r1 = [f for f in failures(wb1) if "Overcharge on price" in f]
        print(f"  injected fault 1 (line 3 billed at the ordered price, overcharge removed): {'CAUGHT' if r1 else 'NOT CAUGHT'}")
        caught += bool(r1)
        wb2 = load_workbook(BOOK); wb2["Reconciliation"]["K7"] = 3360
        r2 = [f for f in failures(wb2) if "Reconciliation!K7 is not a live formula" in f]
        print(f"  injected fault 2 (a total typed in place of its formula): {'CAUGHT' if r2 else 'NOT CAUGHT'}")
        caught += bool(r2)
        print(f"self-test: {caught} of 2 injected faults caught -> {'PASS' if caught == 2 else 'FAIL'}")
        if caught != 2:
            sys.exit(1)
    if bad:
        sys.exit(1)

if __name__ == "__main__":
    main()
