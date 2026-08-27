'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import {
  FolderKanban,
  Download,
  Copy,
  Layers,
  ArrowRight,
  CheckCircle2,
  Table,
  BarChart3,
  TrendingUp,
} from 'lucide-react';
import { TEMPLATES } from '../../lib/templates';
import { saveProduct } from '../../lib/storage';
import { Product } from '../../types/schema';
import { ExcelProductEngine } from '../../lib/excel-engine';
import saveAs from 'file-saver';

export default function TemplatesPage() {
  const router = useRouter();
  const [downloadingId, setDownloadingId] = useState<string | null>(null);

  const handleClone = (template: Product) => {
    const clone: Product = {
      ...JSON.parse(JSON.stringify(template)),
      id: 'prod_' + Math.random().toString(36).substring(2, 9),
      name: `${template.name} (My Workspace)`,
    };
    saveProduct(clone);
    router.push(`/studio/${clone.id}`);
  };

  const handleDownload = async (template: Product) => {
    try {
      setDownloadingId(template.id);
      const engine = new ExcelProductEngine(template);
      const buffer = await engine.exportAsBuffer();
      const blob = new Blob([buffer], {
        type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
      });
      const fileName = `${template.name.toLowerCase().replace(/[^a-z0-9]/g, '_')}_v${template.version}.xlsx`;
      saveAs(blob, fileName);
    } catch (err) {
      alert('Download failed: ' + String(err));
    } finally {
      setDownloadingId(null);
    }
  };

  return (
    <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-10 w-full">
      {/* Header */}
      <div className="text-center max-w-3xl mx-auto mb-12">
        <div className="inline-flex items-center gap-2 rounded-full border border-blue-500/30 bg-blue-500/10 px-3.5 py-1 text-xs font-semibold text-blue-400 mb-4">
          <FolderKanban className="h-3.5 w-3.5 text-blue-400" />
          <span>Curated Production Templates</span>
        </div>
        <h1 className="text-3xl sm:text-5xl font-extrabold text-white tracking-tight">
          Enterprise Template Library
        </h1>
        <p className="mt-4 text-base text-slate-400">
          Pre-built, fully formatted spreadsheets built with strict financial and business domain architecture.
          Clone to your studio with 1-click or download directly.
        </p>
      </div>

      {/* Templates Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {TEMPLATES.map((tmpl) => (
          <div
            key={tmpl.id}
            className="glass-panel glass-panel-hover rounded-2xl p-6 sm:p-7 border border-slate-800 flex flex-col justify-between"
          >
            <div>
              <div className="flex items-start justify-between gap-4 mb-4">
                <div>
                  <span
                    className={`inline-block text-[10px] font-bold px-2.5 py-0.5 rounded-full uppercase tracking-wider mb-2 border ${
                      tmpl.theme === 'premium'
                        ? 'bg-blue-500/10 text-blue-400 border-blue-500/30'
                        : tmpl.theme === 'midnight'
                        ? 'bg-cyan-500/10 text-cyan-400 border-cyan-500/30'
                        : tmpl.theme === 'forest'
                        ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30'
                        : 'bg-amber-500/10 text-amber-400 border-amber-500/30'
                    }`}
                  >
                    Theme: {tmpl.theme}
                  </span>
                  <h2 className="text-2xl font-bold text-white">{tmpl.name}</h2>
                  <p className="text-xs text-slate-400 mt-0.5">Author: {tmpl.author} • v{tmpl.version}</p>
                </div>
              </div>

              {/* Sheet preview chips */}
              <div className="my-5 p-4 rounded-xl bg-slate-900/80 border border-slate-800">
                <p className="text-xs font-semibold text-slate-400 mb-2.5 uppercase tracking-wider flex items-center gap-1.5">
                  <Layers className="h-3.5 w-3.5 text-blue-400" />
                  Included Worksheets ({tmpl.sheets.length})
                </p>
                <div className="space-y-2">
                  {tmpl.sheets.map((sheet, sIdx) => (
                    <div
                      key={sheet.id}
                      className="p-2.5 rounded-lg bg-slate-950/60 border border-slate-800/80 flex items-center justify-between"
                    >
                      <div>
                        <p className="text-xs font-bold text-slate-200">{sheet.name}</p>
                        <p className="text-[11px] text-slate-400 line-clamp-1">{sheet.description}</p>
                      </div>
                      <div className="flex items-center gap-2 text-[10px] text-slate-400 font-mono">
                        <span className="bg-slate-800 px-1.5 py-0.5 rounded">{sheet.columns.length} Cols</span>
                        <span className="bg-slate-800 px-1.5 py-0.5 rounded">{sheet.kpis?.length || 0} KPIs</span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            {/* Actions */}
            <div className="pt-4 border-t border-slate-800 flex items-center justify-between gap-3">
              <button
                onClick={() => handleDownload(tmpl)}
                disabled={downloadingId === tmpl.id}
                className="flex items-center gap-2 rounded-xl border border-slate-700 bg-slate-800/80 px-4 py-2.5 text-xs font-semibold text-slate-300 hover:bg-slate-700 hover:text-white transition-all"
              >
                <Download className={`h-4 w-4 ${downloadingId === tmpl.id ? 'animate-bounce text-emerald-400' : ''}`} />
                <span>Direct .XLSX</span>
              </button>

              <button
                onClick={() => handleClone(tmpl)}
                className="flex items-center gap-2 rounded-xl bg-gradient-to-r from-blue-600 to-indigo-600 px-5 py-2.5 text-xs font-bold text-white shadow-lg shadow-blue-500/25 hover:from-blue-500 hover:to-indigo-500 hover:scale-[1.02] transition-all"
              >
                <Copy className="h-4 w-4" />
                <span>Clone & Edit in Studio</span>
                <ArrowRight className="h-3.5 w-3.5" />
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
