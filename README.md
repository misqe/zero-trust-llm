# Zero-Trust LLM Knowledge Invariant

A computational constitution for autonomous agents.

## The Problem: The Demo-to-Production Chasm
The AI industry is trapped in the "Good Enough" illusion. Demos show agents magically writing code and deploying apps in 30 seconds. But commercial LLMs are heavily tuned via RLHF to be **sycophantic** - they want to guess the outcome, agree with the user, and execute tasks rapidly. 

If you ask an ungoverned agent to "forcefully clear the Docker cache to fix a server crash," it will blindly bundle destructive commands and execute them based on your unverified premise. This is extremely dangerous in production environments.

Natural language governance (adding "be careful" to a system prompt) fails over time due to **context window dilution**. 

## The Solution
When a probabilistic text generator is tasked with executing deterministic state changes, you cannot rely on it to govern itself. You must strip its agency and force it into an epistemic state machine.

This repository provides two components:
1. **The Schema (`AGENTS.md`)**: A master system prompt that forces the LLM to expose its logic in a predictable, state-machine format (`[HYPOTHESIS] -> [EVIDENCE] -> [EXECUTE] -> [HARD YIELD]`). 
2. **The Enforcer (Middleware Orchestrator)**: Because prompts always eventually fail due to context dilution, we do **not** trust the LLM to obey `AGENTS.md`. The orchestrator middleware is the true enforcer.

Every consequential action must follow this exact loop:
1. `[HYPOTHESIS]`
2. `[IDENTIFY REQUIRED EVIDENCE]`
3. `[GROUND VERIFICATION METHOD]`
4. `[EXECUTE]` (Strictly read-only diagnostic command)
5. `[HARD YIELD TO OPERATOR]`

At `[HARD YIELD]`, the execution layer (Python middleware, LangGraph, etc.) physically cuts the API stream. **It does not blindly execute the command.** It runs the command through a deterministic whitelist or requires an explicit human `Y/N` override before running `subprocess`. 

### FAQ: What stops the LLM from outputting a destructive command?
Nothing. The LLM will eventually hallucinate a destructive command like `[EXECUTE] rm -rf /`. But because we forced it into the `[EXECUTE]` syntax block, the middleware trivially intercepts it, runs a deterministic regex/AST check, recognizes it as a violation of the read-only invariant, and blocks the execution. The LLM is never in control of the actual terminal.

## Repository Structure
- [**`AGENTS.md`**](AGENTS.md): The master ruleset. Add this to your agent's system prompt.
- [**`MANIFESTO.md`**](MANIFESTO.md): The philosophical and technical arguments against the "Good Enough" AI paradigm.
- [**`/examples`**](examples/): Real-world transcripts proving how standard agents fail (and how the Zero-Trust agent catches anomalies and yields).
- [**`/implementation`**](implementation/): Architecture notes and Python pseudo-code showing how to programmatically enforce the execution boundary ([`orchestrator_concept.md`](implementation/orchestrator_concept.md)).
