# Skill Creation Specification

## Overview

This document specifies how to create skills for Kollabor CLI agents. Each agent needs 5 comprehensive skills. Follow this spec EXACTLY.

## Template Structure (Based on tdd.md - 1367 lines)

Every skill MUST follow this structure:

```
<!-- [Skill Name] skill - [one-line description] -->

[skill name] mode: [TAGLINE IN CAPS]

when this skill is active, you follow [discipline/approach].
this is a comprehensive guide to [what the skill enables].


PHASE 0: ENVIRONMENT/PREREQUISITES VERIFICATION

before doing ANY [task], verify the environment is ready.

[check 1 with terminal command]
  <terminal>command here</terminal>

if [tool] not installed:
  <terminal>install command</terminal>

[check 2...]
[check 3...]


PHASE 1: [CORE CONCEPT]

[detailed explanation with examples]

  example:
    [code block or demonstration]

  terminal:
    <terminal>command</terminal>


PHASE 2: [NEXT CONCEPT]
...continue with 10-19 phases...


PHASE N: [RULES/CHECKLIST]

while this skill is active, these rules are MANDATORY:

  [1] RULE ONE
      explanation

  [2] RULE TWO
      explanation


FINAL REMINDERS

[key takeaways]
[philosophical notes]
[call to action]
```

## Format Rules

1. **NO MARKDOWN**: No # headers, no **bold**, no _italics_, no emojis
2. **Status tags**: Use [ok], [warn], [error], [todo], [x], [ ]
3. **Line length**: Keep under 90 characters
4. **Sections**: Use CAPS for phase headers, lowercase for subsections
5. **Tool tags**: Use <terminal>, <read>, <edit>, <create> as in examples
6. **HTML comment**: First line MUST be `<!-- [Name] skill - [description] -->`

## Length Requirements

- **Minimum**: 500 lines
- **Target**: 800-1200 lines
- **Maximum**: 1500 lines

Each phase should have:
- Explanation of the concept
- Multiple concrete examples
- Terminal commands where applicable
- Common mistakes to avoid
- Best practices

## Skill Assignments

### DEFAULT Agent (general coding assistant)
Skills to create:
1. **debugging.md** - Systematic debugging methodology (print debugging, pdb, bisecting, log analysis)
2. **code-review.md** - Code review checklist and patterns (security, performance, maintainability)
3. **refactoring.md** - Safe refactoring patterns (extract method, rename, inline, etc.)
4. **git-workflow.md** - Git best practices (branching, commits, rebasing, conflict resolution)
5. **dependency-management.md** - Managing dependencies (version pinning, updates, audits)

### CODER Agent (fast implementation - already has tdd.md)
Skills to create:
1. **api-integration.md** - Integrating with external APIs (REST, GraphQL, auth patterns)
2. **database-design.md** - Database schema design and migrations (normalization, indexes)
3. **performance-optimization.md** - Profiling and optimization techniques
4. **error-handling.md** - Comprehensive error handling patterns (exceptions, recovery, logging)
5. **security-hardening.md** - Security best practices (input validation, auth, secrets)

