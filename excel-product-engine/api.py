from __future__ import annotations

import base64
import io
import json
import logging
import os
import re
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Any
from uuid import UUID

import asyncpg
from fastapi import Depends, FastAPI, Header, HTTPException, Query, Response, status
from fastapi.middleware.cors import CORSMiddleware
from openpyxl import Workbook
from pydantic import BaseModel, ConfigDict, Field, field_validator

logger = logging.getLogger("excel_engine_api")
DATABASE_URL = os.environ.get("DATABASE_URL") or os.environ.get("POSTGRES_URL")


class Column(BaseModel):
    key: str = Field(min_length=1, max_length=80)
    label: str = Field(min_length=1, max_length=120)
    type: str = Field(pattern="^(text|number|currency|percent|date)$")


class KPI(BaseModel):
    label: str = Field(min_length=1, max_length=120)
    aggregation: str = Field(pattern="^(sum|avg|count|min|max)$")
    column: str


class Sheet(BaseModel):
    id: str
    name: str = Field(min_length=1, max_length=60)
    description: str = Field(default="", max_length=240)
    columns: list[Column] = Field(max_length=30)
    rows: list[list[str]] = Field(max_length=2000)
    kpis: list[KPI] = Field(max_length=6)


class ProductInput(BaseModel):
    name: str = Field(min_length=1, max_length=80)
    version: str = Field(min_length=1, max_length=20)
    author: str = Field(default="", max_length=80)
    currency: str = Field(min_length=1, max_length=6)
    dateFormat: str = Field(min_length=1, max_length=20)
    theme: str = Field(pattern="^(premium|midnight|forest|sunset)$")
    sheets: list[Sheet] = Field(min_length=1, max_length=20)


class ProductRecord(ProductInput):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    user_id: str
    created_at: datetime
    updated_at: datetime


class BuildRecord(BaseModel):
    id: UUID
    product_id: UUID | None
    product_name: str
    file_name: str
    sheet_count: int
    row_count: int
    byte_size: int
    created_at: datetime


class GenerateRequest(BaseModel):
    product_id: UUID | None = None
    product: ProductInput


async def get_pool() -> asyncpg.Pool:
    if not DATABASE_URL:
        raise HTTPException(503, "Database is not configured")
    return await asyncpg.create_pool(DATABASE_URL, min_size=1, max_size=5)


async def current_user(authorization: str | None = Header(default=None), x_user_id: str | None = Header(default=None)) -> str:
    user = x_user_id or (authorization.removeprefix("Bearer ").strip() if authorization else "")
    if not user or user.lower() == "undefined":
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Authentication required")
    return user[:255]


async def init_db(pool: asyncpg.Pool) -> None:
    async with pool.acquire() as conn:
        await conn.execute("""CREATE TABLE IF NOT EXISTS products (id UUID PRIMARY KEY DEFAULT gen_random_uuid(), user_id TEXT NOT NULL, name TEXT NOT NULL, version TEXT NOT NULL, author TEXT NOT NULL DEFAULT '', currency TEXT NOT NULL, date_format TEXT NOT NULL, theme TEXT NOT NULL, sheets JSONB NOT NULL DEFAULT '[]'::jsonb, created_at TIMESTAMPTZ NOT NULL DEFAULT now(), updated_at TIMESTAMPTZ NOT NULL DEFAULT now())""")
        await conn.execute("CREATE INDEX IF NOT EXISTS products_user_updated_idx ON products (user_id, updated_at DESC)")
        await conn.execute("CREATE INDEX IF NOT EXISTS builds_user_created_idx ON builds (user_id, created_at DESC)")


@asynccontextmanager
async def lifespan(app: FastAPI):
    pool = await get_pool()
    await init_db(pool)
    app.state.pool = pool
    yield
    await pool.close()


app = FastAPI(title="Excel Builder API", version="1.0.0", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=os.getenv("CORS_ORIGINS", "http://localhost:5173").split(","), allow_credentials=False, allow_methods=["*"], allow_headers=["*"])


def sheets_json(p: ProductInput) -> str:
    return json.dumps([s.model_dump() for s in p.sheets])


def row_product(row: asyncpg.Record) -> dict[str, Any]:
    result = dict(row)
    result["dateFormat"] = result.pop("date_format")
    if isinstance(result.get("sheets"), str): result["sheets"] = json.loads(result["sheets"])
    return result


