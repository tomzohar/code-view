# code-view — Vision

> **The code viewer for the agentic era of software development.**

## The problem

Software development has inverted. Developers used to spend most of their time *writing* code and a fraction *reading* it. With agentic tools — Claude Code, Codex, OpenCode, Gemini CLI, Aider — the ratio has flipped: the agent writes, the human **reads, judges, and steers**. Yet the terminal, where these agents live, has never had a first-class reading experience.

Today a developer supervising an agent session either:

1. Squints at raw `git diff` output scrolling past in the agent's transcript,
2. Alt-tabs to a full IDE just to *look* at what changed (heavyweight, breaks flow, often fights with the agent over file state), or
3. Stitches together `delta` + `lazygit` + `tig` + shell aliases into a fragile personal setup that still doesn't know anything about *agents*.

Reading code is now the bottleneck of the entire development loop. The tool that removes that bottleneck wins.

## The vision

**code-view** is an open-source, terminal-native code viewer that makes reading, reviewing, and reacting to code as fast as agents can write it.

You run `cv` in a pane next to your agent session. It shows your repository as a living thing: a navigable file tree, beautifully rendered code, and diffs that update **live** as the agent edits. When the agent finishes a turn, you don't ask "what did it do?" — you're already looking at it. You approve, annotate, or reject hunks with single keystrokes, and your structured feedback flows straight back into the agent's context.

The terminal is the agent's home. code-view makes it the human's home too.

## Mission

Give every developer supervising AI agents a state-of-the-art reading and review surface in the terminal — free, open source, and fast enough to keep up with machines.

## Product principles

1. **Reading is the product.** Every decision optimizes for comprehension speed: typography-grade rendering within terminal constraints, structural diffs, syntax awareness, minimal chrome.
2. **Live by default.** The repo is watched; the view is never stale. An agent edit appears in the viewer in under 100 ms. No refresh keystroke should ever be necessary.
3. **Keyboard-first, zero-config-first.** `cv` with no arguments does the right thing in any git repo. Every action is reachable without a mouse; defaults are excellent before any config file exists.
4. **The human stays in command.** code-view never edits code on its own. It observes, renders, and transmits *human* judgment (approvals, comments, rejections) to agents. Trust comes from being read-only over source and write-only over feedback.
5. **Agent-agnostic, agent-aware.** Works with any tool that changes files (that includes a plain `git pull`). Integrates deeply — hooks, structured feedback files, session awareness — with Claude Code, Codex, OpenCode, and whatever comes next, without ever *requiring* an agent.
6. **Composable citizen of the terminal.** Plays well with tmux/zellij/kitty splits, respects `$PAGER` conventions, pipes in and out, works over SSH. Disrupt the workflow, not the ecosystem.
7. **Fast is a feature, always.** Cold start under 50 ms, 60 fps scrolling on a 10k-line diff, graceful on a Raspberry Pi over SSH. Performance regressions are release blockers.

## Who it's for

- **The agent supervisor** — runs one or more Claude Code/Codex sessions daily and needs to review machine-generated changes continuously, not at PR time.
- **The terminal-native developer** — lives in tmux and neovim, refuses to open a browser or IDE to read a diff.
- **The multi-session operator** — runs parallel agents across worktrees and needs to know *which session changed which files* and whether the work drifted from the spec.
- **The open-source reviewer** — reviews external contributions and wants a faster local review loop than the GitHub web UI.

## North star & success metrics

**North star: time-to-judgment** — the elapsed time from "agent finished a change" to "human has understood it and issued a verdict." Everything we build should shrink it.

Supporting metrics: daily active reviewing sessions, median hunks reviewed per minute, % of reviews that produce structured feedback consumed by an agent, cold-start latency, GitHub stars/contributors as community proxies.

## What code-view is not

- Not an editor. Not an IDE. Not trying to become one.
- Not an agent, an orchestrator, or a session manager — it's the *review surface* those tools plug into.
- Not a git client. We render git's output brilliantly; we don't replace `git`, `lazygit`, or your merge tool (v1 has no commit/stage/push actions beyond feedback-driven quick actions).
- Not a SaaS. The core is local, offline, MIT-licensed, forever.

## One-line pitches

- For the README: *"A state-of-the-art code and diff viewer for your terminal — built for the age of AI coding agents."*
- For a colleague: *"It's the missing 'reading half' of Claude Code."*
- For Hacker News: *"Agents write code faster than you can read it. cv fixes the reading part."*
