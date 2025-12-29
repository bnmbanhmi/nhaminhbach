---
tags: #task-ai
status: #ready
owner: [Human]
ai_agent: [Coding Agent]
epic: [[E2]]
sprint: [[250820_qc_cockpit_public_launch]]
estimated_duration: [2hr]
complexity: [Medium]
---

# AI Task: Deploy web frontend to custom domain

**Duration:** 2hr  
**Complexity:** Medium  
**AI Agent:** Coding Agent

## 🎯 Objective (AI Context)
**What:** Deploy the `packages/web` frontend to a custom domain the team owns and make it accessible publicly (HTTPS).  
**Why:** Provide stable public URL for the QC cockpit and public MVP.  
**Success:** The site is reachable at the provided custom domain over HTTPS and the domain is configured to point to the deployed hosting service.

## 🧠 AI Agent Instructions
**Context Files to Read:**
- `/packages/web/README.md` - hosting/build instructions
- `/firebase.json` - if Firebase Hosting is available
- `/cloudbuild.yaml` - CI/CD build steps

**Technical Requirements:**
- Use an existing hosting provider supported by the project (Firebase Hosting, Cloud Run with IAP, or static hosting on Cloud Storage + CDN)
- Configure DNS records for the custom domain (A/CNAME/ALIAS as required)
- Provision HTTPS certificate (automated via provider or using Let's Encrypt)
- Update project docs with domain and DNS instructions

**Integration Points:**
- Optional: Firebase Hosting if `firebase.json` present
- Optional: Cloud Run URL + Cloud Load Balancer if dynamic server required
- DNS provider control panel for domain records

## ✅ Acceptance Criteria (AI Verification)
- [ ] Custom domain resolves to the hosted frontend URL
- [ ] HTTPS is active and valid for the domain
- [ ] The frontend serves the QC cockpit pages correctly
- [ ] Documentation added to the repo with DNS steps and verification commands

## 🧾 AI Agent Preparation Checklist
**Before Starting:**
- [ ] Confirm which hosting provider we will use (recommend Firebase Hosting or Cloud Run + Load Balancer)
- [ ] Ensure the user can add DNS records for their domain or provide domain registrar access
- [ ] Verify `packages/web` builds correctly locally

**Implementation Approach:**
- [ ] Build `packages/web` and verify locally
- [ ] Choose hosting path: Firebase Hosting (simple static) or Cloud Run + LB (dynamic)
- [ ] Configure hosting and add custom domain binding
- [ ] Create documentation `docs/deploy_custom_domain.md` with DNS changes and verification steps
- [ ] Run smoke test against custom domain

## 📊 Progress Tracking
**Status:** Ready  
**Current Step:** None  
**Next Action:** Start the implementation after user confirms domain name and preferred hosting provider (or give access to DNS settings)

## 🔗 Context & Dependencies
**Depends On:** Domain ownership and ability to add DNS records  
**Enables:** Public access to QC cockpit and user testing  
**Reference:** Firebase Hosting docs, Cloud Run + HTTPS docs, Cloud Load Balancing docs

---
**Final Status:** [Complete/Partial] | **Quality:** [Production Ready/Needs Review/Prototype]
