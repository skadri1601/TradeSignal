import { useState } from 'react';
import { ChevronDown, ChevronUp, HelpCircle, Mail } from 'lucide-react';

interface FAQItem {
  question: string;
  answer: string;
  category: string;
}

const faqs: FAQItem[] = [
  // Billing
  {
    category: 'Billing & Payments',
    question: 'How do I upgrade my subscription?',
    answer: 'You can upgrade your subscription at any time by visiting the Pricing page and selecting a higher tier. Your billing will be prorated for the remainder of your current billing period.',
  },
  {
    category: 'Billing & Payments',
    question: 'What payment methods do you accept?',
    answer: 'We accept all major credit cards (Visa, Mastercard, American Express) and debit cards through Stripe, our secure payment processor.',
  },
  {
    category: 'Billing & Payments',
    question: 'When will I be charged?',
    answer: 'You will be charged immediately when you subscribe or upgrade. For monthly subscriptions, you will be charged on the same date each month. For annual subscriptions, you will be charged once per year.',
  },
  {
    category: 'Billing & Payments',
    question: 'Can I change my subscription tier?',
    answer: 'Yes! You can upgrade or downgrade your subscription at any time. Upgrades take effect immediately with prorated billing. Downgrades take effect at the end of your current billing period.',
  },
  {
    category: 'Billing & Payments',
    question: 'How do I cancel my subscription?',
    answer: 'You can cancel your subscription at any time from your Profile page. Your subscription will remain active until the end of your current billing period, and you will continue to have access to all features until then.',
  },
  {
    category: 'Billing & Payments',
    question: 'Will I get a refund if I cancel?',
    answer: 'We offer a 30-day money-back guarantee for new subscriptions. If you cancel within 30 days of your initial purchase, you will receive a full refund. After 30 days, refunds are handled on a case-by-case basis.',
  },
  {
    category: 'Billing & Payments',
    question: 'How do I request a refund?',
    answer: 'To request a refund, please contact our support team through the Contact Us page or email support@tradesignal.com. Include your order number and reason for the refund request. We typically process refunds within 5-7 business days.',
  },
  {
    category: 'Billing & Payments',
    question: 'Where can I find my receipts and invoices?',
    answer: 'You can view and download all your receipts and invoices from the Order History page. Each order includes links to download receipts and invoices in PDF format.',
  },
  {
    category: 'Billing & Payments',
    question: 'What happens if my payment fails?',
    answer: 'If your payment fails, we will attempt to charge your card again. You will receive email notifications about failed payments. If payment continues to fail, your subscription may be paused until payment is successful.',
  },
  // Features
  {
    category: 'Features & Usage',
    question: 'What are the limits for each tier?',
    answer: 'Free tier: 5 AI requests/day, 3 alerts, 10 companies tracked, 30 days historical data. Plus tier: 50 AI requests/day, 20 alerts, 50 companies, 1 year historical data. Pro tier: 500 AI requests/day, 100 alerts, unlimited companies, unlimited historical data. Enterprise: Unlimited everything.',
  },
  {
    category: 'Features & Usage',
    question: 'What happens when I reach my usage limit?',
    answer: 'When you reach your daily or monthly limit, you will see a notification prompting you to upgrade. You can continue using the service, but certain features may be restricted until you upgrade or your limit resets.',
  },
  {
    category: 'Features & Usage',
    question: 'Do limits reset daily or monthly?',
    answer: 'AI request limits reset daily at midnight UTC. Alert limits and company tracking limits are based on your subscription tier and do not reset - they are maximum concurrent limits.',
  },
  // Platform & Features
  {
    category: 'Platform & Features',
    question: 'What is TradeSignal and who is it for?',
    answer: 'TradeSignal is a real-time insider trading intelligence platform designed for retail investors, day traders, and financial analysts. We track SEC Form 4 filings, congressional trades (STOCK Act), and institutional flows with LUNA, our advanced AI. Our mission is to level the playing field by giving you the same data institutional investors use to make decisions.',
  },
  {
    category: 'Platform & Features',
    question: 'What makes TradeSignal different from other platforms?',
    answer: 'Unlike traditional screeners, TradeSignal uses LUNA, our proprietary AI engine based on Google Gemini and OpenAI architectures. LUNA analyzes sentiment, detects anomalies, and identifies high-conviction patterns that raw data charts miss. We process 15 million+ filings with 92% sentiment accuracy.',
  },
  {
    category: 'Platform & Features',
    question: 'What is LUNA AI and how does it work?',
    answer: 'LUNA (Large Understanding Network for Analysis) is our custom-tuned Large Language Model engine. It reads thousands of SEC filings to parse text, context, and footnotes, identifying non-standard transaction codes and sentiment that traditional screeners miss. LUNA assigns "Bullish" or "Bearish" sentiment scores to complex transaction patterns with 92% accuracy.',
  },
  // Data & Technology
  {
    category: 'Data & Technology',
    question: 'Where do you get your insider trading data?',
    answer: 'Our primary source is the SEC EDGAR database. We ingest Form 4 filings in near real-time directly from the source. For market data (stock prices), we use Finnhub and Alpha Vantage.',
  },
  {
    category: 'Data & Technology',
    question: 'Is the data real-time?',
    answer: 'Yes. Insider trades appear on our platform within minutes of being filed with the SEC. Market price data may have a standard 15-minute delay depending on the exchange and your subscription tier.',
  },
  {
    category: 'Data & Technology',
    question: 'How does your AI analysis work?',
    answer: 'We utilize LUNA, our custom-tuned Large Language Model engine based on Google Gemini and OpenAI architectures. LUNA parses the text, context, and footnotes of filings to identify non-standard transaction codes and sentiment that traditional screeners miss.',
  },
  {
    category: 'Data & Technology',
    question: 'How accurate is the Congressional trading data?',
    answer: 'Congressional data is sourced from STOCK Act disclosures. Please note that by law, representatives have up to 45 days to report a trade, so this data is inherently delayed relative to the transaction date.',
  },
];

