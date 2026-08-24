export type ColumnType = "text" | "number" | "currency" | "percent" | "date";

export type Aggregation = "sum" | "avg" | "count" | "min" | "max";

export interface ColumnDef {
  key: string;
  label: string;
  type: ColumnType;
}

export interface KpiDef {
  label: string;
  aggregation: Aggregation;
  column: string;
}

export interface SheetDef {
  id: string;
  name: string;
  description: string;
  columns: ColumnDef[];
  rows: string[][];
  kpis: KpiDef[];
}

export interface ProductDef {
  name: string;
  version: string;
  author: string;
  currency: string;
  dateFormat: string;
  theme: ThemeName;
  sheets: SheetDef[];
}

export type ThemeName = "premium" | "midnight" | "forest" | "sunset";

export interface Theme {
  label: string;
  primary: string;
  accent: string;
  header: string;
  band: string;
  text: string;
}

export const THEMES: Record<ThemeName, Theme> = {
  premium: {
    label: "Premium",
    primary: "FF10241B",
    accent: "FF17B26A",
    header: "FF10241B",
    band: "FFEFF6F1",
    text: "FFFFFFFF",
  },
  midnight: {
    label: "Midnight",
    primary: "FF10192E",
    accent: "FF3B82F6",
    header: "FF10192E",
    band: "FFEEF3FC",
    text: "FFFFFFFF",
  },
  forest: {
    label: "Forest",
    primary: "FF1B3A2B",
    accent: "FF6BBF59",
    header: "FF1B3A2B",
    band: "FFF0F6EC",
    text: "FFFFFFFF",
  },
  sunset: {
    label: "Sunset",
    primary: "FF3A1E14",
    accent: "FFE8743B",
    header: "FF3A1E14",
    band: "FFFCF1EA",
    text: "FFFFFFFF",
  },
};

export const CURRENCIES = ["INR", "USD", "EUR", "GBP", "AUD", "JPY"] as const;
export const DATE_FORMATS = ["DD/MM/YYYY", "MM/DD/YYYY", "YYYY-MM-DD"] as const;

export const CURRENCY_SYMBOLS: Record<string, string> = {
  INR: "₹",
  USD: "$",
  EUR: "€",
  GBP: "£",
  AUD: "A$",
  JPY: "¥",
};

export function newId() {
  return Math.random().toString(36).slice(2, 10);
}

export function emptySheet(name = "Sheet 1"): SheetDef {
  return {
    id: newId(),
    name,
    description: "",
    columns: [
      { key: "date", label: "Date", type: "date" },
      { key: "item", label: "Item", type: "text" },
      { key: "amount", label: "Amount", type: "currency" },
    ],
    rows: [],
    kpis: [{ label: "Total Amount", aggregation: "sum", column: "amount" }],
  };
}

export interface TemplateDef {
  id: string;
  title: string;
  blurb: string;
  build: () => Omit<ProductDef, "author">;
}

