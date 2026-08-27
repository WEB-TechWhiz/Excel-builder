import { Product } from '../types/schema';
import { TEMPLATES } from './templates';

const STORAGE_KEY = 'excel_studio_products';

export function getStoredProducts(): Product[] {
  if (typeof window === 'undefined') return TEMPLATES;
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(TEMPLATES));
      return TEMPLATES;
    }
    return JSON.parse(raw);
  } catch {
    return TEMPLATES;
  }
}

export function saveProduct(product: Product): Product {
  const products = getStoredProducts();
  const index = products.findIndex((p) => p.id === product.id);
  const now = new Date().toISOString();
  const updatedProduct = {
    ...product,
    updated_at: now,
    created_at: product.created_at || now,
  };

  if (index >= 0) {
    products[index] = updatedProduct;
  } else {
    products.unshift(updatedProduct);
  }

  if (typeof window !== 'undefined') {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(products));
  }
  return updatedProduct;
}

export function getProductById(id: string): Product | undefined {
  const products = getStoredProducts();
  return products.find((p) => p.id === id);
}

export function deleteProduct(id: string): void {
  const products = getStoredProducts().filter((p) => p.id !== id);
  if (typeof window !== 'undefined') {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(products));
  }
}

export function createNewProduct(): Product {
  const id = 'prod_' + Math.random().toString(36).substring(2, 9);
  const newProduct: Product = {
    id,
    name: 'Untitled Spreadsheet Product',
    version: '1.0.0',
    author: 'Studio Creator',
    currency: 'USD',
    dateFormat: 'YYYY-MM-DD',
    theme: 'premium',
    sheets: [
      {
        id: 'sheet_1',
        name: 'Sheet 1',
        description: 'Primary data sheet',
        columns: [
          { key: 'item', label: 'Item Name', type: 'text' },
          { key: 'category', label: 'Category', type: 'text' },
          { key: 'amount', label: 'Amount ($)', type: 'currency' },
        ],
        kpis: [
          { label: 'Total Amount', aggregation: 'sum', column: 'amount', format: 'currency' },
          { label: 'Item Count', aggregation: 'count', column: 'item', format: 'number' },
        ],
        rows: [
          ['Consulting Service', 'Services', '4500'],
          ['Software Subscription', 'SaaS', '1200'],
          ['Hardware Purchase', 'Capital Goods', '3800'],
        ],
      },
    ],
  };
  return saveProduct(newProduct);
}
