import { createFileRoute, Link } from "@tanstack/react-router";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useServerFn } from "@tanstack/react-start";
import { useEffect, useState } from "react";
import { ArrowLeft, Download, Plus, Save, Trash2 } from "lucide-react";
import { toast } from "sonner";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  CURRENCIES,
  DATE_FORMATS,
  THEMES,
  emptySheet,
  newId,
  type ColumnType,
  type ProductDef,
  type SheetDef,
  type ThemeName,
} from "@/lib/engine/types";
import { generateWorkbook, getProduct, updateProduct } from "@/lib/workbooks.functions";

export const Route = createFileRoute("/_authenticated/builder/$id")({
  head: () => ({
    meta: [
      { title: "Workbook builder — Excel Builder Studio" },
      {
        name: "description",
        content:
          "Design sheets, columns, data rows and KPI formulas, then generate the Excel workbook.",
      },
      { property: "og:title", content: "Workbook builder — Excel Builder Studio" },
      {
        property: "og:description",
        content: "Configure your spreadsheet product and export a styled .xlsx file.",
      },
    ],
  }),
  component: Builder,
});

const COLUMN_TYPES: ColumnType[] = ["text", "number", "currency", "percent", "date"];
const AGGREGATIONS = ["sum", "avg", "count", "min", "max"] as const;

