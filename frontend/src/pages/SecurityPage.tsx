import { Shield, Lock, Eye, FileCheck, AlertTriangle, CheckCircle2, Mail, ExternalLink } from 'lucide-react';
import { Link } from 'react-router-dom';

const SecurityPage = () => {
  const securityFeatures = [
    {
      icon: Lock,
      title: "End-to-End Encryption",
      description: "All data transmitted between your browser and our servers is encrypted using industry-standard TLS 1.3 protocol.",
      details: ["AES-256 encryption at rest", "TLS 1.3 in transit", "Zero-knowledge architecture for API keys"]
    },
    {
      icon: Shield,
      title: "SOC 2 Type II Compliant",
      description: "We undergo regular third-party security audits to ensure the highest standards of data protection.",
      details: ["Annual penetration testing", "Quarterly vulnerability scans", "24/7 security monitoring"]
    },
    {
      icon: Eye,
      title: "Privacy-First Design",
      description: "We never sell your data. Your trading strategies and watchlists remain completely private.",
      details: ["GDPR & CCPA compliant", "Data minimization principles", "Opt-in analytics only"]
    },
    {
      icon: FileCheck,
      title: "Secure Data Storage",
      description: "Your data is stored in enterprise-grade data centers with redundancy and automated backups.",
      details: ["Multi-region redundancy", "Daily encrypted backups", "99.99% uptime SLA"]
    }
  ];

  const complianceItems = [
    { name: "SOC 2 Type II", status: "Certified", year: "2024" },
    { name: "GDPR", status: "Compliant", year: "2024" },
    { name: "CCPA", status: "Compliant", year: "2024" },
    { name: "ISO 27001", status: "In Progress", year: "2025" }
  ];

  const vulnerabilityProgram = {
    scope: [
      "Web application (tradesignal.com)",
      "API endpoints (api.tradesignal.com)",
      "Mobile apps (iOS & Android)",
      "Infrastructure & cloud services"
    ],
    outOfScope: [
      "Social engineering attacks",
      "Denial of Service (DoS/DDoS)",
      "Physical security testing",
      "Third-party services"
    ]
  };

  return (
    <div className="min-h-screen bg-[#0a0a0a] text-white">
      {/* Hero Section */}
      <section className="pt-32 pb-16 px-4 bg-gradient-to-b from-[#0f0f1a] to-[#0a0a0a]">
        <div className="max-w-5xl mx-auto text-center">
          <div className="inline-flex items-center gap-2 bg-green-500/10 border border-green-500/20 rounded-full px-4 py-2 mb-6">
            <Shield className="w-4 h-4 text-green-400" />
            <span className="text-sm text-green-300">Security & Compliance</span>
          </div>
          <h1 className="text-5xl font-bold mb-6">
            Your Security is
            <span className="block bg-gradient-to-r from-green-400 via-blue-400 to-green-400 bg-clip-text text-transparent mt-2">
              Our Priority
            </span>
          </h1>
          <p className="text-xl text-gray-400 max-w-3xl mx-auto mb-8">
            We implement industry-leading security practices to protect your data and ensure compliance with global privacy regulations.
          </p>
        </div>
      </section>

      {/* Trust Badges */}
      <section className="py-12 px-4 border-b border-white/5">
        <div className="max-w-7xl mx-auto grid grid-cols-2 md:grid-cols-4 gap-6">
          {complianceItems.map((item, index) => (
            <div key={index} className="bg-[#0f0f1a] border border-white/10 rounded-2xl p-6 text-center">
              <div className="flex items-center justify-center mb-3">
                {item.status === 'Certified' || item.status === 'Compliant' ? (
                  <CheckCircle2 className="w-6 h-6 text-green-400" />
                ) : (
                  <AlertTriangle className="w-6 h-6 text-yellow-400" />
                )}
              </div>
              <h3 className="text-lg font-bold mb-1">{item.name}</h3>
              <p className="text-sm text-gray-400">{item.status}</p>
              <span className="text-xs text-gray-500 mt-1 block">{item.year}</span>
            </div>
          ))}
        </div>
      </section>

      {/* Security Features */}
      <section className="py-16 px-4">
        <div className="max-w-7xl mx-auto">
          <h2 className="text-3xl font-bold text-center mb-12">How We Protect Your Data</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            {securityFeatures.map((feature, index) => (
              <div key={index} className="bg-[#0f0f1a] border border-white/10 rounded-2xl p-8 hover:border-green-500/30 transition-all">
                <div className="bg-green-500/10 p-4 rounded-2xl inline-flex mb-6">
                  <feature.icon className="w-8 h-8 text-green-400" />
                </div>
                <h3 className="text-2xl font-bold mb-3">{feature.title}</h3>
                <p className="text-gray-400 mb-6">{feature.description}</p>
                <ul className="space-y-2">
                  {feature.details.map((detail, detailIndex) => (
                    <li key={detailIndex} className="flex items-start gap-2 text-sm text-gray-300">
                      <CheckCircle2 className="w-4 h-4 text-green-400 flex-shrink-0 mt-0.5" />
                      {detail}
                    </li>
                  ))}
                </ul>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Bug Bounty Program */}
      <section className="py-16 px-4 bg-[#0f0f1a]">
        <div className="max-w-5xl mx-auto">
          <div className="text-center mb-12">
            <AlertTriangle className="w-12 h-12 text-yellow-400 mx-auto mb-4" />
            <h2 className="text-3xl font-bold mb-4">Responsible Disclosure Program</h2>
            <p className="text-gray-400 max-w-2xl mx-auto">
              We welcome security researchers to help us keep TradeSignal secure. Report vulnerabilities responsibly and earn rewards.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mb-12">
            {/* In Scope */}
            <div className="bg-[#0a0a0a] border border-white/10 rounded-2xl p-8">
              <h3 className="text-xl font-bold mb-4 flex items-center gap-2">
                <CheckCircle2 className="w-5 h-5 text-green-400" />
                In Scope
              </h3>
              <ul className="space-y-2">
                {vulnerabilityProgram.scope.map((item, index) => (
                  <li key={index} className="flex items-start gap-2 text-sm text-gray-300">
                    <span className="text-green-400 mt-0.5">✓</span>
                    {item}
                  </li>
                ))}
              </ul>
            </div>

            {/* Out of Scope */}
            <div className="bg-[#0a0a0a] border border-white/10 rounded-2xl p-8">
              <h3 className="text-xl font-bold mb-4 flex items-center gap-2">
                <AlertTriangle className="w-5 h-5 text-red-400" />
                Out of Scope
              </h3>
              <ul className="space-y-2">
                {vulnerabilityProgram.outOfScope.map((item, index) => (
                  <li key={index} className="flex items-start gap-2 text-sm text-gray-300">
                    <span className="text-red-400 mt-0.5">✗</span>
                    {item}
                  </li>
                ))}
              </ul>
            </div>
          </div>

          {/* Reward Tiers */}
          <div className="bg-gradient-to-br from-purple-500/10 to-blue-500/10 border border-purple-500/20 rounded-2xl p-8">
            <h3 className="text-xl font-bold mb-6">Reward Tiers</h3>
            <div className="grid grid-cols-1 sm:grid-cols-4 gap-4">
              <div className="text-center">
                <div className="text-3xl font-bold text-red-400 mb-1">$5,000</div>
                <div className="text-sm text-gray-400">Critical</div>
              </div>
              <div className="text-center">
                <div className="text-3xl font-bold text-orange-400 mb-1">$2,500</div>
                <div className="text-sm text-gray-400">High</div>
              </div>
              <div className="text-center">
                <div className="text-3xl font-bold text-yellow-400 mb-1">$1,000</div>
                <div className="text-sm text-gray-400">Medium</div>
              </div>
              <div className="text-center">
                <div className="text-3xl font-bold text-green-400 mb-1">$250</div>
                <div className="text-sm text-gray-400">Low</div>
              </div>
            </div>
          </div>

          {/* Disclosure Guidelines */}
          <div className="mt-8 bg-[#0a0a0a] border border-white/10 rounded-2xl p-8">
            <h3 className="text-xl font-bold mb-4">Disclosure Guidelines</h3>
            <ul className="space-y-3 text-sm text-gray-300">
              <li className="flex items-start gap-3">
                <span className="bg-purple-500/20 text-purple-400 rounded-full w-6 h-6 flex items-center justify-center flex-shrink-0 text-xs font-bold mt-0.5">1</span>
                <span>Report vulnerabilities to <a href="mailto:security@tradesignal.com" className="text-purple-400 hover:text-purple-300">security@tradesignal.com</a> with detailed reproduction steps</span>
              </li>
              <li className="flex items-start gap-3">
                <span className="bg-purple-500/20 text-purple-400 rounded-full w-6 h-6 flex items-center justify-center flex-shrink-0 text-xs font-bold mt-0.5">2</span>
                <span>Allow us 90 days to investigate and resolve before public disclosure</span>
              </li>
              <li className="flex items-start gap-3">
                <span className="bg-purple-500/20 text-purple-400 rounded-full w-6 h-6 flex items-center justify-center flex-shrink-0 text-xs font-bold mt-0.5">3</span>
                <span>Do not access, modify, or delete user data during testing</span>
              </li>
              <li className="flex items-start gap-3">
                <span className="bg-purple-500/20 text-purple-400 rounded-full w-6 h-6 flex items-center justify-center flex-shrink-0 text-xs font-bold mt-0.5">4</span>
                <span>Act in good faith and avoid privacy violations or service disruption</span>
              </li>
            </ul>
          </div>
        </div>
      </section>

      {/* Security Contact */}
      <section className="py-16 px-4">
        <div className="max-w-4xl mx-auto">
          <div className="bg-[#0f0f1a] border border-white/10 rounded-2xl p-8">
            <div className="flex items-start gap-6">
              <div className="bg-green-500/10 p-4 rounded-2xl">
                <Mail className="w-8 h-8 text-green-400" />
              </div>
              <div className="flex-1">
                <h3 className="text-2xl font-bold mb-2">Security Contact</h3>
                <p className="text-gray-400 mb-4">
                  For security-related inquiries, vulnerability reports, or compliance questions:
                </p>
                <a
                  href="mailto:security@tradesignal.com"
                  className="inline-flex items-center gap-2 text-green-400 hover:text-green-300 font-medium mb-4"
                >
                  security@tradesignal.com <ExternalLink className="w-4 h-4" />
                </a>
                <p className="text-sm text-gray-500">
                  PGP Key: <code className="bg-black/40 px-2 py-1 rounded text-xs">4A2E 8B9C 1D3F 7E6A</code>
                </p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Additional Resources */}
      <section className="py-16 px-4 bg-gradient-to-b from-[#0a0a0a] to-[#0f0f1a]">
        <div className="max-w-7xl mx-auto">
          <h2 className="text-3xl font-bold text-center mb-12">Security Resources</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <Link
              to="/privacy"
              className="bg-[#0f0f1a] border border-white/10 rounded-2xl p-8 text-center hover:border-purple-500/30 transition-all group"
            >
              <FileCheck className="w-8 h-8 text-purple-400 mx-auto mb-4" />
              <h3 className="text-lg font-bold mb-2 group-hover:text-purple-400 transition-colors">Privacy Policy</h3>
              <p className="text-sm text-gray-400">How we collect, use, and protect your data</p>
            </Link>
            <Link
              to="/terms"
              className="bg-[#0f0f1a] border border-white/10 rounded-2xl p-8 text-center hover:border-purple-500/30 transition-all group"
            >
              <FileCheck className="w-8 h-8 text-blue-400 mx-auto mb-4" />
              <h3 className="text-lg font-bold mb-2 group-hover:text-blue-400 transition-colors">Terms of Service</h3>
              <p className="text-sm text-gray-400">Our legal agreement with users</p>
            </Link>
            <a
              href="https://status.tradesignal.com"
              target="_blank"
              rel="noopener noreferrer"
              className="bg-[#0f0f1a] border border-white/10 rounded-2xl p-8 text-center hover:border-green-500/30 transition-all group"
            >
              <Shield className="w-8 h-8 text-green-400 mx-auto mb-4" />
              <h3 className="text-lg font-bold mb-2 group-hover:text-green-400 transition-colors">Status Page</h3>
              <p className="text-sm text-gray-400">Real-time system status and uptime</p>
            </a>
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="py-20 px-4">
        <div className="max-w-4xl mx-auto text-center">
          <div className="bg-[#0f0f1a] border border-green-500/20 rounded-3xl p-12">
            <Shield className="w-12 h-12 text-green-400 mx-auto mb-4" />
            <h2 className="text-3xl font-bold mb-4">Questions About Security?</h2>
            <p className="text-gray-400 mb-8">
              Our security team is here to answer any questions you may have about how we protect your data.
            </p>
            <a
              href="mailto:security@tradesignal.com"
              className="inline-flex items-center gap-2 bg-white text-black px-8 py-4 rounded-full font-bold hover:bg-gray-200 transition-all"
            >
              <Mail className="w-5 h-5" />
              Contact Security Team
            </a>
          </div>
        </div>
      </section>
    </div>
  );
};

export default SecurityPage;
