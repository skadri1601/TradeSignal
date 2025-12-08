import React from 'react';
import PublicNavbar from '../public/PublicNavbar';
import GlobalFooter from './GlobalFooter';
import { Outlet } from 'react-router-dom';

const PublicLayout = ({ children }: { children?: React.ReactNode }) => {
  return (
    <div className="min-h-screen bg-[#0a0a0a] text-white selection:bg-purple-500/30 font-sans">
      <PublicNavbar />
      <main className="pt-24 pb-0 min-h-screen">
         {/* If children are passed, render them (for direct wrapping), else render Outlet (for routing) */}
         {children || <Outlet />}
      </main>
      
      <GlobalFooter />
    </div>
  );
};

export default PublicLayout;