function Builder() {
  const { id } = Route.useParams();
  const qc = useQueryClient();
  const fetchProduct = useServerFn(getProduct);
  const save = useServerFn(updateProduct);
  const generate = useServerFn(generateWorkbook);

  const query = useQuery({
    queryKey: ["product", id],
    queryFn: () => fetchProduct({ data: { id } }),
  });

  const [draft, setDraft] = useState<ProductDef | null>(null);
  const [activeSheet, setActiveSheet] = useState(0);

  useEffect(() => {
    const row = query.data;
    if (!row) return;
    setDraft({
      name: row.name,
      version: row.version,
      author: row.author,
      currency: row.currency,
      dateFormat: row.date_format,
      theme: row.theme as ThemeName,
      sheets: (row.sheets as unknown as SheetDef[]) ?? [],
    });
  }, [query.data]);

  const saveMutation = useMutation({
    mutationFn: (product: ProductDef) => save({ data: { id, product } }),
    onSuccess: () => {
      toast.success("Saved");
      qc.invalidateQueries({ queryKey: ["products"] });
    },
    onError: (e: Error) => toast.error(e.message),
  });

  const buildMutation = useMutation({
    mutationFn: (product: ProductDef) => generate({ data: { productId: id, product } }),
    onSuccess: (res) => {
      const bytes = Uint8Array.from(atob(res.base64), (c) => c.charCodeAt(0));
      const url = URL.createObjectURL(
        new Blob([bytes as unknown as BlobPart], {
          type: "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        }),
      );
      const a = document.createElement("a");
      a.href = url;
      a.download = res.fileName;
      a.click();
      URL.revokeObjectURL(url);
      toast.success(`Built ${res.fileName}`);
      qc.invalidateQueries({ queryKey: ["builds"] });
    },
    onError: (e: Error) => toast.error(e.message),
  });

  if (query.isLoading || !draft) {
    return <p className="mx-auto max-w-6xl px-6 py-12 text-sm text-muted-foreground">Loading…</p>;
  }

  const update = (patch: Partial<ProductDef>) => setDraft({ ...draft, ...patch });
  const updateSheet = (index: number, patch: Partial<SheetDef>) =>
    setDraft({
      ...draft,
      sheets: draft.sheets.map((s, i) => (i === index ? { ...s, ...patch } : s)),
    });

  const sheet = draft.sheets[activeSheet];

  return (
    <main className="mx-auto max-w-6xl px-6 py-8">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <Link
          to="/dashboard"
          className="inline-flex items-center gap-1.5 text-sm text-muted-foreground hover:text-foreground"
        >
          <ArrowLeft className="h-4 w-4" /> All products
        </Link>
        <div className="flex gap-2">
          <Button
            variant="outline"
            onClick={() => saveMutation.mutate(draft)}
            disabled={saveMutation.isPending}
          >
            <Save className="mr-1.5 h-4 w-4" /> Save
          </Button>
          <Button onClick={() => buildMutation.mutate(draft)} disabled={buildMutation.isPending}>
            <Download className="mr-1.5 h-4 w-4" />
            {buildMutation.isPending ? "Building…" : "Generate .xlsx"}
          </Button>
        </div>
      </div>

      <section className="panel mt-6 grid gap-4 p-6 md:grid-cols-3">
        <div className="space-y-2 md:col-span-2">
          <Label htmlFor="name">Product name</Label>
          <Input id="name" value={draft.name} onChange={(e) => update({ name: e.target.value })} />
        </div>
        <div className="space-y-2">
          <Label htmlFor="version">Version</Label>
          <Input
            id="version"
            value={draft.version}
            onChange={(e) => update({ version: e.target.value })}
          />
        </div>
        <div className="space-y-2">
          <Label htmlFor="author">Author</Label>
          <Input
            id="author"
            value={draft.author}
            onChange={(e) => update({ author: e.target.value })}
          />
        </div>
        <div className="space-y-2">
          <Label>Currency</Label>
          <Select value={draft.currency} onValueChange={(v) => update({ currency: v })}>
            <SelectTrigger>
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              {CURRENCIES.map((c) => (
                <SelectItem key={c} value={c}>
                  {c}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
        <div className="space-y-2">
          <Label>Date format</Label>
          <Select value={draft.dateFormat} onValueChange={(v) => update({ dateFormat: v })}>
            <SelectTrigger>
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              {DATE_FORMATS.map((d) => (
                <SelectItem key={d} value={d}>
                  {d}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
        <div className="space-y-2 md:col-span-3">
          <Label>Theme</Label>
          <div className="flex flex-wrap gap-2">
            {(Object.keys(THEMES) as ThemeName[]).map((t) => (
              <button
                key={t}
                onClick={() => update({ theme: t })}
                className={`flex items-center gap-2 rounded-lg border px-3 py-2 text-sm transition-colors ${
                  draft.theme === t ? "border-accent bg-secondary" : "border-border"
                }`}
              >
                <span
                  className="h-4 w-4 rounded"
                  style={{ background: `#${THEMES[t].accent.slice(2)}` }}
                />
                {THEMES[t].label}
              </button>
            ))}
          </div>
        </div>
      </section>

      <section className="mt-8">
        <div className="flex flex-wrap items-center gap-2">
          {draft.sheets.map((s, i) => (
            <button
              key={s.id}
              onClick={() => setActiveSheet(i)}
              className={`rounded-t-lg border-b-2 px-4 py-2 text-sm font-medium ${
                i === activeSheet
                  ? "border-accent text-foreground"
                  : "border-transparent text-muted-foreground"
              }`}
            >
              {s.name}
            </button>
          ))}
          <Button
            variant="ghost"
            size="sm"
            onClick={() => {
              setDraft({
                ...draft,
                sheets: [...draft.sheets, emptySheet(`Sheet ${draft.sheets.length + 1}`)],
              });
              setActiveSheet(draft.sheets.length);
            }}
          >
            <Plus className="mr-1 h-4 w-4" /> Add sheet
          </Button>
        </div>

        {sheet && (
          <div className="panel space-y-6 p-6">
            <div className="grid gap-4 md:grid-cols-3">
              <div className="space-y-2">
                <Label>Sheet name</Label>
                <Input
                  value={sheet.name}
                  onChange={(e) => updateSheet(activeSheet, { name: e.target.value })}
                />
              </div>
              <div className="space-y-2 md:col-span-2">
                <Label>Description</Label>
                <Textarea
                  rows={1}
                  value={sheet.description}
                  onChange={(e) => updateSheet(activeSheet, { description: e.target.value })}
                />
              </div>
            </div>

            {/* Columns */}
            <div>
              <div className="flex items-center justify-between">
                <h3 className="font-display text-sm font-semibold uppercase tracking-wide text-muted-foreground">
                  Columns
                </h3>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() =>
                    updateSheet(activeSheet, {
                      columns: [
                        ...sheet.columns,
                        { key: newId(), label: `Column ${sheet.columns.length + 1}`, type: "text" },
                      ],
                      rows: sheet.rows.map((r) => [...r, ""]),
                    })
                  }
                >
                  <Plus className="mr-1 h-4 w-4" /> Add column
                </Button>
              </div>
              <div className="mt-3 space-y-2">
                {sheet.columns.map((col, ci) => (
                  <div key={col.key} className="flex flex-wrap items-center gap-2">
                    <Input
                      className="max-w-56"
                      value={col.label}
                      onChange={(e) =>
                        updateSheet(activeSheet, {
                          columns: sheet.columns.map((c, i) =>
                            i === ci ? { ...c, label: e.target.value } : c,
                          ),
                        })
                      }
                    />
                    <Select
                      value={col.type}
                      onValueChange={(v) =>
                        updateSheet(activeSheet, {
                          columns: sheet.columns.map((c, i) =>
                            i === ci ? { ...c, type: v as ColumnType } : c,
                          ),
                        })
                      }
                    >
                      <SelectTrigger className="w-40">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        {COLUMN_TYPES.map((t) => (
                          <SelectItem key={t} value={t}>
                            {t}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                    <Button
                      variant="ghost"
                      size="icon"
                      aria-label={`Remove ${col.label}`}
                      onClick={() =>
                        updateSheet(activeSheet, {
                          columns: sheet.columns.filter((_, i) => i !== ci),
                          rows: sheet.rows.map((r) => r.filter((_, i) => i !== ci)),
                          kpis: sheet.kpis.filter((k) => k.column !== col.key),
                        })
                      }
                    >
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  </div>
                ))}
              </div>
            </div>

            {/* KPIs */}
            <div>
              <div className="flex items-center justify-between">
                <h3 className="font-display text-sm font-semibold uppercase tracking-wide text-muted-foreground">
                  KPI cards
                </h3>
                <Button
                  variant="ghost"
                  size="sm"
                  disabled={sheet.columns.length === 0 || sheet.kpis.length >= 6}
                  onClick={() =>
                    updateSheet(activeSheet, {
                      kpis: [
                        ...sheet.kpis,
                        {
                          label: "New KPI",
                          aggregation: "sum",
                          column: sheet.columns[0]!.key,
                        },
                      ],
                    })
                  }
                >
                  <Plus className="mr-1 h-4 w-4" /> Add KPI
                </Button>
              </div>
              <div className="mt-3 space-y-2">
                {sheet.kpis.map((kpi, ki) => (
                  <div key={ki} className="flex flex-wrap items-center gap-2">
                    <Input
                      className="max-w-56"
                      value={kpi.label}
                      onChange={(e) =>
                        updateSheet(activeSheet, {
                          kpis: sheet.kpis.map((k, i) =>
                            i === ki ? { ...k, label: e.target.value } : k,
                          ),
                        })
                      }
                    />
                    <Select
                      value={kpi.aggregation}
                      onValueChange={(v) =>
                        updateSheet(activeSheet, {
                          kpis: sheet.kpis.map((k, i) =>
                            i === ki
                              ? { ...k, aggregation: v as (typeof AGGREGATIONS)[number] }
                              : k,
                          ),
                        })
                      }
                    >
                      <SelectTrigger className="w-32">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        {AGGREGATIONS.map((a) => (
                          <SelectItem key={a} value={a}>
                            {a}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                    <Select
                      value={kpi.column}
                      onValueChange={(v) =>
                        updateSheet(activeSheet, {
                          kpis: sheet.kpis.map((k, i) => (i === ki ? { ...k, column: v } : k)),
                        })
                      }
                    >
                      <SelectTrigger className="w-44">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        {sheet.columns.map((c) => (
                          <SelectItem key={c.key} value={c.key}>
                            {c.label}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                    <Button
                      variant="ghost"
                      size="icon"
                      aria-label={`Remove ${kpi.label}`}
                      onClick={() =>
                        updateSheet(activeSheet, {
                          kpis: sheet.kpis.filter((_, i) => i !== ki),
                        })
                      }
                    >
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  </div>
                ))}
              </div>
            </div>

            {/* Data grid */}
            <div>
              <div className="flex items-center justify-between">
                <h3 className="font-display text-sm font-semibold uppercase tracking-wide text-muted-foreground">
                  Data
                </h3>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() =>
                    updateSheet(activeSheet, {
                      rows: [...sheet.rows, sheet.columns.map(() => "")],
                    })
                  }
                >
                  <Plus className="mr-1 h-4 w-4" /> Add row
                </Button>
              </div>
              <div className="mt-3 overflow-x-auto rounded-lg border border-border">
                <table className="w-full text-sm">
                  <thead className="bg-secondary">
                    <tr>
                      {sheet.columns.map((c) => (
                        <th key={c.key} className="px-3 py-2 text-left font-medium">
                          {c.label}
                        </th>
                      ))}
                      <th className="w-10" />
                    </tr>
                  </thead>
                  <tbody>
                    {sheet.rows.map((row, ri) => (
                      <tr key={ri} className="border-t border-border">
                        {sheet.columns.map((c, ci) => (
                          <td key={c.key} className="p-1">
                            <input
                              className="w-full rounded bg-transparent px-2 py-1 font-mono text-xs outline-none focus:bg-secondary"
                              value={row[ci] ?? ""}
                              onChange={(e) =>
                                updateSheet(activeSheet, {
                                  rows: sheet.rows.map((r, i) =>
                                    i === ri
                                      ? r.map((cell, j) => (j === ci ? e.target.value : cell))
                                      : r,
                                  ),
                                })
                              }
                            />
                          </td>
                        ))}
                        <td className="p-1">
                          <button
                            aria-label={`Delete row ${ri + 1}`}
                            className="text-muted-foreground hover:text-destructive"
                            onClick={() =>
                              updateSheet(activeSheet, {
                                rows: sheet.rows.filter((_, i) => i !== ri),
                              })
                            }
                          >
                            <Trash2 className="h-3.5 w-3.5" />
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
              {sheet.rows.length === 0 && (
                <p className="mt-2 text-xs text-muted-foreground">
                  No rows yet — KPI formulas activate once the sheet has data.
                </p>
              )}
            </div>

            {draft.sheets.length > 1 && (
              <Button
                variant="ghost"
                size="sm"
                className="text-destructive"
                onClick={() => {
                  setDraft({
                    ...draft,
                    sheets: draft.sheets.filter((_, i) => i !== activeSheet),
                  });
                  setActiveSheet(0);
                }}
              >
                <Trash2 className="mr-1 h-4 w-4" /> Delete this sheet
              </Button>
            )}
          </div>
        )}
      </section>
    </main>
  );
}
