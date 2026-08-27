# 📊 ExcelStudio Pro — Next.js Enterprise Full-Stack Suite

A unified Next.js 15+ (App Router, React 19, TypeScript, TailwindCSS v4, ExcelJS) full-stack application bringing together the entire declarative Excel Product Engine ecosystem.

---

## 🌟 Key Features

1. **Visual Spreadsheet Studio (`/studio/[id]`)**:
   - Multi-sheet tabbed management (Add, rename, delete, duplicate).
   - Column designer with types: `text`, `number`, `currency`, `percent`, `date`, `formula`.
   - Dynamic KPI Card builder with live formula aggregations (`SUM`, `AVG`, `COUNT`, `MIN`, `MAX`).
   - Interactive Data Grid with inline cell editing and live row deletion.
   - Dual View: Studio Grid Editor & Live In-Engine Theme Preview.

2. **Enterprise Excel Engine & Exporter (`lib/excel-engine.ts` & `/api/generate`)**:
   - Isomorphic ExcelJS compiler creating beautiful `.xlsx` workbooks.
   - Branded banner headers with timestamp badges.
   - 3-row KPI metric summary blocks with Excel formulas.
   - Formatted data tables with alternating zebra backgrounds, auto-fit column widths, and bottom total rows.

3. **Design System & Theme Palettes (`lib/palettes.ts`)**:
   - `Premium Sapphire` (Navy / Gold)
   - `Midnight Onyx` (Dark Slate / Cyan)
   - `Forest Emerald` (Emerald / Mint)
   - `Sunset Amber` (Amber / Rust)

4. **AI Prompt-to-Workbook Bridge (`/ai` & `/api/ai`)**:
   - Natural language prompt synthesis.
   - OpenAI integration + built-in fallback smart rule-based schema generator.

5. **Curated Template Showcase (`/templates`)**:
   - Financial OS (9-Sheet model)
   - SaaS Metrics & Unit Economics Cockpit
   - Sales CRM & Pipeline Tracker
   - Inventory Operations & Stock Valuation

---

## 🚀 Quick Start

### 1. Install Dependencies
```bash
npm install
```

### 2. Run Development Server
```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

### 3. Build for Production
```bash
npm run build
npm run start
```
