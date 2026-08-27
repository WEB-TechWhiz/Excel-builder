import { NextRequest, NextResponse } from 'next/server';
import { Product, Sheet, Column, KPI, ThemeName, ColumnType } from '../../../types/schema';

interface UploadedFilePayload {
  name: string;
  type: string;
  size: number;
  content?: string;
  base64?: string;
  parsedSheets?: {
    name: string;
    columns: string[];
    rows: string[][];
  }[];
}

// Helper to infer column type from values
function inferColumnType(values: string[], colName: string): ColumnType {
  const name = colName.toLowerCase();
  if (name.includes('price') || name.includes('cost') || name.includes('revenue') || name.includes('amount') || name.includes('mrr') || name.includes('arr') || name.includes('salary') || name.includes('val') || name.includes('$')) {
    return 'currency';
  }
  if (name.includes('rate') || name.includes('percent') || name.includes('margin') || name.includes('ratio') || name.includes('%') || name.includes('probability')) {
    return 'percent';
  }
  if (name.includes('date') || name.includes('time') || name.includes('period') || name.includes('month') || name.includes('year') || name.includes('quarter')) {
    return 'date';
  }

  const sample = values.filter((v) => v && v.trim()).slice(0, 10);
  if (sample.length === 0) return 'text';

  const isAllNumeric = sample.every((v) => !isNaN(parseFloat(v.replace(/[$,%]/g, ''))));
  if (isAllNumeric) {
    if (sample.some((v) => v.includes('$'))) return 'currency';
    if (sample.some((v) => v.includes('%'))) return 'percent';
    return 'number';
  }

  return 'text';
}