const GlossarySection = () => (
  <div className="mt-20 border-t border-white/10 pt-16">
    <h2 className="text-3xl font-bold text-center mb-12">Glossary of Terms</h2>
    <div className="grid md:grid-cols-2 gap-8">
      {[
        { term: "SEC Form 4", def: "A document that must be filed with the SEC whenever there is a material change in the holdings of company insiders." },
        { term: "10b5-1 Plan", def: "A pre-scheduled trading plan that allows insiders to sell a predetermined number of shares at a set time, often used to avoid accusations of insider trading." },
        { term: "Short-Swing Profit Rule", def: "A regulation preventing insiders from profiting from short-term price swings (within 6 months), discouraging quick flips." },
        { term: "Beneficial Owner", def: "Any person who, directly or indirectly, has the power to vote or dispose of a stock, even if they don't hold the title." },
        { term: "Cluster Buying", def: "When multiple insiders at the same company purchase shares within a short timeframe, often considered a strong bullish signal." },
        { term: "STOCK Act", def: "Stop Trading on Congressional Knowledge Act. A law designed to combat insider trading by members of Congress and their staff." }
      ].map((item, i) => (
        <div key={i} className="bg-white/5 p-6 rounded-xl border border-white/5 hover:border-purple-500/20 transition-colors">
          <h3 className="text-lg font-bold text-white mb-2">{item.term}</h3>
          <p className="text-sm text-gray-400 leading-relaxed">{item.def}</p>
        </div>
      ))}
    </div>
  </div>
);

