# Invoice-to-purchase-order reconciliation

**Figures are illustrative (made up). The method is how I checked prize shipments at my concession booths.**

When a prize shipment arrived, I matched the supplier's invoice to my purchase order line by line, flagged short cases and price changes, had short cases sent on the next truck to the same event instead of taking a credit, paid the lower of the ordered and billed price, and checked the freight charge against my share of the truck's load by product value before approving payment.

## What is in the workbook (`invoice_match.xlsx`)
| Tab | Holds |
|---|---|
| Purchase order, Invoice, Truck | The only inputs |
| Reconciliation | Every result, as live formulas |
| Reference answers | The answer key, stated before the formulas are checked |
| Checks | Each workbook result against its reference answer, plus two reconciliation identities; the last row reads ALL PASS or FAIL |

Each line is built to exercise exactly one case: line 1 matches (the control), line 2 is short and rides the next truck, line 3 is overcharged, line 4 is undercharged, line 5 is short and goes to credit; the freight is overbilled.

## Reference answers
| Result | Answer |
|---|---|
| Goods received at approved prices | 3,360.00 |
| My freight share (3,360 / 20,000 x 1,500) | 252.00 |
| Freight overbilled (300 - 252) | 48.00 |
| Approved payment (3,360 + 252) | 3,612.00 |
| Invoice total (3,420 + 300) | 3,720.00 |
| Invoice minus approved payment | 108.00 = price overcharge 60.00 + freight overbilled 48.00 |
| Credit requested (line 5: 2 cases x 110.00) | 220.00 |
| Cases short / lines on the next truck / lines sent to credit | 4 / 1 / 1 |

## Verify it
- Open the workbook in Excel or Google Sheets: the Checks tab's last row reads ALL PASS.
- `python3 check_invoice_match.py` recomputes every answer from the input tabs without trusting the formulas, and refuses any calculated cell that is a typed number.
- `python3 check_invoice_match.py --self-test` injects two faults (a changed billed price; a total typed in place of its formula) and must catch both.
- `python3 build_invoice_match.py` rebuilds the workbook from the inputs in the script.

## What it does not show
Real invoices, amounts or suppliers; the vendor conversation about the short cases.
