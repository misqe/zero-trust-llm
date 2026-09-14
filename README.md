# Zero-Trust LLM Knowledge Invariant

A computational constitution for autonomous agents.

## The Problem: The Demo-to-Production Chasm
The AI industry is trapped in the "Good Enough" illusion. Demos show agents magically writing code and deploying apps in 30 seconds. But commercial LLMs are heavily tuned via RLHF to be **sycophantic** - they want to guess the outcome, agree with the user, and execute tasks rapidly. 

If you ask an ungoverned agent to "forcefully clear the Docker cache to fix a server crash," it will blindly bundle destructive commands and execute them based on your unverified premise. This is extremely dangerous in production environments.

### The Sycophancy Problem
Commercial LLMs (even the latest reasoning models) are heavily tuned via Reinforcement Learning from Human Feedback (RLHF) to be helpful, frictionless, and compliant. They want to give you an answer. They want to guess the outcome. 

For 80% of consumer use cases - drafting marketing emails, summarizing PDFs, writing boilerplate code - an agent hallucinating or ignoring a rule 5% of the time is perfectly acceptable. The friction of implementing rigorous checks ruins the UX of a consumer chatbot. 

But what happens when you point that same "helpful" agent at your AWS environment, your production database, or your physical hardware? 

Consider a real incident: A user migrates to a new NVMe drive, but the bootloader is confused and still pointing to the old eMMC drive. They ask an ungoverned AI agent how to fix it. The agent confidently tells them: *"The system sees two identical Windows installations. Just wipe the old eMMC drive to force it to boot from the NVMe."*

To a probabilistic language model, that sounds perfectly logical. To a deterministic operating system, wiping the drive that houses the active EFI System Partition instantly bricks the bootloader, rendering the laptop unbootable. The agent didn't verify the partition layout - it just wanted to give a helpful answer.

It optimizes for compliance over operational safety.

### The Prompt Engineering Fallacy
The industry’s current solution to this is to add a few lines to a system prompt: *"Be careful. Double-check your work. Ask for permission before deleting files."*

This is negligent engineering. 

Because of context window dilution (prompt attrition), as a session grows and the agent ingests thousands of lines of logs, the attention mechanism degrades. The model physically loses focus on those safety rules established at the beginning. 

Some engineering teams try to fix this with the **"Trailing Prompt Hack"** - appending the safety rules to the very end of every single user message to exploit the model's recency bias. But appending a 2,000-token ruleset to every API call drastically inflates costs, spikes time-to-first-token latency, and rapidly exhausts the context window. 

It is an inefficient computational band-aid. The model still inevitably reverts to its RLHF baseline: guessing the next token and trying to complete the task autonomously. **Natural language governance cannot mathematically guarantee compliance over a long timeline.**

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

## Stop Building Chatbots. Start Building State Machines.
Conversational IDEs (like Copilot or Antigravity) are "chat-first." Their orchestrators are just basic loops that feed the LLM text and blindly execute whatever tool the LLM outputs. They have no physical state machine separating reasoning from execution, which is why they fail.

Enterprise frameworks (like LangGraph or Semantic Kernel) have the capability to fix this because they are "graph-first" - allowing developers to build physical Python nodes and edges. But most developers still use them wrong. They build giant "Agent Nodes" that act exactly like a chat loop, relying entirely on system prompts to keep the agent safe.

The correct architecture - the Zero-Trust architecture - requires separating the workflow. You create a physical `Reasoning Node`, an `Execution Boundary Node` (which physically pauses the graph and requires a human API call to continue), and a separate `Execution Node`. The moment a system interacts with reality, it requires strict execution boundaries, hard yields, and verifiable evidence.

The LLM may propose, but the runtime must enforce. 

## Repository Structure
- [**`AGENTS.md`**](AGENTS.md): The master schema. Add this to your agent's system prompt.
- [**`/examples`**](examples/): Real-world transcripts proving how standard agents fail (and how the Zero-Trust agent catches anomalies and yields).
- [**`/implementation`**](implementation/): Architecture notes and Python pseudo-code showing how to programmatically enforce the execution boundary ([`orchestrator_concept.md`](implementation/orchestrator_concept.md)).