export default function FAQPage() {
  const [openIndex, setOpenIndex] = useState<number | null>(null);
  const [selectedCategory, setSelectedCategory] = useState<string>('All');

  const categories = ['All', ...Array.from(new Set(faqs.map(faq => faq.category)))];
  const filteredFaqs = selectedCategory === 'All' 
    ? faqs 
    : faqs.filter(faq => faq.category === selectedCategory);

  return (
    <div className="min-h-screen bg-black text-white selection:bg-purple-500 selection:text-white font-sans overflow-x-hidden pb-20">
      
      {/* Hero Section */}
      <section className="relative pt-32 pb-20 overflow-hidden">
        {/* Abstract Background Elements */}
        <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[800px] h-[500px] bg-purple-600/20 rounded-full blur-[100px] -z-10" />
        
        <div className="max-w-7xl mx-auto px-6 text-center relative z-10">
          <h1 className="text-4xl lg:text-6xl font-bold mb-6">
            Frequently Asked <br />
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-purple-400 to-blue-400">
              Questions
            </span>
          </h1>
          <p className="text-xl text-gray-400 max-w-2xl mx-auto mb-8">
            Find answers to common questions about billing, payments, refunds, and features.
          </p>
          <p className="text-gray-400 max-w-3xl mx-auto text-center">
            TradeSignal provides real-time insider trading intelligence by tracking SEC Form 4 filings,
            congressional trades, and market-moving transactions with LUNA, our advanced AI engine.
            Below are answers to common questions about our service.
          </p>
        </div>
      </section>

      <div className="max-w-4xl mx-auto px-6 space-y-12">
        {/* Category Filter */}
        <div className="flex flex-wrap justify-center gap-3">
          {categories.map((category) => (
            <button
              key={category}
              onClick={() => setSelectedCategory(category)}
              className={`px-5 py-2.5 rounded-full font-medium transition-all duration-300 ${
                selectedCategory === category
                  ? 'bg-purple-600 text-white shadow-lg shadow-purple-500/30'
                  : 'bg-white/5 border border-white/10 text-gray-400 hover:bg-white/10 hover:text-white'
              }`}
            >
              {category}
            </button>
          ))}
        </div>

        {/* FAQ List */}
        <div className="space-y-4">
          {filteredFaqs.map((faq, index) => (
            <div 
              key={index} 
              className="bg-gray-900/50 border border-white/10 rounded-2xl overflow-hidden hover:border-purple-500/30 transition-colors"
            >
              <button
                onClick={() => setOpenIndex(openIndex === index ? null : index)}
                className="w-full flex items-start justify-between text-left p-6"
              >
                <div className="flex-1 pr-4">
                  <div className="flex items-center space-x-2 mb-2">
                    <HelpCircle className="h-4 w-4 text-purple-400" />
                    <span className="text-xs font-semibold text-purple-400 tracking-wider uppercase">{faq.category}</span>
                  </div>
                  <h3 className="text-lg font-semibold text-white">{faq.question}</h3>
                </div>
                {openIndex === index ? (
                  <ChevronUp className="h-5 w-5 text-gray-400 mt-1 flex-shrink-0" />
                ) : (
                  <ChevronDown className="h-5 w-5 text-gray-400 mt-1 flex-shrink-0" />
                )}
              </button>
              
              <div 
                className={`overflow-hidden transition-all duration-300 ease-in-out ${
                  openIndex === index ? 'max-h-96 opacity-100' : 'max-h-0 opacity-0'
                }`}
              >
                <div className="px-6 pb-6 pt-0 text-gray-400 leading-relaxed border-t border-white/5">
                  <div className="pt-4">{faq.answer}</div>
                </div>
              </div>
            </div>
          ))}
        </div>

        <GlossarySection />

        {/* Contact Support */}
        <div className="bg-gradient-to-br from-blue-900/40 to-purple-900/40 border border-white/10 rounded-3xl p-8 text-center relative overflow-hidden">
          <div className="relative z-10">
            <h3 className="text-2xl font-bold text-white mb-3">Still have questions?</h3>
            <p className="text-gray-400 mb-8 max-w-xl mx-auto">
              Can't find what you're looking for? Our support team is here to help you with any issue.
            </p>
            <a
              href="/contact"
              className="inline-flex items-center gap-2 px-8 py-3 bg-white text-black font-semibold rounded-full hover:bg-gray-100 transition-all hover:scale-105"
            >
              <Mail className="w-4 h-4" />
              Contact Support
            </a>
          </div>
          {/* Background decoration */}
          <div className="absolute top-0 right-0 w-64 h-64 bg-purple-500/10 rounded-full blur-[80px] -z-0" />
          <div className="absolute bottom-0 left-0 w-64 h-64 bg-blue-500/10 rounded-full blur-[80px] -z-0" />
        </div>
      </div>
    </div>
  );
}


