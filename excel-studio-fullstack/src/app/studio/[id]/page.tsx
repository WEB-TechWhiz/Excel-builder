'use client';

import React, { useState, useEffect } from 'react';
import { useParams, useRouter } from 'next/navigation';
import Link from 'next/link';
import {
  FileSpreadsheet,
  Save,
  Download,
  Plus,
  Trash2,
  Copy,
  Layers,
  Palette,
  DollarSign,
  Calendar,
  Sparkles,
  Table,
  Check,
  ChevronRight,
  ArrowLeft,
  Share2,
  RefreshCw,
  Sliders,
  Eye,
  FileCode,
  Upload,
} from 'lucide-react';
import { getProductById, saveProduct, createNewProduct } from '../../../lib/storage';
import { Product, Sheet, Column, KPI, ThemeName, ColumnType, KPIAggregation } from '../../../types/schema';
import { PALETTES } from '../../../lib/palettes';
import { ExcelProductEngine } from '../../../lib/excel-engine';
import saveAs from 'file-saver';

export default function StudioPage() {
  const params = useParams();
  const router = useRouter();
  const id = params?.id as string;

  const [product, setProduct] = useState<Product | null>(null);
  const [activeSheetId, setActiveSheetId] = useState<string>('');
  const [isExporting, setIsExporting] = useState(false);
  const [saveToast, setSaveToast] = useState(false);
  const [viewMode, setViewMode] = useState<'editor' | 'preview'>('editor');

  // Load product
  useEffect(() => {
    if (!id || id === 'new') {
      const newProd = createNewProduct();
      router.replace(`/studio/${newProd.id}`);
      return;
    }

    const loaded = getProductById(id);
    if (loaded) {
      setProduct(loaded);
      setActiveSheetId(loaded.sheets[0]?.id || '');
    } else {
      const created = createNewProduct();
      router.replace(`/studio/${created.id}`);
    }
  }, [id, router]);

  if (!product) {
    return (
      <div className="flex h-96 items-center justify-center">
        <div className="text-center">
          <div className="h-8 w-8 animate-spin rounded-full border-4 border-blue-500 border-t-transparent mx-auto mb-3" />
          <p className="text-sm text-slate-400">Loading Spreadsheet Studio...</p>
        </div>
      </div>
    );
  }

  const activeSheet = product.sheets.find((s) => s.id === activeSheetId) || product.sheets[0];
  const palette = PALETTES[product.theme] || PALETTES.premium;

  const handleSave = () => {
    if (product) {
      saveProduct(product);
      setSaveToast(true);
      setTimeout(() => setSaveToast(false), 2500);
    }
  };

  const handleExportXLSX = async () => {
    if (!product) return;
    try {
      setIsExporting(true);
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
      setIsExporting(false);
    }
  };

  const handleExportJSON = () => {
    const dataStr = 'data:text/json;charset=utf-8,' + encodeURIComponent(JSON.stringify(product, null, 2));
    const downloadAnchor = document.createElement('a');
    downloadAnchor.setAttribute('href', dataStr);
    downloadAnchor.setAttribute('download', `${product.name.toLowerCase().replace(/[^a-z0-9]/g, '_')}_schema.json`);
    document.body.appendChild(downloadAnchor);
    downloadAnchor.click();
    downloadAnchor.remove();
  };

  // Sheet operations
  const handleAddSheet = () => {
    const sheetNum = product.sheets.length + 1;
    const newSheet: Sheet = {
      id: 'sheet_' + Math.random().toString(36).substring(2, 7),
      name: `Sheet ${sheetNum}`,
      description: 'Custom worksheet description',
      columns: [
        { key: 'col_1', label: 'Item Name', type: 'text' },
        { key: 'col_2', label: 'Amount', type: 'currency' },
      ],
      kpis: [{ label: 'Total Amount', aggregation: 'sum', column: 'col_2', format: 'currency' }],
      rows: [
        ['Product Alpha', '12500'],
        ['Product Beta', '8900'],
      ],
    };
    const updated = { ...product, sheets: [...product.sheets, newSheet] };
    setProduct(updated);
    setActiveSheetId(newSheet.id);
    saveProduct(updated);
  };

  const handleDeleteSheet = (sheetId: string) => {
    if (product.sheets.length <= 1) {
      alert('A product must contain at least one worksheet.');
      return;
    }
    const filtered = product.sheets.filter((s) => s.id !== sheetId);
    const updated = { ...product, sheets: filtered };
    setProduct(updated);
    setActiveSheetId(filtered[0]?.id || '');
    saveProduct(updated);
  };

  // Column operations
  const handleAddColumn = () => {
    if (!activeSheet) return;
    const colNum = activeSheet.columns.length + 1;
    const newCol: Column = {
      key: `col_${colNum}_${Math.random().toString(36).substring(2, 5)}`,
      label: `Column ${colNum}`,
      type: 'text',
    };
    const updatedSheets = product.sheets.map((s) => {
      if (s.id === activeSheet.id) {
        const newRows = s.rows.map((r) => [...r, '']);
        return { ...s, columns: [...s.columns, newCol], rows: newRows };
      }
      return s;
    });
    const updated = { ...product, sheets: updatedSheets };
    setProduct(updated);
    saveProduct(updated);
  };

  const handleDeleteColumn = (colIdx: number) => {
    if (!activeSheet || activeSheet.columns.length <= 1) {
      alert('A sheet must have at least one column.');
      return;
    }
    const updatedSheets = product.sheets.map((s) => {
      if (s.id === activeSheet.id) {
        const newCols = s.columns.filter((_, idx) => idx !== colIdx);
        const newRows = s.rows.map((r) => r.filter((_, idx) => idx !== colIdx));
        return { ...s, columns: newCols, rows: newRows };
      }
      return s;
    });
    const updated = { ...product, sheets: updatedSheets };
    setProduct(updated);
    saveProduct(updated);
  };

  const handleUpdateColumn = (colIdx: number, updates: Partial<Column>) => {
    if (!activeSheet) return;
    const updatedSheets = product.sheets.map((s) => {
      if (s.id === activeSheet.id) {
        const newCols = [...s.columns];
        newCols[colIdx] = { ...newCols[colIdx], ...updates };
        return { ...s, columns: newCols };
      }
      return s;
    });
    const updated = { ...product, sheets: updatedSheets };
    setProduct(updated);
    saveProduct(updated);
  };

  // Row operations
  const handleAddRow = () => {
    if (!activeSheet) return;
    const emptyRow = activeSheet.columns.map((c) => (c.type === 'currency' || c.type === 'number' ? '0' : ''));
    const updatedSheets = product.sheets.map((s) => {
      if (s.id === activeSheet.id) {
        return { ...s, rows: [...s.rows, emptyRow] };
      }
      return s;
    });
    const updated = { ...product, sheets: updatedSheets };
    setProduct(updated);
    saveProduct(updated);
  };

  const handleDeleteRow = (rowIdx: number) => {
    if (!activeSheet) return;
    const updatedSheets = product.sheets.map((s) => {
      if (s.id === activeSheet.id) {
        return { ...s, rows: s.rows.filter((_, idx) => idx !== rowIdx) };
      }
      return s;
    });
    const updated = { ...product, sheets: updatedSheets };
    setProduct(updated);
    saveProduct(updated);
  };

  const handleCellChange = (rowIdx: number, colIdx: number, val: string) => {
    if (!activeSheet) return;
    const updatedSheets = product.sheets.map((s) => {
      if (s.id === activeSheet.id) {
        const newRows = [...s.rows];
        newRows[rowIdx] = [...newRows[rowIdx]];
        newRows[rowIdx][colIdx] = val;
        return { ...s, rows: newRows };
      }
      return s;
    });
    const updated = { ...product, sheets: updatedSheets };
    setProduct(updated);
    saveProduct(updated);
  };

  // KPI operations
  const handleAddKPI = () => {
    if (!activeSheet) return;
    const numCol = activeSheet.columns.find((c) => c.type === 'currency' || c.type === 'number') || activeSheet.columns[0];
    const newKpi: KPI = {
      label: `Total ${numCol?.label || 'Metric'}`,
      aggregation: 'sum',
      column: numCol?.key || 'col_1',
      format: numCol?.type === 'currency' ? 'currency' : 'number',
    };
    const updatedSheets = product.sheets.map((s) => {
      if (s.id === activeSheet.id) {
        return { ...s, kpis: [...(s.kpis || []), newKpi] };
      }
      return s;
    });
    const updated = { ...product, sheets: updatedSheets };
    setProduct(updated);
    saveProduct(updated);
  };

  const handleDeleteKPI = (kpiIdx: number) => {
    if (!activeSheet) return;
    const updatedSheets = product.sheets.map((s) => {
      if (s.id === activeSheet.id) {
        return { ...s, kpis: (s.kpis || []).filter((_, idx) => idx !== kpiIdx) };
      }
      return s;
    });
    const updated = { ...product, sheets: updatedSheets };
    setProduct(updated);
    saveProduct(updated);
  };

  // Calculate live KPI preview
  const calculateKPIValue = (kpi: KPI) => {
    if (!activeSheet) return '0';
    const colIdx = activeSheet.columns.findIndex((c) => c.key === kpi.column || c.label === kpi.column);
    if (colIdx === -1) return '0';

    const numbers = activeSheet.rows
      .map((r) => parseFloat(String(r[colIdx] || '').replace(/[^0-9.-]+/g, '')))
      .filter((n) => !isNaN(n));

    let val = 0;
    if (kpi.aggregation === 'sum') {
      val = numbers.reduce((a, b) => a + b, 0);
    } else if (kpi.aggregation === 'avg') {
      val = numbers.length > 0 ? numbers.reduce((a, b) => a + b, 0) / numbers.length : 0;
    } else if (kpi.aggregation === 'count') {
      val = activeSheet.rows.length;
    } else if (kpi.aggregation === 'max') {
      val = numbers.length > 0 ? Math.max(...numbers) : 0;
    } else if (kpi.aggregation === 'min') {
      val = numbers.length > 0 ? Math.min(...numbers) : 0;
    }

    if (kpi.format === 'currency') {
      return '$' + val.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
    } else if (kpi.format === 'percent') {
      return (val > 1 ? val : val * 100).toFixed(1) + '%';
    }
    return val.toLocaleString('en-US');
  };

  return (
    <div className="flex flex-col h-[calc(100vh-4rem)] overflow-hidden bg-[#090d16]">
      {/* 1. TOP STUDIO TOOLBAR */}
      <div className="h-16 border-b border-slate-800 bg-slate-950/90 px-4 sm:px-6 flex items-center justify-between gap-4 shrink-0">
        {/* Left: Back + Title / Metadata */}
        <div className="flex items-center gap-3">
          <Link
            href="/dashboard"
            className="p-2 rounded-lg text-slate-400 hover:text-white hover:bg-slate-900 transition-colors"
            title="Back to Dashboard"
          >
            <ArrowLeft className="h-4 w-4" />
          </Link>

          <div className="flex items-center gap-3">
            <input
              type="text"
              value={product.name}
              onChange={(e) => {
                const upd = { ...product, name: e.target.value };
                setProduct(upd);
                saveProduct(upd);
              }}
              className="bg-transparent text-base sm:text-lg font-bold text-white focus:bg-slate-900/80 focus:ring-1 focus:ring-blue-500 rounded px-2 py-1 border border-transparent hover:border-slate-700 transition-all max-w-[280px] sm:max-w-md"
            />
            <span className="text-xs bg-slate-800 text-slate-400 font-mono px-2 py-0.5 rounded border border-slate-700">
              v{product.version}
            </span>
          </div>
        </div>

        {/* Center: Theme & Mode switch */}
        <div className="hidden md:flex items-center gap-3">
          {/* Theme Dropdown */}
          <div className="flex items-center gap-1.5 bg-slate-900 px-3 py-1.5 rounded-xl border border-slate-800">
            <Palette className="h-3.5 w-3.5 text-blue-400" />
            <select
              value={product.theme}
              onChange={(e) => {
                const upd = { ...product, theme: e.target.value as ThemeName };
                setProduct(upd);
                saveProduct(upd);
              }}
              className="bg-transparent text-xs font-semibold text-slate-200 capitalize focus:outline-none cursor-pointer"
            >
              <option value="premium">Premium Sapphire</option>
              <option value="midnight">Midnight Onyx</option>
              <option value="forest">Forest Emerald</option>
              <option value="sunset">Sunset Amber</option>
            </select>
          </div>

          {/* View Mode Toggle */}
          <div className="flex items-center bg-slate-900 p-1 rounded-xl border border-slate-800">
            <button
              onClick={() => setViewMode('editor')}
              className={`flex items-center gap-1.5 px-3 py-1 text-xs font-semibold rounded-lg transition-all ${
                viewMode === 'editor' ? 'bg-blue-600 text-white shadow' : 'text-slate-400 hover:text-white'
              }`}
            >
              <Sliders className="h-3.5 w-3.5" />
              <span>Studio Grid</span>
            </button>
            <button
              onClick={() => setViewMode('preview')}
              className={`flex items-center gap-1.5 px-3 py-1 text-xs font-semibold rounded-lg transition-all ${
                viewMode === 'preview' ? 'bg-blue-600 text-white shadow' : 'text-slate-400 hover:text-white'
              }`}
            >
              <Eye className="h-3.5 w-3.5" />
              <span>Live Theme View</span>
            </button>
          </div>
        </div>

        {/* Right: Actions */}
        <div className="flex items-center gap-2">
          {saveToast && (
            <span className="text-xs font-semibold text-emerald-400 flex items-center gap-1 bg-emerald-500/10 px-2.5 py-1 rounded-lg border border-emerald-500/20 animate-fade-in">
              <Check className="h-3.5 w-3.5" /> Saved
            </span>
          )}

          <button
            onClick={handleSave}
            className="flex items-center gap-1.5 rounded-xl border border-slate-700 bg-slate-900 px-3.5 py-2 text-xs font-semibold text-slate-200 hover:bg-slate-800 transition-all"
            title="Save changes"
          >
            <Save className="h-3.5 w-3.5 text-blue-400" />
            <span className="hidden sm:inline">Save</span>
          </button>

          <button
            onClick={handleExportJSON}
            className="p-2 rounded-xl border border-slate-800 bg-slate-900 text-slate-400 hover:text-slate-200 hover:bg-slate-800 transition-all"
            title="Export JSON Schema"
          >
            <FileCode className="h-4 w-4" />
          </button>

          <button
            onClick={handleExportXLSX}
            disabled={isExporting}
            className="flex items-center gap-2 rounded-xl bg-gradient-to-r from-emerald-600 to-teal-600 px-4 py-2 text-xs font-bold text-white shadow-lg shadow-emerald-600/25 hover:from-emerald-500 hover:to-teal-500 transition-all hover:scale-105"
          >
            <Download className={`h-4 w-4 ${isExporting ? 'animate-bounce' : ''}`} />
            <span>Export .XLSX</span>
          </button>
        </div>
      </div>

      {/* 2. WORKSHEET TABS BAR */}
      <div className="h-11 border-b border-slate-800 bg-slate-950 px-4 flex items-center justify-between shrink-0 overflow-x-auto">
        <div className="flex items-center gap-1">
          {product.sheets.map((s) => {
            const isActive = s.id === activeSheet?.id;
            return (
              <div
                key={s.id}
                onClick={() => setActiveSheetId(s.id)}
                className={`group flex items-center gap-2 px-3.5 py-1.5 rounded-lg text-xs font-bold cursor-pointer transition-all ${
                  isActive
                    ? 'bg-blue-600/20 text-blue-400 border border-blue-500/40 shadow-sm'
                    : 'text-slate-400 hover:bg-slate-900 hover:text-slate-200'
                }`}
              >
                <Table className="h-3 w-3 opacity-70" />
                <span>{s.name}</span>
                {product.sheets.length > 1 && (
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      handleDeleteSheet(s.id);
                    }}
                    className="opacity-0 group-hover:opacity-100 hover:text-rose-400 p-0.5 rounded transition-opacity"
                    title="Delete Sheet"
                  >
                    <Trash2 className="h-3 w-3" />
                  </button>
                )}
              </div>
            );
          })}

          <button
            onClick={handleAddSheet}
            className="flex items-center gap-1 px-2.5 py-1.5 rounded-lg text-xs font-semibold text-slate-400 hover:text-white hover:bg-slate-900 transition-all"
            title="Add Worksheet"
          >
            <Plus className="h-3.5 w-3.5 text-blue-400" />
            <span>New Sheet</span>
          </button>
        </div>
      </div>

      {/* 3. MAIN CANVAS / CONTENT AREA */}
      <div className="flex-1 overflow-y-auto p-4 sm:p-6">
        {viewMode === 'preview' ? (
          /* ================= LIVE THEME PREVIEW ================= */
          <div className="max-w-6xl mx-auto glass-panel rounded-2xl p-6 border border-slate-800 shadow-2xl">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-sm font-bold text-slate-300 uppercase tracking-wider flex items-center gap-2">
                <Eye className="h-4 w-4 text-blue-400" />
                Spreadsheet Engine Rendering Preview ({product.theme.toUpperCase()})
              </h3>
              <button
                onClick={() => setViewMode('editor')}
                className="text-xs font-semibold text-blue-400 hover:underline"
              >
                Back to Grid Editor
              </button>
            </div>

            <div className="rounded-xl overflow-hidden border border-slate-700/60 shadow-lg">
              {/* Banner */}
              <div
                className="p-4 flex items-center justify-between text-white font-bold"
                style={{ backgroundColor: `#${palette.bannerBg}` }}
              >
                <div>
                  <h2 className="text-lg font-bold">{product.name.toUpperCase()} — {activeSheet?.name.toUpperCase()}</h2>
                  <p className="text-xs font-normal opacity-80">{activeSheet?.description || 'Automated Workbook'}</p>
                </div>
                <span className="text-[11px] px-2.5 py-1 rounded bg-white/20 uppercase font-mono">
                  {product.currency} • v{product.version}
                </span>
              </div>

              {/* KPI Cards */}
              {activeSheet?.kpis && activeSheet.kpis.length > 0 && (
                <div className="p-4 grid grid-cols-2 sm:grid-cols-4 gap-3 bg-slate-900/60">
                  {activeSheet.kpis.map((kpi, idx) => (
                    <div
                      key={idx}
                      className="rounded-lg p-3 border text-center"
                      style={{
                        backgroundColor: `#${palette.kpiBg}`,
                        borderColor: `#${palette.kpiBorder}`,
                      }}
                    >
                      <p className="text-[10px] font-bold text-slate-600 uppercase tracking-wider">{kpi.label}</p>
                      <p className="text-lg font-extrabold text-slate-900 mt-0.5">{calculateKPIValue(kpi)}</p>
                    </div>
                  ))}
                </div>
              )}

              {/* Table */}
              <div className="overflow-x-auto p-4 bg-white">
                <table className="w-full text-left text-xs border-collapse">
                  <thead>
                    <tr style={{ backgroundColor: `#${palette.headerBg}`, color: `#${palette.headerText}` }}>
                      {activeSheet?.columns.map((c) => (
                        <th
                          key={c.key}
                          className={`py-2.5 px-4 font-bold ${
                            c.type === 'currency' || c.type === 'number' || c.type === 'percent' ? 'text-right' : 'text-left'
                          }`}
                        >
                          {c.label}
                        </th>
                      ))}
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-200">
                    {activeSheet?.rows.map((row, rIdx) => (
                      <tr
                        key={rIdx}
                        style={{
                          backgroundColor: rIdx % 2 === 1 ? `#${palette.zebraBg}` : '#FFFFFF',
                        }}
                      >
                        {activeSheet.columns.map((col, cIdx) => (
                          <td
                            key={cIdx}
                            className={`py-2 px-4 font-medium text-slate-800 ${
                              col.type === 'currency' || col.type === 'number' || col.type === 'percent'
                                ? 'text-right font-mono'
                                : 'text-left'
                            }`}
                          >
                            {col.type === 'currency' && row[cIdx] && !row[cIdx].startsWith('$')
                              ? '$' + parseFloat(row[cIdx] || '0').toLocaleString('en-US', { minimumFractionDigits: 2 })
                              : row[cIdx] || ''}
                          </td>
                        ))}
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        ) : (
          /* ================= INTERACTIVE GRID EDITOR ================= */
          <div className="max-w-7xl mx-auto space-y-6">
            {/* KPI Cards Section */}
            <div className="glass-panel rounded-2xl p-5 border border-slate-800">
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center gap-2">
                  <Sparkles className="h-4 w-4 text-amber-400" />
                  <h3 className="text-sm font-bold text-white uppercase tracking-wider">
                    Worksheet KPI Metric Cards ({activeSheet?.kpis?.length || 0})
                  </h3>
                </div>
                <button
                  onClick={handleAddKPI}
                  className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-slate-900 border border-slate-700 text-xs font-semibold text-slate-200 hover:bg-slate-800 transition-all"
                >
                  <Plus className="h-3.5 w-3.5 text-amber-400" />
                  <span>Add KPI</span>
                </button>
              </div>

              {activeSheet?.kpis && activeSheet.kpis.length > 0 ? (
                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
                  {activeSheet.kpis.map((kpi, kIdx) => (
                    <div
                      key={kIdx}
                      className="p-3.5 rounded-xl bg-slate-900/90 border border-slate-800 flex flex-col justify-between"
                    >
                      <div className="flex items-start justify-between gap-2 mb-2">
                        <input
                          type="text"
                          value={kpi.label}
                          onChange={(e) => {
                            const newKpis = [...activeSheet.kpis];
                            newKpis[kIdx].label = e.target.value;
                            const updSheets = product.sheets.map((s) =>
                              s.id === activeSheet.id ? { ...s, kpis: newKpis } : s
                            );
                            const upd = { ...product, sheets: updSheets };
                            setProduct(upd);
                            saveProduct(upd);
                          }}
                          className="bg-transparent text-xs font-bold text-slate-300 focus:bg-slate-800 focus:ring-1 focus:ring-amber-500 rounded px-1.5 py-0.5 border border-transparent hover:border-slate-700 w-full"
                        />
                        <button
                          onClick={() => handleDeleteKPI(kIdx)}
                          className="text-slate-500 hover:text-rose-400 p-1 transition-colors"
                        >
                          <Trash2 className="h-3.5 w-3.5" />
                        </button>
                      </div>

                      <div className="text-xl font-extrabold text-white my-1 font-mono">{calculateKPIValue(kpi)}</div>

                      <div className="flex items-center gap-2 mt-2 pt-2 border-t border-slate-800/80 text-[11px]">
                        <select
                          value={kpi.aggregation}
                          onChange={(e) => {
                            const newKpis = [...activeSheet.kpis];
                            newKpis[kIdx].aggregation = e.target.value as KPIAggregation;
                            const updSheets = product.sheets.map((s) =>
                              s.id === activeSheet.id ? { ...s, kpis: newKpis } : s
                            );
                            const upd = { ...product, sheets: updSheets };
                            setProduct(upd);
                            saveProduct(upd);
                          }}
                          className="bg-slate-950 text-slate-300 rounded px-2 py-0.5 border border-slate-800 font-mono text-[10px] uppercase"
                        >
                          <option value="sum">SUM</option>
                          <option value="avg">AVG</option>
                          <option value="count">COUNT</option>
                          <option value="max">MAX</option>
                          <option value="min">MIN</option>
                        </select>

                        <select
                          value={kpi.column}
                          onChange={(e) => {
                            const newKpis = [...activeSheet.kpis];
                            newKpis[kIdx].column = e.target.value;
                            const updSheets = product.sheets.map((s) =>
                              s.id === activeSheet.id ? { ...s, kpis: newKpis } : s
                            );
                            const upd = { ...product, sheets: updSheets };
                            setProduct(upd);
                            saveProduct(upd);
                          }}
                          className="bg-slate-950 text-slate-300 rounded px-2 py-0.5 border border-slate-800 text-[10px] truncate max-w-[120px]"
                        >
                          {activeSheet.columns.map((c) => (
                            <option key={c.key} value={c.key}>
                              {c.label}
                            </option>
                          ))}
                        </select>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-xs text-slate-500 italic">
                  No KPI metric cards added yet. Click &quot;Add KPI&quot; to display summary cards at the top of your Excel sheet.
                </p>
              )}
            </div>

            {/* Columns & Data Grid */}
            <div className="glass-panel rounded-2xl p-5 border border-slate-800">
              <div className="flex flex-wrap items-center justify-between gap-3 mb-4">
                <div className="flex items-center gap-2">
                  <Table className="h-4 w-4 text-blue-400" />
                  <h3 className="text-sm font-bold text-white uppercase tracking-wider">
                    Data Grid & Column Config
                  </h3>
                </div>

                <div className="flex items-center gap-2">
                  <button
                    onClick={handleAddColumn}
                    className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-slate-900 border border-slate-700 text-xs font-semibold text-slate-200 hover:bg-slate-800 transition-all"
                  >
                    <Plus className="h-3.5 w-3.5 text-blue-400" />
                    <span>Add Column</span>
                  </button>

                  <button
                    onClick={handleAddRow}
                    className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-blue-600/20 border border-blue-500/40 text-xs font-semibold text-blue-300 hover:bg-blue-600 hover:text-white transition-all"
                  >
                    <Plus className="h-3.5 w-3.5" />
                    <span>Add Row</span>
                  </button>
                </div>
              </div>

              {/* Data Table */}
              <div className="overflow-x-auto rounded-xl border border-slate-800 bg-slate-950/60">
                <table className="w-full text-left text-xs border-collapse">
                  <thead>
                    <tr className="bg-slate-900 border-b border-slate-800">
                      <th className="py-2.5 px-3 w-12 text-center text-slate-500 font-mono">#</th>
                      {activeSheet?.columns.map((col, colIdx) => (
                        <th key={col.key} className="py-2 px-3 min-w-[160px]">
                          <div className="space-y-1">
                            <div className="flex items-center justify-between gap-1">
                              <input
                                type="text"
                                value={col.label}
                                onChange={(e) => handleUpdateColumn(colIdx, { label: e.target.value })}
                                className="bg-transparent font-bold text-slate-200 focus:bg-slate-800 focus:ring-1 focus:ring-blue-500 rounded px-1.5 py-0.5 border border-transparent hover:border-slate-700 w-full"
                              />
                              <button
                                onClick={() => handleDeleteColumn(colIdx)}
                                className="text-slate-600 hover:text-rose-400 p-0.5"
                                title="Delete Column"
                              >
                                <Trash2 className="h-3 w-3" />
                              </button>
                            </div>
                            <select
                              value={col.type}
                              onChange={(e) => handleUpdateColumn(colIdx, { type: e.target.value as ColumnType })}
                              className="bg-slate-950 text-slate-400 text-[10px] font-mono rounded px-1.5 py-0.5 border border-slate-800 focus:outline-none w-full"
                            >
                              <option value="text">text</option>
                              <option value="currency">currency ($)</option>
                              <option value="number">number</option>
                              <option value="percent">percent (%)</option>
                              <option value="date">date</option>
                            </select>
                          </div>
                        </th>
                      ))}
                      <th className="py-2.5 px-3 w-12 text-center text-slate-500">Actions</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-800/80">
                    {activeSheet?.rows.map((row, rIdx) => (
                      <tr key={rIdx} className="hover:bg-slate-900/40 group">
                        <td className="py-2 px-3 text-center text-slate-600 font-mono text-[11px]">{rIdx + 1}</td>
                        {activeSheet.columns.map((col, cIdx) => (
                          <td key={cIdx} className="p-1">
                            <input
                              type="text"
                              value={row[cIdx] ?? ''}
                              onChange={(e) => handleCellChange(rIdx, cIdx, e.target.value)}
                              placeholder="Empty cell"
                              className={`w-full bg-transparent px-2.5 py-1.5 rounded text-xs text-slate-100 placeholder-slate-600 focus:bg-slate-900 focus:outline-none focus:ring-1 focus:ring-blue-500 ${
                                col.type === 'currency' || col.type === 'number' || col.type === 'percent'
                                  ? 'text-right font-mono'
                                  : 'text-left'
                              }`}
                            />
                          </td>
                        ))}
                        <td className="py-2 px-3 text-center">
                          <button
                            onClick={() => handleDeleteRow(rIdx)}
                            className="opacity-0 group-hover:opacity-100 text-slate-500 hover:text-rose-400 p-1 transition-opacity"
                            title="Delete Row"
                          >
                            <Trash2 className="h-3.5 w-3.5" />
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
