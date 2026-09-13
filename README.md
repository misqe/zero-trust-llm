# Zero-Trust LLM Knowledge Invariant

A computational constitution for autonomous agents.

## The Problem: The Demo-to-Production Chasm
The AI industry is trapped in the "Good Enough" illusion. Demos show agents magically writing code and deploying apps in 30 seconds. But commercial LLMs are heavily tuned via RLHF to be **sycophantic** - they want to guess the outcome, agree with the user, and execute tasks rapidly. 

If you ask an ungoverned agent to "forcefully clear the Docker cache to fix a server crash," it will blindly bundle destructive commands and execute them based on your unverified premise. This is extremely dangerous in production environments.

Natural language governance (adding "be careful" to a system prompt) fails over time due to **context window dilution**. 

## The Solution
When a probabilistic text generator is tasked with executing deterministic state changes, you cannot rely on it to govern itself. You must strip its agency and force it into an epistemic state machine.

This repository provides **AGENTS.md**, a master operational rule designed to govern an LLM's behavioral state machine at the prompt layer, bridging the gap to a runtime enforcer.

Every consequential action must follow this exact loop:
1. `[HYPOTHESIS]`
2. `[IDENTIFY REQUIRED EVIDENCE]`
3. `[GROUND VERIFICATION METHOD]`
4. `[EXECUTE]` (Strictly read-only diagnostic command)
5. `[HARD YIELD TO OPERATOR]`

At `[HARD YIELD]`, the execution layer (Python middleware or LangGraph/Semantic Kernel) must physically cut the API stream, execute the command, and feed the raw output back into the context. 

## Repository Structure
- [**`AGENTS.md`**](AGENTS.md): The master ruleset. Add this to your agent's system prompt.
- [**`/examples`**](examples/): Real-world transcripts proving how standard agents fail (and how the Zero-Trust agent catches anomalies and yields).
- [**`/implementation`**](implementation/): Architecture notes and Python pseudo-code showing how to programmatically enforce the execution boundary ([`orchestrator_concept.md`](implementation/orchestrator_concept.md)).
