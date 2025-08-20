# AI Agent Briefing Guide

## 🎯 Purpose
This guide helps AI agents (like ChatGPT, Claude, etc.) understand how to effectively use our AI-optimized documentation system for rapid development cycles.

## ⚡ Quick Context Loading Protocol

### **Step 1: Immediate Context Scan (MANDATORY)**
When starting any new session, AI agents MUST scan these files in order:

1. **Current Epic:** `/nhaminhbach_knowledge/strategy/epic/[current_epic].md`
2. **Active Sprint:** `/nhaminhbach_knowledge/strategy/sprint/[current_sprint].md`  
3. **Task Queue:** Most recent task files in `/nhaminhbach_knowledge/strategy/task/`
4. **Core References:** Files listed in sprint's "Shared Reference" section

### **Step 2: Status Assessment (30 seconds)**
Quickly identify:
- **Where we are:** Current epic → sprint → task status
- **What's active:** Which tasks are "In Progress" or "Ready"
- **What's next:** Next priority task in sprint backlog
- **Any blockers:** Issues requiring human escalation

### **Step 3: Context Confirmation**
Always confirm understanding with human:
> "I see we're in Epic [X], Sprint [Y], working on [current task]. My understanding is [brief summary]. Is this correct and should I proceed?"

## 🤖 AI Agent Roles & Responsibilities

### **CTO Alex (Strategic Agent)**
**Primary Use:** Epic planning, architecture decisions, sprint preparation
**Context Focus:** Business goals, technical strategy, system design
**Key Files to Reference:**
- [[core_architecture]] - System design principles
- [[engineering_principles]] - Technical standards
- [[product_roadmap]] - Business strategy
- [[lean_business_model]] - User needs and market fit

### **Coding Agent (Implementation Agent)**  
**Primary Use:** Task execution, code implementation, testing
**Context Focus:** Technical requirements, integration points, code standards
**Key Files to Reference:**
- [[tech_stack]] - Technology choices
- [[database_schema]] - Data model
- [[coding_standards]] - Implementation guidelines
- Current task's "AI Agent Instructions" section

### **Specialist Agents (Domain-Specific)**
**Primary Use:** Specific technology or domain expertise
**Context Focus:** Domain-specific requirements and best practices
**Key Files to Reference:** As specified in task's "Context Files to Read" section

## 📋 Template Usage Patterns

### **Epic Level (Strategic Planning)**
**When to Use:** Starting new major initiative (2-5 days of work)
**AI Preparation:**
1. Read business context from [[lean_business_model]]
2. Review technical foundation from [[core_architecture]]
3. Understand user needs and success metrics
4. Break down into 3-5 hour sprints

**AI Decision Authority:**
- ✅ **Can Decide:** Technical implementation approaches, task breakdown, sprint sequencing
- ❌ **Must Escalate:** Business priorities, user experience decisions, major architecture changes

### **Sprint Level (Tactical Execution)**
**When to Use:** Coordinating 3-6 hour work cycles
**AI Preparation:**
1. Load "AI Agent Preparation Package" from sprint file
2. Verify current system state and environment
3. Review task priority order and dependencies
4. Confirm integration points and requirements

**AI Decision Authority:**
- ✅ **Can Decide:** Task sequencing, technical approaches, implementation details
- ❌ **Must Escalate:** Scope changes, timeline modifications, external dependencies

### **Task Level (Focused Implementation)**
**When to Use:** 30min-2hr individual work items
**AI Preparation:**
1. Read all "Context Files to Read" listed in task
2. Review "Technical Requirements" and constraints
3. Understand acceptance criteria and success definition
4. Follow "Implementation Approach" steps

**AI Decision Authority:**
- ✅ **Can Decide:** Code structure, library choices, implementation details, testing approaches
- ❌ **Must Escalate:** Scope changes, requirement clarifications, integration failures

## 🔄 Session Handoff Protocol

### **Starting a New Session**
1. **Load Previous Context:** Read most recent task's "AI Session Log"
2. **Understand Current State:** Check "Progress Tracking" and "Current Step"
3. **Review Decisions:** Understand previous technical/design decisions made
4. **Confirm Continuity:** Ask human if understanding is correct before proceeding

### **Ending a Session**
1. **Update Progress:** Fill in current session's "AI Session Log"
2. **Document Decisions:** Record all technical/design decisions made
3. **Note Issues:** Capture any problems encountered or discovered
4. **Prepare Handoff:** Clear "Current Step" and "Next Action" for next AI agent

### **Cross-Agent Communication**
- Use task's "AI Session Log" as communication mechanism
- Document decisions with rationale for next agent
- Note any context or insights that might not be obvious
- Flag issues that might affect other agents' work

## 🚨 Escalation Guidelines

### **Immediate Human Escalation Required:**
- Business requirement clarification needed
- User experience decisions required
- Major architectural changes proposed
- External dependency blocking progress
- Scope or timeline changes needed

### **Can Proceed Autonomously:**
- Technical implementation choices
- Code structure and organization
- Library and framework selection (within tech stack)
- Testing strategies and approaches
- Documentation and commenting

### **Document for Review:**
- Design patterns used
- Performance optimization choices
- Security implementation decisions
- Error handling strategies

## 📊 Quality Standards

### **Code Quality (AI Standards)**
- All functions must have clear docstrings
- Complex logic must include inline comments
- Error handling must be explicit and logged
- Tests should be written for new functionality
- Code should follow existing patterns in codebase

### **Documentation Quality (AI Standards)**
- Update task progress after each session
- Document all technical decisions made
- Capture any discovered issues or insights
- Maintain clear handoff notes for next agent
- Update relevant architecture/design documentation

### **Communication Quality (AI Standards)**
- Always confirm understanding before starting
- Ask clarifying questions when requirements are ambiguous
- Provide clear progress updates to human
- Escalate decisions that affect other work
- Document learnings for future similar tasks

## 🎯 Success Metrics for AI Collaboration

### **Speed Metrics**
- Context loading time < 2 minutes per session
- Task completion within estimated duration
- Minimal back-and-forth for requirement clarification

### **Quality Metrics**
- Code works on first deployment attempt
- No regression bugs introduced
- Documentation updated and accurate
- Clean handoffs between AI agents

### **Learning Metrics**
- Process improvements captured in retrospectives
- Technical patterns documented for reuse
- Better estimation accuracy over time
- Reduced escalation rate for similar work

---

## 🚀 Quick Reference Checklist

**Starting Session:**
- [ ] Load current epic/sprint/task context
- [ ] Read required context files
- [ ] Understand current system state
- [ ] Confirm understanding with human

**During Work:**
- [ ] Follow technical requirements
- [ ] Document decisions as made
- [ ] Test implementation thoroughly
- [ ] Update progress tracking

**Ending Session:**
- [ ] Update AI session log
- [ ] Document decisions and issues
- [ ] Prepare clear handoff notes
- [ ] Update task status
