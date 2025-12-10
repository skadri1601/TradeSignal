import CompanyAnalysis from '../components/ai/CompanyAnalysis';

export default function PatternsPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-white">Pattern Analysis</h1>
        <p className="mt-2 text-gray-400">
          Use LUNA AI to analyze insider trading patterns for specific companies.
        </p>
      </div>
      <CompanyAnalysis />
    </div>
  );
}