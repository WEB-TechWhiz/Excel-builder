import { createServerFn } from "@tanstack/react-start";
import { z } from "zod";

import { requireSupabaseAuth } from "@/integrations/supabase/auth-middleware";

const columnSchema = z.object({
  key: z.string().min(1),
  label: z.string().min(1),
  type: z.enum(["text", "number", "currency", "percent", "date"]),
});

const kpiSchema = z.object({
  label: z.string().min(1),
  aggregation: z.enum(["sum", "avg", "count", "min", "max"]),
  column: z.string(),
});

const sheetSchema = z.object({
  id: z.string(),
  name: z.string().min(1).max(60),
  description: z.string().max(240).default(""),
  columns: z.array(columnSchema).max(30),
  rows: z.array(z.array(z.string().max(400))).max(2000),
  kpis: z.array(kpiSchema).max(6),
});

export const productSchema = z.object({
  name: z.string().min(1).max(80),
  version: z.string().min(1).max(20),
  author: z.string().max(80).default(""),
  currency: z.string().min(1).max(6),
  dateFormat: z.string().min(1).max(20),
  theme: z.enum(["premium", "midnight", "forest", "sunset"]),
  sheets: z.array(sheetSchema).min(1).max(20),
});

export type ProductInput = z.infer<typeof productSchema>;

export const listProducts = createServerFn({ method: "GET" })
  .middleware([requireSupabaseAuth])
  .handler(async ({ context }) => {
    const { data, error } = await context.supabase
      .from("products")
      .select("*")
      .order("updated_at", { ascending: false });
    if (error) throw new Error(error.message);
    return data;
  });

export const getProduct = createServerFn({ method: "GET" })
  .middleware([requireSupabaseAuth])
  .inputValidator((data: unknown) => z.object({ id: z.string().uuid() }).parse(data))
  .handler(async ({ context, data }) => {
    const { data: row, error } = await context.supabase
      .from("products")
      .select("*")
      .eq("id", data.id)
      .maybeSingle();
    if (error) throw new Error(error.message);
    if (!row) throw new Error("Product not found");
    return row;
  });

export const createProduct = createServerFn({ method: "POST" })
  .middleware([requireSupabaseAuth])
  .inputValidator((data: unknown) => productSchema.parse(data))
  .handler(async ({ context, data }) => {
    const { data: row, error } = await context.supabase
      .from("products")
      .insert({
        user_id: context.userId,
        name: data.name,
        version: data.version,
        author: data.author,
        currency: data.currency,
        date_format: data.dateFormat,
        theme: data.theme,
        sheets: data.sheets,
      })
      .select()
      .single();
    if (error) throw new Error(error.message);
    return row;
  });

export const updateProduct = createServerFn({ method: "POST" })
  .middleware([requireSupabaseAuth])
  .inputValidator((data: unknown) =>
    z.object({ id: z.string().uuid(), product: productSchema }).parse(data),
  )
  .handler(async ({ context, data }) => {
    const p = data.product;
    const { data: row, error } = await context.supabase
      .from("products")
      .update({
        name: p.name,
        version: p.version,
        author: p.author,
        currency: p.currency,
        date_format: p.dateFormat,
        theme: p.theme,
        sheets: p.sheets,
      })
      .eq("id", data.id)
      .select()
      .single();
    if (error) throw new Error(error.message);
    return row;
  });

export const deleteProduct = createServerFn({ method: "POST" })
  .middleware([requireSupabaseAuth])
  .inputValidator((data: unknown) => z.object({ id: z.string().uuid() }).parse(data))
  .handler(async ({ context, data }) => {
    const { error } = await context.supabase.from("products").delete().eq("id", data.id);
    if (error) throw new Error(error.message);
    return { ok: true };
  });

export const listBuilds = createServerFn({ method: "GET" })
  .middleware([requireSupabaseAuth])
  .handler(async ({ context }) => {
    const { data, error } = await context.supabase
      .from("builds")
      .select("*")
      .order("created_at", { ascending: false })
      .limit(25);
    if (error) throw new Error(error.message);
    return data;
  });

export const generateWorkbook = createServerFn({ method: "POST" })
  .middleware([requireSupabaseAuth])
  .inputValidator((data: unknown) =>
    z
      .object({ productId: z.string().uuid().nullable().default(null), product: productSchema })
      .parse(data),
  )
  .handler(async ({ context, data }) => {
    const { buildWorkbook } = await import("./engine/build.server");
    const buffer = await buildWorkbook(data.product);
    const fileName = `${data.product.name.replace(/[^a-z0-9]+/gi, "-").toLowerCase()}-v${data.product.version}.xlsx`;
    const rowCount = data.product.sheets.reduce((sum, s) => sum + s.rows.length, 0);

    const { error } = await context.supabase.from("builds").insert({
      user_id: context.userId,
      product_id: data.productId,
      product_name: data.product.name,
      file_name: fileName,
      sheet_count: data.product.sheets.length,
      row_count: rowCount,
      byte_size: buffer.byteLength,
    });
    if (error) console.error("build log failed", error.message);

    return { fileName, base64: buffer.toString("base64"), bytes: buffer.byteLength };
  });
