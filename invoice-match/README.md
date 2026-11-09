# Three-way match: purchase order, receiving count, supplier invoice

**Figures are illustrative (made up). The method is how I checked prize shipments at my concession booths.**

When a prize shipment arrived, I matched the supplier's invoice to my purchase order and to my own count of what came off the truck, line by line, and flagged every difference. Price differences went back to the sales rep; short cases rode the next truck to the same event before I'd take a credit; billing for more than arrived was disputed from my count; items never ordered went back to the supplier; and I checked the freight charge against my share of the truck's load by product value before approving payment.

One rule is added for this example and is not a claim about my practice: until the rep confirms a price, the workbook approves the lower of the ordered and billed price.

## How it lines up with current practice
- **Three-way match** (purchase order + goods receipt + invoice) is the standard control for physical goods, because only the receiving count catches billing for goods that never arrived. A two-way match (purchase order + invoice) would pass line 7.
- **Every exception has a category and an owner**, so nothing sits in one generic queue.
- **No tolerance:** every difference was flagged. Many teams set a materiality tolerance so small differences pass; I didn't, and the workbook follows my practice.

## What is in the workbook (`invoice_match.xlsx`)
| Tab | Holds |
|---|---|
| Purchase order, Receiving, Invoice, Truck | The only inputs. The invoice is in the supplier's order, keyed by item code |
| Reconciliation | Each invoice line pulled from the purchase order and my count by item code (XLOOKUP, "not on purchase order" when not found), a duplicate check (COUNTIF), the exception, its action and owner, and the approved amount |
| Reference answers | The answer key, stated before the formulas are checked |
| Checks | Each result against its reference answer (amounts not approved by category with SUMIFS), plus two identities; the last row reads ALL PASS or FAIL |

Each invoice line exercises exactly one case: 1 price over, 2 match (the control), 3 not on the purchase order, 4 short with no later truck (credit), 5 short with a later truck to the same event, 6 price under, 7 billed for more than received, 8 billed twice. The freight is overbilled.

## Reference answers
| Result | Answer |
|---|---|
| Goods approved | 3,560.00 |
| My freight share (3,560 / 20,000 x 1,500) | 267.00 |
| Freight overbilled (300 - 267) | 33.00 |
| Approved payment (3,560 + 267) | 3,827.00 |
| Invoice total (5,110 + 300) | 5,410.00 |
| Invoice minus approved payment | 1,583.00 = price overcharge 60 + items not ordered 190 + billed for more than received 100 + duplicate line 1,200 + freight overbilled 33 |
| Credit requested (line 4: 2 cases x 110.00) | 220.00 |
| Lines: match / price difference / short / billed for more than received / not on the purchase order / billed twice | 1 / 2 / 2 / 1 / 1 / 1 |

## Verify it
- Open the workbook in Excel 2021 or later, Microsoft 365, or Google Sheets: the Checks tab's last row reads ALL PASS.
- `python3 check_invoice_match.py` recomputes every answer from the input tabs without trusting the formulas, refuses any calculated cell that is a typed number, and refuses an XLOOKUP missing the prefix Excel needs.
- `python3 check_invoice_match.py --self-test` runs only after a clean pass, injects four faults, and must catch each with its own named failure.
- `python3 build_invoice_match.py` rebuilds the workbook from the inputs in the script.

## What it does not show
Real invoices, amounts or suppliers; the conversations with the rep and the supplier.
