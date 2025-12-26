import { Eye, Keyboard, Volume2, Type, Monitor, Heart, Mail, CheckCircle2 } from 'lucide-react';
import { Link } from 'react-router-dom';

const AccessibilityPage = () => {
  const features = [
    {
      icon: Eye,
      title: "Screen Reader Support",
      description: "Full compatibility with NVDA, JAWS, and VoiceOver",
      items: [
        "Semantic HTML5 markup for proper document structure",
        "ARIA labels and landmarks for navigation",
        "Alternative text for all images and icons",
        "Skip navigation links for keyboard users",
        "Live regions for dynamic content updates"
      ]
    },
    {
      icon: Keyboard,
      title: "Keyboard Navigation",
      description: "Complete keyboard accessibility for all features",
      items: [
        "Tab navigation through all interactive elements",
        "Arrow keys for dropdown and menu navigation",
        "Enter and Space for button activation",
        "Escape key to close modals and dropdowns",
        "Visible focus indicators on all focusable elements"
      ]
    },
    {
      icon: Type,
      title: "Text & Visual Customization",
      description: "Adjust text size and contrast for better readability",
      items: [
        "Text resizable up to 200% without loss of functionality",
        "High contrast mode with WCAG AAA compliance",
        "Adjustable font sizes in user settings",
        "Support for browser zoom up to 400%",
        "Clear visual hierarchy and spacing"
      ]
    },
    {
      icon: Monitor,
      title: "Responsive Design",
      description: "Optimized for all devices and screen sizes",
      items: [
        "Mobile-first responsive layout",
        "Touch-friendly interface with 44px minimum target size",
        "Portrait and landscape orientation support",
        "Consistent experience across desktop, tablet, and mobile",
        "Adaptive UI for different viewport sizes"
      ]
    },
    {
      icon: Volume2,
      title: "Audio & Visual Alternatives",
      description: "Multiple ways to consume information",
      items: [
        "Captions and transcripts for video content (coming soon)",
        "Visual and audio alerts for notifications",
        "Text alternatives for charts and graphs",
        "Color not used as the only visual means of information",
        "Icon labels and tooltips for clarity"
      ]
    },
    {
      icon: Heart,
      title: "Cognitive Accessibility",
      description: "Clear, simple, and consistent user experience",
      items: [
        "Consistent navigation across all pages",
        "Plain language and clear instructions",
        "Error messages with helpful guidance",
        "Predictable UI behavior and interactions",
        "Sufficient time for form completion (no arbitrary timeouts)"
      ]
    }
  ];

  const wcagCompliance = [
    { level: "A", status: "Compliant", description: "Essential accessibility features" },
    { level: "AA", status: "Compliant", description: "Enhanced accessibility (our target)" },
    { level: "AAA", status: "Partial", description: "Highest level (in progress)" }
  ];

  const keyboardShortcuts = [
    { keys: "Tab", action: "Navigate to next interactive element" },
    { keys: "Shift + Tab", action: "Navigate to previous interactive element" },
    { keys: "Enter / Space", action: "Activate buttons and links" },
    { keys: "Esc", action: "Close modals and dropdowns" },
    { keys: "Arrow Keys", action: "Navigate within dropdowns and menus" },
    { keys: "/ (Slash)", action: "Focus search bar" },
    { keys: "Ctrl/Cmd + K", action: "Open command palette (PRO)" }
  ];

  return (
    <div className="min-h-screen bg-[#0a0a0a] text-white">
      {/* Hero Section */}
      <section className="pt-32 pb-16 px-4 bg-gradient-to-b from-[#0f0f1a] to-[#0a0a0a]">
        <div className="max-w-5xl mx-auto text-center">
          <div className="inline-flex items-center gap-2 bg-blue-500/10 border border-blue-500/20 rounded-full px-4 py-2 mb-6">
            <Heart className="w-4 h-4 text-blue-400" />
            <span className="text-sm text-blue-300">Accessibility</span>
          </div>
          <h1 className="text-5xl font-bold mb-6">
            Accessible to
            <span className="block bg-gradient-to-r from-blue-400 via-purple-400 to-blue-400 bg-clip-text text-transparent mt-2">
              Everyone
            </span>
          </h1>
          <p className="text-xl text-gray-400 max-w-3xl mx-auto mb-8">
            We're committed to making TradeSignal accessible to all traders, regardless of ability. Our platform follows WCAG 2.1 Level AA standards.
          </p>
        </div>
      </section>

      {/* WCAG Compliance */}
      <section className="py-12 px-4 border-b border-white/5">
        <div className="max-w-7xl mx-auto">
          <h2 className="text-2xl font-bold text-center mb-8">WCAG 2.1 Compliance Status</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {wcagCompliance.map((level, index) => (
              <div key={index} className="bg-[#0f0f1a] border border-white/10 rounded-2xl p-6 text-center">
                <div className="flex items-center justify-center mb-4">
                  {level.status === 'Compliant' ? (
                    <CheckCircle2 className="w-8 h-8 text-green-400" />
                  ) : (
                    <Eye className="w-8 h-8 text-yellow-400" />
                  )}
                </div>
                <h3 className="text-2xl font-bold mb-2">Level {level.level}</h3>
                <span className={`inline-block px-3 py-1 rounded-full text-xs font-medium mb-3 ${
                  level.status === 'Compliant' ? 'bg-green-500/20 text-green-400' : 'bg-yellow-500/20 text-yellow-400'
                }`}>
                  {level.status}
                </span>
                <p className="text-sm text-gray-400">{level.description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Accessibility Features */}
      <section className="py-16 px-4">
        <div className="max-w-7xl mx-auto">
          <h2 className="text-3xl font-bold text-center mb-12">Accessibility Features</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {features.map((feature, index) => (
              <div key={index} className="bg-[#0f0f1a] border border-white/10 rounded-2xl p-8 hover:border-blue-500/30 transition-all">
                <div className="bg-blue-500/10 p-4 rounded-2xl inline-flex mb-6">
                  <feature.icon className="w-6 h-6 text-blue-400" />
                </div>
                <h3 className="text-xl font-bold mb-2">{feature.title}</h3>
                <p className="text-gray-400 text-sm mb-6">{feature.description}</p>
                <ul className="space-y-2">
                  {feature.items.map((item, itemIndex) => (
                    <li key={itemIndex} className="flex items-start gap-2 text-sm text-gray-300">
                      <CheckCircle2 className="w-4 h-4 text-blue-400 flex-shrink-0 mt-0.5" />
                      <span>{item}</span>
                    </li>
                  ))}
                </ul>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Keyboard Shortcuts */}
      <section className="py-16 px-4 bg-[#0f0f1a]">
        <div className="max-w-5xl mx-auto">
          <div className="text-center mb-12">
            <Keyboard className="w-12 h-12 text-purple-400 mx-auto mb-4" />
            <h2 className="text-3xl font-bold mb-4">Keyboard Shortcuts</h2>
            <p className="text-gray-400">Navigate TradeSignal efficiently using your keyboard</p>
          </div>

          <div className="bg-[#0a0a0a] border border-white/10 rounded-2xl overflow-hidden">
            <table className="w-full">
              <thead className="bg-white/5 border-b border-white/5">
                <tr>
                  <th className="text-left px-6 py-4 text-sm font-semibold text-gray-300">Keys</th>
                  <th className="text-left px-6 py-4 text-sm font-semibold text-gray-300">Action</th>
                </tr>
              </thead>
              <tbody>
                {keyboardShortcuts.map((shortcut, index) => (
                  <tr key={index} className="border-b border-white/5 hover:bg-white/5 transition-colors">
                    <td className="px-6 py-4">
                      <kbd className="bg-white/10 border border-white/20 rounded px-3 py-1.5 text-sm font-mono">
                        {shortcut.keys}
                      </kbd>
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-300">{shortcut.action}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </section>

      {/* Known Issues & Roadmap */}
      <section className="py-16 px-4">
        <div className="max-w-5xl mx-auto">
          <h2 className="text-3xl font-bold text-center mb-12">Ongoing Improvements</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            {/* Known Issues */}
            <div className="bg-[#0f0f1a] border border-white/10 rounded-2xl p-8">
              <h3 className="text-xl font-bold mb-6 flex items-center gap-2">
                <Eye className="w-5 h-5 text-yellow-400" />
                Known Issues
              </h3>
              <ul className="space-y-3 text-sm text-gray-300">
                <li className="flex items-start gap-2">
                  <span className="text-yellow-400 mt-0.5">⚠</span>
                  Charts may not be fully accessible to screen readers (working on data table alternatives)
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-yellow-400 mt-0.5">⚠</span>
                  Some third-party chart libraries have limited keyboard navigation
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-yellow-400 mt-0.5">⚠</span>
                  Video content does not yet have captions (Q1 2025 roadmap)
                </li>
              </ul>
            </div>

            {/* Roadmap */}
            <div className="bg-[#0f0f1a] border border-white/10 rounded-2xl p-8">
              <h3 className="text-xl font-bold mb-6 flex items-center gap-2">
                <CheckCircle2 className="w-5 h-5 text-green-400" />
                Coming Soon
              </h3>
              <ul className="space-y-3 text-sm text-gray-300">
                <li className="flex items-start gap-2">
                  <CheckCircle2 className="w-4 h-4 text-green-400 mt-0.5 flex-shrink-0" />
                  Screen reader-friendly data tables for all charts
                </li>
                <li className="flex items-start gap-2">
                  <CheckCircle2 className="w-4 h-4 text-green-400 mt-0.5 flex-shrink-0" />
                  Closed captions for all video tutorials
                </li>
                <li className="flex items-start gap-2">
                  <CheckCircle2 className="w-4 h-4 text-green-400 mt-0.5 flex-shrink-0" />
                  Enhanced voice control support
                </li>
                <li className="flex items-start gap-2">
                  <CheckCircle2 className="w-4 h-4 text-green-400 mt-0.5 flex-shrink-0" />
                  WCAG 2.1 Level AAA compliance (target Q2 2025)
                </li>
              </ul>
            </div>
          </div>
        </div>
      </section>

      {/* Assistive Technologies */}
      <section className="py-16 px-4 bg-[#0f0f1a]">
        <div className="max-w-5xl mx-auto text-center">
          <h2 className="text-3xl font-bold mb-8">Tested with Assistive Technologies</h2>
          <p className="text-gray-400 mb-12 max-w-3xl mx-auto">
            We regularly test TradeSignal with popular assistive technologies to ensure compatibility
          </p>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
            {[
              { name: "JAWS", platform: "Windows" },
              { name: "NVDA", platform: "Windows" },
              { name: "VoiceOver", platform: "macOS/iOS" },
              { name: "TalkBack", platform: "Android" }
            ].map((tech, index) => (
              <div key={index} className="bg-[#0a0a0a] border border-white/10 rounded-2xl p-6">
                <div className="text-2xl font-bold text-purple-400 mb-2">{tech.name}</div>
                <div className="text-sm text-gray-500">{tech.platform}</div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Feedback */}
      <section className="py-20 px-4 bg-gradient-to-b from-[#0a0a0a] to-[#0f0f1a]">
        <div className="max-w-4xl mx-auto text-center">
          <div className="bg-[#0f0f1a] border border-blue-500/20 rounded-3xl p-12">
            <Mail className="w-12 h-12 text-blue-400 mx-auto mb-4" />
            <h2 className="text-3xl font-bold mb-4">Help Us Improve Accessibility</h2>
            <p className="text-gray-400 mb-8">
              If you encounter any accessibility barriers or have suggestions for improvement, please let us know. Your feedback helps us build a better platform for everyone.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <a
                href="mailto:accessibility@tradesignal.com"
                className="inline-flex items-center justify-center gap-2 bg-white text-black px-8 py-4 rounded-full font-bold hover:bg-gray-200 transition-all"
              >
                <Mail className="w-5 h-5" />
                accessibility@tradesignal.com
              </a>
              <Link
                to="/support"
                className="inline-flex items-center justify-center gap-2 bg-white/5 border border-white/10 text-white px-8 py-4 rounded-full font-bold hover:bg-white/10 transition-all"
              >
                Visit Help Center
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* Commitment Statement */}
      <section className="py-16 px-4">
        <div className="max-w-4xl mx-auto">
          <div className="bg-[#0f0f1a] border border-white/10 rounded-2xl p-8">
            <h2 className="text-2xl font-bold mb-4">Our Commitment</h2>
            <div className="prose prose-invert max-w-none text-gray-300 space-y-4">
              <p>
                TradeSignal is committed to ensuring digital accessibility for people with disabilities. We are continually improving the user experience for everyone and applying the relevant accessibility standards.
              </p>
              <p>
                We aim to meet WCAG 2.1 Level AA standards and are working toward Level AAA compliance. Our team conducts regular accessibility audits and works with users who have disabilities to identify and fix issues.
              </p>
              <p>
                This is an ongoing effort, and we welcome feedback from our community. If you have any questions or suggestions about the accessibility of TradeSignal, please contact us at{' '}
                <a href="mailto:accessibility@tradesignal.com" className="text-blue-400 hover:text-blue-300">
                  accessibility@tradesignal.com
                </a>
              </p>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
};

export default AccessibilityPage;
