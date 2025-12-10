import { ReactNode } from 'react';
import Sidebar from './Sidebar';
import TopBar from './TopBar';
import GlobalFooter from './GlobalFooter';

interface LayoutProps {
  children: ReactNode;
}

export default function Layout({ children }: LayoutProps) {
  return (
    <div className="min-h-screen bg-[#0a0a0a] text-white">
      <Sidebar />
      <div className="ml-64 flex flex-col min-h-screen">
        <TopBar />
        <main className="p-8 flex-grow">
          {children}
        </main>
        <GlobalFooter />
      </div>
    </div>
  );
}
