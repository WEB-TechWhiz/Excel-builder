/**
 * build.server.ts
 *
 * Server-side workbook generation � delegates to the FastAPI Python backend
 * (excel-engine-api) which uses the excel-product-engine library.
 *
 * Previously this ran ExcelJS locally on the Node server. Now it is a thin
 * HTTP proxy so all theming, styling, and formula logic lives in Python.
 */

import type { ProductDef } from "./types";

const API_BASE =
  typeof process !== "undefined" && process.env.API_URL
    ? process.env.API_URL
    : "http://localhost:8000";

function getIdentity(): string {
  return (typeof import.meta !== "undefined" && import.meta.env?.VITE_USER_ID) || "local-user";
}

export async function buildWorkbook(
  product: ProductDef,
  productId?: string | null,
 ): Promise<Buffer> {
  const res = await fetch(`${API_BASE}/api/v1/workbooks/generate`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-User-Id": getIdentity(),
    },
    body: JSON.stringify({ product_id: productId ?? null, product }),
  });

  if (!res.ok) {
    const text = await res.text().catch(() => res.statusText);
    throw new Error(`Excel engine error ${res.status}: ${text}`);
  }

  const json = (await res.json()) as { base64: string; file_name: string; bytes: number };
  return Buffer.from(json.base64, "base64");
}
