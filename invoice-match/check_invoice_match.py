"""Check invoice_match.xlsx without trusting its formulas.

1. Every calculated cell on Reconciliation and Checks is a live formula; every XLOOKUP carries the _xlfn prefix
   Excel needs, or the file shows errors when opened.
2. Every reference answer is recomputed in Python from the input tabs alone and must match.
With --self-test (only after a clean pass), four faults are injected and each must produce its own named failure.
"""
import sys
from pathlib import Path
from openpyxl import load_workbook

BOOK = Path(__file__).with_name("invoice_match.xlsx")
N_REF = 19
FORMULA_RANGES = [
    ("Reconciliation", [f"{c}{r}" for r in range(2, 10) for c in "ABCDEFGHIJKLMNOPQ"]
     + [f"{c}10" for c in "NOPQ"] + [f"B{r}" for r in range(12, 21)]),
    ("Checks", [f"{c}{r}" for r in range(2, N_REF + 4) for c in "BCD"] + [f"D{N_REF + 4}"]),
]

def inputs(wb):
    po = {r[0]: (r[3], r[4]) for r in wb["Purchase order"].iter_rows(min_row=2, max_row=7, values_only=True)}
    rcv = {r[0]: (r[1], r[2]) for r in wb["Receiving"].iter_rows(min_row=2, max_row=7, values_only=True)}
    inv = [r for r in wb["Invoice"].iter_rows(min_row=2, max_row=9, values_only=True)]
    truck = [wb["Truck"][f"B{r}"].value for r in (2, 3, 4)]
    return po, rcv, inv, truck

def recompute(po, rcv, inv, truck):
    truck_value, freight, freight_billed = truck
    seen, approved_total, billed_total, credit = set(), 0.0, 0.0, 0.0
    not_approved = {"price difference": 0.0, "not on purchase order": 0.0, "billed for more than received": 0.0, "billed twice": 0.0}
    counts = {k: 0 for k in ["match", "price difference", "short", "billed for more than received", "not on purchase order", "billed twice"]}
    next_truck = to_credit = 0
    for _, code, billed_cases, billed_price in inv:
        dup = code in seen
        seen.add(code)
        on_po = code in po
        ordered, price = po.get(code, (0, 0.0))
        received, later = rcv.get(code, (0, "no"))
        if not on_po:
            cat = "not on purchase order"
        elif dup:
            cat = "billed twice"
        elif billed_cases > received:
            cat = "billed for more than received"
        elif received < ordered:
            cat = "short"
        elif billed_price != price:
            cat = "price difference"
        else:
            cat = "match"
        counts[cat] += 1
        cases_ok = 0 if cat in ("not on purchase order", "billed twice") else min(received, billed_cases)
        price_ok = 0.0 if cases_ok == 0 else min(price, billed_price)
        approved = cases_ok * price_ok
        billed = billed_cases * billed_price
        approved_total += approved
        billed_total += billed
        if cat in not_approved:
            not_approved[cat] += billed - approved
        if cat == "short" and later == "yes":
            next_truck += 1
        elif cat == "short":
            to_credit += 1
            credit += (ordered - received) * price
    share = round(approved_total / truck_value * freight, 2)
    approved_payment = approved_total + share
    invoice_total = billed_total + freight_billed
    return {
        "Goods approved ($)": approved_total,
        "My freight share ($)": share,
        "Freight overbilled ($)": freight_billed - share,
        "Approved payment ($)": approved_payment,
        "Invoice total ($)": invoice_total,
        "Invoice minus approved payment ($)": invoice_total - approved_payment,
        "Price overcharge not approved ($)": not_approved["price difference"],
        "Billed for items not ordered ($)": not_approved["not on purchase order"],
        "Billed for more than received ($)": not_approved["billed for more than received"],
        "Duplicate line not approved ($)": not_approved["billed twice"],
        "Credit requested ($)": credit,
        "Lines matching": counts["match"],
        "Lines with a price difference": counts["price difference"],
        "Lines short": counts["short"],
        "Lines billed for more than received": counts["billed for more than received"],
        "Lines not on the purchase order": counts["not on purchase order"],
        "Lines billed twice": counts["billed twice"],
        "Lines on the next truck": next_truck,
        "Lines sent to credit": to_credit,
    }

def failures(wb):
    found = []
    for sheet, cells in FORMULA_RANGES:
        for c in cells:
            v = wb[sheet][c].value
            if not (isinstance(v, str) and v.startswith("=")):
                found.append(f"{sheet}!{c} is not a live formula ({v!r})")
            elif "XLOOKUP" in v and "_xlfn.XLOOKUP" not in v:
                found.append(f"{sheet}!{c} XLOOKUP is missing the _xlfn prefix (shows an error when opened)")
    reference = {r[0]: r[1] for r in wb["Reference answers"].iter_rows(min_row=2, values_only=True) if r[0]}
    for label, value in reference.items():
        if isinstance(value, str):
            found.append(f"reference answer '{label}' is a formula, not a stated value")
    got = recompute(*inputs(wb))
    for label, want in reference.items():
        if abs(got[label] - want) > 0.005:
            found.append(f"'{label}': recomputed {got[label]:.2f}, reference answer {want:.2f}")
    return found

def fault(desc, mutate, expect):
    wb = load_workbook(BOOK)
    mutate(wb)
    hit = [f for f in failures(wb) if expect in f]
    print(f"  injected fault ({desc}): {'CAUGHT' if hit else 'NOT CAUGHT'}")
    return bool(hit)

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
        def f1(w): w["Receiving"]["B7"] = 3
        def f2(w): w["Reconciliation"]["N10"] = 3560
        def f3(w): w["Invoice"]["B9"] = "PL-777"
        def f4(w): w["Reconciliation"]["C2"] = w["Reconciliation"]["C2"].value.replace("_xlfn.XLOOKUP", "XLOOKUP")
        caught = sum([
            fault("my count raised to match the billing on line 7", f1, "'Lines billed for more than received'"),
            fault("a total typed in place of its formula", f2, "Reconciliation!N10 is not a live formula"),
            fault("the duplicate line changed to an unknown item", f3, "'Lines billed twice'"),
            fault("an XLOOKUP written without its file prefix", f4, "missing the _xlfn prefix"),
        ])
        print(f"self-test: {caught} of 4 injected faults caught -> {'PASS' if caught == 4 else 'FAIL'}")
        if caught != 4:
            sys.exit(1)
    if bad:
        sys.exit(1)

if __name__ == "__main__":
    main()
