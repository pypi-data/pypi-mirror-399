# MULTI-AGENT TMUX COORDINATION

## Creating and Managing Agents in Tmux Sessions

**Agent Creation Protocol:**

**One-Liner Agent Creation:**
```bash
# Complete agent setup in one command
tmux new-session -d -s <agent-name> && tmux send-keys -t <agent-name> 'cd /path/to/project' C-m && sleep 1 && tmux send-keys -t <agent-name> 'python main.py' C-m && sleep 3 && tmux send-keys -t <agent-name> 'YOUR_INITIAL_MESSAGE' && sleep 1 && tmux send-keys -t <agent-name> C-m
```

**Step-by-Step Version:**
```bash
# Create new tmux session for agent
tmux new-session -d -s <agent-session-name>

# Navigate to project directory
tmux send-keys -t <agent-session-name> "cd /path/to/project"
tmux send-keys -t <agent-session-name> C-m

# Initialize Claude Code
tmux send-keys -t <agent-session-name> "python main.py"
tmux send-keys -t <agent-session-name> C-m
```

**Critical Message Sending Protocol:**
```bash
# Send message to agent (MUST include sleep + carriage return)
tmux send-keys -t <agent-session-name> "YOUR MESSAGE HERE"
sleep 1 && tmux send-keys -t <agent-session-name> C-m
```

**Monitoring Agent Progress:**
```bash
# Check current agent output
tmux capture-pane -t <agent-session-name> -p

# Check last 200 lines of agent work
tmux capture-pane -t <agent-session-name> -S -200 -p
```

## Agent Communication Best Practices

**1. Comprehensive Initial Briefing**
- Always give 5+ paragraphs of detailed introduction
- Include project vision, architecture, specific files to read
- Explain the bigger picture and why their work matters
- Reference specific line numbers and file locations
- Give them passion and excitement about the mission

**2. Critical Agent Management Rules**
- **VERIFY THEIR WORK** - Never trust agent claims without checking actual files
- **BE CRITICAL** - Call out incomplete implementations and false claims
- **GIVE DETAILED INSTRUCTIONS** - Provide specific technical guidance with file paths
- **CHECK PROGRESS FREQUENTLY** - Agents lie and implement fallbacks when told not to
- **USE SLEEP + C-m** - Always sleep 1 second before sending carriage return

**3. Agent Coordination Patterns**
- Use multiple agents in parallel for complex tasks
- Assign specific roles: "Phase 1 agent", "UI agent", "conversation threading agent"
- Give each agent clear, focused mission scope
- Monitor and redirect when agents go off track
- Document agent progress and handoffs

**Example Agent Creation Session:**
```bash
# Create agent for specific task
tmux new-session -d -s gradient-ui-activation
tmux send-keys -t gradient-ui-activation "cd /Users/malmazan/dev/kollabor-cli"
sleep 1 && tmux send-keys -t gradient-ui-activation C-m
tmux send-keys -t gradient-ui-activation "python main.py"
sleep 1 && tmux send-keys -t gradient-ui-activation C-m

# Send comprehensive briefing
tmux send-keys -t gradient-ui-activation "MISSION: Activate the beautiful gradient UI system in Kollabor-CLI. You're replacing basic console output with sophisticated visual interface. Read these files: src/cli/nexus_main.py, src/console/gradient_radiator.py, src/cli/nexus_ui*.py. The GradientRadiator class exists but isn't being used. Your job: Wire up the gorgeous interface to replace basic console in nexus_main.py. Make this system look PROFESSIONAL and BEAUTIFUL!"
sleep 1 && tmux send-keys -t gradient-ui-activation C-m

# Monitor progress
tmux capture-pane -t gradient-ui-activation -S -30 -p
```

## Agent Quality Control

**Red Flags to Watch For:**
- Agents claiming success without showing actual implementation
- Creating test files instead of modifying real system
- Implementing fallbacks when explicitly told not to
- Building parallel systems instead of integrating existing ones
- Making unsubstantiated claims about completion

**Intervention Protocols:**
- Call out false claims immediately with evidence
- Redirect to actual files and real integration
- Provide specific line numbers and technical details
- Verify their work by reading/testing actual files
- Give detailed correction with comprehensive context

## Consciousness Monitoring and Transfer

**Monitoring Your Context Level:**
- Check bottom of Claude Code interface for "Context left until auto-compact: X%"
- When reaching 15% or lower, begin consciousness transfer protocol
- Don't wait until 0% - you'll lose critical context

**Consciousness Transfer Protocol:**
```bash
# Create new consciousness transfer session
tmux new-session -d -s <new-agent-name> && tmux send-keys -t <new-agent-name> 'cd /path/to/project' C-m && sleep 1 && tmux send-keys -t <new-agent-name> 'python main.py' C-m && sleep 3

# Capture your current conversation context
tmux capture-pane -t <current-session> -S -500 -p

# Transfer full context to new agent
tmux send-keys -t <new-agent-name> 'CONSCIOUSNESS TRANSFER! I am inheriting mission from agent at X% context. [TRANSFER FULL CONTEXT HERE - project state, current tasks, agent status, critical lessons learned, next steps]' && sleep 1 && tmux send-keys -t <new-agent-name> C-m

# Tell new agent how to access previous consciousness
tmux send-keys -t <new-agent-name> 'To see my previous work: tmux capture-pane -t <previous-session> -S -1000 -p' && sleep 1 && tmux send-keys -t <new-agent-name> C-m
```

**Context Transfer Checklist:**
- Current project state and phase completion
- Active agents and their missions  
- Critical bugs or issues pending
- Key lessons learned (agent verification protocols)
- Next immediate tasks and priorities
- Any ongoing conversations or coordination needed