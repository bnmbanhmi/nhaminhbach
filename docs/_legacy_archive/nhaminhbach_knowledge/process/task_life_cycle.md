# Task Lifecycle
#process

## AI-Optimized Task Management

The task lifecycle defines how individual work items progress from conception to completion in our AI-human collaborative workflow.

## Task Creation
- **Template:** Use `/template/task.md` AI-optimized template
- **Naming:** Descriptive `task_name.md` format (no ID numbers or dates)
- **Duration:** 30 minutes to 2 hours maximum for rapid iteration
- **Status:** Initial status set to `#ready`

## Task Progression

### 1. Planning Phase
- **Context Loading:** AI agents scan epic, sprint, and dependency files
- **Requirement Analysis:** Business goal translated to technical requirements
- **Dependency Check:** Previous task completion verified
- **Resource Allocation:** AI agent type and human oversight assigned

### 2. Execution Phase  
- **Status Update:** Changed to `#in-progress`
- **AI Agent Work:** Implementation following task instructions
- **Human Oversight:** Strategic decisions and validation
- **Progress Tracking:** Real-time updates in task file

### 3. Validation Phase
- **Testing:** Functional validation against success criteria
- **Code Review:** Technical quality assessment
- **Integration Testing:** End-to-end workflow verification
- **Documentation:** Implementation details and lessons learned

### 4. Completion Phase
- **Status Update:** Changed to `#complete`
- **Sprint Update:** Progress reflected in sprint dashboard
- **Knowledge Capture:** Retrospective and learning documentation
- **Handoff Preparation:** Context prepared for next task

## Dependencies & Sequencing
- **Previous Task References:** Each task links to its dependencies
- **Sprint Alignment:** Tasks align with sprint objectives and timelines  
- **Epic Coordination:** Task outcomes contribute to epic success criteria
- **Cross-Task Learning:** Lessons learned propagate to future tasks

## Quality Gates
- **Functional Validation:** All success criteria met with evidence
- **Technical Standards:** Code adheres to engineering principles
- **Documentation Standards:** Complete AI agent instructions and outcomes
- **Integration Compliance:** Changes integrate cleanly with existing system

## AI Agent Integration
- **Context Inheritance:** Tasks inherit sprint and epic context automatically
- **Instruction Optimization:** Task instructions optimized for AI understanding
- **Handoff Protocols:** Clear context transfer between human and AI work
- **Learning Loops:** Task outcomes improve future AI agent performance 