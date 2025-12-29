<!-- # AI + Human Development Process Diagram

This diagram models the current development workflow in this repository: epics → AI-optimized sprint planning → AI + human execution → code review & deployment → retrospective & knowledge capture. It highlights human roles, AI agent roles, artifacts, and escalation/quality gates.

Below is a Mermaid flowchart you can preview in editors that support Mermaid (VS Code Mermaid Preview, GitHub, Obsidian, etc.). -->

```mermaid
flowchart LR
  Epic["Epic\n(Strategic goals)"]
  SprintPlanning["Sprint Planning\n(PO + AI-optimized templates)"]
  SprintBacklog["Sprint Backlog\n(.foam/templates/sprint.md)"]
  Assign["Task Assignment\n(Assign to AI agents & humans)"]
  AIWork["AI Agents Execute\n(Frontend, Backend, UI/UX, Transformer, Env)"]
  HumanWork["Human Engineers\n(implement, review, escalate)"]
  CodeReview["Code Review Gate\n(Human oversight + AI checks)"]
  CI["CI / Deploy\n(automated tests & deployment)"]
  QA["QA / Human Validation\n(acceptance, manual tests)"]
  Retrospective["Retrospective & AI Learning\n(process improvements)"]
  DocsUpdate["Docs & Principles Update\n(knowledge capture)"]

  Epic --> SprintPlanning --> SprintBacklog --> Assign
  Assign --> AIWork
  Assign --> HumanWork
  AIWork --> CodeReview
  HumanWork --> CodeReview
  CodeReview -->|pass| CI --> QA --> Retrospective --> DocsUpdate --> Epic
  CodeReview -->|fail| HumanWork
  QA -->|blocker| HumanWork
  Retrospective --> SprintPlanning

  subgraph Humans
    PO["Product Owner / PM"]
    Eng["Engineer / Dev"]
    Reviewer["Reviewer / QA"]
    Lead["Lead / CTO"]
  end

  subgraph AIAgents
    Front["Frontend Agent"]
    Back["Backend Agent"]
    UIUX["UI/UX Agent"]
    Transformer["Transformer / LLM Agent"]
    Env["Environment Agent / Devops"]
  end

  SprintPlanning --- PO
  SprintPlanning --- Lead
  Assign --- Front
  Assign --- Back
  Assign --- UIUX
  Assign --- Transformer
  Assign --- Env
  AIWork --- Front
  AIWork --- Back
  AIWork --- UIUX
  AIWork --- Transformer
  AIWork --- Env
  HumanWork --- Eng
  CodeReview --- Reviewer
  DocsUpdate --- PO
  DocsUpdate --- Lead

  %% Decision & escalation annotations
  Assign -.->|"Human Escalation"| HumanWork
  CodeReview -.->|"Critical Decision"| Lead

  classDef ai fill:#eef6ff,stroke:#58a,stroke-width:1px
  classDef human fill:#fff8e6,stroke:#aa6,stroke-width:1px
  class AIAgents ai
  class Humans human

  %% Legend
  subgraph Legend["Legend"]
    L1["Yellow = Human roles"]
    L2["Blue = AI agents"]
    L3["Round arrows = feedback loops"]
  end
```

<!-- Notes and references
- Sprint timebox: 2–6 hours (see `nhaminhbach_knowledge/process/sprint_planning.md`).
- AI agent handoff patterns: `nhaminhbach_knowledge/process/ai_agent_briefing_guide.md`.
- Sprint templates & artifacts: `.foam/templates/sprint.md` and `nhaminhbach_knowledge/strategy/sprint/*`.
- Retrospective-driven process updates: see `nhaminhbach_knowledge/strategy/sprint_retrospective_s8.md`.

How to use
- Open this file in an editor supporting Mermaid to preview the diagram.
- If you want an export (SVG/PNG) or a PlantUML version, tell me which format and I will add it. -->

```mermaid
graph TD
    subgraph "Core Workflow"
        Human -- "Plan" --> Sprint
        Human -- "Define user story" --> Epic
        Human -- "Asign" --> Task
        AI -- "Complete" --> Task
        Task -- "State" --> AI
        Sprint -- "State" --> AI
        Epic -- "State" --> AI
        Human -- "Modify" --> CoreDocs["Core Documents"]
        Human -. "Chat" .-> AI["AI"]
    end

    subgraph "AI Operations & Improvement Loop"
        AI -- "Modify" --> CodeBase["Code Base"]
        AI -- "Self-improve" --> SystemInstruction["System Instruction"]
        SystemInstruction -- "Instruct" --> AI
        Improve --> AI
    end

    subgraph "Sprint Lifecycle"
        s_plan["Sprint plan"] --> s_impl["Implementation"]
        s_impl --> s_tasks["tasks"]
        s_tasks --> s_review["review"]
        s_review --> s_docs["docs"]
        s_docs --> s_plan
    end

    subgraph "Task Lifecycle"
        t_plan["task plan"] --> t_impl["Implementation"]
        t_impl --> t_code["Code (bug)"]
        t_code --> t_review["review"]
        t_review --> t_docs["docs"]
        t_docs --> t_plan
    end

    %% Cross-subgraph connections
    Sprint --> s_plan
    Task --> t_plan
    s_docs -- "Complete Sprint docs" --> Epic
    t_docs -- "Complete task docs" --> Task
    CodeBase -- "distill knowledge" --> Epic
```

