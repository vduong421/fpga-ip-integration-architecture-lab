# FPGA Architecture Analysis Skill

## When Used

Use when the user asks about FPGA IP integration risk, timing slack, CDC/RDC exposure, constraints, power, area, readiness, or next review actions.

## Input

- deterministic FPGA architecture report
- ranked IP blocks
- risk scores
- timing slack
- clock/reset domain counts
- constraint readiness
- review actions

## Expected Output

- answer
- evidence
- next_action
- recommendation
- decision
- risks
- operator_actions

## Rules

- Use deterministic report values only.
- Rank IP blocks by computed risk_score, timing_slack_ns, power_mw, and domain count.
- Highlight high-risk IP blocks separately from ready IP blocks.
- Recommend concrete engineering actions such as timing closure, CDC review, RDC review, constraint completion, and power review.