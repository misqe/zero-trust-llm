# Zero-Trust Self-Learning Architecture (Conceptual Workflow)

This document demonstrates how to build an agentic system that continuously learns and improves its own knowledge base **without sacrificing deterministic governance or succumbing to context dilution.**

Instead of asking the LLM to "remember" lessons in a massive chat loop, the orchestrator uses **background Reflection Agents** to compile isolated markdown files (`skills/` and `rules/`). The orchestrator then deterministically injects these files into future contexts using a semantic vector search.

```python
import os
import json
import subprocess
import hashlib
from typing import List, Dict

# -----------------------------------------------------------------------------
# 1. THE REFLECTION ENGINE (Background Sub-Agent)
# -----------------------------------------------------------------------------

def spawn_reflection_agent(hypothesis: str, command: str, result: str, outcome_state: str):
    """
    Spawns a background LLM process that does NOT have execution access.
    Its sole job is to distill the execution log into a deterministic markdown file.
    """
    if outcome_state == "[CONFIRMED]":
        # Success: Compile a new 'Skill'
        prompt = f"""
        Analyze this successful execution:
        Hypothesis: {hypothesis}
        Command: {command}
        Result: {result}
        
        Write a concise markdown 'Skill' document that explains this exact procedure
        so future agents can replicate it. Focus on the exact syntax and dependencies.
        """
        skill_content = llm_generate(prompt)
        write_to_disk("skills", hypothesis, skill_content)
        print("[SYSTEM] Background Reflection Complete. New Skill compiled.")

    elif outcome_state == "[INCONGRUITY ANOMALY]":
        # Failure: Compile a new 'Anti-Pattern Rule'
        prompt = f"""
        Analyze this failed execution:
        Hypothesis: {hypothesis}
        Command: {command}
        Result: {result}
        
        Write a concise markdown 'Rule' document warning future agents NOT to make 
        this specific mistake. Explain the root cause of the anomaly.
        """
        rule_content = llm_generate(prompt)
        write_to_disk("rules", hypothesis, rule_content)
        print("[SYSTEM] Background Reflection Complete. New Anti-Pattern Rule compiled.")

def write_to_disk(folder: str, topic: str, content: str):
    # Hashes topic to create a safe filename
    filename = hashlib.md5(topic.encode()).hexdigest()[:8] + ".md"
    os.makedirs(f".agents/{folder}", exist_ok=True)
    with open(f".agents/{folder}/{filename}", "w") as f:
        f.write(content)


# -----------------------------------------------------------------------------
# 2. THE DETERMINISTIC CONTEXT INJECTOR (RAG)
# -----------------------------------------------------------------------------

def vector_search(query: str, folder: str, top_k: int = 2) -> List[str]:
    """
    Conceptual vector search. Finds the most semantically relevant markdown files 
    based on the current user query.
    """
    # In reality, this would use ChromaDB, Pinecone, or a local embedding model.
    # We are simulating a search that returns file paths to relevant lessons.
    return [f".agents/{folder}/example_relevant_doc.md"]

def build_deterministic_prompt(user_query: str) -> str:
    """
    The orchestrator physically constructs the prompt just-in-time, bypassing 
    context dilution by only including highly relevant, verified historical data.
    """
    base_prompt = open("AGENTS.md").read()
    
    # Dynamically retrieve relevant anti-patterns (Rules)
    relevant_rules_paths = vector_search(user_query, "rules")
    injected_rules = "\n".join([open(path).read() for path in relevant_rules_paths if os.path.exists(path)])
    
    # Dynamically retrieve relevant procedures (Skills)
    relevant_skills_paths = vector_search(user_query, "skills")
    injected_skills = "\n".join([open(path).read() for path in relevant_skills_paths if os.path.exists(path)])

    final_payload = f"""
    {base_prompt}
    
    ## Relevant Historical Rules (Do NOT violate these):
    {injected_rules}
    
    ## Relevant Historical Skills (Use these procedures):
    {injected_skills}
    
    USER QUERY: {user_query}
    """
    return final_payload


# -----------------------------------------------------------------------------
# 3. THE ORCHESTRATOR LOOP (Execution)
# -----------------------------------------------------------------------------

def main_loop(user_query: str):
    # 1. Deterministically build the prompt (The LLM doesn't "remember", the DB does)
    context_payload = build_deterministic_prompt(user_query)
    
    # 2. LLM proposes hypothesis and execution
    agent_response = llm_generate(context_payload)
    
    # 3. Intercept Execution Block (Using the logic from orchestrator_concept.md)
    command = extract_execute_block(agent_response)
    
    if command:
        if not is_command_safe(command):
            # Human in the loop override logic here
            pass 
        
        # 4. Interact with physical reality
        result = subprocess.run(["powershell", "-Command", command], capture_output=True, text=True)
        outcome_state = "[CONFIRMED]" if result.returncode == 0 else "[INCONGRUITY ANOMALY]"
        
        # 5. ASYNC REFLECTION: Spawn background process to learn from the execution
        # This isolates the learning process from the execution state machine.
        spawn_reflection_agent(user_query, command, result.stdout, outcome_state)
        
        # 6. Continue execution loop...

# Dummy implementation for conceptual completeness
def llm_generate(prompt): return "Simulated Output"
def extract_execute_block(text): return "echo test"
def is_command_safe(command): return True
```

### The Architectural Benefits
1. **Zero Context Dilution**: The main LLM never has to keep 100 turns of trial-and-error in its head. The context window stays perfectly clean, containing only the `AGENTS.md` schema and the specific lessons related to the current task.
2. **Deterministic Governance**: The `spawn_reflection_agent` process is heavily sandboxed. It can read the execution logs, but it has zero access to the `subprocess` module. The execution boundary is strictly maintained by the Orchestrator.
3. **Auditability**: Every "lesson learned" by the system is written to disk as a plaintext markdown file. Engineers can review, edit, or delete `.agents/rules/` to manually correct the AI's learning.
