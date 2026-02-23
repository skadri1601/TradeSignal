import { ReactNode } from 'react';
import DashboardNavbar from './DashboardNavbar';
import GlobalFooter from './GlobalFooter';

interface LayoutProps {
  children: ReactNode;
}

export default function Layout({ children }: LayoutProps) {
  return (
    <div className="min-h-screen bg-black text-white selection:bg-purple-500/30 font-sans">
      <DashboardNavbar />
      <div className="flex flex-col min-h-screen pt-24">
        <main className="flex-grow px-4 sm:px-6 lg:px-8 max-w-7xl mx-auto w-full">
          {children}
        </main>
        <GlobalFooter />
      </div>
    </div>
  );
}