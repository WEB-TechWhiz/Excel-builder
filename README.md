# 📊 Excel Product Engine & Builder Suite

[![Python Version](https://img.shields.io/badge/python-3.12%2B-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115%2B-009688.svg)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-19-61DAFB.svg)](https://react.dev/)
[![TanStack](https://img.shields.io/badge/TanStack-Start%20%2F%20Router-FF4154.svg)](https://tanstack.com/)
[![TailwindCSS](https://img.shields.io/badge/TailwindCSS-v4-38B2AC.svg)](https://tailwindcss.com/)
[![Supabase](https://img.shields.io/badge/Supabase-Auth%20%26%20Postgres-3ECF8E.svg)](https://supabase.com/)
[![OpenPyXL](https://img.shields.io/badge/OpenPyXL-3.1.5%2B-green.svg)](https://openpyxl.readthedocs.io/)
[![License](https://img.shields.io/badge/License-Proprietary-red.svg)](#)

A full-stack enterprise ecosystem for designing, managing, generating, and distributing production-grade Excel products (such as Financial OS, Business Dashboards, CRM, Sales Trackers, and Inventory Systems) from a declarative, reusable engine and an interactive visual web builder.

---

## 📑 Table of Contents

1. [Project Overview & Vision](#-project-overview--vision)
2. [Why Build This Platform? (Architectural Rationale)](#-why-build-this-platform-architectural-rationale)
3. [Full Project Directory Structure](#-full-project-directory-structure)
4. [Complete API Route Specification](#-complete-api-route-specification)
5. [Core Subsystems & Features](#-core-subsystems--features)
   - [1. Headless Python Excel Engine](#1-headless-python-excel-engine)
   - [2. Interactive Visual Web Builder (TanStack / React 19)](#2-interactive-visual-web-builder-tanstack--react-19)
   - [3. Supabase Auth & PostgreSQL Cloud Persistence](#3-supabase-auth--postgresql-cloud-persistence)
   - [4. AI / LLM Natural Language Bridge](#4-ai--llm-natural-language-bridge)
   - [5. CLI Build, Validation & Release Pipeline](#5-cli-build-validation--release-pipeline)
6. [Integrations Guide: What to Integrate & Why](#-integrations-guide-what-to-integrate--why)
7. [Environment Configuration & Variables](#-environment-configuration--variables)
8. [Getting Started (Step-by-Step Setup)](#-getting-started-step-by-step-setup)
9. [Database Schema (PostgreSQL / Supabase)](#-database-schema-postgresql--supabase)
10. [Testing, Quality Assurance & Build Commands](#-testing-quality-assurance--build-commands)

---

## 🌟 Project Overview & Vision

Spreadsheets run global commerce, yet creating professional, production-ready spreadsheet templates is historically painful, error-prone, unversioned, and inconsistent.

The **Excel Product Engine Suite** solves this by decoupling spreadsheet *mechanics* (formulas, theme styling, typography, column widths, KPI cards, charts, protection, validation) from *business domain content* (financial models, sales pipelines, inventory).

### Key Highlights
- **Declarative Schema-Driven Generation**: Define spreadsheets as JSON/YAML schemas; produce high-fidelity `.xlsx` files deterministically.
- **Visual Web Studio**: A modern web interface allowing users to visually build multi-sheet products, configure columns/types, add KPI cards, select themes, and export workbooks in real-time.
- **Enterprise Design System**: Automatic application of typography hierarchy, cell padding, number formatting, zebra striping, and curated palettes (`premium`, `midnight`, `forest`, `sunset`).
- **AI Prompt-to-Workbook Bridge**: Natural-language generation converting prompts into validated schema specifications and instant `.xlsx` workbooks using LLM intelligence.
- **Strict Verification Engine**: Pre-release formula parsing, circular reference detection, syntax checking, and test coverage before releasing to end users.

---

## 🎯 Why Build This Platform? (Architectural Rationale)

| The Traditional Way (Manual Excel) | The Excel Product Engine Way | Why It Matters |
| :--- | :--- | :--- |
| **Manual Formatting**: Hardcoding cell colors, fonts, and borders cell-by-cell. | **Centralized Design System**: `StyleManager` applies uniform themes dynamically. | Ensures brand consistency across 100+ sheets without human styling error. |
| **Silent Formula Errors**: Broken formula references (`#REF!`, `#VALUE!`) shipped unnoticed. | **Automated Formula Validator**: In-memory formula validation & recalculation engine. | 100% bug-free releases guaranteed before files reach customers. |
| **No Version Control**: Files saved as `Financial_Model_v2_final_FINAL.xlsx`. | **Git & Database Backed**: Declarative YAML/JSON models stored in PostgreSQL. | Full versioning, diffing, rollback, and team collaboration. |
| **Desktop-Only Workflow**: Requires desktop Excel installations and manual file sharing. | **Cloud-Enabled Web App + REST API**: Browser-based builder with FastAPI microservice. | Accessible anywhere, automatable via CI/CD and programmatic webhooks. |
| **Slow Prototyping**: Hours spent drafting grid structures and formulas from scratch. | **AI-Assisted Generation**: LLM converts user intent into a validated workbook in seconds. | Drastically speeds up product turnaround and client delivery. |

---

## 📁 Full Project Directory Structure

```text
excel-product-engine-complete/
│
├── README.md                               # Root project documentation (this file)
│
├── excel-product-engine/                   # 🐍 Python Core Engine & FastAPI Backend
│   ├── api.py                              # FastAPI REST API server (endpoints & asyncpg)
│   ├── pyproject.toml                      # Python build configuration & dependencies
│   ├── requirements.txt                    # Core production dependencies
│   ├── requirements-dev.txt                # Development & testing dependencies
│   ├── .env.example                        # Backend environment variable template
│   ├── CHANGELOG.md                        # Engine version history & completed milestones
│   │
│   ├── src/
│   │   └── excel_engine/                   # Core Reusable Engine Package
│   │       ├── __init__.py                 # Package exports
│   │       ├── logging_config.py           # Structured logging configuration
│   │       ├── core/                       # Low-level Excel workbook & sheet abstractions
│   │       │   ├── workbook.py             # ExcelWorkbook wrapper over openpyxl
│   │       │   ├── worksheet.py            # Worksheet manipulation & cell operations
│   │       │   ├── address.py              # CellAddress and CellRange coordinate math
│   │       │   └── metadata.py             # Workbook metadata (author, title, version)
│   │       ├── config/                     # Configuration and Pydantic schemas
│   │       │   ├── product_config.py       # Product YAML/JSON specification models
│   │       │   ├── settings.py             # Global engine runtime settings
│   │       │   └── theme_config.py         # Color palettes, fonts & theme definitions
│   │       ├── styles/                     # Visual design system
│   │       │   ├── style_manager.py        # Theme-to-openpyxl font/fill/border resolver
│   │       │   └── palettes.py             # Curated color tokens (premium, midnight, etc.)
│   │       ├── components/                 # Reusable layout & UI components
│   │       │   ├── banner.py               # Title banners and headers
│   │       │   ├── kpi_card.py             # Summary KPI metric display cards
│   │       │   ├── table.py                # Structured, formatted data tables
│   │       │   ├── navbar.py               # Cross-sheet navigation bars
│   │       │   └── progress_bar.py         # Visual cell-based progress indicators
│   │       ├── formulas/                   # Formula builder & syntax utilities
│   │       ├── charts/                     # Chart generation engine (bar, line, pie)
│   │       ├── data/                       # Data seeding, generators & formatters
│   │       ├── protection/                 # Sheet protection & locked cell rules
│   │       ├── validation/                 # Formula verification & integrity checks
│   │       ├── exporters/                  # PDF, XLSX, and CSV export handlers
│   │       ├── exceptions/                 # Custom typed exception hierarchy
│   │       └── llm/                        # Claude / Anthropic natural language bridge
│   │           ├── bridge.py               # Prompt -> WorkbookSpec generation
│   │           └── generate.py             # CLI entry point for LLM generation
│   │
│   ├── products/                           # 📦 Packaged Products built on the engine
│   │   ├── registry.py                     # Product catalog registry
│   │   └── financial_os/                   # Financial OS flagship product (9 sheets)
│   │       ├── product.py                  # Financial OS assembly pipeline
│   │       ├── config.yaml                 # Product metadata & structure config
│   │       └── sheets/                     # Individual sheet definitions (Dashboard, Net Worth, etc.)
│   │
│   ├── scripts/                            # 🛠️ Automation & Pipeline Scripts
│   │   ├── build.py                        # Build product workbooks from config
│   │   ├── validate.py                     # Standalone workbook integrity validator
│   │   └── release.py                      # Build, validate, and package releases to dist/
│   │
│   ├── tests/                              # Comprehensive test suite (260+ tests, 95% coverage)
│   │   ├── unit/                           # Unit tests for core engine modules
│   │   ├── integration/                    # Integration tests across components
│   │   └── product/                        # End-to-end product verification tests
│   │
│   └── dist/                               # Release artifacts and distribution bundles
│
└── excel-product-frontend/                 # ⚛️ Modern Web Application Frontend
    └── excel-builder-app/                  # TanStack Start / React 19 visual builder
        ├── package.json                    # Frontend dependencies & scripts
        ├── vite.config.ts                  # Vite + TanStack Start configuration
        ├── tsconfig.json                   # TypeScript compiler configuration
        ├── .env                            # Frontend environment variables
        ├── public/                         # Static web assets & icons
        │
        └── src/
            ├── router.tsx                  # TanStack Router instance & configuration
            ├── routeTree.gen.ts            # Auto-generated type-safe route tree
            ├── server.ts                   # TanStack Start server handler
            ├── styles.css                  # Tailwind CSS v4 & custom design tokens
            │
            ├── routes/                     # Application Page Routes
            │   ├── __root.tsx              # Root layout (Navbar, AuthProvider, Toaster)
            │   ├── index.tsx               # Marketing Landing & Feature showcase
            │   ├── auth.tsx                # Supabase Login & Registration page
            │   └── _authenticated/         # Protected User Routes (Auth Guards)
            │       ├── route.tsx           # Authenticated layout & session guard
            │       ├── dashboard.tsx       # User Products Dashboard & Build History
            │       └── builder.$id.tsx     # Visual Product Canvas & Sheet Editor
            │
            ├── components/                 # UI Component Library (Radix + Tailwind)
            │   ├── ui/                     # Button, Dialog, Card, Input, Tabs, Toast, etc.
            │   ├── builder/                # Visual Sheet Editor, Column Manager, KPI Builder
            │   └── preview/                # In-browser spreadsheet preview grid
            │
            ├── integrations/               # External service clients
            │   └── supabase/               # Supabase JS client & Auth state hooks
            │
            └── lib/                        # Utilities & API Clients
                ├── api-client.ts           # Typed HTTP client communicating with FastAPI backend
                ├── utils.ts                # Tailwind class mergers & string formatters
                └── workbooks.functions.ts  # Client-side ExcelJS generator & download helpers
```

---

## 🔌 Complete API Route Specification

The Python backend (`excel-product-engine/api.py`) runs a high-performance **FastAPI** service with native asynchronous PostgreSQL pooling (`asyncpg`).

**Base URL**: `http://localhost:8000`  
**Interactive Swagger Docs**: `http://localhost:8000/docs`  
**OpenAPI JSON Specification**: `http://localhost:8000/openapi.json`

### Authentication Headers
All protected `/api/v1/*` routes require user identification via either:
1. `X-User-Id: <user_unique_id>` (Used for frontend client session mapping)
2. `Authorization: Bearer <supabase_jwt_or_user_token>`

---

### Endpoint Summary Matrix

| Method | Endpoint | Auth | Purpose |
| :--- | :--- | :---: | :--- |
| `GET` | `/health` | No | Liveness probe (returns service status) |
| `GET` | `/ready` | No | Readiness probe (verifies PostgreSQL database connection) |
| `GET` | `/api/v1/products` | Yes | List all product specifications belonging to the authenticated user |
| `POST` | `/api/v1/products` | Yes | Create a new product specification (theme, sheets, columns, KPIs) |
| `GET` | `/api/v1/products/{product_id}` | Yes | Fetch a single product specification by its UUID |
| `PATCH` | `/api/v1/products/{product_id}` | Yes | Update an existing product specification |
| `DELETE` | `/api/v1/products/{product_id}` | Yes | Delete a product specification |
| `GET` | `/api/v1/builds` | Yes | List recent workbook build artifacts and history |
| `POST` | `/api/v1/workbooks/generate` | Yes | Generate a binary `.xlsx` spreadsheet and return Base64 payload |

---

### Detailed Endpoint Documentation

#### 1. Liveness Probe
```http
GET /health
```
**Response (200 OK):**
```json
{
  "status": "ok"
}
```

---

#### 2. Readiness Probe
```http
GET /ready
```
**Response (200 OK):**
```json
{
  "status": "ready"
}
```
*Note: Returns `503 Service Unavailable` if the PostgreSQL connection pool is unreachable.*

---

#### 3. List User Products
```http
GET /api/v1/products
Headers:
  X-User-Id: user_12345
```
**Response (200 OK):**
```json
[
  {
    "id": "7b06cb81-9b16-43e5-827d-9dc6e719543e",
    "user_id": "user_12345",
    "name": "SaaS Financial Model",
    "version": "1.0.0",
    "author": "Acme Corp",
    "currency": "USD",
    "dateFormat": "YYYY-MM-DD",
    "theme": "premium",
    "sheets": [
      {
        "id": "sheet_1",
        "name": "Revenue Summary",
        "description": "Monthly recurring revenue and growth metrics",
        "columns": [
          { "key": "month", "label": "Month", "type": "text" },
          { "key": "mrr", "label": "MRR", "type": "currency" },
          { "key": "growth", "label": "Growth Rate", "type": "percent" }
        ],
        "rows": [
          ["Jan 2026", "50000", "0.08"],
          ["Feb 2026", "54000", "0.08"]
        ],
        "kpis": [
          { "label": "Total MRR", "aggregation": "sum", "column": "mrr" }
        ]
      }
    ],
    "created_at": "2026-08-25T14:30:00Z",
    "updated_at": "2026-08-25T14:30:00Z"
  }
]
```

---

#### 4. Create Product Specification
```http
POST /api/v1/products
Headers:
  Content-Type: application/json
  X-User-Id: user_12345
```
**Request Body:**
```json
{
  "name": "Inventory Tracker",
  "version": "1.0.0",
  "author": "Operations Team",
  "currency": "USD",
  "dateFormat": "YYYY-MM-DD",
  "theme": "forest",
  "sheets": [
    {
      "id": "sheet_stock",
      "name": "Current Stock",
      "description": "Warehouse SKU inventory and reorder alerts",
      "columns": [
        { "key": "sku", "label": "SKU", "type": "text" },
        { "key": "quantity", "label": "Quantity in Stock", "type": "number" },
        { "key": "unit_cost", "label": "Unit Cost", "type": "currency" }
      ],
      "rows": [
        ["SKU-001", "150", "24.50"],
        ["SKU-002", "40", "110.00"]
      ],
      "kpis": [
        { "label": "Total Units", "aggregation": "sum", "column": "quantity" }
      ]
    }
  ]
}
```
**Response (201 Created):** Returns the newly created `ProductRecord` with server-generated `id`, `created_at`, and `updated_at`.

---

#### 5. Generate Binary `.xlsx` Workbook
```http
POST /api/v1/workbooks/generate
Headers:
  Content-Type: application/json
  X-User-Id: user_12345
```
**Request Body:**
```json
{
  "product_id": "7b06cb81-9b16-43e5-827d-9dc6e719543e",
  "product": {
    "name": "SaaS Financial Model",
    "version": "1.0.0",
    "author": "Acme Corp",
    "currency": "USD",
    "dateFormat": "YYYY-MM-DD",
    "theme": "premium",
    "sheets": [
      {
        "id": "sheet_1",
        "name": "Revenue Summary",
        "description": "Monthly recurring revenue",
        "columns": [
          { "key": "month", "label": "Month", "type": "text" },
          { "key": "mrr", "label": "MRR", "type": "currency" }
        ],
        "rows": [
          ["Jan 2026", "50000"]
        ],
        "kpis": []
      }
    ]
  }
}
```
**Response (200 OK):**
```json
{
  "file_name": "saas-financial-model-v1.0.0.xlsx",
  "base64": "UEsDBBQAAAAIAKx5... (Base64 encoded XLSX payload)",
  "bytes": 18452
}
```

---

#### 6. List Build History
```http
GET /api/v1/builds?limit=25
Headers:
  X-User-Id: user_12345
```
**Response (200 OK):**
```json
[
  {
    "id": "18c21345-d856-4fe4-9988-51f7bb9c2409",
    "product_id": "7b06cb81-9b16-43e5-827d-9dc6e719543e",
    "product_name": "SaaS Financial Model",
    "file_name": "saas-financial-model-v1.0.0.xlsx",
    "sheet_count": 1,
    "row_count": 1,
    "byte_size": 18452,
    "created_at": "2026-08-25T14:35:12Z"
  }
]
```

---

## 🏗️ Core Subsystems & Features

### 1. Headless Python Excel Engine
The engine (`src/excel_engine`) encapsulates all Excel logic into a clean object-oriented architecture:
- **Core Wrappers**: `ExcelWorkbook` and `Worksheet` wrap openpyxl to eliminate coordinate arithmetic errors and raw cell manipulation.
- **Design & Themes**: `StyleManager` maps semantic roles (Headers, KPI Values, Footers, Data Cells) to exact fonts, fills, and borders for themes (`premium`, `midnight`, `forest`, `sunset`).
- **Reusable Component Library**:
  - `add_title_banner`: Formatted title block with metadata subtitle.
  - `add_kpi_card`: Card metric with automatic formula linkage and format string.
  - `add_data_table`: Formatted data grid with zebra striping, custom column widths, and header styles.
  - `add_navbar`: Functional cross-sheet hyperlinks for seamless user navigation.

### 2. Interactive Visual Web Builder (TanStack / React 19)
The web client (`excel-product-frontend/excel-builder-app`) provides an intuitive visual studio:
- **Visual Sheet Configurator**: Add/remove sheets, reorder columns, configure data types (`text`, `number`, `currency`, `percent`, `date`).
- **KPI Card Configurator**: Define aggregated summary cards (`sum`, `avg`, `count`, `min`, `max`) that calculate automatically in Excel.
- **Dual Export Strategy**:
  - *Client-side*: Fast, instantaneous in-browser export using ExcelJS.
  - *Backend engine*: Full-fidelity compilation via FastAPI backend with rich openpyxl themes and formatting.

### 3. Supabase Auth & PostgreSQL Cloud Persistence
- Cloud persistence of product templates and generated build metadata.
- User management with email/password authentication and secure JWT validation.
- Row-Level Security (RLS) ensuring users only access their own product templates.

### 4. AI / LLM Natural Language Bridge
- Located in `src/excel_engine/llm`.
- Converts natural-language requests (e.g., *"Build an HR tracker tracking Employee Name, Department, Salary, and Start Date with department headcounts"*) into a strict `WorkbookSpec`.
- Validates the generated schema against Pydantic models before passing it to the deterministic build engine, ensuring zero hallucinations in generated formulas.

### 5. CLI Build, Validation & Release Pipeline
Located in `excel-product-engine/scripts/`:
- **`build.py`**: Compiles YAML/JSON product configs into `.xlsx` workbooks.
- **`validate.py`**: Verifies formula syntax, circular dependencies, and cell references.
- **`release.py`**: Automates full release packaging into `dist/` with documentation, licenses, and release notes.

---

## 🧩 Integrations Guide: What to Integrate & Why

When deploying and extending this project, integrate the following services:

### 1. Supabase (Authentication & Database)
- **Why**: Eliminates manual user management and database provisioning while providing instant Row-Level Security (RLS) and real-time synchronization.
- **What to Integrate**:
  - Connect `VITE_SUPABASE_URL` and `VITE_SUPABASE_PUBLISHABLE_KEY` in the frontend.
  - Configure `DATABASE_URL` in the FastAPI backend pointing to the Supabase PostgreSQL transaction pooler.

### 2. Anthropic Claude (Optional AI Bridge)
- **Why**: Enables non-technical users to generate complete multi-sheet spreadsheet products simply by typing plain-English prompts.
- **What to Integrate**: Set `ANTHROPIC_API_KEY` in `excel-product-engine/.env`.

### 3. FastAPI + Uvicorn (Microservice Backend)
- **Why**: Provides a high-throughput, asynchronous REST layer for cloud spreadsheet compilation, template CRUD, and CI/CD integration.
- **What to Integrate**: Expose port `8000` (or custom `$PORT`) with CORS configured to allow the frontend origin.

---

## ⚙️ Environment Configuration & Variables

### Backend Configuration (`excel-product-engine/.env`)

| Variable | Required | Default | Description |
| :--- | :---: | :---: | :--- |
| `DATABASE_URL` | Yes (for API) | `None` | PostgreSQL connection string (`postgresql://...`) |
| `PORT` | No | `8000` | HTTP port for FastAPI server |
| `CORS_ORIGINS` | No | `http://localhost:5173` | Comma-separated list of allowed frontend origins |
| `EXCEL_ENGINE_OUTPUT_DIR` | No | `output` | Directory for locally generated workbooks |
| `EXCEL_ENGINE_LOG_LEVEL` | No | `INFO` | Logging level (`DEBUG`, `INFO`, `WARNING`, `ERROR`) |
| `ANTHROPIC_API_KEY` | Optional | `None` | API key for natural-language workbook generation |
| `EXCEL_ENGINE_LLM_MODEL` | Optional | `claude-haiku-4-5-20251001` | LLM model identifier |

### Frontend Configuration (`excel-product-frontend/excel-builder-app/.env`)

| Variable | Required | Description |
| :--- | :---: | :--- |
| `VITE_SUPABASE_URL` | Yes | URL of your Supabase project instance |
| `VITE_SUPABASE_PUBLISHABLE_KEY` | Yes | Supabase anonymous / publishable public key |
| `VITE_API_URL` | Yes | URL pointing to the FastAPI backend (e.g. `http://localhost:8000`) |

---

## 🚀 Getting Started (Step-by-Step Setup)

### Prerequisites
- **Python 3.12+**
- **Node.js 20+** or **Bun**
- **PostgreSQL database** (Local or Supabase)

---

### Step 1: Backend Setup & Server Start

```bash
# 1. Navigate to backend directory
cd excel-product-engine

# 2. Create and activate a virtual environment
python -m venv .venv
# On Windows:
.venv\Scripts\activate
# On Linux/macOS:
# source .venv/bin/activate

# 3. Install dependencies in editable mode
pip install -e ".[dev,llm]"

# 4. Configure environment variables
cp .env.example .env
# Edit .env and set DATABASE_URL (or POSTGRES_URL)

# 5. Start the FastAPI development server
python api.py
# Server will start on http://localhost:8000
```

---

### Step 2: Frontend Setup & Web App Start

```bash
# 1. Open a new terminal and navigate to the frontend app
cd excel-product-frontend/excel-builder-app

# 2. Install Node dependencies
npm install

# 3. Start the Vite development server
npm run dev
# Frontend will start on http://localhost:5173
```

---

### Step 3: Generating Workbooks via CLI

You can also build products directly from the command line without the web UI:

```bash
cd excel-product-engine

# Build the flagship Financial OS product:
python scripts/build.py financial_os

# Validate any generated workbook:
python scripts/validate.py output/Financial_OS_v1.0.0.xlsx

# Package a full distribution release:
python scripts/release.py financial_os
```

---

## 🗄️ Database Schema (PostgreSQL / Supabase)

The backend auto-initializes the necessary database tables on startup. If configuring manually in Supabase SQL editor:

```sql
-- 1. Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 2. Products Table
CREATE TABLE IF NOT EXISTS products (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id TEXT NOT NULL,
    name TEXT NOT NULL,
    version TEXT NOT NULL,
    author TEXT NOT NULL DEFAULT '',
    currency TEXT NOT NULL,
    date_format TEXT NOT NULL,
    theme TEXT NOT NULL,
    sheets JSONB NOT NULL DEFAULT '[]'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Index for fast user queries ordered by update timestamp
CREATE INDEX IF NOT EXISTS products_user_updated_idx ON products (user_id, updated_at DESC);

-- 3. Builds History Table
CREATE TABLE IF NOT EXISTS builds (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id TEXT NOT NULL,
    product_id UUID REFERENCES products(id) ON DELETE SET NULL,
    product_name TEXT NOT NULL,
    file_name TEXT NOT NULL,
    sheet_count INT NOT NULL,
    row_count INT NOT NULL,
    byte_size INT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Index for fast build history retrieval
CREATE INDEX IF NOT EXISTS builds_user_created_idx ON builds (user_id, created_at DESC);
```

---

## 🧪 Testing, Quality Assurance & Build Commands

### Backend Engine Tests
```bash
cd excel-product-engine

# Run all test suites with coverage report:
pytest

# Run static type checking (strict mode):
mypy src/excel_engine

# Run code style and linting checks:
ruff check src products scripts tests
```

### Frontend Checks
```bash
cd excel-product-frontend/excel-builder-app

# Lint TypeScript and React code:
npm run lint

# Build production bundle:
npm run build
```

---

## 📄 License & Attribution

Proprietary Software — Developed by **MuffinCodes / TechWhiz**.  
All rights reserved. Unauthorized reproduction, modification, or distribution is prohibited.