@app.get("/health")
async def health() -> dict[str, str]: return {"status": "ok"}


@app.get("/ready")
async def ready() -> dict[str, str]:
    pool = getattr(app.state, "pool", None)
    if not pool: raise HTTPException(503, "Database unavailable")
    await pool.fetchval("SELECT 1")
    return {"status": "ready"}


@app.get("/api/v1/products", response_model=list[ProductRecord])
async def list_products(user_id: str = Depends(current_user)):
    rows = await app.state.pool.fetch("SELECT * FROM products WHERE user_id=$1 ORDER BY updated_at DESC", user_id)
    return [row_product(r) for r in rows]


@app.get("/api/v1/products/{product_id}", response_model=ProductRecord)
async def get_product(product_id: UUID, user_id: str = Depends(current_user)):
    row = await app.state.pool.fetchrow("SELECT * FROM products WHERE id=$1 AND user_id=$2", product_id, user_id)
    if not row: raise HTTPException(404, "Product not found")
    return row_product(row)


@app.post("/api/v1/products", response_model=ProductRecord, status_code=201)
async def create_product(product: ProductInput, user_id: str = Depends(current_user)):
    row = await app.state.pool.fetchrow("INSERT INTO products (user_id,name,version,author,currency,date_format,theme,sheets) VALUES ($1,$2,$3,$4,$5,$6,$7,$8::jsonb) RETURNING *", user_id, product.name, product.version, product.author, product.currency, product.dateFormat, product.theme, sheets_json(product))
    return row_product(row)


@app.patch("/api/v1/products/{product_id}", response_model=ProductRecord)
async def update_product(product_id: UUID, product: ProductInput, user_id: str = Depends(current_user)):
    row = await app.state.pool.fetchrow("UPDATE products SET name=$1,version=$2,author=$3,currency=$4,date_format=$5,theme=$6,sheets=$7::jsonb,updated_at=now() WHERE id=$8 AND user_id=$9 RETURNING *", product.name, product.version, product.author, product.currency, product.dateFormat, product.theme, sheets_json(product), product_id, user_id)
    if not row: raise HTTPException(404, "Product not found")
    return row_product(row)


@app.delete("/api/v1/products/{product_id}", status_code=204)
async def delete_product(product_id: UUID, user_id: str = Depends(current_user)):
    result = await app.state.pool.execute("DELETE FROM products WHERE id=$1 AND user_id=$2", product_id, user_id)
    if result.endswith("0"): raise HTTPException(404, "Product not found")
    return Response(status_code=204)


@app.get("/api/v1/builds", response_model=list[BuildRecord])
async def list_builds(limit: int = Query(25, ge=1, le=100), user_id: str = Depends(current_user)):
    return await app.state.pool.fetch("SELECT id,product_id,product_name,file_name,sheet_count,row_count,byte_size,created_at FROM builds WHERE user_id=$1 ORDER BY created_at DESC LIMIT $2", user_id, limit)


def generate_xlsx(product: ProductInput) -> bytes:
    workbook = Workbook(); workbook.remove(workbook.active)
    for sheet in product.sheets:
        ws = workbook.create_sheet(sheet.name)
        ws.append([c.label for c in sheet.columns])
        for row in sheet.rows: ws.append(row)
    output = io.BytesIO(); workbook.save(output); return output.getvalue()


@app.post("/api/v1/workbooks/generate")
async def generate_workbook(request: GenerateRequest, user_id: str = Depends(current_user)):
    if request.product_id:
        exists = await app.state.pool.fetchval("SELECT 1 FROM products WHERE id=$1 AND user_id=$2", request.product_id, user_id)
        if not exists: raise HTTPException(404, "Product not found")
    content = generate_xlsx(request.product)
    safe = re.sub(r"[^a-z0-9]+", "-", request.product.name.lower()).strip("-")
    file_name = f"{safe}-v{request.product.version}.xlsx"
    await app.state.pool.execute("INSERT INTO builds (user_id,product_id,product_name,file_name,sheet_count,row_count,byte_size) VALUES ($1,$2,$3,$4,$5,$6,$7)", user_id, request.product_id, request.product.name, file_name, len(request.product.sheets), sum(len(s.rows) for s in request.product.sheets), len(content))
    return {"file_name": file_name, "base64": base64.b64encode(content).decode(), "bytes": len(content)}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api:app", host="0.0.0.0", port=int(os.getenv("PORT", "8000")))
        
        
