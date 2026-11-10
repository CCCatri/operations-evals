# operations-evals

Evaluation items built from operations I ran (Catri Concessions, 2008–2019). Each item is a task, the evidence allowed, a reference answer, grading anchors and graded example answers, the same parts an AI evaluation set uses.

| Item | Task | Rubric | Graded examples |
|---|---|---|---|
| [booth-recount-operating-problem.md](booth-recount-operating-problem.md) | The night stock count doesn't match the day's revenue; recommend what to do tomorrow | 3 points: Fail / Acceptable / Excellent, with reason code `INSUFFICIENT_EVIDENCE` | Two answers graded Fail, with the line that catches each |

Figures are withheld on purpose: the process and the grading are exact; the numbers are not the point.

## Inter-annotator agreement

**2026-11-09, fresh run (blind).** An AI model in a new session with no memory received only the blind file: the task, allowed evidence, reference answer, rubric and three unlabeled answers (the two graded examples above and the Excellent version the item states), with no grades.

| Answer | Author | Second grader | Reason code (second grader) |
|---|---|---|---|
| "I recounted and the gap is real, so I'd replace the closer." | Fail | Fail | Not applied: the failure is attribution from the aggregate gap |
| The Excellent version | Excellent | Excellent (borderline with Acceptable; leaned Excellent because the recount had already confirmed the gap) | — |
| The closing-shift recommendation | Fail | Fail | `INSUFFICIENT_EVIDENCE` |

Agreement: 3 of 3 verdicts. Small sample: three answers, one second grader, which is an AI model.

Rubric defect found: the Excellent anchor asks for every result branch to be spelled out, while the full-credit sentence asks only for "insufficient to identify a person" plus what to check next, so one answer can meet one bar and not the other. The not-blind first pass (below) flagged the same line. **Revised 2026-11-09: one bar.** The item's own Excellent answer takes the next step from where the evidence stands without spelling out every branch, which is why the second grader called it borderline; the Excellent anchor now asks for that next step, and the full-credit sentence points to the anchor (naming insufficiency without the next step is Acceptable). The revised rubric has not yet been re-run blind.

**2026-11-10, re-run blind on the revised rubric.** A fresh AI model with no memory received only the blind file: the item's task, allowed evidence, procedure, reference answer and revised anchors, and three unlabeled answers in a new order. Agreement: 2 of 3. Both Fails matched. The item's own Excellent version was graded Acceptable: it gave no reason for its next step ("and says why"), and it said the gap could not yet be placed, not that a person could not yet be named ("Says the evidence cannot yet identify a person"). The grader also found that the full-credit sentence still restated only part of the anchor, so the two were still two bars. Fixed the same day: the full-credit sentence points to the anchor without restating it, and the Excellent version gives its reason and says nobody can be named yet. These fixes have not yet been re-run blind.

**2026-11-09, first pass: not blind.** An AI model graded the same three answers, but earlier in its session it had read the author's Fail grades on two of them, so only its Excellent match was independent. It also flagged whether `INSUFFICIENT_EVIDENCE` covers a single unstated role ("the closer"). Superseded by the fresh run.

## Three-way match: purchase order, receiving count, invoice
[`invoice-match/`](invoice-match/): a supplier invoice matched line by line against my purchase order and my own count of what arrived, with each exception categorized and routed to its owner (price, short, billed for more than received, never ordered, billed twice, freight). The figures are illustrative; the method is how I checked prize shipments. It includes an answer key, a Checks tab that must read ALL PASS, and an independent checker that must catch four injected faults.
