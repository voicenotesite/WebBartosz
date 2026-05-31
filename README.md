# Bartosz Web – Python Portfolio

![Python](https://img.shields.io/badge/python-3.12+-3776AB?style=flat-square&logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?style=flat-square&logo=fastapi)
![GraphQL](https://img.shields.io/badge/GraphQL-Strawberry-E10098?style=flat-square)
![GitHub Pages](https://img.shields.io/badge/GitHub%20Pages-✓-222?style=flat-square&logo=github)
![License](https://img.shields.io/badge/License-MIT-yellow?style=flat-square)

**Portfolio page for Python fullstack projects — live status monitor, project cards, GUI manager download.**

## Overview

A single-page portfolio site hosted on GitHub Pages. Shows all Python portfolio projects with live status monitoring via Cloudflare Tunnel health checks. Includes a GUI manager app for controlling backend services.

## Projects

| # | Project | Status | Tech |
|---|---------|--------|------|
| 1 | **URL Shortener** | ✅ Live | FastAPI + React + TailwindCSS |
| 2 | **GraphQL Blog** | ✅ Live | FastAPI + Strawberry + SQLAlchemy |
| 3 | **AI Chat Proxy** | ✅ Live | FastAPI + SSE + 5 Providers |
| 4 | **Async Task Queue** | ⬜ Coming | WebSocket + Redis |
| 5 | **RAG PDF Q&A** | ⬜ Coming | LangChain + ChromaDB |

## Features

- **Live status bar** — checks each project's `/health` endpoint every 30s
- **Project cards** — screenshots, tech tags, links to live demo + GitHub
- **GUI Manager** — one-click start/stop for backend + tunnel (`manager.py`)
- **Dark theme** — professional dark UI with gradient accents
- **Fully static** — zero server cost, hosted on GitHub Pages

## Structure

```
├── index.html      # Portfolio page (vanilla HTML + CSS + JS)
├── manager.py      # GUI app for controlling backend services
├── screenshots/    # Project screenshots
└── .git/
```

## Deploy

Push to `main` branch — GitHub Pages auto-deploys.

## License

MIT

## 🌐 Ecosystem

This project is part of the [Bartosz Web Portfolio](https://voicenotesite.github.io/WebBartosz/) ecosystem.
