import { useState } from 'react';
import { ChevronDown, ChevronUp } from 'lucide-react';

interface FAQItem {
  question: string;
  answer: string;
}

const faqData: FAQItem[] = [
  {
    question: 'What is TradeSignal?',
    answer: 'TradeSignal is a comprehensive platform that tracks insider trading activities, congressional trades, and provides real-time market intelligence to help you make informed investment decisions.',
  },
  {
    question: 'How do I get started?',
    answer: 'Simply create a free account to get started. You can browse basic features immediately, and upgrade to a paid plan for access to advanced features like AI insights, real-time alerts, and detailed analytics.',
  },
  {
    question: 'What subscription plans are available?',
    answer: 'We offer several subscription tiers: Free (basic features), Basic, Plus, Pro, and Enterprise. Each tier provides different levels of access to our data and features. Visit our pricing page for detailed information.',
  },
  {
    question: 'How accurate is the insider trading data?',
    answer: 'Our data is sourced directly from SEC filings (Form 4, Form 144) and is updated in real-time. We ensure the highest level of accuracy by cross-referencing multiple data sources and maintaining strict quality controls.',
  },
  {
    question: 'Can I set up alerts for specific stocks?',
    answer: 'Yes! With a Basic plan or higher, you can create custom alerts for specific stocks, insiders, or trade types. You\'ll receive notifications via email or push notifications when matching trades occur.',
  },
  {
    question: 'Is my data secure?',
    answer: 'Absolutely. We use industry-standard encryption, secure authentication, and follow best practices for data protection. Your personal information and payment details are never shared with third parties.',
  },
  {
    question: 'What payment methods do you accept?',
    answer: 'We accept all major credit cards and process payments securely through Stripe. All transactions are encrypted and secure.',
  },
  {
    question: 'Can I cancel my subscription anytime?',
    answer: 'Yes, you can cancel your subscription at any time from your account settings. Your access will continue until the end of your current billing period.',
  },
];

interface FAQItemProps {
  item: FAQItem;
  isOpen: boolean;
  onToggle: () => void;
}

function FAQItemComponent({ item, isOpen, onToggle }: FAQItemProps) {
  return (
    <div className="border border-white/10 rounded-xl overflow-hidden transition-all duration-300 hover:border-purple-500/30 bg-white/5">
      <button
        onClick={onToggle}
        className="w-full px-6 py-4 flex items-center justify-between text-left hover:bg-white/5 transition-colors"
      >
        <span className="font-semibold text-white pr-4">{item.question}</span>
        <div className="flex-shrink-0">
          {isOpen ? (
            <ChevronUp className="w-5 h-5 text-purple-400" />
          ) : (
            <ChevronDown className="w-5 h-5 text-gray-400" />
          )}
        </div>
      </button>
      {isOpen && (
        <div className="px-6 py-4 bg-black/20 border-t border-white/5">
          <p className="text-gray-400 leading-relaxed">{item.answer}</p>
        </div>
      )}
    </div>
  );
}

export default function FAQSection() {
  const [openIndex, setOpenIndex] = useState<number | null>(null);

  const toggleItem = (index: number) => {
    setOpenIndex(openIndex === index ? null : index);
  };

  return (
    <div className="space-y-4">
      <h2 className="text-2xl font-bold text-white mb-6">
        Frequently Asked Questions
      </h2>
      <div className="space-y-3">
        {faqData.map((item, index) => (
          <FAQItemComponent
            key={index}
            item={item}
            isOpen={openIndex === index}
            onToggle={() => toggleItem(index)}
          />
        ))}
      </div>
    </div>
  );
}
