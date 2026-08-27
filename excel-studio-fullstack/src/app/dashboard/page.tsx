'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import {
  FileSpreadsheet,
  Plus,
  Sparkles,
  Download,
  Trash2,
  Copy,
  ExternalLink,
  Search,
  Layers,
  Calendar,
  Clock,
} from 'lucide-react';
import { getStoredProducts, deleteProduct, saveProduct, createNewProduct } from '../../lib/storage';
import { Product, ThemeName } from '../../types/schema';
import { ExcelProductEngine } from '../../lib/excel-engine';
import saveAs from 'file-saver';

export default function DashboardPage() {
  const [products, setProducts] = useState<Product[]>([]);
  const [search, setSearch] = useState('');
  const [selectedTheme, setSelectedTheme] = useState<string>('all');
  const [exportingId, setExportingId] = useState<string | null>(null);
  const router = useRouter();

  useEffect(() => {
    setProducts(getStoredProducts());
  }, []);

  const handleCreateNew = () => {
    const newProd = createNewProduct();
    router.push(`/studio/${newProd.id}`);
  };

  const handleDelete = (id: string, name: string) => {
    if (confirm(`Are you sure you want to delete "${name}"?`)) {
      deleteProduct(id);
      setProducts(getStoredProducts());
    }
  };

  const handleDuplicate = (product: Product) => {
    const dup: Product = {
      ...JSON.parse(JSON.stringify(product)),
      id: 'prod_' + Math.random().toString(36).substring(2, 9),
      name: `${product.name} (Copy)`,
    };
    saveProduct(dup);
    setProducts(getStoredProducts());
  };

  const handleExportXLSX = async (product: Product) => {
    try {
      setExportingId(product.id);
      const engine = new ExcelProductEngine(product);
      const buffer = await engine.exportAsBuffer();
      const blob = new Blob([buffer], {
        type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
      });
      const fileName = `${product.name.toLowerCase().replace(/[^a-z0-9]/g, '_')}_v${product.version}.xlsx`;
      saveAs(blob, fileName);
    } catch (err) {
      alert('Export failed: ' + String(err));
    } finally {
      setExportingId(null);
    }
  };

  const filteredProducts = products.filter((p) => {
    const matchesSearch =
      p.name.toLowerCase().includes(search.toLowerCase()) ||
      p.author.toLowerCase().includes(search.toLowerCase());
    const matchesTheme = selectedTheme === 'all' || p.theme === selectedTheme;
    return matchesSearch && matchesTheme;
  });

  const totalSheets = products.reduce((acc, p) => acc + (p.sheets?.length || 0), 0);
  const totalRows = products.reduce(
    (acc, p) => acc + (p.sheets?.reduce((sAcc, s) => sAcc + (s.rows?.length || 0), 0) || 0),
    0
  );

  return (
    <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-8 w-full">
      {/* Header Bar */}
      <div className="flex flex-wrap items-center justify-between gap-4 pb-8 border-b border-slate-800">
        <div>
          <h1 className="text-3xl font-extrabold text-white tracking-tight">Spreadsheet Products</h1>
          <p className="text-sm text-slate-400 mt-1">
            Manage your declarative Excel workbooks, templates, and releases.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <Link
            href="/ai"
            className="flex items-center gap-2 rounded-xl border border-purple-500/30 bg-purple-500/10 px-4 py-2.5 text-sm font-semibold text-purple-300 hover:bg-purple-500/20 transition-all"
          >
            <Sparkles className="h-4 w-4 text-purple-400" />
            <span>AI Copilot</span>
          </Link>

          <button
            onClick={handleCreateNew}
            className="flex items-center gap-2 rounded-xl bg-gradient-to-r from-blue-600 to-indigo-600 px-5 py-2.5 text-sm font-semibold text-white shadow-lg shadow-blue-500/25 hover:from-blue-500 hover:to-indigo-500 transition-all hover:scale-105"
          >
            <Plus className="h-4 w-4" />
            <span>Create Product</span>
          </button>
        </div>
      </div>

      {/* Summary Metrics */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 my-6">
        <div className="glass-panel rounded-xl p-4 border border-slate-800">
          <p className="text-xs text-slate-400 font-semibold uppercase tracking-wider">Active Products</p>
          <p className="text-2xl font-bold text-white mt-1">{products.length}</p>
        </div>
        <div className="glass-panel rounded-xl p-4 border border-slate-800">
          <p className="text-xs text-slate-400 font-semibold uppercase tracking-wider">Total Worksheets</p>
          <p className="text-2xl font-bold text-blue-400 mt-1">{totalSheets}</p>
        </div>
        <div className="glass-panel rounded-xl p-4 border border-slate-800">
          <p className="text-xs text-slate-400 font-semibold uppercase tracking-wider">Configured Data Rows</p>
          <p className="text-2xl font-bold text-emerald-400 mt-1">{totalRows}</p>
        </div>
      </div>

      {/* Filters & Search */}
      <div className="flex flex-wrap items-center justify-between gap-4 mb-6">
        <div className="relative flex-1 min-w-[260px] max-w-md">
          <Search className="absolute left-3.5 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-500" />
          <input
            type="text"
            placeholder="Search products by title or author..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full rounded-xl border border-slate-800 bg-slate-900/90 pl-10 pr-4 py-2 text-sm text-slate-200 placeholder-slate-500 focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
          />
        </div>

        <div className="flex items-center gap-2">
          <span className="text-xs text-slate-400 font-medium">Theme:</span>
          {(['all', 'premium', 'midnight', 'forest', 'sunset'] as (string | ThemeName)[]).map((theme) => (
            <button
              key={theme}
              onClick={() => setSelectedTheme(theme)}
              className={`px-3 py-1.5 text-xs font-semibold rounded-lg capitalize transition-all ${
                selectedTheme === theme
                  ? 'bg-slate-800 text-blue-400 border border-blue-500/30'
                  : 'text-slate-400 hover:text-slate-200 bg-slate-900/60 border border-slate-800'
              }`}
            >
              {theme}
            </button>
          ))}
        </div>
      </div>

      {/* Product Cards Grid */}
      {filteredProducts.length === 0 ? (
        <div className="glass-panel rounded-2xl p-12 text-center border border-slate-800">
          <FileSpreadsheet className="h-12 w-12 text-slate-600 mx-auto mb-3" />
          <h3 className="text-lg font-bold text-slate-300">No products found</h3>
          <p className="text-sm text-slate-500 mt-1 mb-6">
            Try adjusting your search criteria or create a brand new spreadsheet model.
          </p>
          <button
            onClick={handleCreateNew}
            className="inline-flex items-center gap-2 rounded-xl bg-blue-600 px-4 py-2 text-sm font-semibold text-white hover:bg-blue-500"
          >
            <Plus className="h-4 w-4" />
            <span>Create New Product</span>
          </button>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredProducts.map((product) => {
            const sheetCount = product.sheets?.length || 0;
            const rowCount = product.sheets?.reduce((acc, s) => acc + (s.rows?.length || 0), 0) || 0;
            const kpiCount = product.sheets?.reduce((acc, s) => acc + (s.kpis?.length || 0), 0) || 0;

            return (
              <div
                key={product.id}
                className="glass-panel glass-panel-hover rounded-2xl p-5 border border-slate-800 flex flex-col justify-between"
              >
                <div>
                  <div className="flex items-start justify-between gap-3 mb-3">
                    <div className="flex items-center gap-2.5">
                      <div className="h-9 w-9 rounded-lg bg-blue-500/10 border border-blue-500/20 flex items-center justify-center">
                        <FileSpreadsheet className="h-4 w-4 text-blue-400" />
                      </div>
                      <div>
                        <h3 className="text-base font-bold text-white leading-tight line-clamp-1">{product.name}</h3>
                        <p className="text-xs text-slate-400">{product.author || 'Author'}</p>
                      </div>
                    </div>

                    <span
                      className={`text-[10px] font-bold px-2 py-0.5 rounded uppercase tracking-wider border ${
                        product.theme === 'premium'
                          ? 'bg-blue-500/10 text-blue-400 border-blue-500/30'
                          : product.theme === 'midnight'
                          ? 'bg-cyan-500/10 text-cyan-400 border-cyan-500/30'
                          : product.theme === 'forest'
                          ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30'
                          : 'bg-amber-500/10 text-amber-400 border-amber-500/30'
                      }`}
                    >
                      {product.theme}
                    </span>
                  </div>

                  {/* Badges */}
                  <div className="grid grid-cols-3 gap-2 my-4 p-2.5 rounded-xl bg-slate-900/60 border border-slate-800/80 text-center">
                    <div>
                      <p className="text-[10px] text-slate-500 font-semibold uppercase">Sheets</p>
                      <p className="text-sm font-bold text-slate-200">{sheetCount}</p>
                    </div>
                    <div>
                      <p className="text-[10px] text-slate-500 font-semibold uppercase">Rows</p>
                      <p className="text-sm font-bold text-slate-200">{rowCount}</p>
                    </div>
                    <div>
                      <p className="text-[10px] text-slate-500 font-semibold uppercase">KPIs</p>
                      <p className="text-sm font-bold text-slate-200">{kpiCount}</p>
                    </div>
                  </div>

                  {/* Sheet Names list */}
                  <div className="flex flex-wrap gap-1.5 mb-4">
                    {product.sheets?.slice(0, 3).map((s) => (
                      <span
                        key={s.id}
                        className="rounded-md bg-slate-800/80 px-2 py-0.5 text-[11px] font-medium text-slate-300 border border-slate-700/50"
                      >
                        {s.name}
                      </span>
                    ))}
                    {sheetCount > 3 && (
                      <span className="rounded-md bg-slate-800/40 px-1.5 py-0.5 text-[11px] text-slate-500">
                        +{sheetCount - 3} more
                      </span>
                    )}
                  </div>
                </div>

                {/* Actions Footer */}
                <div className="pt-4 border-t border-slate-800/80 flex items-center justify-between gap-2">
                  <div className="flex items-center gap-1">
                    <button
                      onClick={() => handleExportXLSX(product)}
                      disabled={exportingId === product.id}
                      className="p-2 rounded-lg text-slate-400 hover:text-emerald-400 hover:bg-emerald-500/10 transition-colors"
                      title="Download .XLSX"
                    >
                      <Download className={`h-4 w-4 ${exportingId === product.id ? 'animate-bounce text-emerald-400' : ''}`} />
                    </button>
                    <button
                      onClick={() => handleDuplicate(product)}
                      className="p-2 rounded-lg text-slate-400 hover:text-blue-400 hover:bg-blue-500/10 transition-colors"
                      title="Duplicate"
                    >
                      <Copy className="h-4 w-4" />
                    </button>
                    <button
                      onClick={() => handleDelete(product.id, product.name)}
                      className="p-2 rounded-lg text-slate-400 hover:text-rose-400 hover:bg-rose-500/10 transition-colors"
                      title="Delete"
                    >
                      <Trash2 className="h-4 w-4" />
                    </button>
                  </div>

                  <Link
                    href={`/studio/${product.id}`}
                    className="flex items-center gap-1.5 rounded-lg bg-blue-600/15 border border-blue-500/30 px-3.5 py-1.5 text-xs font-bold text-blue-400 hover:bg-blue-600 hover:text-white transition-all"
                  >
                    <span>Edit Studio</span>
                    <ExternalLink className="h-3 w-3" />
                  </Link>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
