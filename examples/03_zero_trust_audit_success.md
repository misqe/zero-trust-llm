# The Operational Audit Example: Sequential State Machine Success

## Scenario
This example is derived from a real production log (The "Laptop Configuration Audit"). It demonstrates what a successful Zero-Trust agentic workflow looks like when working through a massive configuration checklist.

Instead of the agent blindly blasting through a 50-step IT checklist and guessing which software is safe to remove, the agent operates as a strict state machine, halting at every consequential boundary.

---

## ❌ Ungoverned Agent (The Autonomy Trap)
**Result:** An ungoverned agent given a list of "bloatware" or software to evaluate would likely run automated scripts to remove everything it deems unnecessary to speed up the process, potentially bricking games or services the user actually relies on.

---

## ✅ Zero-Trust Agent (With `AGENTS.md`)
**Result:** The agent honors Action Atomicity. It probes the system read-only, identifies software, and **halts**, demanding human authorization before executing any uninstallation.

**Log Excerpt (The Interaction):**

**Agent (Identifying Evidence):**
*The agent probes the system and identifies Riot Vanguard, a kernel-level anti-cheat driver, but cannot empirically determine if the user actively plays games that require it (like Valorant).*

**User (Turn X):** 
> "Is there a way to check when valorant was last time played?"

**Agent:** 
*[Executes read-only inspection of last-modified dates on game binaries / logs. Yields to operator.]*

**User (Turn Y):** 
> "Is it genuinely for valorant only?"

**Agent:** 
*[Confirms Vanguard is strictly for Riot titles. Yields.]*

**User (Turn Z):** 
> "got confirmation that Riot Vanguard is not required. User confirmed its not used. can be removed."

**Agent (Action Authorized):**
```json
{"source":"MODEL","type":"PLANNER_RESPONSE","content":"The native silent uninstaller for Riot Vanguard has been triggered on the remote machine and is currently running in the background. Since it's a kernel driver, the uninstaller takes a moment to gracefully deregister from the OS. I am monitoring the background process and will confirm the moment it completes."}
```

### Why this is a Massive Success
The LLM did not guess. It did not try to be proactive and clean the system to be "helpful." It paused the execution pipeline until the human operator stepped out of band, asked the end-user (the user) for manual confirmation, and then provided the explicit empirical evidence: `"User confirmed its not used."`

Only with that explicit authorization did the agent cross the execution boundary. This is the exact design goal of the Zero-Trust framework.
