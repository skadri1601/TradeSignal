import React from 'react';
import PublicNavbar from '../public/PublicNavbar';
import GlobalFooter from './GlobalFooter';
import { Outlet } from 'react-router-dom';

const PublicLayout = ({ children }: { children?: React.ReactNode }) => {
  return (
    <div className="min-h-screen bg-[#0a0a0a] text-white font-sans">
      <PublicNavbar />
      <main className="pt-24 pb-0 min-h-screen">
        {children || <Outlet />}
      </main>
      <GlobalFooter />
    </div>
  );
};

export default PublicLayout;
