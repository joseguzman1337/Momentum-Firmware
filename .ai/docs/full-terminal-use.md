# Full Terminal Use

Full Terminal Use lets Warp's agent operate directly inside interactive terminal applications, such as database shells, debuggers, text editors, long-running servers, and more.

The agent can see the live terminal buffer (terminal state), write to the PTY to run commands, respond to prompts, and continue working inside the running process while you stay in control.

For full details and the latest updates, see:

- Warp docs: https://docs.warp.dev/agents/full-terminal-use

## Overview

With Full Terminal Use, Warp’s agent can attach to interactive tools like `psql`, `vim`, `python`, `gdb`, `top`, or your dev server, read the terminal output as it changes, and interact with the application as if you were typing.

You can either ask the agent to start an interactive program, or you can start it yourself and then tag the agent in once the tool is already running. In both cases, the agent sees the same terminal buffer (and PTY session) you do and can act on it.

## Key capabilities

- Start or join interactive commands (e.g. databases, debuggers, REPLs, dev servers).
- See the live terminal buffer and propose concrete terminal actions.
- Let you take over or hand back control at any time.
- Respect your approval settings (ask/always ask/always allow) for PTY writes.
- Honor Warp secret-redaction and privacy protections.

Refer to the online docs for detailed examples, screenshots, and workflows.