import { createFileRoute, Link, useNavigate } from "@tanstack/react-router";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useServerFn } from "@tanstack/react-start";
import { FileSpreadsheet, Plus, Trash2, Clock } from "lucide-react";
import { toast } from "sonner";

import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { TEMPLATES, THEMES, type ProductDef } from "@/lib/engine/types";
import { createProduct, deleteProduct, listBuilds, listProducts } from "@/lib/workbooks.functions";

export const Route = createFileRoute("/_authenticated/dashboard")({
  head: () => ({
    meta: [
      { title: "Your Excel products — Excel Builder Studio" },
      {
        name: "description",
        content:
          "Manage workbook blueprints, start from a template and review every generated Excel build.",
      },
      { property: "og:title", content: "Your Excel products — Excel Builder Studio" },
      {
        property: "og:description",
        content: "Blueprints, templates and generated workbook history in one place.",
      },
    ],
  }),
  component: Dashboard,
});

function Dashboard() {
  const navigate = useNavigate();
  const qc = useQueryClient();
  const fetchProducts = useServerFn(listProducts);
  const fetchBuilds = useServerFn(listBuilds);
  const create = useServerFn(createProduct);
  const remove = useServerFn(deleteProduct);

  const products = useQuery({ queryKey: ["products"], queryFn: () => fetchProducts() });
  const builds = useQuery({ queryKey: ["builds"], queryFn: () => fetchBuilds() });

  const createMutation = useMutation({
    mutationFn: (product: ProductDef) => create({ data: product }),
    onSuccess: (row) => {
      qc.invalidateQueries({ queryKey: ["products"] });
      navigate({ to: "/builder/$id", params: { id: row.id } });
    },
    onError: (e: Error) => toast.error(e.message),
  });

  const deleteMutation = useMutation({
    mutationFn: (id: string) => remove({ data: { id } }),
    onSuccess: () => {
      toast.success("Product deleted");
      qc.invalidateQueries({ queryKey: ["products"] });
    },
    onError: (e: Error) => toast.error(e.message),
  });

  return (
    <main className="mx-auto max-w-6xl px-6 py-10">
      <h1 className="font-display text-3xl font-semibold">Products</h1>
      <p className="mt-1 text-sm text-muted-foreground">
        Each product is a blueprint the engine turns into a styled, formula-wired workbook.
      </p>

      <section className="mt-8">
        <h2 className="text-sm font-semibold uppercase tracking-wide text-muted-foreground">
          Start from a template
        </h2>
        <div className="mt-3 grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
          {TEMPLATES.map((t) => (
            <button
              key={t.id}
              disabled={createMutation.isPending}
              onClick={() => createMutation.mutate({ ...t.build(), author: "" })}
              className="panel group p-4 text-left transition-shadow hover:shadow-lift"
            >
              <div className="flex items-center gap-2 font-display font-semibold">
                <Plus className="h-4 w-4 text-accent" />
                {t.title}
              </div>
              <p className="mt-2 text-xs text-muted-foreground">{t.blurb}</p>
            </button>
          ))}
        </div>
      </section>

      <section className="mt-12">
        <h2 className="text-sm font-semibold uppercase tracking-wide text-muted-foreground">
          Saved products
        </h2>
        {products.isLoading ? (
          <p className="mt-3 text-sm text-muted-foreground">Loading…</p>
        ) : products.data?.length ? (
          <div className="mt-3 grid gap-3 md:grid-cols-2">
            {products.data.map((p) => {
              const sheets = Array.isArray(p.sheets) ? p.sheets.length : 0;
              return (
                <div key={p.id} className="panel flex items-center justify-between gap-4 p-5">
                  <div className="min-w-0">
                    <Link
                      to="/builder/$id"
                      params={{ id: p.id }}
                      className="font-display text-lg font-semibold hover:underline"
                    >
                      {p.name}
                    </Link>
                    <div className="mt-2 flex flex-wrap gap-1.5">
                      <Badge variant="secondary">v{p.version}</Badge>
                      <Badge variant="secondary">{p.currency}</Badge>
                      <Badge variant="secondary">
                        {THEMES[p.theme as keyof typeof THEMES]?.label ?? p.theme}
                      </Badge>
                      <Badge variant="secondary">
                        {sheets} sheet{sheets === 1 ? "" : "s"}
                      </Badge>
                    </div>
                  </div>
                  <Button
                    variant="ghost"
                    size="icon"
                    aria-label={`Delete ${p.name}`}
                    onClick={() => deleteMutation.mutate(p.id)}
                  >
                    <Trash2 className="h-4 w-4" />
                  </Button>
                </div>
              );
            })}
          </div>
        ) : (
          <p className="mt-3 text-sm text-muted-foreground">
            No products yet — pick a template above.
          </p>
        )}
      </section>

      <section className="mt-12">
        <h2 className="flex items-center gap-2 text-sm font-semibold uppercase tracking-wide text-muted-foreground">
          <Clock className="h-4 w-4" /> Build history
        </h2>
        {builds.data?.length ? (
          <div className="panel mt-3 divide-y divide-border">
            {builds.data.map((b) => (
              <div key={b.id} className="flex items-center justify-between gap-4 px-5 py-3 text-sm">
                <span className="flex min-w-0 items-center gap-2">
                  <FileSpreadsheet className="h-4 w-4 shrink-0 text-accent" />
                  <span className="truncate font-mono text-xs">{b.file_name}</span>
                </span>
                <span className="shrink-0 text-xs text-muted-foreground">
                  {b.sheet_count} sheets · {b.row_count} rows · {Math.round(b.byte_size / 1024)} KB
                </span>
              </div>
            ))}
          </div>
        ) : (
          <p className="mt-3 text-sm text-muted-foreground">No workbooks generated yet.</p>
        )}
      </section>
    </main>
  );
}
