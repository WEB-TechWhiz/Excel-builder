import { createServerFn } from "@tanstack/react-start";
import { z } from "zod";
import { apiGet, apiPost } from "./api-client";

const columnSchema = z.object({ key: z.string().min(1), label: z.string().min(1), type: z.enum(["text", "number", "currency", "percent", "date"]) });
const kpiSchema = z.object({ label: z.string().min(1), aggregation: z.enum(["sum", "avg", "count", "min", "max"]), column: z.string() });
const sheetSchema = z.object({ id: z.string(), name: z.string().min(1).max(60), description: z.string().max(240).default(""), columns: z.array(columnSchema).max(30), rows: z.array(z.array(z.string().max(400))).max(2000), kpis: z.array(kpiSchema).max(6) });
export const productSchema = z.object({ name: z.string().min(1).max(80), version: z.string().min(1).max(20), author: z.string().max(80).default(""), currency: z.string().min(1).max(6), dateFormat: z.string().min(1).max(20), theme: z.enum(["premium", "midnight", "forest", "sunset"]), sheets: z.array(sheetSchema).min(1).max(20) });
export type ProductInput = z.infer<typeof productSchema>;

export const listProducts = createServerFn({ method: "GET" }).handler(() => apiGet("/api/v1/products"));
export const getProduct = createServerFn({ method: "GET" }).validator((data: unknown) => z.object({ id: z.string().uuid() }).parse(data)).handler(({ data }) => apiGet(`/api/v1/products/${data.id}`));
export const createProduct = createServerFn({ method: "POST" }).validator((data: unknown) => productSchema.parse(data)).handler(({ data }) => apiPost("/api/v1/products", data));
export const updateProduct = createServerFn({ method: "POST" }).validator((data: unknown) => z.object({ id: z.string().uuid(), product: productSchema }).parse(data)).handler(({ data }) => apiPost(`/api/v1/products/${data.id}`, data.product));
export const deleteProduct = createServerFn({ method: "POST" }).validator((data: unknown) => z.object({ id: z.string().uuid() }).parse(data)).handler(async ({ data }) => { await fetch(`${import.meta.env.VITE_API_URL || "http://localhost:8000"}/api/v1/products/${data.id}`, { method: "DELETE", headers: { "X-User-Id": import.meta.env.VITE_USER_ID || "local-user" } }); return { ok: true }; });
export const listBuilds = createServerFn({ method: "GET" }).handler(() => apiGet("/api/v1/builds"));
export const generateWorkbook = createServerFn({ method: "POST" }).validator((data: unknown) => z.object({ productId: z.string().uuid().nullable().default(null), product: productSchema }).parse(data)).handler(({ data }) => apiPost("/api/v1/workbooks/generate", { product_id: data.productId, product: data.product }));
