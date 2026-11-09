# operations-evals

Evaluation items built from operations I ran (Catri Concessions, 2008–2019). Each item is a task, the evidence allowed, a reference answer, grading anchors and graded example answers, the same parts an AI evaluation set uses.

| Item | Task | Rubric | Graded examples |
|---|---|---|---|
| [booth-recount-operating-problem.md](booth-recount-operating-problem.md) | The night stock count doesn't match the day's revenue; recommend what to do tomorrow | 3 points: Fail / Acceptable / Excellent, with reason code `INSUFFICIENT_EVIDENCE` | Two answers graded Fail, with the line that catches each |

Figures are withheld on purpose: the process and the grading are exact; the numbers are not the point.

## Calibration

**2026-11-09, first pass: not blind.** An AI model graded three unlabeled answers (the two graded examples above and the Excellent version the item states) after receiving the task, allowed evidence, reference answer and rubric. Its verdicts matched the author's on all three, but earlier in the same session it had read the author's Fail grades on two of them, so only its Excellent match is independent. It flagged two rubric lines as ambiguous to apply:
1. Whether `INSUFFICIENT_EVIDENCE` covers a single unstated role ("the closer") or only invented figures, shifts and time windows.
2. How the Excellent anchor's "if the recount resolves the gap, stop" branch applies to an answer that reports the recount already done.

**Fresh run: pending.** A new session with no memory, given only the blind file: the task, allowed evidence, reference answer, rubric and three unlabeled answers.
