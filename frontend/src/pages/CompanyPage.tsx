import { useParams, Link } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { companiesApi } from '../api/companies';
import { earningsApi } from '../api/earnings';
import { congressionalTradesApi } from '../api/congressionalTrades';
import { patternsApi } from '../api/patterns';
import { researchApi } from '../api/research';
import TradeList from '../components/trades/TradeList';
import LoadingSpinner from '../components/common/LoadingSpinner';
import { LegalDisclaimer } from '../components/LegalDisclaimer';
import { IVTBadge, TSScoreBadge, RiskLevelBadge } from '../components/research';
import { UpgradeCTA } from '../components/UpgradeCTA';
import { formatCurrency } from '../utils/formatters';
import {
  Building2,
  ExternalLink,
  Calendar,
  TrendingUp,
  TrendingDown,
  Landmark,
  BarChart3,
  ArrowRight,
  AlertCircle,
  CheckCircle,
  MinusCircle,
  LineChart
} from 'lucide-react';

export default function CompanyPage() {
  const { ticker } = useParams<{ ticker: string }>();

  const { data: company, isLoading: companyLoading } = useQuery({
    queryKey: ['company', ticker],
    queryFn: () => companiesApi.getCompany(ticker!),
    enabled: !!ticker,
  });

  const { data: trades, isLoading: tradesLoading } = useQuery({
    queryKey: ['companyTrades', ticker],
    queryFn: () => companiesApi.getCompanyTrades(ticker!),
    enabled: !!ticker,
  });

  // Earnings data
  const { data: earnings, isLoading: earningsLoading } = useQuery({
    queryKey: ['companyEarnings', ticker],
    queryFn: () => earningsApi.getCompanyEarnings(ticker!, 8),
    enabled: !!ticker,
  });

  // Congressional trades for this company
  const { data: congressionalTrades, isLoading: congressionalLoading } = useQuery({
    queryKey: ['congressionalTrades', ticker],
    queryFn: () => congressionalTradesApi.getTrades({ ticker, limit: 5 }),
    enabled: !!ticker,
  });

  // Pattern analysis
  const { data: patternAnalysis, isLoading: patternLoading } = useQuery({
    queryKey: ['patternAnalysis', ticker],
    queryFn: () => patternsApi.analyzeCompany(ticker!, 90),
    enabled: !!ticker,
  });

  // Research data queries
  const { data: researchIVT, isLoading: ivtLoading, error: ivtError } = useQuery({
    queryKey: ['researchIVT', ticker],
    queryFn: () => researchApi.getIVT(ticker!),
    enabled: !!ticker,
    retry: false, // Don't retry on 402 (payment required)
  });

  const { data: researchTSScore, isLoading: tsScoreLoading, error: tsScoreError } = useQuery({
    queryKey: ['researchTSScore', ticker],
    queryFn: () => researchApi.getTSScore(ticker!),
    enabled: !!ticker,
    retry: false,
  });

  const { data: researchRiskLevel, isLoading: riskLevelLoading, error: riskLevelError } = useQuery({
    queryKey: ['researchRiskLevel', ticker],
    queryFn: () => researchApi.getRiskLevel(ticker!),
    enabled: !!ticker,
    retry: false,
  });

  // Check if any error is a 402 (payment required) vs 404 (not found)
  const hasPaymentRequiredError = 
    (ivtError as any)?.response?.status === 402 ||
    (tsScoreError as any)?.response?.status === 402 ||
    (riskLevelError as any)?.response?.status === 402;

  if (companyLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <LoadingSpinner />
      </div>
    );
  }

  if (!company) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-400">Company not found</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <LegalDisclaimer />
      
      {/* Company Header */}
      <div className="card">
        <div className="flex items-start justify-between">
          <div className="flex items-center space-x-4">
            <div className="p-3 bg-blue-500/20 rounded-lg">
              <Building2 className="h-8 w-8 text-blue-400" />
            </div>
            <div>
              <h1 className="text-3xl font-bold text-white">{company.name}</h1>
              <p className="text-lg text-gray-400 mt-1">{company.ticker}</p>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-6">
          <div>
            <p className="text-sm text-gray-400">Sector</p>
            <p className="text-lg font-semibold text-white">{company.sector || 'N/A'}</p>
          </div>
          <div>
            <p className="text-sm text-gray-400">Industry</p>
            <p className="text-lg font-semibold text-white">{company.industry || 'N/A'}</p>
          </div>
          <div>
            <p className="text-sm text-gray-400">Market Cap</p>
            <p className="text-lg font-semibold text-white">
              {company.market_cap ? formatCurrency(company.market_cap) : 'N/A'}
            </p>
          </div>
        </div>

        {company.website && (
          <div className="mt-4">
            <a
              href={company.website}
              target="_blank"
              rel="noopener noreferrer"
              className="text-blue-400 hover:text-blue-300 inline-flex items-center transition-colors"
            >
              {company.website}
              <ExternalLink className="h-4 w-4 ml-1" />
            </a>
          </div>
        )}
      </div>

      {/* Pattern Analysis Summary */}
      <div className="card">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center space-x-2">
            <BarChart3 className="h-5 w-5 text-purple-400" />
            <h2 className="text-xl font-bold text-white">AI Pattern Analysis</h2>
          </div>
          <Link
            to={`/patterns?ticker=${ticker}`}
            className="text-blue-400 hover:text-blue-300 text-sm flex items-center transition-colors"
          >
            Full Analysis <ArrowRight className="h-4 w-4 ml-1" />
          </Link>
        </div>
        {patternLoading ? (
          <div className="flex items-center justify-center h-24">
            <LoadingSpinner />
          </div>
        ) : patternAnalysis ? (
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="bg-white/5 rounded-lg p-4 border border-white/5">
              <p className="text-sm text-gray-400">Pattern</p>
              <p className={`text-lg font-semibold ${
                patternAnalysis.trend === 'BULLISH' ? 'text-green-400' :
                patternAnalysis.trend === 'BEARISH' ? 'text-red-400' : 'text-gray-300'
              }`}>
                {patternAnalysis.pattern.replace('_', ' ')}
              </p>
            </div>
            <div className="bg-white/5 rounded-lg p-4 border border-white/5">
              <p className="text-sm text-gray-400">Trend</p>
              <div className="flex items-center">
                {patternAnalysis.trend === 'BULLISH' ? (
                  <TrendingUp className="h-5 w-5 text-green-400 mr-1" />
                ) : patternAnalysis.trend === 'BEARISH' ? (
                  <TrendingDown className="h-5 w-5 text-red-400 mr-1" />
                ) : (
                  <MinusCircle className="h-5 w-5 text-gray-500 mr-1" />
                )}
                <span className={`text-lg font-semibold ${
                  patternAnalysis.trend === 'BULLISH' ? 'text-green-400' :
                  patternAnalysis.trend === 'BEARISH' ? 'text-red-400' : 'text-gray-300'
                }`}>
                  {patternAnalysis.trend}
                </span>
              </div>
            </div>
            <div className="bg-white/5 rounded-lg p-4 border border-white/5">
              <p className="text-sm text-gray-400">Recommendation</p>
              <p className={`text-lg font-semibold ${
                patternAnalysis.recommendation === 'BUY' || patternAnalysis.recommendation === 'CONSIDER_BUY' ? 'text-green-400' :
                patternAnalysis.recommendation === 'SELL' || patternAnalysis.recommendation === 'CONSIDER_SELL' ? 'text-red-400' : 'text-gray-300'
              }`}>
                {patternAnalysis.recommendation.replace('_', ' ')}
              </p>
            </div>
            <div className="bg-white/5 rounded-lg p-4 border border-white/5">
              <p className="text-sm text-gray-400">Confidence</p>
              <div className="flex items-center">
                <div className="w-full bg-gray-700 rounded-full h-2 mr-2">
                  <div
                    className={`h-2 rounded-full ${
                      patternAnalysis.confidence > 0.7 ? 'bg-green-500' :
                      patternAnalysis.confidence > 0.4 ? 'bg-yellow-500' : 'bg-red-500'
                    }`}
                    style={{ width: `${patternAnalysis.confidence * 100}%` }}
                  />
                </div>
                <span className="text-sm font-medium text-white">{Math.round(patternAnalysis.confidence * 100)}%</span>
              </div>
            </div>
          </div>
        ) : (
          <p className="text-gray-500 text-center py-4">No pattern data available</p>
        )}
      </div>

      {/* Research Analysis Section */}
      <div className="card">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center space-x-2">
            <LineChart className="h-5 w-5 text-indigo-400" />
            <h2 className="text-xl font-bold text-white">Research Analysis</h2>
          </div>
        </div>

        {ivtLoading || tsScoreLoading || riskLevelLoading ? (
          <div className="flex items-center justify-center h-24">
            <LoadingSpinner />
          </div>
        ) : researchIVT || researchTSScore || researchRiskLevel ? (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {researchIVT && (
              <IVTBadge
                currentPrice={researchIVT.current_price}
                intrinsicValue={researchIVT.intrinsic_value}
                discountPct={researchIVT.discount_pct}
                calculationDate={researchIVT.calculation_date}
              />
            )}
            {researchTSScore && (
              <TSScoreBadge
                score={researchTSScore.score}
                rating={researchTSScore.rating}
                priceToIVT={researchTSScore.price_to_ivt_ratio}
                riskAdjusted={researchTSScore.risk_adjusted}
              />
            )}
            {researchRiskLevel && (
              <RiskLevelBadge
                level={researchRiskLevel.level}
                category={researchRiskLevel.category}
                volatilityScore={researchRiskLevel.volatility_score}
              />
            )}
          </div>
        ) : hasPaymentRequiredError ? (
          <UpgradeCTA
            variant="card"
            feature="Research Analysis"
            requiredTier="pro"
            message="Access intrinsic value analysis, TradeSignal scores, risk assessments, and more with PRO"
          />
        ) : (
          <p className="text-gray-500 text-center py-4">Research data not yet available for this company. Coverage coming soon.</p>
        )}
      </div>

      {/* Earnings Section */}
      <div className="card">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center space-x-2">
            <Calendar className="h-5 w-5 text-blue-400" />
            <h2 className="text-xl font-bold text-white">Earnings</h2>
          </div>
          <Link
            to={`/earnings/${ticker}`}
            className="text-blue-400 hover:text-blue-300 text-sm flex items-center transition-colors"
          >
            View Details <ArrowRight className="h-4 w-4 ml-1" />
          </Link>
        </div>
        {earningsLoading ? (
          <div className="flex items-center justify-center h-24">
            <LoadingSpinner />
          </div>
        ) : earnings ? (
          <div className="space-y-4">
            {/* Next Earnings Date */}
            {earnings.next_earnings_date && (
              <div className="bg-blue-900/20 border border-blue-500/30 rounded-lg p-4">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-blue-300 font-medium">Next Earnings Date</p>
                    <p className="text-xl font-bold text-blue-100">
                      {new Date(earnings.next_earnings_date).toLocaleDateString('en-US', {
                        weekday: 'long',
                        year: 'numeric',
                        month: 'long',
                        day: 'numeric'
                      })}
                    </p>
                  </div>
                  {earnings.upcoming_earnings[0] && (
                    <div className="text-right">
                      <p className="text-sm text-blue-300">Days Until</p>
                      <p className="text-2xl font-bold text-blue-100">
                        {earnings.upcoming_earnings[0].days_until}
                      </p>
                    </div>
                  )}
                </div>
              </div>
            )}

            {/* Recent Earnings History */}
            {earnings.earnings_history.length > 0 && (
              <div>
                <h3 className="text-sm font-medium text-gray-400 mb-2">Recent Earnings History</h3>
                <div className="overflow-x-auto">
                  <table className="min-w-full divide-y divide-white/5">
                    <thead className="bg-black/20">
                      <tr>
                        <th className="px-4 py-2 text-left text-xs font-medium text-gray-400 uppercase">Date</th>
                        <th className="px-4 py-2 text-left text-xs font-medium text-gray-400 uppercase">Estimate</th>
                        <th className="px-4 py-2 text-left text-xs font-medium text-gray-400 uppercase">Actual</th>
                        <th className="px-4 py-2 text-left text-xs font-medium text-gray-400 uppercase">Surprise</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-white/5">
                      {earnings.earnings_history.slice(0, 4).map((earning, idx) => (
                        <tr key={idx}>
                          <td className="px-4 py-2 text-sm text-white">
                            {new Date(earning.date).toLocaleDateString()}
                          </td>
                          <td className="px-4 py-2 text-sm text-gray-400">
                            {earning.estimate !== null ? `$${earning.estimate.toFixed(2)}` : '-'}
                          </td>
                          <td className="px-4 py-2 text-sm text-white font-medium">
                            {earning.actual !== null ? `$${earning.actual.toFixed(2)}` : '-'}
                          </td>
                          <td className="px-4 py-2">
                            {earning.surprise !== null ? (
                              <span className={`inline-flex items-center text-sm font-medium ${
                                earning.surprise > 0 ? 'text-green-400' : earning.surprise < 0 ? 'text-red-400' : 'text-gray-400'
                              }`}>
                                {earning.surprise > 0 ? (
                                  <CheckCircle className="h-4 w-4 mr-1" />
                                ) : earning.surprise < 0 ? (
                                  <AlertCircle className="h-4 w-4 mr-1" />
                                ) : null}
                                {earning.surprise > 0 ? '+' : ''}{(earning.surprise * 100).toFixed(1)}%
                              </span>
                            ) : '-'}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}
          </div>
        ) : (
          <p className="text-gray-500 text-center py-4">No earnings data available</p>
        )}
      </div>

      {/* Congressional Trades Section */}
      <div className="card">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center space-x-2">
            <Landmark className="h-5 w-5 text-indigo-400" />
            <h2 className="text-xl font-bold text-white">Congressional Trades</h2>
          </div>
          <Link
            to={`/congressional-trades?ticker=${ticker}`}
            className="text-blue-400 hover:text-blue-300 text-sm flex items-center transition-colors"
          >
            View All <ArrowRight className="h-4 w-4 ml-1" />
          </Link>
        </div>
        {congressionalLoading ? (
          <div className="flex items-center justify-center h-24">
            <LoadingSpinner />
          </div>
        ) : congressionalTrades && congressionalTrades.items.length > 0 ? (
          <div className="space-y-3">
            {congressionalTrades.items.map((trade) => (
              <div
                key={trade.id}
                className="flex items-center justify-between p-3 bg-white/5 border border-white/5 rounded-lg"
              >
                <div className="flex-1">
                  <div className="flex items-center space-x-2">
                    <span className={`px-2 py-0.5 text-xs font-medium rounded ${
                      trade.transaction_type === 'BUY'
                        ? 'bg-green-500/20 text-green-300'
                        : 'bg-red-500/20 text-red-300'
                    }`}>
                      {trade.transaction_type}
                    </span>
                    <span className="font-medium text-white">
                      {trade.congressperson?.display_name || trade.congressperson?.name || 'Unknown'}
                    </span>
                    <span className="text-xs text-gray-500">
                      ({trade.congressperson?.chamber || 'N/A'})
                    </span>
                  </div>
                  <p className="text-sm text-gray-400 mt-1">
                    {trade.amount_range_display || 'Amount not disclosed'} • {new Date(trade.transaction_date).toLocaleDateString()}
                  </p>
                </div>
                {trade.congressperson?.party && (
                  <span className={`px-2 py-1 text-xs font-medium rounded ${
                    trade.congressperson.party === 'DEMOCRAT' ? 'bg-blue-500/20 text-blue-300' :
                    trade.congressperson.party === 'REPUBLICAN' ? 'bg-red-500/20 text-red-300' :
                    'bg-gray-700 text-gray-300'
                  }`}>
                    {trade.congressperson.party.charAt(0)}
                  </span>
                )}
              </div>
            ))}
            {congressionalTrades.total > 5 && (
              <p className="text-sm text-gray-500 text-center pt-2">
                + {congressionalTrades.total - 5} more trades
              </p>
            )}
          </div>
        ) : (
          <p className="text-gray-500 text-center py-4">No congressional trades found for this company</p>
        )}
      </div>

      {/* Recent Insider Trades */}
      <div className="card">
        <h2 className="text-xl font-bold text-white mb-4">Recent Insider Trades</h2>
        {tradesLoading ? (
          <div className="flex items-center justify-center h-32">
            <LoadingSpinner />
          </div>
        ) : (
          <TradeList trades={trades || []} />
        )}
      </div>
    </div>
  );
}