# Required feature handoff

Owner preference recorded 5 November 2026: every implemented feature handoff must explain how to test it, not merely say tests pass.

Include when applicable:

- Where to execute commands: local Git Bash or EC2 shell.
- Whether commit/push/pull, image rebuild, service restart or browser refresh is required.
- Exact input/upload filename and its location; label synthetic versus actual provider data.
- Dataset dates, timezone, required settings and permission/qualification limits.
- Ordered test steps, expected visible/API/CLI outcomes and meaningful failure checks.
- What was verified by the agent versus what still requires owner/EC2 testing.

Never imply ignored local data files will arrive through git pull. Give the acquisition/transfer steps when the test needs such files on another machine. Do not substitute synthetic data while describing a real-data test.
