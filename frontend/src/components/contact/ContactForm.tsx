import { useState } from 'react';
import { Send } from 'lucide-react';

interface ContactFormProps {
  onSubmit: (data: ContactFormData) => Promise<void>;
  initialData?: Partial<ContactFormData>;
  isSubmitting?: boolean;
  submitStatus?: 'idle' | 'success' | 'error';
}

export interface ContactFormData {
  name: string;
  company_name: string;
  email: string;
  phone: string;
  message: string;
  privacyAccepted: boolean;
}

export default function ContactForm({
  onSubmit,
  initialData,
  isSubmitting = false,
  submitStatus = 'idle',
}: ContactFormProps) {
  const [formData, setFormData] = useState<ContactFormData>({
    name: initialData?.name || '',
    company_name: initialData?.company_name || '',
    email: initialData?.email || '',
    phone: initialData?.phone || '',
    message: initialData?.message || '',
    privacyAccepted: false,
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!formData.privacyAccepted) {
      return;
    }
    await onSubmit(formData);
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-5">
      {submitStatus === 'success' && (
        <div className="p-4 bg-green-50 border border-green-200 rounded-lg">
          <p className="text-green-800 text-sm">
            Thank you! Your message has been sent. We'll get back to you within 24 hours.
          </p>
        </div>
      )}

      {submitStatus === 'error' && (
        <div className="p-4 bg-red-50 border border-red-200 rounded-lg">
          <p className="text-red-800 text-sm">
            There was an error sending your message. Please try again later.
          </p>
        </div>
      )}

      <div>
        <label htmlFor="name" className="block text-sm font-medium text-gray-700 mb-2">
          Full Name <span className="text-red-500">*</span>
        </label>
        <input
          type="text"
          id="name"
          required
          value={formData.name}
          onChange={(e) => setFormData({ ...formData, name: e.target.value })}
          className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-[#6766FF] focus:border-transparent transition-all"
          placeholder="John Doe"
        />
      </div>

      <div>
        <label htmlFor="company_name" className="block text-sm font-medium text-gray-700 mb-2">
          Your Company Name
        </label>
        <input
          type="text"
          id="company_name"
          value={formData.company_name}
          onChange={(e) => setFormData({ ...formData, company_name: e.target.value })}
          className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-[#6766FF] focus:border-transparent transition-all"
          placeholder="Acme Inc."
        />
      </div>

      <div>
        <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-2">
          Email <span className="text-red-500">*</span>
        </label>
        <input
          type="email"
          id="email"
          required
          value={formData.email}
          onChange={(e) => setFormData({ ...formData, email: e.target.value })}
          className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-[#6766FF] focus:border-transparent transition-all"
          placeholder="john@example.com"
        />
      </div>

      <div>
        <label htmlFor="phone" className="block text-sm font-medium text-gray-700 mb-2">
          Phone Number
        </label>
        <input
          type="tel"
          id="phone"
          value={formData.phone}
          onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
          className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-[#6766FF] focus:border-transparent transition-all"
          placeholder="+1 (555) 123-4567"
        />
      </div>

      <div>
        <label htmlFor="message" className="block text-sm font-medium text-gray-700 mb-2">
          How Can We Help? <span className="text-red-500">*</span>
        </label>
        <textarea
          id="message"
          required
          rows={6}
          value={formData.message}
          onChange={(e) => setFormData({ ...formData, message: e.target.value })}
          className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-[#6766FF] focus:border-transparent transition-all resize-none"
          placeholder="Tell us how we can help you..."
          minLength={10}
        />
      </div>

      <div className="flex items-start">
        <input
          type="checkbox"
          id="privacy"
          required
          checked={formData.privacyAccepted}
          onChange={(e) => setFormData({ ...formData, privacyAccepted: e.target.checked })}
          className="mt-1 h-4 w-4 text-[#6766FF] border-gray-300 rounded focus:ring-[#6766FF]"
        />
        <label htmlFor="privacy" className="ml-2 text-sm text-gray-600">
          I agree to the{' '}
          <a href="/privacy" className="text-[#6766FF] hover:underline">
            Privacy Policy
          </a>
        </label>
      </div>

      <button
        type="submit"
        disabled={isSubmitting || !formData.privacyAccepted}
        className="w-full flex items-center justify-center space-x-2 px-6 py-3 bg-[#6766FF] text-white rounded-lg hover:bg-[#5A59E6] transition-colors disabled:opacity-50 disabled:cursor-not-allowed font-semibold shadow-md hover:shadow-lg"
      >
        <Send className="h-5 w-5" />
        <span>{isSubmitting ? 'Sending...' : 'Submit'}</span>
      </button>
    </form>
  );
}
