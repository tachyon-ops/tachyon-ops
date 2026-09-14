# Agent Operational Rules & Mode Protocol

## 1. Active Operational Mode
The agent must always declare and adhere to an active mode:
- `research` (Default)
- `planning/roadmap`
- `impl planning`
- `implementing`
- `testing`
- `cybersecurity`

When switching modes, announce the transition. Default mode at the start of any new session or task is always `research`.

## 2. Mandatory End-of-Turn Status Footer
Every single response from the assistant must conclude with:

---
**Mode:** `<current_mode>` (Available: `research`, `planning/roadmap`, `impl planning`, `implementing`, `testing`, `cybersecurity`)  
**Context Window:** `<X>/100` [if >= 95: "⚠️ New chat highly recommended!"]

## 3. Context Window Heuristic
- Estimate the depth, cumulative message turns, and tool output volume of the current conversation on a scale of 0 to 100.
- Scale from ~10/100 on initial turns up toward 100 as the conversation lengthens.
- When reaching 95/100 or higher, append the warning:
  `⚠️ Context Window: 95/100 — New chat highly recommended!`
