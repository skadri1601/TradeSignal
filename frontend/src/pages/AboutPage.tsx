import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { ArrowRight, Users, Linkedin, Instagram, Twitter } from 'lucide-react';

// Animation Variants
const fadeInUp = {
  hidden: { opacity: 0, y: 30 },
  visible: { opacity: 1, y: 0, transition: { duration: 0.6, ease: "easeOut" } }
};

const staggerContainer = {
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
      desc: "No noise, just signal. Our AI filters out the fluff to deliver actionable insights you can trust.",
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

// 4. Team Section (Updated to match design request)
const TeamSection = () => {
  const team = [
    {
      name: "Ralph Edwards",
      role: "Web Designer",
      gradient: "bg-gradient-to-br from-[#E0F2FE] to-[#DBEAFE]", // Blue
      image: "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?fit=crop&w=300&h=300"
    },
    {
      name: "Esther Howard",
      role: "CEO at StoryPixel",
      gradient: "bg-gradient-to-br from-[#FCE7F3] to-[#F3E8FF]", // Pink
      image: "https://images.unsplash.com/photo-1494790108377-be9c29b29330?fit=crop&w=300&h=300"
    },
    {
      name: "Ronald Richards",
      role: "Marketing Coordinator",
      gradient: "bg-gradient-to-br from-[#FEF3C7] to-[#FED7AA]", // Orange
      image: "https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?fit=crop&w=300&h=300"
    },
    {
      name: "Darlene Robertson",
      role: "President of Sales",
      gradient: "bg-gradient-to-br from-[#E0E7FF] to-[#DDD6FE]", // Purple
      image: "https://images.unsplash.com/photo-1438761681033-6461ffad8d80?fit=crop&w=300&h=300"
    }
  ];

  return (
    <section className="py-32 bg-black text-white">
      <div className="max-w-7xl mx-auto px-6">
        <div className="text-center mb-20">
          <h2 className="text-4xl md:text-5xl font-bold mb-4">Meet Our Teams</h2>
          <p className="text-gray-400 max-w-2xl mx-auto text-lg">
             At TradeSignal, our passion and innovation drive everything we do—and we're proud to have that dedication recognized across leading platforms.
          </p>
        </div>

        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
          {team.map((member, i) => (
            <motion.div 
              key={i}
              whileHover="hover"
              initial="initial"
              className={`relative p-6 rounded-3xl ${member.gradient} text-gray-900 h-64 flex flex-col overflow-hidden group cursor-pointer`}
            >
              <div className="flex items-start gap-4 relative z-10">
                <img 
                  src={member.image} 
                  alt={member.name} 
                  className="w-16 h-16 rounded-2xl object-cover shadow-sm"
                />
                <div>
                  <h3 className="text-lg font-bold leading-tight">{member.name}</h3>
                  <p className="text-sm text-gray-600 font-medium mt-1">{member.role}</p>
                </div>
              </div>

              {/* Decorative grid pattern */}
              <div className="absolute inset-0 opacity-20 pointer-events-none" 
                   style={{ backgroundImage: 'linear-gradient(#000 1px, transparent 1px), linear-gradient(90deg, #000 1px, transparent 1px)', backgroundSize: '20px 20px' }}>
              </div>

              {/* Social Icons - Reveal on Hover */}
              <motion.div 
                variants={{
                  initial: { opacity: 0, y: 20 },
                  hover: { opacity: 1, y: 0 }
                }}
                transition={{ duration: 0.3 }}
                className="absolute bottom-6 right-6 flex gap-2 z-20"
              >
                 <a href="#" className="w-8 h-8 bg-white rounded-full flex items-center justify-center hover:scale-110 transition-transform shadow-sm text-gray-700 hover:text-blue-600"><Linkedin className="w-4 h-4" /></a>
                 <a href="#" className="w-8 h-8 bg-white rounded-full flex items-center justify-center hover:scale-110 transition-transform shadow-sm text-gray-700 hover:text-pink-600"><Instagram className="w-4 h-4" /></a>
                 <a href="#" className="w-8 h-8 bg-white rounded-full flex items-center justify-center hover:scale-110 transition-transform shadow-sm text-gray-700 hover:text-black"><Twitter className="w-4 h-4" /></a>
              </motion.div>
            </motion.div>
          ))}
        </div>
        
        <div className="mt-16 text-center">
          <button className="px-8 py-4 bg-[#A78BFA] hover:bg-[#8B5CF6] text-black font-semibold rounded-full transition-all hover:scale-105 flex items-center gap-2 mx-auto shadow-lg shadow-purple-500/20">
            Apply Now To Join Our Team <ArrowRight className="w-4 h-4" />
          </button>
        </div>
      </div>
    </section>
  );
};

// Main Page Component
const AboutPage = () => {
  return (
    <div className="min-h-screen bg-black text-white font-sans selection:bg-purple-500/30">
      <AboutHero />
      <ValuesSection />
      <ImpactSection />
      <TeamSection />
    </div>
  );
};

export default AboutPage;