// Convert parsed spreadsheet / CSV data into a styled Product specification
function convertParsedDataToProduct(file: UploadedFilePayload, userPrompt: string): Product {
  const id = 'prod_upload_' + Math.random().toString(36).substring(2, 9);
  const cleanName = file.name.replace(/\.[^/.]+$/, '').replace(/[-_]/g, ' ');
  const titleName = cleanName.charAt(0).toUpperCase() + cleanName.slice(1);

  // Pick theme based on file or prompt
  const p = (userPrompt + ' ' + file.name).toLowerCase();
  let theme: ThemeName = 'premium';
  if (p.includes('saas') || p.includes('tech') || p.includes('cloud') || p.includes('dark')) theme = 'midnight';
  else if (p.includes('sale') || p.includes('crm') || p.includes('revenue') || p.includes('green')) theme = 'forest';
  else if (p.includes('stock') || p.includes('invent') || p.includes('order') || p.includes('amber')) theme = 'sunset';

  const sheets: Sheet[] = [];

  if (file.parsedSheets && file.parsedSheets.length > 0) {
    file.parsedSheets.forEach((parsedSheet, sIdx) => {
      const colNames = parsedSheet.columns && parsedSheet.columns.length > 0
        ? parsedSheet.columns
        : ['Column A', 'Column B', 'Column C'];

      const columns: Column[] = colNames.map((colLabel, colIdx) => {
        const sampleValues = parsedSheet.rows.map((r) => r[colIdx] || '');
        const colType = inferColumnType(sampleValues, colLabel);
        return {
          key: `col_${colIdx}_` + colLabel.toLowerCase().replace(/[^a-z0-9]/g, '_').slice(0, 20),
          label: colLabel,
          type: colType,
        };
      });

      // Generate KPIs for numeric/currency columns
      const kpis: KPI[] = [];
      columns.forEach((col) => {
        if ((col.type === 'currency' || col.type === 'number') && kpis.length < 4) {
          kpis.push({
            label: `Total ${col.label}`,
            aggregation: 'sum',
            column: col.key,
            format: col.type === 'currency' ? 'currency' : 'number',
          });
        } else if (col.type === 'percent' && kpis.length < 4) {
          kpis.push({
            label: `Avg ${col.label}`,
            aggregation: 'avg',
            column: col.key,
            format: 'percent',
          });
        }
      });

      if (kpis.length === 0 && columns.length > 0) {
        kpis.push({
          label: 'Total Records',
          aggregation: 'count',
          column: columns[0].key,
          format: 'number',
        });
      }

      sheets.push({
        id: `sheet_${sIdx}_` + Math.random().toString(36).substring(2, 6),
        name: parsedSheet.name || `Sheet ${sIdx + 1}`,
        description: `Imported and enhanced from ${file.name}`,
        columns,
        rows: parsedSheet.rows.slice(0, 200),
        kpis,
      });
    });
  } else if (file.content) {
    // Parse CSV or raw text lines
    const lines = file.content.split(/\r?\n/).filter((l) => l.trim().length > 0);
    const headers = lines[0] ? lines[0].split(',').map((h) => h.replace(/^["']|["']$/g, '').trim()) : ['Col 1', 'Col 2'];
    const dataRows = lines.slice(1).map((l) => l.split(',').map((c) => c.replace(/^["']|["']$/g, '').trim()));

    const columns: Column[] = headers.map((h, idx) => {
      const sampleVals = dataRows.map((r) => r[idx] || '');
      return {
        key: `col_${idx}_` + h.toLowerCase().replace(/[^a-z0-9]/g, '_'),
        label: h,
        type: inferColumnType(sampleVals, h),
      };
    });

    const kpis: KPI[] = [];
    columns.forEach((col) => {
      if ((col.type === 'currency' || col.type === 'number') && kpis.length < 4) {
        kpis.push({
          label: `Total ${col.label}`,
          aggregation: 'sum',
          column: col.key,
          format: col.type === 'currency' ? 'currency' : 'number',
        });
      }
    });

    sheets.push({
      id: 'sheet_uploaded_1',
      name: titleName || 'Data Overview',
      description: `Structured dataset extracted from ${file.name}`,
      columns,
      rows: dataRows.slice(0, 200),
      kpis,
    });
  }

  return {
    id,
    name: `${titleName} — AI Enhanced Suite`,
    version: '1.0.0',
    author: 'AI Copilot',
    currency: 'USD',
    dateFormat: 'YYYY-MM-DD',
    theme,
    sheets: sheets.length > 0 ? sheets : [
      {
        id: 'sheet_fallback',
        name: 'Overview',
        columns: [{ key: 'item', label: 'Item Name', type: 'text' }, { key: 'amount', label: 'Amount ($)', type: 'currency' }],
        rows: [['Sample A', '1500'], ['Sample B', '3400']],
        kpis: [{ label: 'Total Amount', aggregation: 'sum', column: 'amount', format: 'currency' }],
      },
    ],
  };
}

// Built-in intelligent template synthesizer fallback
function synthesizeWorkbookFromPrompt(prompt: string): Product {
  const p = prompt.toLowerCase();
  const id = 'ai_prod_' + Math.random().toString(36).substring(2, 8);

  if (p.includes('saas') || p.includes('mrr') || p.includes('arr') || p.includes('churn') || p.includes('subscription')) {
    return {
      id,
      name: 'AI-Generated SaaS Metrics & Cohort Analyzer',
      version: '1.0.0',
      author: 'AI Copilot',
      currency: 'USD',
      dateFormat: 'YYYY-MM-DD',
      theme: 'midnight',
      sheets: [
        {
          id: 'ai_saas_metrics',
          name: 'SaaS Unit Economics',
          description: 'Key SaaS recurring revenue indicators generated by AI',
          columns: [
            { key: 'period', label: 'Month', type: 'text' },
            { key: 'new_mrr', label: 'New MRR ($)', type: 'currency' },
            { key: 'expansion', label: 'Expansion ($)', type: 'currency' },
            { key: 'churn', label: 'Churn ($)', type: 'currency' },
            { key: 'net_mrr', label: 'Net MRR ($)', type: 'currency' },
            { key: 'churn_rate', label: 'Churn Rate (%)', type: 'percent' },
          ],
          kpis: [
            { label: 'Total New Bookings', aggregation: 'sum', column: 'new_mrr', format: 'currency' },
            { label: 'Total Churn Losses', aggregation: 'sum', column: 'churn', format: 'currency' },
            { label: 'Average Churn Rate', aggregation: 'avg', column: 'churn_rate', format: 'percent' },
          ],
          rows: [
            ['Jan 2026', '54000', '18000', '6500', '65500', '2.4%'],
            ['Feb 2026', '62000', '21000', '7200', '75800', '2.2%'],
            ['Mar 2026', '71000', '25000', '7800', '88200', '2.0%'],
            ['Apr 2026', '84000', '29000', '8400', '104600', '1.8%'],
          ],
        },
      ],
    };
  }

  if (p.includes('crm') || p.includes('sale') || p.includes('lead') || p.includes('pipeline') || p.includes('deal')) {
    return {
      id,
      name: 'AI-Generated Sales Pipeline & Win-Loss Model',
      version: '1.0.0',
      author: 'AI Copilot',
      currency: 'USD',
      dateFormat: 'YYYY-MM-DD',
      theme: 'forest',
      sheets: [
        {
          id: 'ai_sales_crm',
          name: 'Sales Pipeline Tracker',
          description: 'Deal flow, assigned reps, and forecast conversion',
          columns: [
            { key: 'deal_name', label: 'Prospect / Client', type: 'text' },
            { key: 'owner', label: 'Deal Owner', type: 'text' },
            { key: 'stage', label: 'Current Stage', type: 'text' },
            { key: 'value', label: 'Contract Value ($)', type: 'currency' },
            { key: 'probability', label: 'Win Probability (%)', type: 'percent' },
          ],
          kpis: [
            { label: 'Total Pipeline Value', aggregation: 'sum', column: 'value', format: 'currency' },
            { label: 'Avg Probability', aggregation: 'avg', column: 'probability', format: 'percent' },
          ],
          rows: [
            ['Apex FinTech Systems', 'Alex Morgan', 'Negotiation', '125000', '85%'],
            ['Quantum Healthcare', 'Sarah Jenkins', 'Proposal Sent', '240000', '60%'],
            ['Starlight Logistics', 'David Chen', 'Discovery', '85000', '35%'],
            ['HyperScale Cloud', 'Elena Rostova', 'Closing', '320000', '90%'],
          ],
        },
      ],
    };
  }

  if (p.includes('invent') || p.includes('warehouse') || p.includes('stock') || p.includes('supply') || p.includes('order')) {
    return {
      id,
      name: 'AI-Generated Inventory & Reorder System',
      version: '1.0.0',
      author: 'AI Copilot',
      currency: 'USD',
      dateFormat: 'YYYY-MM-DD',
      theme: 'sunset',
      sheets: [
        {
          id: 'ai_inventory',
          name: 'Warehouse Stock Control',
          description: 'SKU counts, storage limits, and unit valuation',
          columns: [
            { key: 'sku', label: 'SKU Code', type: 'text' },
            { key: 'item', label: 'Item Description', type: 'text' },
            { key: 'quantity', label: 'Quantity on Hand', type: 'number' },
            { key: 'unit_price', label: 'Unit Cost ($)', type: 'currency' },
            { key: 'total_val', label: 'Total Asset Value ($)', type: 'currency' },
          ],
          kpis: [
            { label: 'Total Units Stocked', aggregation: 'sum', column: 'quantity', format: 'number' },
            { label: 'Total Stock Valuation', aggregation: 'sum', column: 'total_val', format: 'currency' },
          ],
          rows: [
            ['SKU-501', 'Smart IoT Sensor Module', '2400', '45', '108000'],
            ['SKU-502', 'High-Density Lithium Pack', '650', '280', '182000'],
            ['SKU-503', 'Aluminum Enclosure 4U', '420', '110', '46200'],
          ],
        },
      ],
    };
  }

  // Default financial model synthesis
  return {
    id,
    name: `AI-Generated Model: ${prompt.slice(0, 40)}`,
    version: '1.0.0',
    author: 'AI Copilot',
    currency: 'USD',
    dateFormat: 'YYYY-MM-DD',
    theme: 'premium',
    sheets: [
      {
        id: 'ai_custom_sheet',
        name: 'Financial Overview',
        description: 'Auto-synthesized dataset according to your prompt parameters',
        columns: [
          { key: 'line_item', label: 'Line Item', type: 'text' },
          { key: 'category', label: 'Classification', type: 'text' },
          { key: 'target_q1', label: 'Q1 Target ($)', type: 'currency' },
          { key: 'actual_q1', label: 'Q1 Actual ($)', type: 'currency' },
          { key: 'variance', label: 'Variance ($)', type: 'currency' },
        ],
        kpis: [
          { label: 'Total Budgeted Target', aggregation: 'sum', column: 'target_q1', format: 'currency' },
          { label: 'Total Actual Spend', aggregation: 'sum', column: 'actual_q1', format: 'currency' },
        ],
        rows: [
          ['Product R&D & Engineering', 'Direct OpEx', '350000', '325000', '-25000'],
          ['Cloud Infrastructure & DB', 'COGS', '120000', '118000', '-2000'],
          ['Growth & Performance Ads', 'Marketing', '220000', '245000', '25000'],
          ['Executive & Legal Support', 'G&A', '85000', '81000', '-4000'],
        ],
      },
    ],
  };
}

export async function POST(req: NextRequest) {
  try {
    const body = await req.json();
    const { prompt, file } = body;

    const userPrompt = (prompt || '').trim();
    const uploadedFile: UploadedFilePayload | undefined = file;

    if (!userPrompt && !uploadedFile) {
      return NextResponse.json({ error: 'Please enter a description or upload a file.' }, { status: 400 });
    }

    const apiKey = process.env.OPENAI_API_KEY;

    if (apiKey) {
      try {
        let userContent = userPrompt || 'Analyze and format this uploaded spreadsheet file into an enterprise product.';
        if (uploadedFile) {
          userContent += `\n\nUploaded File: ${uploadedFile.name} (${uploadedFile.type}, ${uploadedFile.size} bytes)`;
          if (uploadedFile.parsedSheets && uploadedFile.parsedSheets.length > 0) {
            userContent += `\nFile Content Excerpt:\n` + JSON.stringify(uploadedFile.parsedSheets.slice(0, 3));
          } else if (uploadedFile.content) {
            userContent += `\nFile Content Excerpt:\n` + uploadedFile.content.slice(0, 3000);
          }
        }

        const res = await fetch('https://api.openai.com/v1/chat/completions', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            Authorization: `Bearer ${apiKey}`,
          },
          body: JSON.stringify({
            model: 'gpt-4o-mini',
            temperature: 0.2,
            response_format: { type: 'json_object' },
            messages: [
              {
                role: 'system',
                content: `You are an expert Excel template architect. Generate a complete Product specification in JSON with properties:
                {
                  "name": string,
                  "version": "1.0.0",
                  "author": "AI Copilot",
                  "currency": "USD",
                  "dateFormat": "YYYY-MM-DD",
                  "theme": "premium" | "midnight" | "forest" | "sunset",
                  "sheets": [
                    {
                      "id": string,
                      "name": string,
                      "description": string,
                      "columns": [ { "key": string, "label": string, "type": "text"|"number"|"currency"|"percent"|"date" } ],
                      "rows": string[][],
                      "kpis": [ { "label": string, "aggregation": "sum"|"avg"|"count"|"min"|"max", "column": string, "format": "currency"|"number"|"percent" } ]
                    }
                  ]
                }`,
              },
              { role: 'user', content: userContent },
            ],
          }),
        });

        if (res.ok) {
          const data = await res.json();
          const parsed = JSON.parse(data.choices[0].message.content);
          if (parsed && parsed.sheets && parsed.sheets.length > 0) {
            parsed.id = 'ai_' + Math.random().toString(36).substring(2, 9);
            return NextResponse.json({ success: true, product: parsed });
          }
        }
      } catch (llmErr) {
        console.warn('[AI Endpoint] LLM call failed, falling back to smart synthesizer:', llmErr);
      }
    }

    // Fallback: If file was uploaded, convert it directly into a clean Product specification!
    if (uploadedFile) {
      const synthesizedFromUpload = convertParsedDataToProduct(uploadedFile, userPrompt);
      return NextResponse.json({ success: true, product: synthesizedFromUpload });
    }

    // Fallback: prompt based synthesizer
    const synthesized = synthesizeWorkbookFromPrompt(userPrompt);
    return NextResponse.json({ success: true, product: synthesized });
  } catch (err: any) {
    console.error('[API/AI] Error:', err);
    return NextResponse.json({ error: err.message || 'Failed to synthesize spreadsheet.' }, { status: 500 });
  }
}
