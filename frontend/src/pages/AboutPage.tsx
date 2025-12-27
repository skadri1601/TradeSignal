import { motion, Variants } from 'framer-motion';
import { Github, Linkedin, Globe } from 'lucide-react';

// Animation Variants
const fadeInUp: Variants = {
  hidden: { opacity: 0, y: 30 },
  visible: { opacity: 1, y: 0, transition: { duration: 0.6, ease: "easeOut" } }
};

const staggerContainer: Variants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      staggerChildren: 0.2
    }
  }
};

// 1. Hero Section
const AboutHero = () => (
  <section className="relative pt-32 pb-20 lg:pt-48 lg:pb-32 overflow-hidden px-6">
    <div className="absolute inset-0 pointer-events-none">
       <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] bg-purple-600/20 rounded-full blur-[120px]"></div>
    </div>
    <div className="max-w-4xl mx-auto text-center relative z-10">
      <motion.h1 
        initial="hidden"
        whileInView="visible"
        viewport={{ once: true }}
        variants={fadeInUp}
        className="text-5xl lg:text-7xl font-bold text-white mb-6 tracking-tight"
      >
        Empowering Traders with <br />
        <span className="text-transparent bg-clip-text bg-gradient-to-r from-purple-400 to-blue-400">
          Institutional Intelligence.
        </span>
      </motion.h1>
      <motion.p 
        initial="hidden"
        whileInView="visible"
        viewport={{ once: true }}
        variants={fadeInUp}
        className="text-xl text-gray-400 max-w-2xl mx-auto leading-relaxed"
      >
        TradeSignal was built to level the playing field. We believe financial transparency shouldn't be a luxury—it should be a standard.
      </motion.p>
    </div>
  </section>
);

// 2. Values Section (Numbered Cards)
const ValuesSection = () => {
  const values = [
    {
      id: "01",
      title: "Radical Transparency",
      desc: "We believe in democratizing access to financial data. What the insiders know, you should know too.",
      gradient: "from-blue-900/40 to-purple-900/40"
    },
    {
      id: "02",
      title: "Data-Driven Precision",
      desc: "No noise, just signal. LUNA filters out the fluff to deliver high-confidence, actionable insights you can trust.",
      gradient: "from-purple-900/40 to-pink-900/40"
    },
    {
      id: "03",
      title: "Security First",
      desc: "Your data and privacy are paramount. We employ bank-level encryption to keep your strategies safe.",
      gradient: "from-indigo-900/40 to-blue-900/40"
    }
  ];

  return (
    <section className="py-24 bg-black relative">
       <div className="max-w-7xl mx-auto px-6">
         <motion.div 
           initial="hidden"
           whileInView="visible"
           viewport={{ once: true }}
           variants={staggerContainer}
           className="grid md:grid-cols-3 gap-8"
         >
           {values.map((value) => (
             <motion.div 
               key={value.id}
               variants={fadeInUp}
               whileHover={{ y: -10 }}
               className={`p-8 rounded-3xl border border-white/10 bg-gradient-to-br ${value.gradient} backdrop-blur-xl`}
             >
               <span className="text-4xl font-bold text-white/20 mb-6 block font-mono">{value.id}</span>
               <h3 className="text-2xl font-bold text-white mb-4">{value.title}</h3>
               <p className="text-gray-400 leading-relaxed">{value.desc}</p>
             </motion.div>
           ))}
         </motion.div>
       </div>
    </section>
  );
};

// 3. Stats / Impact Section
const ImpactSection = () => (
  <section className="py-24 bg-gradient-to-b from-black to-gray-900">
    <div className="max-w-7xl mx-auto px-6">
      <div className="grid md:grid-cols-4 gap-12 text-center">
        {[
          { label: "Active Traders", value: "10k+" },
          { label: "Trades Analyzed", value: "2M+" },
          { label: "Data Sources", value: "50+" },
          { label: "Uptime", value: "99.9%" },
        ].map((stat, i) => (
          <div key={i}>
            <div className="text-4xl lg:text-5xl font-bold text-white mb-2">{stat.value}</div>
            <div className="text-gray-500 uppercase tracking-widest text-sm font-semibold">{stat.label}</div>
          </div>
        ))}
      </div>
    </div>
  </section>
);

