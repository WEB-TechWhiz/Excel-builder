import type { Metadata } from 'next';
import Navbar from '../components/Navbar';
import './globals.css';

export const metadata: Metadata = {
  title: 'Excel Product Studio & Engine — Enterprise Full-Stack Suite',
  description: 'Design, build, validate, and export production-grade Excel products, financial models, and business dashboards declaratively with AI.',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark">
      <body className="min-h-screen bg-[#090d16] text-slate-100 antialiased flex flex-col selection:bg-blue-600 selection:text-white">
        <Navbar />
        <main className="flex-1 flex flex-col">{children}</main>
        <footer className="border-t border-slate-800/60 bg-slate-950/60 py-6 text-center text-xs text-slate-500">
          <p>© 2026 Excel Product Engine & Studio Suite. Built with React 19, Next.js & ExcelJS.</p>
        </footer>
      </body>
    </html>
  );
}
