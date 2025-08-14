# Process: Knowledge Capture & Distillation

## Philosophy
Our goal is to transform messy, real-time conversations into structured, timeless wisdom. We do not archive noise; we distill signals.

## Level 1: Real-time Scribing
- **Trigger:** During any lengthy or significant conversation with an agent.
- **Action:** User issues a `/summarize` command periodically.
- **Output:** A concise, bullet-point summary of the last few interactions. This serves as a checkpoint.

## Level 2: End-of-Task Synthesis
- **Trigger:** A Task is moved to `status: done`.
- **Action:** User activates `Librarian AI` with the `/capture` command, providing the conversation transcript (or summaries from Level 1).
- **Output:** A structured "Decision Chronicle" is generated inside the relevant Task file, following the `[[Template - Task Retrospective]]`.

## Level 3: DNA Update
- **Trigger:** Immediately after a Decision Chronicle is generated.
- **Action:** User prompts `Librarian AI` to analyze the "Core Principle" and "Flaw" sections.
- **Output:** A list of proposed changes (ADD/MODIFY) to relevant files in the `/knowledge/principles/` or `/knowledge/processes/` directories. These changes must be manually approved by the user.