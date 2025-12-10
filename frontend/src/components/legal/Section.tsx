import React from 'react';

interface SectionProps {
  title: string;
  children: React.ReactNode;
}

const Section = ({ title, children }: SectionProps) => {
  return (
    <section className="mb-12">
      <h2 className="text-3xl font-bold text-white mb-6">
        {title}
      </h2>
      <div className="text-gray-300 leading-relaxed space-y-4">
        {children}
      </div>
    </section>
  );
};

export default Section;
