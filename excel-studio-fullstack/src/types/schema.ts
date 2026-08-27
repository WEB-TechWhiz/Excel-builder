export type ColumnType = 'text' | 'number' | 'currency' | 'percent' | 'date' | 'formula';

export interface Column {
  key: string;
  label: string;
  type: ColumnType;
  formula?: string;
  width?: number;
}

export type KPIAggregation = 'sum' | 'avg' | 'count' | 'min' | 'max';

export interface KPI {
  id?: string;
  label: string;
  aggregation: KPIAggregation;
  column: string;
  target?: number;
  format?: 'currency' | 'number' | 'percent';
}

export interface Sheet {
  id: string;
  name: string;
  description?: string;
  columns: Column[];
  rows: string[][];
  kpis: KPI[];
}

export type ThemeName = 'premium' | 'midnight' | 'forest' | 'sunset';

export interface Product {
  id: string;
  name: string;
  version: string;
  author: string;
  currency: string;
  dateFormat: string;
  theme: ThemeName;
  sheets: Sheet[];
  created_at?: string;
  updated_at?: string;
}

export interface BuildRecord {
  id: string;
  product_id?: string;
  product_name: string;
  file_name: string;
  sheet_count: number;
  row_count: number;
  byte_size: number;
  created_at: string;
}

export interface ThemeColors {
  name: string;
  primary: string;
  primaryDark: string;
  secondary: string;
  accent: string;
  surface: string;
  surfaceMuted: string;
  border: string;
  text: string;
  textMuted: string;
  bannerBg: string;
  bannerText: string;
  kpiBg: string;
  kpiBorder: string;
  headerBg: string;
  headerText: string;
  zebraBg: string;
  totalBg: string;
}
