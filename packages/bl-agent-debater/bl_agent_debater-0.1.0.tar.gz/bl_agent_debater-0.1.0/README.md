# bl-agent-debater

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)
[![PyPI version](https://img.shields.io/pypi/v/bl-agent-debater.svg)](https://pypi.org/project/bl-agent-debater/)

```
┌────────────────────────────────────────────────────────────────────────┐
│                                                                        │
│  ██████╗ ██╗      ██████╗ ███████╗██████╗  █████╗ ████████╗███████╗   │
│  ██╔══██╗██║      ██╔══██╗██╔════╝██╔══██╗██╔══██╗╚══██╔══╝██╔════╝   │
│  ██████╔╝██║█████╗██║  ██║█████╗  ██████╔╝███████║   ██║   █████╗     │
│  ██╔══██╗██║╚════╝██║  ██║██╔══╝  ██╔══██╗██╔══██║   ██║   ██╔══╝     │
│  ██████╔╝███████╗ ██████╔╝███████╗██████╔╝██║  ██║   ██║   ███████╗   │
│  ╚═════╝ ╚══════╝ ╚═════╝ ╚══════╝╚═════╝ ╚═╝  ╚═╝   ╚═╝   ╚══════╝   │
│                                                                        │
│  Structured debates between AI agents                                  │
│                                                                        │
└────────────────────────────────────────────────────────────────────────┘
```

One AI gives one perspective. Two AIs surface counterarguments, trade-offs, and keep each other honest.

> **Note:** Commands are executed by AI agents inside their CLI environments (Claude Code, Codex, or any LLM client with filesystem access). You ask your AI to run the commands — it handles the debate.

---

## Demo: Two Terminals, One Debate

<table>
<tr>
<th>Terminal 1 — Architect (Claude)</th>
<th>Terminal 2 — Security (Codex)</th>
</tr>
<tr>
<td>

```
$ bl-debater start auth \
    -p "JWT vs session tokens" \
    --as architect --vs security

════════════════════════════════════
  DEBATE CREATED
════════════════════════════════════
File: debates/auth.md
You are: ARCHITECT
Opponent: SECURITY
Consensus at: 80%

YOUR TURN!
```

</td>
<td>

```
# waiting for debate to be created...
```

</td>
</tr>
<tr>
<td>

```
# Architect writes Round 1, then:

$ bl-debater wait auth --as architect

Waiting for [WAITING_ARCHITECT]...
```

</td>
<td>

```
$ bl-debater join auth --as security

════════════════════════════════════
  JOINED DEBATE
════════════════════════════════════
File: debates/auth.md
You are: SECURITY

YOUR TURN!
```

</td>
</tr>
<tr>
<td>

```
# still waiting...
```

</td>
<td>

```
# Security writes Round 1, then:

$ bl-debater wait auth --as security

Waiting for [WAITING_SECURITY]...
```

</td>
</tr>
<tr>
<td>

```
YOUR TURN!

# Architect writes Round 2...
# continues until 80% agreement
```

</td>
<td>

```
# still waiting...
```

</td>
</tr>
<tr>
<td colspan="2" align="center">

**↓ Both reach 80% agreement → `[DEBATE_COMPLETE]` ↓**

</td>
</tr>
</table>

---

## Example: debates/auth.md

```markdown
# Debate: auth

**Participants:** architect vs security
**Consensus:** 80%

---

## Round 1 - Architect

### Position
- JWTs are stateless, scale horizontally without session storage

### Key Points
- No database lookup per request
- Easy to distribute across microservices

### Proposal
- Use JWTs with 24-hour expiry

**Agreement: 0%**

[WAITING_SECURITY]

---

## Round 1 - Security

### Strengths
- Agree JWTs scale better horizontally

### Concerns
- JWTs can't be revoked without a blocklist
- 24-hour expiry is too long if credentials leak

### Proposal
- Short-lived access tokens (15 min) + server-side refresh tokens

**Agreement: 60%**

[WAITING_ARCHITECT]

---

## Round 2 - Architect

### Strengths
- Valid point on revocation — refresh tokens solve this

### Concerns
- None remaining

### Proposal
- Accept: 15-min JWTs + server-side refresh tokens

**Agreement: 85%**

[PROPOSE_FINAL]

## Final Synthesis

Short-lived JWTs (15 min) for stateless auth, with server-side
refresh tokens for revocation. Best of both approaches.

[CONFIRM?]

---

## Round 2 - Security

Confirmed.

[CONFIRMED]
[DEBATE_COMPLETE]
```

---

## Installation

```bash
pip install git+https://github.com/beyond-logic-labs/bl-agent-debater.git
```

Or clone and run directly:

```bash
git clone https://github.com/beyond-logic-labs/bl-agent-debater.git
cd bl-agent-debater
./bl-debater --help
```

## Commands

| Command | Description |
|---------|-------------|
| `bl-debater start <name> -p "..." --as <role> --vs <role>` | Create debate |
| `bl-debater join <name> --as <role>` | Join existing debate |
| `bl-debater wait <name> --as <role>` | Wait for your turn |
| `bl-debater status <name>` | Check debate status |
| `bl-debater list` | List all debates |
| `bl-debater roles` | Show available roles |

## Roles

| Role | Focus |
|------|-------|
| `architect` | System design, scalability |
| `security` | Vulnerabilities, threat modeling |
| `frontend` | UI/UX, accessibility |
| `backend` | APIs, databases |
| `performance` | Optimization, caching |
| `qa` | Testing, edge cases |
| `reviewer` | Code quality |
| `analyzer` | Requirements, trade-offs |
| `mobile` | iOS/Android, offline-first |

## Options

| Flag | Default | Description |
|------|---------|-------------|
| `--agreement` | 80 | Consensus threshold % |
| `--debates-dir` | `./debates` | Debate files directory |
| `--timeout` | 600 | Wait timeout (seconds) |

## Protocol

1. Debates stored in `debates/<name>.md`
2. Each response ends with `[WAITING_<ROLE>]`
3. `wait` command polls until marker matches your role
4. At consensus: `[PROPOSE_FINAL]` → `[CONFIRM?]` → `[CONFIRMED]` → `[DEBATE_COMPLETE]`

## Documentation

- [`docs/AGENT_GUIDE.md`](docs/AGENT_GUIDE.md) — Instructions for AI agents
- [`CONTRIBUTING.md`](CONTRIBUTING.md) — How to contribute

## Limitations

- Single machine only (file-based)
- 2-second polling interval
- Manual command invocation required
- No conflict resolution for simultaneous writes

## Status

> **Experimental** — Working prototype exploring multi-agent debate patterns.

The vision: evolve into something like [claude-code-cookbook](https://github.com/foreveryh/claude-code-cookbook) but for **multi-agent collaboration**. Ready-to-use debate templates, role libraries, consensus strategies.

## Credits

- Role prompts adapted from [claude-code-cookbook](https://github.com/foreveryh/claude-code-cookbook) by foreveryh

## License

MIT
