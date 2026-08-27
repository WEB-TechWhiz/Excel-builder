'use client';

import React, { useState, useRef } from 'react';
import { useRouter } from 'next/navigation';
import {
  Sparkles,
  ArrowRight,
  FileSpreadsheet,
  Layers,
  CheckCircle2,
  Loader2,
  Paperclip,
  X,
  FileText,
  UploadCloud,
  FileCode,
  FileCheck,
} from 'lucide-react';
import { Product } from '../../types/schema';
import { saveProduct } from '../../lib/storage';
import ExcelJS from 'exceljs';

interface AttachedFile {
  file: File;
  name: string;
  size: number;
  type: string;
  content?: string;
  parsedSheets?: {
    name: string;
    columns: string[];
    rows: string[][];
  }[];
}

export default function AIPage() {
  const [prompt, setPrompt] = useState('');
  const [loading, setLoading] = useState(false);
  const [generatedProduct, setGeneratedProduct] = useState<Product | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [attachedFile, setAttachedFile] = useState<AttachedFile | null>(null);
  const [isDragging, setIsDragging] = useState(false);
  const [parsingFile, setParsingFile] = useState(false);

  const fileInputRef = useRef<HTMLInputElement>(null);
  const router = useRouter();

  const samplePrompts = [
    'Create an enterprise SaaS financial tracker with MRR, ARR, churn rate, expansion revenue, and CAC payback',
    'Build a B2B sales pipeline CRM tracker with deal stages, deal owner, contract values, and win probability KPIs',
    'Generate an inventory warehouse management sheet with SKU numbers, unit costs, reorder triggers, and total valuation',
    'Design an executive quarterly OpEx budget tracker comparing targets, actual spend, and variances by department',
  ];

  // Handle file selection and client-side extraction
  const processSelectedFile = async (file: File) => {
    try {
      setParsingFile(true);
      setError(null);

      const fileName = file.name.toLowerCase();

      if (fileName.endsWith('.xlsx') || fileName.endsWith('.xls')) {
        const buffer = await file.arrayBuffer();
        const workbook = new ExcelJS.Workbook();
        await workbook.xlsx.load(buffer);

        const parsedSheets: { name: string; columns: string[]; rows: string[][] }[] = [];

        workbook.eachSheet((worksheet) => {
          const sheetRows: string[][] = [];
          worksheet.eachRow({ includeEmpty: false }, (row) => {
            const rowValues = Array.isArray(row.values) ? row.values.slice(1) : [];
            sheetRows.push(rowValues.map((v) => (v !== null && v !== undefined ? String(v) : '')));
          });

          if (sheetRows.length > 0) {
            const columns = sheetRows[0] || [];
            const dataRows = sheetRows.slice(1);
            parsedSheets.push({
              name: worksheet.name,
              columns,
              rows: dataRows,
            });
          }
        });

        setAttachedFile({
          file,
          name: file.name,
          size: file.size,
          type: file.type || 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
          parsedSheets,
        });
      } else if (fileName.endsWith('.csv') || fileName.endsWith('.txt') || fileName.endsWith('.json') || fileName.endsWith('.md')) {
        const text = await file.text();
        setAttachedFile({
          file,
          name: file.name,
          size: file.size,
          type: file.type || 'text/plain',
          content: text,
        });
      } else {
        // Fallback for images / documents / pdf
        setAttachedFile({
          file,
          name: file.name,
          size: file.size,
          type: file.type || 'application/octet-stream',
        });
      }
    } catch (err: any) {
      setError('Failed to parse attached file: ' + (err.message || String(err)));
    } finally {
      setParsingFile(false);
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      processSelectedFile(e.target.files[0]);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      processSelectedFile(e.dataTransfer.files[0]);
    }
  };

  const handleGenerate = async (queryText?: string) => {
    const textToSubmit = queryText || prompt;
    if (!textToSubmit.trim() && !attachedFile) return;

    try {
      setLoading(true);
      setError(null);
      setGeneratedProduct(null);

      const payload: any = {
        prompt: textToSubmit,
      };

      if (attachedFile) {
        payload.file = {
          name: attachedFile.name,
          type: attachedFile.type,
          size: attachedFile.size,
          content: attachedFile.content,
          parsedSheets: attachedFile.parsedSheets,
        };
      }

      const res = await fetch('/api/ai', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });

      const data = await res.json();
      if (!res.ok || !data.success) {
        throw new Error(data.error || 'Generation failed');
      }

      setGeneratedProduct(data.product);
    } catch (err: any) {
      setError(err.message || 'Failed to generate model');
    } finally {
      setLoading(false);
    }
  };

  const handleOpenInStudio = () => {
    if (!generatedProduct) return;
    const saved = saveProduct(generatedProduct);
    router.push(`/studio/${saved.id}`);
  };

  return (
    <div className="mx-auto max-w-5xl px-4 sm:px-6 py-10 w-full">
      {/* Header */}
      <div className="text-center max-w-2xl mx-auto mb-10">
        <div className="inline-flex items-center gap-2 rounded-full border border-purple-500/30 bg-purple-500/10 px-3.5 py-1 text-xs font-semibold text-purple-300 mb-4">
          <Sparkles className="h-3.5 w-3.5 text-purple-400" />
          <span>AI Natural Language & Document Ingestion</span>
        </div>
        <h1 className="text-3xl sm:text-5xl font-extrabold text-white tracking-tight">
          AI Spreadsheet Architect
        </h1>
        <p className="mt-3 text-sm sm:text-base text-slate-400">
          Describe what you need or upload an existing spreadsheet/data file. Our AI engine extracts data,
          assigns types, creates formulaic KPI cards, and formats the workbook with enterprise themes.
        </p>
      </div>

      {/* Hidden file input */}
      <input
        ref={fileInputRef}
        type="file"
        accept=".xlsx,.xls,.csv,.json,.txt,.pdf,.png,.jpg,.jpeg"
        onChange={handleFileChange}
        className="hidden"
      />

      {/* Prompt Input Box with File Upload integration */}
      <div
        onDragOver={(e) => {
          e.preventDefault();
          setIsDragging(true);
        }}
        onDragLeave={() => setIsDragging(false)}
        onDrop={handleDrop}
        className={`glass-panel rounded-2xl p-6 border transition-all duration-200 shadow-2xl mb-8 ${
          isDragging ? 'border-purple-500 bg-purple-950/20 ring-2 ring-purple-500/40' : 'border-slate-800'
        }`}
      >
        {/* Attached File Chip (if file is uploaded) */}
        {attachedFile && (
          <div className="mb-4 p-3 rounded-xl bg-purple-950/40 border border-purple-500/30 flex items-center justify-between gap-3 animate-fade-in">
            <div className="flex items-center gap-3">
              <div className="h-9 w-9 rounded-lg bg-purple-500/20 border border-purple-500/40 flex items-center justify-center">
                {attachedFile.name.endsWith('.xlsx') || attachedFile.name.endsWith('.csv') ? (
                  <FileSpreadsheet className="h-5 w-5 text-purple-300" />
                ) : (
                  <FileText className="h-5 w-5 text-purple-300" />
                )}
              </div>
              <div>
                <div className="flex items-center gap-2">
                  <span className="text-sm font-bold text-white">{attachedFile.name}</span>
                  <span className="text-[10px] text-slate-400 font-mono">
                    ({(attachedFile.size / 1024).toFixed(1)} KB)
                  </span>
                </div>
                <p className="text-xs text-purple-300">
                  {attachedFile.parsedSheets
                    ? `Parsed ${attachedFile.parsedSheets.length} sheet(s) • Ready for AI transformation`
                    : 'Attached data source for AI ingestion'}
                </p>
              </div>
            </div>

            <button
              onClick={() => setAttachedFile(null)}
              className="p-1.5 rounded-lg text-slate-400 hover:text-rose-400 hover:bg-rose-500/10 transition-colors"
              title="Remove file"
            >
              <X className="h-4 w-4" />
            </button>
          </div>
        )}

        {/* Textarea */}
        <div className="relative">
          <textarea
            rows={3}
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            placeholder={
              attachedFile
                ? `Ask AI how to format, summarize, or enrich "${attachedFile.name}" (or click Generate to auto-synthesize)...`
                : 'Describe your spreadsheet product or drag & drop an Excel/CSV file here...'
            }
            className="w-full rounded-xl border border-slate-700 bg-slate-900/90 p-4 text-sm text-slate-100 placeholder-slate-500 focus:border-purple-500 focus:outline-none focus:ring-1 focus:ring-purple-500"
          />
        </div>

        {/* Actions Bar inside Prompt Box */}
        <div className="mt-4 flex flex-wrap items-center justify-between gap-3 pt-3 border-t border-slate-800/80">
          {/* Left: Attachment trigger */}
          <div className="flex items-center gap-2">
            <button
              type="button"
              onClick={() => fileInputRef.current?.click()}
              disabled={parsingFile}
              className="flex items-center gap-1.5 rounded-xl border border-slate-700 bg-slate-900 px-3.5 py-2 text-xs font-semibold text-slate-200 hover:bg-slate-800 hover:border-purple-500/40 transition-all"
            >
              {parsingFile ? (
                <Loader2 className="h-3.5 w-3.5 animate-spin text-purple-400" />
              ) : (
                <Paperclip className="h-3.5 w-3.5 text-purple-400" />
              )}
              <span>{attachedFile ? 'Change File' : 'Attach Excel / CSV'}</span>
            </button>
            <span className="text-[11px] text-slate-500 hidden sm:inline">
              Supports .xlsx, .csv, .json, .txt
            </span>
          </div>

          {/* Right: Submit button */}
          <button
            onClick={() => handleGenerate()}
            disabled={loading || (!prompt.trim() && !attachedFile)}
            className="flex items-center gap-2 rounded-xl bg-gradient-to-r from-purple-600 to-indigo-600 px-6 py-2.5 text-sm font-bold text-white shadow-lg shadow-purple-500/25 hover:from-purple-500 hover:to-indigo-500 disabled:opacity-50 transition-all hover:scale-[1.02]"
          >
            {loading ? (
              <>
                <Loader2 className="h-4 w-4 animate-spin" />
                <span>Synthesizing Model...</span>
              </>
            ) : (
              <>
                <Sparkles className="h-4 w-4" />
                <span>Generate Workbook</span>
                <ArrowRight className="h-4 w-4" />
              </>
            )}
          </button>
        </div>

        {/* Quick prompt presets (if no file attached) */}
        {!attachedFile && (
          <div className="mt-5 pt-4 border-t border-slate-800/60">
            <p className="text-xs text-slate-400 font-medium mb-2">Prompt Ideas:</p>
            <div className="flex flex-wrap gap-2">
              {samplePrompts.map((p, idx) => (
                <button
                  key={idx}
                  onClick={() => {
                    setPrompt(p);
                    handleGenerate(p);
                  }}
                  className="rounded-lg bg-slate-900/80 hover:bg-purple-950/40 border border-slate-800 hover:border-purple-500/40 px-3 py-1.5 text-xs text-slate-300 hover:text-purple-300 text-left transition-all"
                >
                  {p.slice(0, 50)}...
                </button>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Error display */}
      {error && (
        <div className="p-4 rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-300 text-sm mb-8 animate-fade-in">
          {error}
        </div>
      )}

      {/* Generated Result Preview */}
      {generatedProduct && (
        <div className="glass-panel rounded-2xl p-6 sm:p-8 border border-purple-500/40 shadow-2xl animate-fade-in">
          <div className="flex flex-wrap items-center justify-between gap-4 pb-6 border-b border-slate-800">
            <div>
              <div className="inline-flex items-center gap-1.5 text-xs font-semibold text-emerald-400 bg-emerald-500/10 px-2.5 py-0.5 rounded-full mb-2">
                <CheckCircle2 className="h-3.5 w-3.5" />
                <span>Workbook Synthesized Successfully</span>
              </div>
              <h2 className="text-2xl font-bold text-white">{generatedProduct.name}</h2>
              <p className="text-xs text-slate-400 mt-0.5">
                Theme: <span className="capitalize text-slate-200">{generatedProduct.theme}</span> • Currency: {generatedProduct.currency}
              </p>
            </div>

            <button
              onClick={handleOpenInStudio}
              className="flex items-center gap-2 rounded-xl bg-gradient-to-r from-blue-600 to-indigo-600 px-5 py-2.5 text-sm font-bold text-white shadow-lg shadow-blue-500/25 hover:scale-105 transition-all"
            >
              <FileSpreadsheet className="h-4 w-4" />
              <span>Open in Visual Studio</span>
              <ArrowRight className="h-4 w-4" />
            </button>
          </div>

          {/* Sheets preview */}
          <div className="my-6 space-y-4">
            {generatedProduct.sheets.map((sheet) => (
              <div key={sheet.id} className="p-4 rounded-xl bg-slate-900/90 border border-slate-800">
                <div className="flex items-center justify-between mb-3">
                  <div>
                    <h3 className="text-base font-bold text-slate-100">{sheet.name}</h3>
                    <p className="text-xs text-slate-400">{sheet.description}</p>
                  </div>
                  <span className="text-xs text-slate-400 bg-slate-800 px-2 py-0.5 rounded font-mono">
                    {sheet.columns.length} columns • {sheet.rows.length} rows
                  </span>
                </div>

                {/* KPI metrics row */}
                {sheet.kpis && sheet.kpis.length > 0 && (
                  <div className="grid grid-cols-2 sm:grid-cols-3 gap-2.5 my-3">
                    {sheet.kpis.map((k, kIdx) => (
                      <div key={kIdx} className="p-2.5 rounded-lg bg-slate-950/80 border border-slate-800/80 text-center">
                        <p className="text-[10px] uppercase font-bold text-slate-400">{k.label}</p>
                        <p className="text-xs font-mono text-purple-300 font-semibold mt-0.5">
                          {k.aggregation.toUpperCase()}({k.column})
                        </p>
                      </div>
                    ))}
                  </div>
                )}

                {/* Columns Chips */}
                <div className="flex flex-wrap gap-1.5 mt-3">
                  {sheet.columns.map((c) => (
                    <span
                      key={c.key}
                      className="px-2 py-0.5 rounded bg-slate-800 text-[11px] font-medium text-slate-300 border border-slate-700/60"
                    >
                      {c.label} <span className="text-slate-500 font-mono text-[10px]">({c.type})</span>
                    </span>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
