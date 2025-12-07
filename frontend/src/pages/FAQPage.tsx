import { useState } from 'react';
import { ChevronDown, ChevronUp, HelpCircle } from 'lucide-react';

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
];

export default function FAQPage() {
  const [openIndex, setOpenIndex] = useState<number | null>(null);
  const [selectedCategory, setSelectedCategory] = useState<string>('All');

  const categories = ['All', ...Array.from(new Set(faqs.map(faq => faq.category)))];
  const filteredFaqs = selectedCategory === 'All' 
    ? faqs 
    : faqs.filter(faq => faq.category === selectedCategory);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Frequently Asked Questions</h1>
        <p className="mt-2 text-gray-600">
          Find answers to common questions about billing, payments, refunds, and features
        </p>
      </div>

      {/* Category Filter */}
      <div className="flex flex-wrap gap-2">
        {categories.map((category) => (
          <button
            key={category}
            onClick={() => setSelectedCategory(category)}
            className={`px-4 py-2 rounded-lg font-medium transition-colors ${
              selectedCategory === category
                ? 'bg-blue-600 text-white'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            {category}
          </button>
        ))}
      </div>

      {/* FAQ List */}
      <div className="space-y-4">
        {filteredFaqs.map((faq, index) => (
          <div key={index} className="card">
            <button
              onClick={() => setOpenIndex(openIndex === index ? null : index)}
              className="w-full flex items-start justify-between text-left"
            >
              <div className="flex-1">
                <div className="flex items-center space-x-2 mb-1">
                  <HelpCircle className="h-5 w-5 text-blue-600" />
                  <span className="text-xs font-semibold text-blue-600">{faq.category}</span>
                </div>
                <h3 className="font-semibold text-gray-900">{faq.question}</h3>
              </div>
              {openIndex === index ? (
                <ChevronUp className="h-5 w-5 text-gray-500 ml-4 flex-shrink-0" />
              ) : (
                <ChevronDown className="h-5 w-5 text-gray-500 ml-4 flex-shrink-0" />
              )}
            </button>
            {openIndex === index && (
              <div className="mt-4 pt-4 border-t border-gray-200">
                <p className="text-gray-700 leading-relaxed">{faq.answer}</p>
              </div>
            )}
          </div>
        ))}
      </div>

      {/* Contact Support */}
      <div className="card bg-blue-50 border-blue-200">
        <h3 className="font-semibold text-gray-900 mb-2">Still have questions?</h3>
        <p className="text-gray-700 mb-4">
          Can't find what you're looking for? Our support team is here to help.
        </p>
        <a
          href="/contact"
          className="inline-flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
        >
          Contact Support
        </a>
      </div>
    </div>
  );
}

