# Agent Interaction Protocol
#process 

- **Activation:** Always begin a session with a specific goal by activating the relevant agent (`Activate: [Agent Name]`).
- **One Task, One Thread:** Keep the conversation focused on a single Task whenever possible to ensure clean capture later.
- **Summarize Frequently:** Use the `/summarize` command to create checkpoints and maintain context.
- **Explicit Commands:** Use clear commands (`/capture`, `/plan`, `/review`) to trigger specific agent workflows.