// 4. Mission Section
const MissionSection = () => {
  return (
    <section className="py-32 bg-black text-white relative overflow-hidden">
      {/* Background decoration */}
      <div className="absolute top-0 right-0 w-[500px] h-[500px] bg-purple-900/10 rounded-full blur-[120px] pointer-events-none" />
      
      <div className="max-w-7xl mx-auto px-6">
        <div className="grid md:grid-cols-2 gap-16 items-center">
          <div>
            <motion.div 
              initial={{ opacity: 0, x: -30 }}
              whileInView={{ opacity: 1, x: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.6 }}
            >
              <h2 className="text-4xl md:text-5xl font-bold mb-6 tracking-tight">
                Our Mission
              </h2>
              <p className="text-gray-400 text-lg leading-relaxed mb-6">
                For too long, professional-grade financial intelligence has been locked behind closed doors, accessible only to institutional investors and hedge funds.
              </p>
              <p className="text-gray-400 text-lg leading-relaxed mb-8">
                TradeSignal exists to change that. We analyze millions of data points—from SEC filings to congressional disclosures—to give you the same edge as the "smart money." We believe that transparency isn't just a feature; it's a fundamental right of every market participant.
              </p>
              
              <div className="flex gap-4">
                <div className="pl-4 border-l-2 border-purple-500">
                  <h4 className="text-white font-bold text-lg">Democratization</h4>
                  <p className="text-gray-500 text-sm mt-1">Access for everyone, not just Wall St.</p>
                </div>
                <div className="pl-4 border-l-2 border-blue-500">
                  <h4 className="text-white font-bold text-lg">Transparency</h4>
                  <p className="text-gray-500 text-sm mt-1">Clear, verifiable data sources.</p>
                </div>
              </div>
            </motion.div>
          </div>

          <div className="relative">
            <motion.div 
              initial={{ opacity: 0, scale: 0.9 }}
              whileInView={{ opacity: 1, scale: 1 }}
              viewport={{ once: true }}
              transition={{ duration: 0.6 }}
              className="aspect-square rounded-3xl overflow-hidden relative border border-white/10"
            >
               <div className="absolute inset-0 bg-gradient-to-br from-purple-900/20 to-black z-10" />
               <img 
                 src="https://images.unsplash.com/photo-1642543492481-44e81e3914a7?auto=format&fit=crop&q=80&w=1000" 
                 alt="Data visualization" 
                 className="w-full h-full object-cover opacity-50"
               />
               <div className="absolute bottom-8 left-8 z-20 max-w-xs">
                 <p className="text-white font-medium text-lg border-l-4 border-purple-500 pl-4 bg-black/50 backdrop-blur-md p-4 rounded-r-xl">
                   "Information is the currency of the modern market. We just mint it."
                 </p>
               </div>
            </motion.div>
          </div>
        </div>
        
        <div className="mt-24 text-center">
          <h3 className="text-2xl font-bold text-white mb-8">Join the Movement</h3>
          <button className="px-10 py-4 bg-white text-black font-bold rounded-full hover:bg-gray-200 transition-all hover:scale-105 shadow-lg shadow-white/10">
            Start Your Free Trial
          </button>
        </div>
      </div>
    </section>
  );
};

// 5. Data & Technology Section
const DataSection = () => {
  return (
    <section className="py-24 bg-[#0a0a0a] border-y border-white/5 relative">
      <div className="max-w-7xl mx-auto px-6">
        <div className="text-center mb-16">
          <h2 className="text-3xl md:text-4xl font-bold text-white mb-4">
            Powered by Verifiable Data
          </h2>
          <p className="text-gray-400 max-w-2xl mx-auto">
            We don't rely on rumors. Our platform aggregates, cleans, and analyzes data from official regulatory bodies to ensure accuracy and compliance.
          </p>
        </div>

        <div className="grid md:grid-cols-3 gap-8">
          {/* Source 1 */}
          <div className="bg-gray-900/50 p-8 rounded-2xl border border-white/10 hover:border-blue-500/30 transition-all group">
            <div className="w-12 h-12 bg-blue-900/20 rounded-lg flex items-center justify-center mb-6 group-hover:scale-110 transition-transform">
              <svg className="w-6 h-6 text-blue-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 011.414.586l4 4a1 1 0 01.586 1.414V19a2 2 0 01-2 2z" />
              </svg>
            </div>
            <h3 className="text-xl font-bold text-white mb-3">SEC EDGAR</h3>
            <p className="text-gray-400 text-sm leading-relaxed">
              Real-time feed of <strong>Form 4 filings</strong>. We track purchases and sales by corporate insiders (CEOs, CFOs, Directors) within minutes of disclosure.
            </p>
          </div>

          {/* Source 2 */}
          <div className="bg-gray-900/50 p-8 rounded-2xl border border-white/10 hover:border-purple-500/30 transition-all group">
            <div className="w-12 h-12 bg-purple-900/20 rounded-lg flex items-center justify-center mb-6 group-hover:scale-110 transition-transform">
              <svg className="w-6 h-6 text-purple-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
              </svg>
            </div>
            <h3 className="text-xl font-bold text-white mb-3">Capitol Hill</h3>
            <p className="text-gray-400 text-sm leading-relaxed">
              Monitoring of <strong>STOCK Act disclosures</strong> from the Senate and House of Representatives. See what legislation-makers are trading.
            </p>
          </div>

          {/* Source 3 */}
          <div className="bg-gray-900/50 p-8 rounded-2xl border border-white/10 hover:border-green-500/30 transition-all group">
            <div className="w-12 h-12 bg-green-900/20 rounded-lg flex items-center justify-center mb-6 group-hover:scale-110 transition-transform">
              <svg className="w-6 h-6 text-green-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
              </svg>
            </div>
            <h3 className="text-xl font-bold text-white mb-3">LUNA Advanced AI</h3>
            <p className="text-gray-400 text-sm leading-relaxed">
              <strong>LUNA</strong>, our proprietary Large Language Model engine, reads thousands of filings to detect patterns, anomalies, and sentiment that raw data charts miss.
            </p>
          </div>
        </div>
      </div>
    </section>
  );
};

