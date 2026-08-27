import ExcelJS from 'exceljs';
import { Product, Sheet, Column, KPI, ThemeName } from '../types/schema';
import { PALETTES } from './palettes';

export class ExcelProductEngine {
  private product: Product;

  constructor(product: Product) {
    this.product = product;
  }

  public async generateWorkbook(): Promise<ExcelJS.Workbook> {
    const workbook = new ExcelJS.Workbook();
    workbook.creator = this.product.author || 'Excel Product Studio';
    workbook.lastModifiedBy = this.product.author || 'Excel Product Studio';
    workbook.created = new Date();
    workbook.modified = new Date();
    workbook.title = this.product.name;

    const palette = PALETTES[this.product.theme] || PALETTES.premium;

    for (const sheetData of this.product.sheets) {
      this.buildSheet(workbook, sheetData, palette);
    }

    return workbook;
  }

  private buildSheet(workbook: ExcelJS.Workbook, sheetData: Sheet, palette: typeof PALETTES.premium) {
    const worksheet = workbook.addWorksheet(sheetData.name, {
      views: [{ showGridLines: true }],
    });

    let currentRow = 1;
    const colCount = Math.max(sheetData.columns.length, 6);

    // 1. BANNER HEADER
    worksheet.mergeCells(currentRow, 1, currentRow + 1, colCount);
    const bannerCell = worksheet.getCell(currentRow, 1);
    bannerCell.value = `📊  ${this.product.name.toUpperCase()} — ${sheetData.name.toUpperCase()}`;
    bannerCell.font = {
      name: 'Segoe UI',
      size: 14,
      bold: true,
      color: { argb: 'FF' + palette.bannerText },
    };
    bannerCell.alignment = { vertical: 'middle', horizontal: 'left', indent: 1 };
    bannerCell.fill = {
      type: 'pattern',
      pattern: 'solid',
      fgColor: { argb: 'FF' + palette.bannerBg },
    };

    currentRow += 3; // Gap after banner

    // 2. KPI CARDS SECTION (if any KPIs exist)
    if (sheetData.kpis && sheetData.kpis.length > 0) {
      const kpis = sheetData.kpis.slice(0, 4);
      const kpiSpan = Math.max(1, Math.floor(colCount / kpis.length));

      // Row for KPI Labels
      kpis.forEach((kpi, index) => {
        const startCol = index * kpiSpan + 1;
        const endCol = Math.min(startCol + kpiSpan - 1, colCount);

        if (startCol < endCol) {
          worksheet.mergeCells(currentRow, startCol, currentRow, endCol);
        }
        const labelCell = worksheet.getCell(currentRow, startCol);
        labelCell.value = kpi.label.toUpperCase();
        labelCell.font = { name: 'Segoe UI', size: 9, bold: true, color: { argb: 'FF64748B' } };
        labelCell.alignment = { horizontal: 'center', vertical: 'middle' };
        labelCell.fill = { type: 'pattern', pattern: 'solid', fgColor: { argb: 'FF' + palette.kpiBg } };

        // Value row
        const valRow = currentRow + 1;
        if (startCol < endCol) {
          worksheet.mergeCells(valRow, startCol, valRow, endCol);
        }
        const valueCell = worksheet.getCell(valRow, startCol);
        
        // Find column index
        const colIdx = sheetData.columns.findIndex((c) => c.key === kpi.column || c.label === kpi.column);
        const colLetter = colIdx !== -1 ? String.fromCharCode(65 + colIdx) : 'C';
        const dataStartRow = currentRow + 4; // Start of data table
        const dataEndRow = dataStartRow + Math.max(sheetData.rows.length - 1, 0);

        if (kpi.aggregation === 'sum') {
          valueCell.value = { formula: `SUM(${colLetter}${dataStartRow}:${colLetter}${dataEndRow})` };
        } else if (kpi.aggregation === 'avg') {
          valueCell.value = { formula: `AVERAGE(${colLetter}${dataStartRow}:${colLetter}${dataEndRow})` };
        } else if (kpi.aggregation === 'count') {
          valueCell.value = { formula: `COUNTA(${colLetter}${dataStartRow}:${colLetter}${dataEndRow})` };
        } else if (kpi.aggregation === 'max') {
          valueCell.value = { formula: `MAX(${colLetter}${dataStartRow}:${colLetter}${dataEndRow})` };
        } else if (kpi.aggregation === 'min') {
          valueCell.value = { formula: `MIN(${colLetter}${dataStartRow}:${colLetter}${dataEndRow})` };
        } else {
          valueCell.value = 0;
        }

        valueCell.font = { name: 'Segoe UI', size: 14, bold: true, color: { argb: 'FF' + palette.bannerBg } };
        valueCell.alignment = { horizontal: 'center', vertical: 'middle' };
        valueCell.fill = { type: 'pattern', pattern: 'solid', fgColor: { argb: 'FF' + palette.kpiBg } };

        // Format
        if (kpi.format === 'currency' || (!kpi.format && sheetData.columns[colIdx]?.type === 'currency')) {
          valueCell.numFmt = '$#,##0.00';
        } else if (kpi.format === 'percent' || (!kpi.format && sheetData.columns[colIdx]?.type === 'percent')) {
          valueCell.numFmt = '0.0%';
        } else {
          valueCell.numFmt = '#,##0';
        }

        // Card borders
        for (let r = currentRow; r <= valRow; r++) {
          for (let c = startCol; c <= endCol; c++) {
            worksheet.getCell(r, c).border = {
              top: { style: 'thin', color: { argb: 'FF' + palette.kpiBorder } },
              left: { style: 'thin', color: { argb: 'FF' + palette.kpiBorder } },
              bottom: { style: 'thin', color: { argb: 'FF' + palette.kpiBorder } },
              right: { style: 'thin', color: { argb: 'FF' + palette.kpiBorder } },
            };
          }
        }
      });

      currentRow += 3; // Gap after KPI section
    }

    // 3. TABLE SECTION
    const tableHeaderRow = currentRow;
    sheetData.columns.forEach((col, idx) => {
      const cell = worksheet.getCell(tableHeaderRow, idx + 1);
      cell.value = col.label;
      cell.font = { name: 'Segoe UI', size: 11, bold: true, color: { argb: 'FF' + palette.headerText } };
      cell.fill = { type: 'pattern', pattern: 'solid', fgColor: { argb: 'FF' + palette.headerBg } };
      cell.alignment = {
        vertical: 'middle',
        horizontal: col.type === 'number' || col.type === 'currency' || col.type === 'percent' ? 'right' : 'left',
      };
      cell.border = {
        top: { style: 'medium', color: { argb: 'FF' + palette.bannerBg } },
        bottom: { style: 'medium', color: { argb: 'FF' + palette.bannerBg } },
      };
    });

    currentRow++;

    // 4. DATA ROWS
    sheetData.rows.forEach((row, rowIdx) => {
      const isZebra = rowIdx % 2 === 1;
      const rowFillColor = isZebra ? palette.zebraBg : 'FFFFFF';

      sheetData.columns.forEach((col, colIdx) => {
        const cell = worksheet.getCell(currentRow, colIdx + 1);
        const rawVal = row[colIdx] ?? '';

        if (col.type === 'number') {
          const num = parseFloat(rawVal);
          cell.value = isNaN(num) ? rawVal : num;
          cell.numFmt = '#,##0.00';
          cell.alignment = { horizontal: 'right' };
        } else if (col.type === 'currency') {
          const num = parseFloat(rawVal.replace(/[^0-9.-]+/g, ''));
          cell.value = isNaN(num) ? rawVal : num;
          cell.numFmt = '$#,##0.00';
          cell.alignment = { horizontal: 'right' };
        } else if (col.type === 'percent') {
          let num = parseFloat(rawVal.replace('%', ''));
          if (!isNaN(num) && num > 1) num = num / 100;
          cell.value = isNaN(num) ? rawVal : num;
          cell.numFmt = '0.0%';
          cell.alignment = { horizontal: 'right' };
        } else {
          cell.value = rawVal;
          cell.alignment = { horizontal: 'left' };
        }

        cell.font = { name: 'Segoe UI', size: 10, color: { argb: 'FF1E293B' } };
        cell.fill = { type: 'pattern', pattern: 'solid', fgColor: { argb: 'FF' + rowFillColor } };
        cell.border = {
          bottom: { style: 'thin', color: { argb: 'FFE2E8F0' } },
        };
      });

      currentRow++;
    });

    // 5. TOTALS ROW (if numerical data exists)
    if (sheetData.rows.length > 0) {
      const hasNumeric = sheetData.columns.some((c) => c.type === 'currency' || c.type === 'number');
      if (hasNumeric) {
        sheetData.columns.forEach((col, colIdx) => {
          const cell = worksheet.getCell(currentRow, colIdx + 1);
          const colLetter = String.fromCharCode(65 + colIdx);
          const startR = tableHeaderRow + 1;
          const endR = currentRow - 1;

          if (colIdx === 0) {
            cell.value = 'TOTAL';
            cell.font = { name: 'Segoe UI', size: 11, bold: true, color: { argb: 'FF0F172A' } };
            cell.alignment = { horizontal: 'left' };
          } else if (col.type === 'currency') {
            cell.value = { formula: `SUM(${colLetter}${startR}:${colLetter}${endR})` };
            cell.numFmt = '$#,##0.00';
            cell.font = { name: 'Segoe UI', size: 11, bold: true, color: { argb: 'FF0F172A' } };
            cell.alignment = { horizontal: 'right' };
          } else if (col.type === 'number') {
            cell.value = { formula: `SUM(${colLetter}${startR}:${colLetter}${endR})` };
            cell.numFmt = '#,##0.00';
            cell.font = { name: 'Segoe UI', size: 11, bold: true, color: { argb: 'FF0F172A' } };
            cell.alignment = { horizontal: 'right' };
          }

          cell.fill = { type: 'pattern', pattern: 'solid', fgColor: { argb: 'FF' + palette.totalBg } };
          cell.border = {
            top: { style: 'thin', color: { argb: 'FF' + palette.bannerBg } },
            bottom: { style: 'double', color: { argb: 'FF' + palette.bannerBg } },
          };
        });
      }
    }

    // Auto calculate column widths
    worksheet.columns.forEach((column) => {
      let maxLen = 12;
      column.eachCell?.({ includeEmpty: true }, (cell) => {
        const len = cell.value ? String(cell.value).length : 0;
        if (len > maxLen) maxLen = Math.min(len + 4, 40);
      });
      column.width = maxLen;
    });
  }

  public async exportAsBuffer(): Promise<ArrayBuffer> {
    const workbook = await this.generateWorkbook();
    return await workbook.xlsx.writeBuffer();
  }

  public async exportAsBase64(): Promise<string> {
    const buffer = await this.exportAsBuffer();
    return Buffer.from(buffer).toString('base64');
  }
}