export const TEMPLATES: TemplateDef[] = [
  {
    id: "financial-os",
    title: "Financial OS",
    blurb: "Income, expenses and net-worth tracking with rollup KPIs.",
    build: () => ({
      name: "Financial OS",
      version: "1.0.0",
      currency: "INR",
      dateFormat: "DD/MM/YYYY",
      theme: "premium",
      sheets: [
        {
          id: newId(),
          name: "Income",
          description: "All incoming money by source.",
          columns: [
            { key: "date", label: "Date", type: "date" },
            { key: "source", label: "Source", type: "text" },
            { key: "amount", label: "Amount", type: "currency" },
          ],
          rows: [
            ["2026-01-05", "Salary", "185000"],
            ["2026-01-18", "Freelance", "42000"],
            ["2026-02-05", "Salary", "185000"],
          ],
          kpis: [
            { label: "Total Income", aggregation: "sum", column: "amount" },
            { label: "Avg Inflow", aggregation: "avg", column: "amount" },
          ],
        },
        {
          id: newId(),
          name: "Expenses",
          description: "Spending by category.",
          columns: [
            { key: "date", label: "Date", type: "date" },
            { key: "category", label: "Category", type: "text" },
            { key: "amount", label: "Amount", type: "currency" },
          ],
          rows: [
            ["2026-01-08", "Rent", "48000"],
            ["2026-01-12", "Groceries", "12500"],
            ["2026-02-02", "Travel", "9800"],
          ],
          kpis: [
            { label: "Total Spend", aggregation: "sum", column: "amount" },
            { label: "Largest Expense", aggregation: "max", column: "amount" },
          ],
        },
        {
          id: newId(),
          name: "Investments",
          description: "Portfolio positions and current value.",
          columns: [
            { key: "asset", label: "Asset", type: "text" },
            { key: "units", label: "Units", type: "number" },
            { key: "value", label: "Current Value", type: "currency" },
          ],
          rows: [
            ["Index Fund", "120", "310000"],
            ["Gold ETF", "40", "88000"],
          ],
          kpis: [{ label: "Portfolio Value", aggregation: "sum", column: "value" }],
        },
      ],
    }),
  },
  {
    id: "sales-tracker",
    title: "Sales Tracker",
    blurb: "Pipeline rows, deal values and win-rate KPIs.",
    build: () => ({
      name: "Sales Tracker",
      version: "1.0.0",
      currency: "INR",
      dateFormat: "DD/MM/YYYY",
      theme: "midnight",
      sheets: [
        {
          id: newId(),
          name: "Pipeline",
          description: "Open and closed opportunities.",
          columns: [
            { key: "date", label: "Created", type: "date" },
            { key: "account", label: "Account", type: "text" },
            { key: "stage", label: "Stage", type: "text" },
            { key: "value", label: "Deal Value", type: "currency" },
            { key: "prob", label: "Probability", type: "percent" },
          ],
          rows: [
            ["2026-03-02", "Northwind", "Negotiation", "450000", "0.7"],
            ["2026-03-11", "Acme Corp", "Proposal", "280000", "0.4"],
            ["2026-04-01", "Globex", "Closed Won", "610000", "1"],
          ],
          kpis: [
            { label: "Pipeline Value", aggregation: "sum", column: "value" },
            { label: "Deals", aggregation: "count", column: "account" },
            { label: "Avg Deal Size", aggregation: "avg", column: "value" },
          ],
        },
      ],
    }),
  },
  {
    id: "inventory",
    title: "Inventory Manager",
    blurb: "Stock levels, reorder points and valuation.",
    build: () => ({
      name: "Inventory Manager",
      version: "1.0.0",
      currency: "USD",
      dateFormat: "YYYY-MM-DD",
      theme: "forest",
      sheets: [
        {
          id: newId(),
          name: "Stock",
          description: "Every SKU with quantity on hand.",
          columns: [
            { key: "sku", label: "SKU", type: "text" },
            { key: "name", label: "Product", type: "text" },
            { key: "qty", label: "Qty", type: "number" },
            { key: "cost", label: "Unit Cost", type: "currency" },
          ],
          rows: [
            ["SKU-001", "Desk Lamp", "120", "18.5"],
            ["SKU-002", "Monitor Arm", "45", "62"],
          ],
          kpis: [
            { label: "Units On Hand", aggregation: "sum", column: "qty" },
            { label: "SKUs", aggregation: "count", column: "sku" },
          ],
        },
      ],
    }),
  },
  {
    id: "blank",
    title: "Blank Product",
    blurb: "Start from an empty sheet and design it yourself.",
    build: () => ({
      name: "Untitled Product",
      version: "1.0.0",
      currency: "INR",
      dateFormat: "DD/MM/YYYY",
      theme: "premium",
      sheets: [emptySheet()],
    }),
  },
];