// 1.5. The Information Gap (Problem Statement)
const ProblemSection = () => (
  <section className="py-24 bg-[#0f0f1a] border-b border-white/5">
    <div className="max-w-7xl mx-auto px-6">
      <div className="grid md:grid-cols-2 gap-16 items-center">
        <div className="order-2 md:order-1">
          <div className="space-y-6">
            <div className="flex items-start gap-4">
              <div className="w-12 h-12 rounded-full bg-red-500/10 flex items-center justify-center shrink-0">
                <span className="text-red-500 font-bold text-xl">VS</span>
              </div>
              <div>
                <h3 className="text-xl font-bold text-white mb-2">The Old Way</h3>
                <p className="text-gray-400">Retail investors rely on delayed news, rumors, and outdated quarterly reports. By the time you hear about a move, the smart money has already exited.</p>
              </div>
            </div>
            <div className="flex items-start gap-4">
              <div className="w-12 h-12 rounded-full bg-green-500/10 flex items-center justify-center shrink-0">
                <span className="text-green-500 font-bold text-xl">=</span>
              </div>
              <div>
                <h3 className="text-xl font-bold text-white mb-2">The TradeSignal Way</h3>
                <p className="text-gray-400">We pipe regulatory filings directly to your dashboard the second they hit the server. You see what the CEO sees, when they see it.</p>
              </div>
            </div>
          </div>
        </div>
        <div className="order-1 md:order-2">
          <h2 className="text-3xl md:text-5xl font-bold mb-6 leading-tight">
            The Market Has an <br/> 
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-red-400 to-orange-400">Information Gap.</span>
          </h2>
          <p className="text-lg text-gray-400 leading-relaxed">
            For decades, Wall Street has operated with a distinct advantage: speed and access. While institutions run algorithms on high-speed terminals, individual investors are left refreshing news feeds.
          </p>
        </div>
      </div>
    </div>
  </section>
);

// 6. Built By Section (Portfolio Attribution)
const BuiltBySection = () => (
  <section className="py-24 bg-gradient-to-b from-[#0a0a0a] to-black relative">
    <div className="absolute inset-0 pointer-events-none">
      <div className="absolute bottom-0 left-1/2 -translate-x-1/2 w-[400px] h-[400px] bg-purple-600/10 rounded-full blur-[100px]"></div>
    </div>
    <div className="max-w-4xl mx-auto px-6 text-center relative z-10">
      <motion.div
        initial="hidden"
        whileInView="visible"
        viewport={{ once: true }}
        variants={fadeInUp}
      >
        <h2 className="text-3xl md:text-4xl font-bold text-white mb-4">
          Built By
        </h2>
        <p className="text-xl text-gray-300 mb-2">Saad Kadri</p>
        <p className="text-gray-500 mb-8">Full-Stack Developer</p>

        <div className="flex justify-center gap-6 mb-8">
          <a
            href="https://saadkadri.dev/"
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center gap-2 px-6 py-3 bg-white/5 border border-white/10 rounded-full hover:bg-white/10 hover:border-purple-500/50 transition-all group"
          >
            <Globe className="w-5 h-5 text-purple-400 group-hover:scale-110 transition-transform" />
            <span className="text-gray-300">Portfolio</span>
          </a>
          <a
            href="https://www.linkedin.com/in/saad-kadri-58b8bb205/"
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center gap-2 px-6 py-3 bg-white/5 border border-white/10 rounded-full hover:bg-white/10 hover:border-blue-500/50 transition-all group"
          >
            <Linkedin className="w-5 h-5 text-blue-400 group-hover:scale-110 transition-transform" />
            <span className="text-gray-300">LinkedIn</span>
          </a>
          <a
            href="https://github.com/skadri1601"
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center gap-2 px-6 py-3 bg-white/5 border border-white/10 rounded-full hover:bg-white/10 hover:border-gray-500/50 transition-all group"
          >
            <Github className="w-5 h-5 text-gray-400 group-hover:scale-110 transition-transform" />
            <span className="text-gray-300">GitHub</span>
          </a>
        </div>

        <p className="text-gray-500 text-sm max-w-xl mx-auto">
          This project showcases full-stack development skills including React, TypeScript, FastAPI, PostgreSQL, Redis, and AI/ML integration with Google Gemini.
        </p>
      </motion.div>
    </div>
  </section>
);

// Main Page Component
const AboutPage = () => {
  return (
    <div className="min-h-screen bg-black text-white font-sans selection:bg-purple-500/30">
      <AboutHero />
      <ProblemSection />
      <ValuesSection />
      <ImpactSection />
      <MissionSection />
      <DataSection />
      <BuiltBySection />
    </div>
  );
};

export default AboutPage;
