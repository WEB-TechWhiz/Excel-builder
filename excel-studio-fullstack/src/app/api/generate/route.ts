import { NextRequest, NextResponse } from 'next/server';
import { ExcelProductEngine } from '../../../lib/excel-engine';
import { Product } from '../../../types/schema';

export async function POST(req: NextRequest) {
  try {
    const body = await req.json();
    const product: Product = body.product || body;

    if (!product || !product.sheets || !Array.isArray(product.sheets)) {
      return NextResponse.json(
        { error: 'Invalid product specification. Sheets array is required.' },
        { status: 400 }
      );
    }

    const engine = new ExcelProductEngine(product);
    const buffer = await engine.exportAsBuffer();

    const fileName = `${(product.name || 'workbook').toLowerCase().replace(/[^a-z0-9]/g, '_')}_v${product.version || '1.0.0'}.xlsx`;

    // Return the binary file stream
    return new NextResponse(buffer, {
      status: 200,
      headers: {
        'Content-Type': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        'Content-Disposition': `attachment; filename="${fileName}"`,
        'X-File-Name': fileName,
        'X-Sheet-Count': String(product.sheets.length),
      },
    });
  } catch (err: any) {
    console.error('[API/Generate] Error:', err);
    return NextResponse.json(
      { error: 'Failed to compile Excel workbook: ' + (err.message || String(err)) },
      { status: 500 }
    );
  }
}
