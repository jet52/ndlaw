# Changelog

Public releases of the North Dakota primary-law databases and the minimal MCP
server that serves them. Each release ships the validated database assets on the
[Releases](https://github.com/jet52/ndlaw/releases) page; the code in this
repository is the serve-only runtime and its deployment/auto-update tooling.

Per-release database corrections are summarized in the corresponding GitHub
Release notes. This repository does not carry the development-correction history.

## Unreleased — minimal public repository

First release of the minimal public repository: a clean, serve-only runtime and
deployment, distributed separately from the development pipeline. Ships the
validated corpus as release assets —

- **Opinions** (`opinions.db`): ~19,800 North Dakota Supreme Court and Court of
  Appeals opinions, 1889–present, with the bidirectional citation graph.
- **Primary law**: the North Dakota Constitution (point-in-time), N.D.C.C.
  statutes, court rules, and Administrative Code.
- **Attorney General opinions** (`ag_opinions.db`) and **Judicial Ethics
  Advisory Committee opinions** (`jeac_opinions.db`).
- **Reproduced figures** (`figures.db`).
