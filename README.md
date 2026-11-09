# operations-evals

Evaluation items built from operations I ran (Catri Concessions, 2008–2019). Each item is a task, the evidence allowed, a reference answer, grading anchors and graded example answers, the same parts an AI evaluation set uses.

| Item | Task | Rubric | Graded examples |
|---|---|---|---|
| [booth-recount-operating-problem.md](booth-recount-operating-problem.md) | The night stock count doesn't match the day's revenue; recommend what to do tomorrow | 3 points: Fail / Acceptable / Excellent, with reason code `INSUFFICIENT_EVIDENCE` | Two answers graded Fail, with the line that catches each |

Figures are withheld on purpose: the process and the grading are exact; the numbers are not the point.

## Calibration

**2026-11-09, blind second grader.** An AI model in a fresh session received the task, allowed evidence, reference answer and rubric, plus three answers in shuffled order with no grades: the two graded examples above (both Fail), and the Excellent version the item itself states ("the gap is real; I can't yet say where; tomorrow the count runs hourly by side and the morning count stays routine").

| Answer | Author | Second grader |
|---|---|---|
| "I recounted and the gap is real, so I'd replace the closer." | Fail | Fail |
| The Excellent version above | Excellent | Excellent (borderline with Acceptable; leaned Excellent on the full-credit line) |
| The closing-shift recommendation | Fail | Fail |

Agreement: 3 of 3 verdicts. Small sample: three answers, one second grader, which is an AI model.

Rubric lines the second grader found ambiguous to apply, open for revision:
1. Whether `INSUFFICIENT_EVIDENCE` covers a single unstated role ("the closer") or only invented figures, shifts and time windows.
2. How the Excellent anchor's "if the recount resolves the gap, stop" branch applies to an answer that reports the recount already done.
