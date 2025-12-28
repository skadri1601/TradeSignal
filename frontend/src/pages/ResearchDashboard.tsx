import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { researchApi } from '../api/research';
import type { FullResearchReport } from '../api/research';
import CompanyAutocomplete from '../components/common/CompanyAutocomplete';
import IVTBadge from '../components/research/IVTBadge';
import TSScoreBadge from '../components/research/TSScoreBadge';
import RiskLevelBadge from '../components/research/RiskLevelBadge';
import LoadingSpinner from '../components/common/LoadingSpinner';
import { RefreshCw, TrendingUp, AlertCircle, FileText } from 'lucide-react';

export default function ResearchDashboard() {
  const [selectedTicker, setSelectedTicker] = useState<string>('');

  // Fetch full research report when ticker is selected
  const {
    data: researchData,
    isLoading,
    error,
    refetch,
    isFetching,
  } = useQuery<FullResearchReport | null>({
    queryKey: ['research', 'full-report', selectedTicker],
    queryFn: () => researchApi.getFullReport(selectedTicker),
    enabled: selectedTicker.length > 0,
    staleTime: 1000 * 60 * 5, // 5 minutes
    retry: 2,
  });

  const handleTickerChange = (ticker: string) => {
    setSelectedTicker(ticker.toUpperCase());
  };

  const handleRefresh = () => {
    if (selectedTicker) {
      refetch();
    }
  };

  // Empty state when no ticker selected
  if (!selectedTicker) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Research Dashboard</h1>
          <p className="text-gray-600">
            Comprehensive research metrics powered by insider trading data and fundamental analysis
          </p>
        </div>

        {/* Search Bar */}
        <div className="max-w-2xl mx-auto mb-8">
          <CompanyAutocomplete
            value={selectedTicker}
            onChange={handleTickerChange}
            placeholder="Search for a company ticker (e.g., AAPL, TSLA, MSFT)..."
          />
        </div>

        {/* Empty State */}
        <div className="max-w-2xl mx-auto text-center py-16">
          <div className="inline-flex items-center justify-center w-16 h-16 bg-blue-100 rounded-full mb-4">
            <FileText className="w-8 h-8 text-blue-600" />
          </div>
          <h3 className="text-xl font-semibold text-gray-900 mb-2">
            Search for a company to view research metrics
          </h3>
          <p className="text-gray-600 mb-6">
            Get comprehensive insights including valuation, risk assessment, competitive strength, and management quality scores.
          </p>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm text-gray-500">
            <div className="flex flex-col items-center p-4 bg-gray-50 rounded-lg">
              <TrendingUp className="w-6 h-6 mb-2 text-blue-600" />
              <span className="font-medium">Intrinsic Value</span>
            </div>
            <div className="flex flex-col items-center p-4 bg-gray-50 rounded-lg">
              <TrendingUp className="w-6 h-6 mb-2 text-green-600" />
              <span className="font-medium">TS Score</span>
            </div>
            <div className="flex flex-col items-center p-4 bg-gray-50 rounded-lg">
              <AlertCircle className="w-6 h-6 mb-2 text-yellow-600" />
              <span className="font-medium">Risk Level</span>
            </div>
            <div className="flex flex-col items-center p-4 bg-gray-50 rounded-lg">
              <TrendingUp className="w-6 h-6 mb-2 text-purple-600" />
              <span className="font-medium">More Metrics</span>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8">
      {/* Header */}
      <div className="mb-8">
        <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 mb-4">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 mb-2">Research Dashboard</h1>
            <p className="text-gray-600">
              Viewing research metrics for {selectedTicker}
            </p>
          </div>
          <button
            onClick={handleRefresh}
            disabled={isFetching}
            className="btn-primary inline-flex items-center gap-2"
          >
            <RefreshCw className={`w-4 h-4 ${isFetching ? 'animate-spin' : ''}`} />
            Refresh Data
          </button>
        </div>

        {/* Search Bar */}
        <div className="max-w-2xl">
          <CompanyAutocomplete
            value={selectedTicker}
            onChange={handleTickerChange}
            placeholder="Search for a company ticker (e.g., AAPL, TSLA, MSFT)..."
          />
        </div>
      </div>

      {/* Loading State */}
      {isLoading && (
        <div className="flex flex-col items-center justify-center py-16">
          <LoadingSpinner />
          <p className="mt-4 text-gray-600">Loading research metrics...</p>
        </div>
      )}

      {/* Error State */}
      {error && !isLoading && (
        <div className="max-w-2xl mx-auto">
          <div className="bg-red-50 border border-red-200 rounded-lg p-6 text-center">
            <AlertCircle className="w-12 h-12 text-red-500 mx-auto mb-4" />
            <h3 className="text-lg font-semibold text-red-900 mb-2">
              Failed to load research data
            </h3>
            <p className="text-red-700 mb-4">
              {error instanceof Error ? error.message : 'An error occurred while fetching research metrics'}
            </p>
            <button
              onClick={handleRefresh}
              className="btn-primary inline-flex items-center gap-2"
            >
              <RefreshCw className="w-4 h-4" />
              Try Again
            </button>
          </div>
        </div>
      )}

      {/* Research Data */}
      {researchData && !isLoading && (
        <div className="space-y-6">
          {/* Metric Cards Row */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {/* IVT Badge */}
            {researchData.ivt ? (
              <IVTBadge
                currentPrice={researchData.ivt.current_price}
                intrinsicValue={researchData.ivt.intrinsic_value}
                discountPct={researchData.ivt.discount_pct}
                calculationDate={researchData.ivt.calculation_date}
              />
            ) : (
              <div className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center">
                <p className="text-gray-500">Intrinsic Value data not available</p>
              </div>
            )}

            {/* Risk Level Badge */}
            {researchData.risk_level ? (
              <RiskLevelBadge
                level={researchData.risk_level.level}
                category={researchData.risk_level.category}
                volatilityScore={researchData.risk_level.volatility_score}
              />
            ) : (
              <div className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center">
                <p className="text-gray-500">Risk Level data not available</p>
              </div>
            )}

            {/* TS Score Badge */}
            {researchData.ts_score ? (
              <TSScoreBadge
                score={researchData.ts_score.score}
                rating={researchData.ts_score.rating}
                priceToIVT={researchData.ts_score.price_to_ivt_ratio}
                riskAdjusted={researchData.ts_score.risk_adjusted}
              />
            ) : (
              <div className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center">
                <p className="text-gray-500">TS Score data not available</p>
              </div>
            )}
          </div>

          {/* Competitive Strength Card */}
          {researchData.competitive_strength && (
            <div className="bg-white border border-gray-200 rounded-lg p-6 shadow-sm">
              <h2 className="text-xl font-bold text-gray-900 mb-4">Competitive Strength</h2>
              <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                <div>
                  <p className="text-sm text-gray-600">Rating</p>
                  <p className="text-lg font-semibold text-gray-900">
                    {researchData.competitive_strength.rating}
                  </p>
                </div>
                <div>
                  <p className="text-sm text-gray-600">Trajectory</p>
                  <p className="text-lg font-semibold text-gray-900">
                    {researchData.competitive_strength.trajectory}
                  </p>
                </div>
                {researchData.competitive_strength.composite_score !== undefined && (
                  <div>
                    <p className="text-sm text-gray-600">Composite Score</p>
                    <p className="text-lg font-semibold text-gray-900">
                      {researchData.competitive_strength.composite_score.toFixed(1)}
                    </p>
                  </div>
                )}
              </div>

              {/* Moat Sources Breakdown */}
              <div className="mt-4 pt-4 border-t border-gray-200">
                <h3 className="text-sm font-semibold text-gray-700 mb-3">Moat Sources</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
                  {researchData.competitive_strength.moat_sources.network_effects !== undefined && (
                    <div className="flex items-center justify-between p-3 bg-gray-50 rounded">
                      <span className="text-sm text-gray-700">Network Effects</span>
                      <span className="font-semibold text-blue-600">
                        {(researchData.competitive_strength.moat_sources.network_effects * 100).toFixed(0)}%
                      </span>
                    </div>
                  )}
                  {researchData.competitive_strength.moat_sources.intangible_assets !== undefined && (
                    <div className="flex items-center justify-between p-3 bg-gray-50 rounded">
                      <span className="text-sm text-gray-700">Intangible Assets</span>
                      <span className="font-semibold text-blue-600">
                        {(researchData.competitive_strength.moat_sources.intangible_assets * 100).toFixed(0)}%
                      </span>
                    </div>
                  )}
                  {researchData.competitive_strength.moat_sources.cost_advantages !== undefined && (
                    <div className="flex items-center justify-between p-3 bg-gray-50 rounded">
                      <span className="text-sm text-gray-700">Cost Advantages</span>
                      <span className="font-semibold text-blue-600">
                        {(researchData.competitive_strength.moat_sources.cost_advantages * 100).toFixed(0)}%
                      </span>
                    </div>
                  )}
                  {researchData.competitive_strength.moat_sources.switching_costs !== undefined && (
                    <div className="flex items-center justify-between p-3 bg-gray-50 rounded">
                      <span className="text-sm text-gray-700">Switching Costs</span>
                      <span className="font-semibold text-blue-600">
                        {(researchData.competitive_strength.moat_sources.switching_costs * 100).toFixed(0)}%
                      </span>
                    </div>
                  )}
                  {researchData.competitive_strength.moat_sources.efficient_scale !== undefined && (
                    <div className="flex items-center justify-between p-3 bg-gray-50 rounded">
                      <span className="text-sm text-gray-700">Efficient Scale</span>
                      <span className="font-semibold text-blue-600">
                        {(researchData.competitive_strength.moat_sources.efficient_scale * 100).toFixed(0)}%
                      </span>
                    </div>
                  )}
                </div>
              </div>

              {researchData.competitive_strength.rating_date && (
                <p className="mt-4 text-xs text-gray-500">
                  Last updated: {new Date(researchData.competitive_strength.rating_date).toLocaleDateString()}
                </p>
              )}
            </div>
          )}

          {/* Management Score Card */}
          {researchData.management_score && (
            <div className="bg-white border border-gray-200 rounded-lg p-6 shadow-sm">
              <h2 className="text-xl font-bold text-gray-900 mb-4">Management Excellence</h2>
              <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                <div>
                  <p className="text-sm text-gray-600">Grade</p>
                  <p className="text-2xl font-bold text-gray-900">
                    {researchData.management_score.grade}
                  </p>
                </div>
                {researchData.management_score.composite_score !== undefined && (
                  <div>
                    <p className="text-sm text-gray-600">Composite Score</p>
                    <p className="text-lg font-semibold text-gray-900">
                      {researchData.management_score.composite_score.toFixed(1)}
                    </p>
                  </div>
                )}
              </div>

              {/* Components Breakdown */}
              <div className="mt-4 pt-4 border-t border-gray-200">
                <h3 className="text-sm font-semibold text-gray-700 mb-3">Score Components</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
                  {researchData.management_score.components.ma_track_record !== undefined && (
                    <div className="flex items-center justify-between p-3 bg-gray-50 rounded">
                      <span className="text-sm text-gray-700">M&A Track Record</span>
                      <span className="font-semibold text-purple-600">
                        {(researchData.management_score.components.ma_track_record * 100).toFixed(0)}%
                      </span>
                    </div>
                  )}
                  {researchData.management_score.components.capital_discipline !== undefined && (
                    <div className="flex items-center justify-between p-3 bg-gray-50 rounded">
                      <span className="text-sm text-gray-700">Capital Discipline</span>
                      <span className="font-semibold text-purple-600">
                        {(researchData.management_score.components.capital_discipline * 100).toFixed(0)}%
                      </span>
                    </div>
                  )}
                  {researchData.management_score.components.shareholder_returns !== undefined && (
                    <div className="flex items-center justify-between p-3 bg-gray-50 rounded">
                      <span className="text-sm text-gray-700">Shareholder Returns</span>
                      <span className="font-semibold text-purple-600">
                        {(researchData.management_score.components.shareholder_returns * 100).toFixed(0)}%
                      </span>
                    </div>
                  )}
                  {researchData.management_score.components.financial_leverage !== undefined && (
                    <div className="flex items-center justify-between p-3 bg-gray-50 rounded">
                      <span className="text-sm text-gray-700">Financial Leverage</span>
                      <span className="font-semibold text-purple-600">
                        {(researchData.management_score.components.financial_leverage * 100).toFixed(0)}%
                      </span>
                    </div>
                  )}
                  {researchData.management_score.components.governance !== undefined && (
                    <div className="flex items-center justify-between p-3 bg-gray-50 rounded">
                      <span className="text-sm text-gray-700">Governance</span>
                      <span className="font-semibold text-purple-600">
                        {(researchData.management_score.components.governance * 100).toFixed(0)}%
                      </span>
                    </div>
                  )}
                </div>
              </div>

              {researchData.management_score.scoring_date && (
                <p className="mt-4 text-xs text-gray-500">
                  Last updated: {new Date(researchData.management_score.scoring_date).toLocaleDateString()}
                </p>
              )}
            </div>
          )}

          {/* Report Metadata */}
          {researchData.report_date && (
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
              <p className="text-sm text-blue-800">
                <strong>Report Generated:</strong> {new Date(researchData.report_date).toLocaleString()}
              </p>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
