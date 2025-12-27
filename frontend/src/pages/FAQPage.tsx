import { useState } from 'react';
import { ChevronDown, ChevronUp, HelpCircle, Mail } from 'lucide-react';

interface FAQItem {
  question: string;
  answer: string;
  category: string;
}

// PORTFOLIO MODE: Removed billing FAQs, kept platform and data FAQs
const faqs: FAQItem[] = [
  // Platform & Features
  {
    category: 'Platform & Features',
    question: 'What is TradeSignal and who is it for?',
    answer: 'TradeSignal is a real-time insider trading intelligence platform designed for retail investors, day traders, and financial analysts. We track SEC Form 4 filings, congressional trades (STOCK Act), and institutional flows with LUNA, our AI engine powered by Google Gemini.',
  },
  {
    category: 'Platform & Features',
    question: 'What makes TradeSignal different from other platforms?',
    answer: 'TradeSignal uses LUNA, an AI engine powered by Google Gemini that analyzes sentiment, detects trading clusters, and identifies high-conviction patterns. The platform combines real SEC data with AI-powered insights in a modern, intuitive interface.',
  },
  {
    category: 'Platform & Features',
    question: 'What is LUNA AI and how does it work?',
    answer: 'LUNA is our AI analysis engine built on Google Gemini. It reads SEC filings to parse text, context, and footnotes, identifying transaction patterns and sentiment that traditional screeners miss. LUNA assigns "Bullish" or "Bearish" sentiment scores to complex transactions.',
  },
  {
    category: 'Platform & Features',
    question: 'Is TradeSignal free to use?',
    answer: 'Yes! TradeSignal is currently free to use as a portfolio showcase project. All features are accessible without any subscription or payment. Subscription tiers are planned for future development.',
  },
  // Data & Technology
  {
    category: 'Data & Technology',
    question: 'Where do you get your insider trading data?',
    answer: 'Our primary source is the SEC EDGAR database. We ingest Form 4 filings in near real-time directly from the source. For market data (stock prices), we use Finnhub and Alpha Vantage APIs.',
  },
  {
    category: 'Data & Technology',
    question: 'Is the data real-time?',
    answer: 'Yes. Insider trades appear on our platform within minutes of being filed with the SEC. Market price data may have a standard 15-minute delay depending on the data provider.',
  },
  {
    category: 'Data & Technology',
    question: 'How does your AI analysis work?',
    answer: 'We utilize LUNA, our AI engine powered by Google Gemini. LUNA parses the text, context, and footnotes of SEC filings to identify non-standard transaction codes and sentiment that traditional screeners miss.',
  },
  {
    category: 'Data & Technology',
    question: 'How accurate is the Congressional trading data?',
    answer: 'Congressional data is sourced from STOCK Act disclosures. Please note that by law, representatives have up to 45 days to report a trade, so this data is inherently delayed relative to the transaction date.',
  },
  // Future Enhancements
  {
    category: 'Future Enhancements',
    question: 'Will there be subscription tiers in the future?',
    answer: 'Subscription tiers are planned for future development. Currently, all features are free to access as this is a portfolio showcase project demonstrating full-stack development capabilities.',
  },
  {
    category: 'Future Enhancements',
    question: 'Will there be API access?',
    answer: 'Programmatic API access with API keys is planned for future development. You can explore the current API structure in our interactive API documentation at /api-docs.',
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
            Find answers to common questions about TradeSignal's features and technology.
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


