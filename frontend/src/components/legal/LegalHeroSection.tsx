
interface LegalHeroSectionProps {
  title: string;
  intro: string;
}

const LegalHeroSection = ({ title, intro }: LegalHeroSectionProps) => {
  return (
    <div className="bg-gradient-to-br from-purple-900 via-purple-800 to-purple-900 py-20 px-4">
      <div className="max-w-4xl mx-auto text-center">
        <h1 className="text-5xl md:text-6xl font-bold text-white mb-6">
          {title}
        </h1>
        <p className="text-xl text-purple-100 max-w-3xl mx-auto">
          {intro}
        </p>
      </div>
    </div>
  );
};

export default LegalHeroSection;
