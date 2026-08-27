'use client';

import Link from 'next/link';
import { useState } from 'react';
import {
  FileSpreadsheet,
  Sparkles,
  Layers,
  ShieldCheck,
  Zap,
  Palette,
  ArrowRight,
  Download,
  CheckCircle2,
  Table,
  BarChart3,
} from 'lucide-react';
import { PALETTES } from '../lib/palettes';
import { ThemeName } from '../types/schema';

export default function LandingPage() {
  const [activeTheme, setActiveTheme] = useState<ThemeName>('premium');
  const palette = PALETTES[activeTheme];

  return (
    <div className="flex flex-col items-center justify-center">
      {/* HERO SECTION */}
      <section className="relative w-full overflow-hidden pt-20 pb-16 lg:pt-28 lg:pb-24 border-b border-slate-800/60 bg-gradient-to-b from-slate-950 via-[#090d16] to-[#090d16]">
        {/* Background glow orb */}
        <div className="absolute top-1/4 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[350px] bg-blue-600/15 blur-[120px] rounded-full pointer-events-none" />

        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 relative z-10 text-center">
          <div className="inline-flex items-center gap-2 rounded-full border border-blue-500/30 bg-blue-500/10 px-4 py-1.5 text-xs font-semibold text-blue-400 mb-8 backdrop-blur-md">
            <Sparkles className="h-3.5 w-3.5 text-blue-400 animate-pulse" />
            <span>Next-Gen Enterprise Excel Product Engine</span>
          </div>

          <h1 className="text-4xl sm:text-6xl lg:text-7xl font-extrabold tracking-tight text-white max-w-4xl mx-auto leading-[1.15]">
            Build Production-Grade{' '}
            <span className="bg-gradient-to-r from-blue-400 via-indigo-300 to-amber-300 bg-clip-text text-transparent">
              Excel Products
            </span>{' '}
            at Lightning Speed
          </h1>

          <p className="mt-6 text-lg sm:text-xl text-slate-400 max-w-2xl mx-auto leading-relaxed">
            Decouple spreadsheet mechanics from business domain models. Visually design multi-sheet workbooks,
            configure dynamic KPI cards, apply enterprise color themes, and export flawless `.xlsx` spreadsheets.
          </p>

          <div className="mt-10 flex flex-wrap items-center justify-center gap-4">
            <Link
              href="/studio/new"
              className="flex items-center gap-2 rounded-xl bg-gradient-to-r from-blue-600 to-indigo-600 px-6 py-3.5 text-base font-semibold text-white shadow-xl shadow-blue-500/30 hover:from-blue-500 hover:to-indigo-500 hover:scale-105 transition-all"
            >
              <FileSpreadsheet className="h-5 w-5" />
              <span>Launch Visual Studio</span>
              <ArrowRight className="h-4 w-4" />
            </Link>

            <Link
              href="/ai"
              className="flex items-center gap-2 rounded-xl border border-slate-700 bg-slate-900/80 px-6 py-3.5 text-base font-semibold text-slate-200 hover:bg-slate-800 hover:border-slate-600 transition-all backdrop-blur-md"
            >
              <Sparkles className="h-5 w-5 text-amber-400" />
              <span>AI Prompt Generator</span>
            </Link>

            <Link
              href="/templates"
              className="flex items-center gap-2 rounded-xl border border-slate-800 bg-slate-950/60 px-6 py-3.5 text-base font-medium text-slate-400 hover:text-white hover:border-slate-700 transition-all"
            >
              <Layers className="h-5 w-5 text-blue-400" />
              <span>Explore Templates</span>
            </Link>
          </div>
        </div>
      </section>

      {/* INTERACTIVE PREVIEW PLAYGROUND */}
      <section className="w-full py-16 max-w-7xl px-4 sm:px-6 lg:px-8">
        <div className="glass-panel rounded-2xl p-6 sm:p-8 border border-slate-800 shadow-2xl relative overflow-hidden">
          <div className="flex flex-wrap items-center justify-between gap-4 mb-6 pb-6 border-b border-slate-800">
            <div>
              <h2 className="text-xl font-bold text-white flex items-center gap-2">
                <Table className="h-5 w-5 text-blue-400" />
                Live In-Engine Theme & Canvas Preview
              </h2>
              <p className="text-xs text-slate-400 mt-1">
                Toggle color themes to inspect dynamic typography hierarchy, KPI cards, and data table fills.
              </p>
            </div>

            {/* Theme switcher */}
            <div className="flex items-center gap-2 bg-slate-900/90 p-1.5 rounded-xl border border-slate-800">
              {(['premium', 'midnight', 'forest', 'sunset'] as ThemeName[]).map((t) => (
                <button
                  key={t}
                  onClick={() => setActiveTheme(t)}
                  className={`px-3 py-1.5 text-xs font-semibold rounded-lg capitalize transition-all ${
                    activeTheme === t
                      ? 'bg-blue-600 text-white shadow-md'
                      : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800'
                  }`}
                >
                  {t}
                </button>
              ))}
            </div>
          </div>

          {/* SPREADSHEET MOCKUP */}
          <div
            className="rounded-xl overflow-hidden border border-slate-700/60 shadow-inner"
            style={{ backgroundColor: palette.surface }}
          >
            {/* Banner Header */}
            <div
              className="p-4 sm:p-5 flex items-center justify-between text-white font-bold"
              style={{ backgroundColor: `#${palette.bannerBg}` }}
            >
              <div className="flex items-center gap-3">
                <div className="h-8 w-8 rounded-lg bg-white/10 flex items-center justify-center">
                  <BarChart3 className="h-4 w-4 text-white" />
                </div>
                <div>
                  <h3 className="text-base sm:text-lg font-bold tracking-wide">FINANCIAL OS — REVENUE SUMMARY</h3>
                  <p className="text-xs font-normal opacity-80">Automated Financial Engine • Version 2.4.0</p>
                </div>
              </div>
              <span className="text-xs px-2.5 py-1 rounded bg-white/20 uppercase tracking-widest font-mono">
                {activeTheme}
              </span>
            </div>

            {/* KPI Cards row */}
            <div className="p-4 grid grid-cols-2 sm:grid-cols-4 gap-3 bg-slate-900/40">
              {[
                { label: 'GROSS REVENUE', val: '$6,450,000.00', sub: '+24.5% vs YoY' },
                { label: 'OPERATING EXPENSES', val: '$2,180,000.00', sub: 'Target: $2.4M' },
                { label: 'CUMULATIVE EBITDA', val: '$2,570,000.00', sub: 'Margin: 39.8%' },
                { label: 'AVG PROFIT MARGIN', val: '41.2%', sub: 'Healthy tier' },
              ].map((kpi, idx) => (
                <div
                  key={idx}
                  className="rounded-lg p-3 border text-center transition-all"
                  style={{
                    backgroundColor: `#${palette.kpiBg}`,
                    borderColor: `#${palette.kpiBorder}`,
                  }}
                >
                  <p className="text-[10px] font-bold tracking-wider text-slate-500 uppercase">{kpi.label}</p>
                  <p className="text-base sm:text-lg font-extrabold text-slate-900 mt-0.5">{kpi.val}</p>
                  <p className="text-[10px] text-emerald-600 font-semibold">{kpi.sub}</p>
                </div>
              ))}
            </div>

            {/* Table Mockup */}
            <div className="overflow-x-auto p-4 bg-slate-950/20">
              <table className="w-full text-left text-xs border-collapse">
                <thead>
                  <tr style={{ backgroundColor: `#${palette.headerBg}`, color: `#${palette.headerText}` }}>
                    <th className="py-2.5 px-4 font-bold rounded-l-md">Period</th>
                    <th className="py-2.5 px-4 font-bold text-right">Gross Revenue</th>
                    <th className="py-2.5 px-4 font-bold text-right">Cost of Goods</th>
                    <th className="py-2.5 px-4 font-bold text-right">Operating Expenses</th>
                    <th className="py-2.5 px-4 font-bold text-right">EBITDA</th>
                    <th className="py-2.5 px-4 font-bold text-right rounded-r-md">Net Margin</th>
                  </tr>
                </thead>
                <tbody className="text-slate-800 font-medium divide-y divide-slate-200">
                  {[
                    ['Q1 2026', '$1,250,000.00', '$350,000.00', '$480,000.00', '$420,000.00', '33.6%'],
                    ['Q2 2026', '$1,420,000.00', '$390,000.00', '$510,000.00', '$520,000.00', '36.6%'],
                    ['Q3 2026', '$1,680,000.00', '$440,000.00', '$560,000.00', '$680,000.00', '40.5%'],
                    ['Q4 2026', '$2,100,000.00', '$520,000.00', '$630,000.00', '$950,000.00', '45.2%'],
                  ].map((row, rIdx) => (
                    <tr
                      key={rIdx}
                      style={{
                        backgroundColor: rIdx % 2 === 1 ? `#${palette.zebraBg}` : '#FFFFFF',
                      }}
                    >
                      <td className="py-2.5 px-4 font-semibold text-slate-900">{row[0]}</td>
                      <td className="py-2.5 px-4 text-right font-mono">{row[1]}</td>
                      <td className="py-2.5 px-4 text-right font-mono">{row[2]}</td>
                      <td className="py-2.5 px-4 text-right font-mono">{row[3]}</td>
                      <td className="py-2.5 px-4 text-right font-mono font-bold text-blue-700">{row[4]}</td>
                      <td className="py-2.5 px-4 text-right font-mono font-bold text-emerald-700">{row[5]}</td>
                    </tr>
                  ))}
                  {/* Totals Row */}
                  <tr
                    className="font-bold border-t-2 border-b-4"
                    style={{
                      backgroundColor: `#${palette.totalBg}`,
                      borderColor: `#${palette.bannerBg}`,
                    }}
                  >
                    <td className="py-2.5 px-4 text-slate-900">TOTAL</td>
                    <td className="py-2.5 px-4 text-right font-mono">$6,450,000.00</td>
                    <td className="py-2.5 px-4 text-right font-mono">$1,700,000.00</td>
                    <td className="py-2.5 px-4 text-right font-mono">$2,180,000.00</td>
                    <td className="py-2.5 px-4 text-right font-mono text-blue-800">$2,570,000.00</td>
                    <td className="py-2.5 px-4 text-right font-mono text-emerald-800">39.8%</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </section>

      {/* CORE CAPABILITIES GRID */}
      <section className="w-full py-16 max-w-7xl px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-12">
          <h2 className="text-3xl font-extrabold text-white sm:text-4xl">
            Engineered for Enterprise Spreadsheet Precision
          </h2>
          <p className="mt-3 text-slate-400 max-w-2xl mx-auto">
            Everything you need to turn raw numbers into beautiful, branded financial and operational products.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {[
            {
              icon: Palette,
              title: 'Curated Design Systems',
              desc: 'Automatic typography scale, alternating zebra striping, currency & percent formatting, and 4 high-contrast color palettes.',
              color: 'text-amber-400 bg-amber-500/10 border-amber-500/20',
            },
            {
              icon: Zap,
              title: 'Dynamic KPI Metric Cards',
              desc: 'Auto-generates high-visibility KPI summary blocks with native Excel formula aggregations (SUM, AVG, COUNT, MIN, MAX).',
              color: 'text-blue-400 bg-blue-500/10 border-blue-500/20',
            },
            {
              icon: Sparkles,
              title: 'AI Prompt-to-Workbook Bridge',
              desc: 'Convert natural language prompts into complete, multi-sheet workbook schemas with realistic sample data in seconds.',
              color: 'text-purple-400 bg-purple-500/10 border-purple-500/20',
            },
            {
              icon: Table,
              title: 'Visual Multi-Sheet Studio',
              desc: 'Interactive web builder to configure columns, data types, formula expressions, and grid rows with instant live preview.',
              color: 'text-emerald-400 bg-emerald-500/10 border-emerald-500/20',
            },
            {
              icon: ShieldCheck,
              title: 'Formula Verification & Protection',
              desc: 'Pre-export validation preventing #REF!, circular references, and broken formula coordinates before downloading.',
              color: 'text-cyan-400 bg-cyan-500/10 border-cyan-500/20',
            },
            {
              icon: Download,
              title: 'Dual Engine XLSX Compiler',
              desc: 'Instant in-browser compilation with ExcelJS or headless cloud synthesis via Next.js and FastAPI REST APIs.',
              color: 'text-rose-400 bg-rose-500/10 border-rose-500/20',
            },
          ].map((item, idx) => {
            const Icon = item.icon;
            return (
              <div key={idx} className="glass-panel glass-panel-hover rounded-2xl p-6 border border-slate-800">
                <div className={`h-12 w-12 rounded-xl flex items-center justify-center border mb-5 ${item.color}`}>
                  <Icon className="h-6 w-6" />
                </div>
                <h3 className="text-lg font-bold text-white mb-2">{item.title}</h3>
                <p className="text-sm text-slate-400 leading-relaxed">{item.desc}</p>
              </div>
            );
          })}
        </div>
      </section>

      {/* CTA BANNER */}
      <section className="w-full py-16 max-w-7xl px-4 sm:px-6 lg:px-8 mb-12">
        <div className="relative rounded-3xl bg-gradient-to-r from-blue-900/60 via-indigo-900/40 to-slate-900 p-8 sm:p-12 border border-blue-500/30 overflow-hidden text-center">
          <div className="relative z-10 max-w-3xl mx-auto">
            <h2 className="text-3xl font-extrabold text-white sm:text-4xl">
              Ready to create your next Excel product?
            </h2>
            <p className="mt-4 text-slate-300 text-base sm:text-lg">
              Start from scratch in our Visual Studio or pick one of our enterprise-tested templates.
            </p>
            <div className="mt-8 flex flex-wrap justify-center gap-4">
              <Link
                href="/studio/new"
                className="rounded-xl bg-white px-6 py-3.5 text-base font-bold text-slate-950 shadow-lg hover:bg-slate-100 transition-all hover:scale-105"
              >
                Open Visual Studio
              </Link>
              <Link
                href="/templates"
                className="rounded-xl border border-white/20 bg-white/10 px-6 py-3.5 text-base font-semibold text-white hover:bg-white/20 transition-all"
              >
                Browse Templates
              </Link>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}