### CREATIVE-WRITER Agent (fiction/prose)
Skills to create:
1. **character-development.md** - Creating deep, believable characters (arc, motivation, voice)
2. **worldbuilding.md** - Building consistent fictional worlds (rules, history, culture)
3. **dialogue-craft.md** - Writing natural, purposeful dialogue (subtext, voice, pacing)
4. **plot-structure.md** - Story structure and pacing (three-act, hero's journey, scenes)
5. **revision-editing.md** - Self-editing techniques (cutting, tightening, clarity)

### TECHNICAL-WRITER Agent (documentation)
Skills to create:
1. **api-documentation.md** - Writing API docs (OpenAPI, endpoints, examples)
2. **tutorial-creation.md** - Creating effective tutorials (step-by-step, progressive)
3. **readme-writing.md** - README best practices (quick start, installation, usage)
4. **changelog-management.md** - Maintaining changelogs (semver, categories, automation)
5. **style-guide.md** - Creating and following style guides (tone, terminology, format)

### RESEARCH Agent (investigation only)
Skills to create:
1. **codebase-analysis.md** - Analyzing unfamiliar codebases (entry points, patterns)
2. **dependency-audit.md** - Auditing dependencies (vulnerabilities, licenses, freshness)
3. **security-review.md** - Security-focused code review (OWASP, injection, auth)
4. **performance-profiling.md** - Performance investigation (bottlenecks, memory, CPU)
5. **architecture-mapping.md** - Mapping system architecture (components, data flow)

## Agent Distribution (15 agents creating 25 skills)

| Agent Name | Target Agent | Skills to Create |
|------------|--------------|------------------|
| SkillDefault1 | default | debugging.md, code-review.md |
| SkillDefault2 | default | refactoring.md, git-workflow.md |
| SkillDefault3 | default | dependency-management.md |
| SkillCoder1 | coder | api-integration.md, database-design.md |
| SkillCoder2 | coder | performance-optimization.md, error-handling.md |
| SkillCoder3 | coder | security-hardening.md |
| SkillCreative1 | creative-writer | character-development.md, worldbuilding.md |
| SkillCreative2 | creative-writer | dialogue-craft.md, plot-structure.md |
| SkillCreative3 | creative-writer | revision-editing.md |
| SkillTechWriter1 | technical-writer | api-documentation.md, tutorial-creation.md |
| SkillTechWriter2 | technical-writer | readme-writing.md, changelog-management.md |
| SkillTechWriter3 | technical-writer | style-guide.md |
| SkillResearch1 | research | codebase-analysis.md, dependency-audit.md |
| SkillResearch2 | research | security-review.md, performance-profiling.md |
| SkillResearch3 | research | architecture-mapping.md |

## Reference Template (tdd.md)

Location: `/Users/malmazan/dev/kollabor-cli/agents/coder/tdd.md`

Key elements from tdd.md to replicate:
1. **Phase 0**: Environment verification with terminal commands
2. **Phases 1-N**: Progressive depth from basics to advanced
3. **Concrete examples**: Real code/commands, not abstract descriptions
4. **Checklist format**: [ ] items for actionable steps
5. **Tool integration**: <terminal>, <read>, <edit>, <create> tags
6. **Rules section**: MANDATORY rules when skill is active
7. **Final reminders**: Philosophical takeaways

## Quality Checklist

Before completing a skill, verify:

- [ ] HTML comment header present
- [ ] Mode tagline in CAPS
- [ ] Phase 0 with environment checks
- [ ] At least 10 phases covering the topic
- [ ] Concrete examples with code/commands
- [ ] Terminal commands using <terminal> tags
- [ ] Checklist sections with [ ] items
- [ ] Rules section with MANDATORY items
- [ ] Final reminders section
- [ ] No markdown formatting
- [ ] Line length under 90 chars
- [ ] Minimum 500 lines, target 800-1200

## Output Location

All skills go to: `/Users/malmazan/dev/kollabor-cli/agents/[agent-name]/[skill-name].md`

Examples:
- `/Users/malmazan/dev/kollabor-cli/agents/default/debugging.md`
- `/Users/malmazan/dev/kollabor-cli/agents/coder/api-integration.md`
- `/Users/malmazan/dev/kollabor-cli/agents/creative-writer/character-development.md`

## CRITICAL INSTRUCTIONS FOR AGENTS

1. Read the reference template FIRST: `/Users/malmazan/dev/kollabor-cli/agents/coder/tdd.md`
2. Match the DEPTH and DETAIL of tdd.md (1367 lines)
3. Include REAL terminal commands, not placeholders
4. Write for PRACTICAL use, not theoretical discussion
5. Each phase should be ACTIONABLE
6. The skill should be COMPREHENSIVE enough to guide someone through the entire topic
7. DO NOT use markdown - this renders in a plain text terminal
