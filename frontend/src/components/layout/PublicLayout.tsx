import React from 'react';
import PublicNavbar from '../public/PublicNavbar';
import GlobalFooter from './GlobalFooter';
import { Outlet } from 'react-router-dom';

const PublicLayout = ({ children }: { children?: React.ReactNode }) => {
  return (
    <div className="min-h-screen bg-[#0a0a0a] text-white selection:bg-purple-500/30 font-sans relative overflow-hidden">
      <div className="fixed inset-0 -z-10 overflow-hidden">
        <div className="absolute top-[20%] left-[15%] w-[500px] h-[500px] rounded-full bg-purple-900/[0.04] blur-[120px] animate-[meshFloat1_25s_ease-in-out_infinite]" />
        <div className="absolute top-[60%] right-[10%] w-[400px] h-[400px] rounded-full bg-blue-900/[0.03] blur-[100px] animate-[meshFloat2_30s_ease-in-out_infinite]" />
        <div className="absolute bottom-[10%] left-[40%] w-[600px] h-[600px] rounded-full bg-purple-800/[0.03] blur-[140px] animate-[meshFloat3_35s_ease-in-out_infinite]" />
      </div>

      <PublicNavbar />
      <main className="pt-24 pb-0 min-h-screen relative">
        <div className="animate-[fadeInUp_0.5s_ease-out]">
          {children || <Outlet />}
        </div>
      </main>

      <GlobalFooter />

      <style>{`
        @keyframes meshFloat1 {
          0%, 100% { transform: translate(0, 0) scale(1); }
          33% { transform: translate(30px, -40px) scale(1.05); }
          66% { transform: translate(-20px, 20px) scale(0.95); }
        }
        @keyframes meshFloat2 {
          0%, 100% { transform: translate(0, 0) scale(1); }
          33% { transform: translate(-40px, 30px) scale(1.08); }
          66% { transform: translate(25px, -25px) scale(0.92); }
        }
        @keyframes meshFloat3 {
          0%, 100% { transform: translate(0, 0) scale(1); }
          33% { transform: translate(20px, 35px) scale(1.03); }
          66% { transform: translate(-35px, -15px) scale(0.97); }
        }
        @keyframes fadeInUp {
          from { opacity: 0; transform: translateY(12px); }
          to { opacity: 1; transform: translateY(0); }
        }
      `}</style>
    </div>
  );
};

export default PublicLayout;
