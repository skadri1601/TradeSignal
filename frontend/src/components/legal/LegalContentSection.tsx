import React from 'react';

const LegalContentSection = ({ children }: { children: React.ReactNode }) => {
  return (
    <div className="bg-black py-16 px-4">
      <div className="max-w-4xl mx-auto prose prose-lg prose-invert">
        {children}
      </div>
    </div>
  );
};

export default LegalContentSection;
