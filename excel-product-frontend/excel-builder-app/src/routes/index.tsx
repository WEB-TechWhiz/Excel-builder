import { createFileRoute, Link } from "@tanstack/react-router";
import { FileSpreadsheet, LayoutGrid, Sigma, Palette, Download } from "lucide-react";

export const Route = createFileRoute("/")({
  head: () => ({
    meta: [
      { title: "Excel Builder — Design and ship polished workbooks" },
      {
        name: "description",
        content:
          "Design themed Excel workbooks with KPI cards, live formulas, cover navigation and one-click .xlsx export.",
      },
      { property: "og:title", content: "Excel Builder — Design and ship polished workbooks" },
      {
        property: "og:description",
        content:
          "Blueprint sheets, columns and KPIs in the browser, then export a production-grade .xlsx file.",
      },
      { property: "og:type", content: "website" },
      { name: "twitter:card", content: "summary_large_image" },
    ],
  }),
  component: Landing,
});

const features = [
  {
    icon: LayoutGrid,
    title: "Sheet blueprints",
    body: "Define sheets, typed columns and rows once, then reuse them as reusable products.",
  },
  {
    icon: Sigma,
    title: "Live KPI formulas",
    body: "KPI cards compile to real SUM / AVERAGE / MIN / MAX formulas inside the workbook.",
  },
  {
    icon: Palette,
    title: "Four crafted themes",
    body: "Premium, Midnight, Forest and Sunset palettes applied to headers, bands and links.",
  },
  {
    icon: Download,
    title: "One-click export",
    body: "Server-side generation returns a formatted .xlsx with a hyperlinked cover sheet.",
  },
];

function Landing() {
  return (
    <div className="min-h-screen bg-background text-foreground">
      <header className="mx-auto flex max-w-6xl items-center justify-between px-6 py-6">
        <span className="flex items-center gap-2 font-semibold tracking-tight">
          <FileSpreadsheet className="h-5 w-5 text-primary" />
          Excel Builder
        </span>
        <Link
          to="/auth"
          className="rounded-md bg-primary px-4 py-2 text-sm font-medium text-primary-foreground transition-colors hover:bg-primary/90"
        >
          Sign in
        </Link>
      </header>

      <main>
        <section className="mx-auto max-w-6xl px-6 pb-20 pt-16 text-center">
          <p className="text-xs font-semibold uppercase tracking-[0.2em] text-muted-foreground">
            Workbook engine
          </p>
          <h1 className="mx-auto mt-4 max-w-3xl text-balance text-5xl font-semibold tracking-tight sm:text-6xl">
            Production-grade Excel, generated from a blueprint
          </h1>
          <p className="mx-auto mt-6 max-w-2xl text-lg text-muted-foreground">
            Model your data product in the browser — sheets, typed columns, KPI aggregations and a
            theme — and export a polished, formula-driven workbook in one click.
          </p>
          <div className="mt-10 flex flex-wrap justify-center gap-3">
            <Link
              to="/auth"
              className="rounded-md bg-primary px-6 py-3 text-sm font-medium text-primary-foreground transition-colors hover:bg-primary/90"
            >
              Start building
            </Link>
            <Link
              to="/dashboard"
              className="rounded-md border border-border px-6 py-3 text-sm font-medium transition-colors hover:bg-accent"
            >
              Open dashboard
            </Link>
          </div>
        </section>

        <section className="mx-auto max-w-6xl px-6 pb-24">
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
            {features.map((f) => (
              <article key={f.title} className="rounded-xl border border-border bg-card p-6">
                <f.icon className="h-5 w-5 text-primary" />
                <h2 className="mt-4 text-base font-semibold">{f.title}</h2>
                <p className="mt-2 text-sm text-muted-foreground">{f.body}</p>
              </article>
            ))}
          </div>
        </section>
      </main>

      <footer className="border-t border-border">
        <div className="mx-auto max-w-6xl px-6 py-8 text-sm text-muted-foreground">
          Excel Builder · themed workbook generation
        </div>
      </footer>
    </div>
  );
}
