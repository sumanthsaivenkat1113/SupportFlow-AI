# 🎧 SupportFlow AI

### AI-powered customer support automation for startups

Turn your company policies into a searchable knowledge base, resolve support tickets with **grounded RAG**, and automatically route what AI can't safely handle to your human team.

![SupportFlow AI Landing Page](./docs/images/landing-page.png)

[![Next.js](https://img.shields.io/badge/Next.js-App%20Router-black?logo=next.js)](https://nextjs.org)
[![React](https://img.shields.io/badge/React-UI-61DAFB?logo=react&logoColor=black)](https://react.dev)
[![TypeScript](https://img.shields.io/badge/TypeScript-Strict-3178C6?logo=typescript&logoColor=white)](https://www.typescriptlang.org)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind-CSS-38BDF8?logo=tailwindcss&logoColor=white)](https://tailwindcss.com)
[![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Python](https://img.shields.io/badge/Python-3.x-3776AB?logo=python&logoColor=white)](https://www.python.org)
[![SQLAlchemy](https://img.shields.io/badge/ORM-SQLAlchemy-D71F00?logo=sqlalchemy&logoColor=white)](https://www.sqlalchemy.org)
[![PostgreSQL](https://img.shields.io/badge/Database-PostgreSQL-4169E1?logo=postgresql&logoColor=white)](https://www.postgresql.org)
[![Clerk](https://img.shields.io/badge/Auth-Clerk-6C47FF?logo=clerk&logoColor=white)](https://clerk.com)
[![Groq](https://img.shields.io/badge/LLM-Groq-F55036)](https://groq.com)
[![Gemini](https://img.shields.io/badge/LLM-Gemini-8E75B2?logo=googlegemini&logoColor=white)](https://ai.google.dev)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?logo=docker&logoColor=white)](https://www.docker.com)
[![License](https://img.shields.io/badge/License-MIT-informational)](#-license)

[Features](#-features) •
[Architecture](#-system-architecture) •
[How It Works](#-how-it-works) •
[Tech Stack](#-tech-stack) •
[Getting Started](#-getting-started) •
[Author](#-author)

---

## 📖 Overview

**SupportFlow AI** is a **multi-tenant customer support automation platform**. Companies create isolated workspaces, upload internal policy documents, and upload customer tickets in JSON, Excel, or CSV. The platform builds a searchable knowledge base from those documents using embeddings, then uses **Retrieval-Augmented Generation (RAG)** to produce resolutions that are **grounded in the company's own policies** rather than the model's general knowledge.

Tickets that cannot be safely resolved are never forced through automation. They are separated into a **human-required** result set, so support teams keep full control over sensitive or ambiguous cases.

### 💡 Why it matters

| Problem | How SupportFlow AI solves it |
| --- | --- |
| Repetitive tickets consume support time | Automatically resolves tickets covered by company policy |
| LLMs hallucinate answers | Resolutions are grounded in retrieved policy chunks (Top-K = 3–5) |
| Tickets arrive in inconsistent formats | A normalization step converts JSON, Excel, and CSV into one schema |
| Automation can be risky | Low-confidence or unsupported tickets are routed to humans |
| Company data must stay separate | Workspace-based multi-tenancy isolates every organization's data |

---

## ✨ Features

- 🔐 **Authentication with Clerk**: only authenticated users can create and access workspaces.
- 🏢 **Multi-tenant workspaces**: policies, chunks, embeddings, tickets, and results are scoped per workspace.
- 📚 **Company knowledge base**: upload up to **5 policy PDFs**, extract text, chunk, embed, and store vectors.
- 🧩 **Three chunking strategies**
  - **Semantic Chunking** (default): keeps related information together.
  - **Structure-Aware Chunking**: respects headings, sections, paragraphs, and lists.
  - **Token-Based Chunking**: predictable chunk sizes for controlled context.
- 🎫 **Flexible ticket ingestion**: upload tickets as **JSON, Excel, or CSV**.
- 🧹 **AI-powered ticket normalization**: converts varied ticket structures into a consistent internal representation.
- 🤖 **RAG-based resolution**: vector search retrieves the **Top 3–5** relevant chunks to build the LLM context.
- 👤 **Human-in-the-loop routing**: tickets that can't be safely automated go to a separate human-required set.
- 📦 **Export results**: automated and human-required tickets download independently as **JSON, Excel, or CSV**.

---

## 🏗️ System Architecture

![SupportFlow AI Software Architecture](./docs/images/architecture.png)

SupportFlow AI is built around **two independent pipelines** that meet at retrieval time:

- **Knowledge Pipeline**: prepares company documents for search.
- **Ticket Pipeline**: processes customer tickets using that knowledge.

The Next.js frontend authenticates users through Clerk and communicates with a FastAPI backend. The backend persists application data in PostgreSQL, stores chunk embeddings in a vector database, and calls configurable LLM providers (Groq and Gemini) for generation.

---

## 🔄 How It Works

### 1. Knowledge Pipeline

```text
Company Policy PDFs → Text Extraction → Chunking → Embeddings → Vector DB
                                           │
                       Semantic (default) · Structure-Aware · Token-Based
```

Each embedding is linked to its workspace and source chunk, so retrieval never crosses tenant boundaries.

### 2. Ticket Pipeline

```text
Upload → Normalization → Resolution (RAG) → Export
```

| Stage | What happens |
| --- | --- |
| **Upload** | Tickets arrive as JSON, Excel, or CSV and are attached to the workspace |
| **Normalization** | Different formats are converted into one standard structure |
| **Resolution** | The ticket is embedded, the vector DB returns the Top 3–5 chunks, context is built, and the LLM generates a grounded resolution |
| **Export** | Results are split into automated and human-required files |

Example of a normalized ticket:

```json
{
  "ticket_id": "F1-1001",
  "description": "Customer forgot password and reset link is not working"
}
```

### 3. RAG Resolution Flow

```text
Normalized Ticket
      │
      ▼
 Vector Search ──► Top-K = 3–5 Chunks
                         │
                         ▼
        Ticket + Retrieved Knowledge + Resolution Prompt
                         │
                         ▼
                       LLM
                         │
             ┌───────────┴───────────┐
             ▼                       ▼
        Automated             Human-Required
```

### 4. Export

```text
automated_tickets       → JSON · Excel · CSV
human_required_tickets  → JSON · Excel · CSV
```

---

## 🛠️ Tech Stack

| Layer | Technologies |
| --- | --- |
| **Frontend** | Next.js (App Router), React, TypeScript, Tailwind CSS |
| **Authentication** | Clerk |
| **Backend** | Python, FastAPI, SQLAlchemy, Alembic |
| **Database** | PostgreSQL |
| **AI / LLM** | Groq, Gemini, configurable LLM models, embedding models |
| **RAG** | Semantic / structure-aware / token-based chunking, vector search, Top-K retrieval, context construction, grounded generation |
| **Data Processing** | PDF text extraction, JSON, Excel, CSV |
| **Tooling** | Docker Compose, uv, ESLint |

---

## 📁 Project Structure

```text
SupportFlow AI/
├── compose.yml               # Docker Compose (PostgreSQL, services)
├── docs/
│   └── images/               # README assets (screenshots, architecture diagram)
│       ├── landing-page.png
│       └── architecture.png
│
├── backend/
│   ├── alembic.ini
│   ├── migrations/           # Alembic migration history
│   ├── pyproject.toml
│   └── app/
│       ├── ai/               # LLM, embeddings, RAG logic
│       ├── api/              # FastAPI routes
│       ├── core/             # Configuration & security
│       ├── models/           # SQLAlchemy models
│       ├── schemas/          # Pydantic schemas
│       ├── services/         # Business logic
│       └── main.py
│
└── frontend/
    ├── app/                  # Next.js App Router (dashboard, workspaces)
    ├── client/               # API client
    ├── components/           # Reusable UI components
    ├── lib/                  # Utilities and helpers
    ├── public/               # Static assets served by Next.js
    └── types/                # Shared TypeScript types
```

---

## 🚀 Getting Started

### Prerequisites

- Node.js and npm
- Python 3.x and [uv](https://github.com/astral-sh/uv)
- PostgreSQL
- Docker / Docker Compose
- A [Clerk](https://clerk.com) account, plus Groq and Gemini API keys

### 1. Clone the repository

```bash
git clone <repository-url>
cd "SupportFlow AI"
```

### 2. Configure environment variables

> ⚠️ Never commit `.env` or `.env.local` files containing real secrets.

**Root `.env`**

```env
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=
CLERK_SECRET_KEY=
```

**`backend/.env`**

```env
DATABASE_URL=postgresql+psycopg://postgres:password@localhost:5433/supportflowai
CLERK_PUBLISHABLE_KEY=
CLERK_SECRET_KEY=
FRONTEND_URL=http://localhost:3000
GEMINI_API_KEY=
GROQ_API_KEY=
GROQ_MODEL=openai/gpt-oss-120b
LLM_MODEL=Qwen/Qwen3-8B:nscale
```

**`frontend/.env.local`**

```env
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=
CLERK_SECRET_KEY=
NEXT_PUBLIC_API_URL=http://localhost:8000
```

| Variable | Purpose |
| --- | --- |
| `DATABASE_URL` | PostgreSQL connection string |
| `CLERK_PUBLISHABLE_KEY` / `CLERK_SECRET_KEY` | Clerk authentication |
| `FRONTEND_URL` | Frontend origin used by the backend |
| `GEMINI_API_KEY` | Gemini API authentication |
| `GROQ_API_KEY` / `GROQ_MODEL` | Groq API key and model |
| `LLM_MODEL` | Configurable LLM model identifier |
| `NEXT_PUBLIC_API_URL` | Backend base URL for the frontend |

### 3. Start PostgreSQL

```bash
docker compose up -d
```

### 4. Run the backend

```bash
cd backend
uv sync
uv run alembic upgrade head
uv run uvicorn app.main:app --reload --port 8000
```

Backend: `http://localhost:8000`

### 5. Run the frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend: `http://localhost:3000`

### 🗄️ Database migrations

```bash
uv run alembic revision --autogenerate -m "migration message"   # create
uv run alembic upgrade head                                     # apply
uv run alembic downgrade -1                                     # rollback
```

---

## 🎯 Project Goals

- Make company knowledge searchable.
- Process tickets from multiple file formats.
- Normalize tickets into a consistent structure.
- Generate grounded AI resolutions using RAG.
- Keep tickets that need human judgment in a separate workflow.
- Provide structured JSON, Excel, and CSV exports.

---

## 🧠 Key Technical Challenges

| Challenge | Solution |
| --- | --- |
| **Preventing LLM hallucination** | Grounded every response in retrieved policy chunks (Top-K = 3–5) and routed unsupported tickets to humans instead of forcing an answer. |
| **Multi-tenant data isolation** | Scoped every chunk, embedding, ticket, and result to a `workspace_id` so retrieval can never cross tenant boundaries. |
| **Heterogeneous ticket formats** | Built an AI-powered normalization layer that maps JSON, Excel, and CSV inputs into a single canonical schema. |
| **Chunking quality vs. context size** | Implemented three chunking strategies (semantic, structure-aware, token-based) to balance retrieval precision against context window limits. |
| **Trustworthy automation** | Designed a confidence-aware router that only automates tickets the knowledge base can safely answer. |

---

## 🤝 Contributing

Contributions, issues, and feature requests are welcome.

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Commit your changes: `git commit -m "feat: add your feature"`
4. Push the branch: `git push origin feature/your-feature`
5. Open a pull request

---

## 📄 License

This project is licensed under the [MIT License](./LICENSE).

---

# 👨‍💻 Author

### **Sumanth Gunji**

Passionate about building **clean, scalable, and intelligent applications** that combine modern web technologies with AI to create meaningful user experiences.

[![GitHub](https://img.shields.io/badge/GitHub-Follow-181717?logo=github&logoColor=white)](https://github.com/your-username)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-Connect-0A66C2?logo=linkedin&logoColor=white)](https://linkedin.com/in/your-profile)
[![Email](https://img.shields.io/badge/Email-Contact-EA4335?logo=gmail&logoColor=white)](mailto:your-email@example.com)

---

<div align="center">

⭐ If you found this project interesting, consider giving it a star!

</div>