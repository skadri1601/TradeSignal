import { motion, Variants } from 'framer-motion';
import { Sparkles, Wrench, Bug, AlertCircle } from 'lucide-react';

// Animation Variants
const fadeInUp: Variants = {
  hidden: { opacity: 0, y: 30 },
  visible: { opacity: 1, y: 0, transition: { duration: 0.6, ease: "easeOut" } }
};

const staggerContainer: Variants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      staggerChildren: 0.15
    }
  }
};

// Release Note Item Component
const ReleaseNoteItem = ({ icon: Icon, text, type }: { icon: any, text: string, type: 'feature' | 'improvement' | 'fix' | 'breaking' }) => {
  const colorMap = {
    feature: 'text-green-400',
    improvement: 'text-blue-400',
    fix: 'text-orange-400',
    breaking: 'text-red-400'
  };

  return (
    <motion.li variants={fadeInUp} className="flex items-start gap-3">
      <Icon className={`w-5 h-5 mt-0.5 flex-shrink-0 ${colorMap[type]}`} />
      <span className="text-gray-300">{text}</span>
    </motion.li>
  );
};

// Release Version Component
const ReleaseVersion = ({
  version,
  date,
  features = [],
  improvements = [],
  fixes = [],
  breaking = []
}: {
  version: string;
  date: string;
  features?: string[];
  improvements?: string[];
  fixes?: string[];
  breaking?: string[];
}) => (
  <motion.div
    variants={fadeInUp}
    className="bg-gradient-to-br from-gray-800/50 to-gray-900/50 rounded-2xl p-8 border border-gray-700/50 backdrop-blur-sm"
  >
    <div className="flex items-center justify-between mb-6">
      <h3 className="text-2xl font-bold text-white">Version {version}</h3>
      <span className="text-sm text-gray-400">{date}</span>
    </div>

    <motion.ul variants={staggerContainer} initial="hidden" whileInView="visible" viewport={{ once: true }} className="space-y-3">
      {breaking.map((item, idx) => (
        <ReleaseNoteItem key={`breaking-${idx}`} icon={AlertCircle} text={item} type="breaking" />
      ))}
      {features.map((item, idx) => (
        <ReleaseNoteItem key={`feature-${idx}`} icon={Sparkles} text={item} type="feature" />
      ))}
      {improvements.map((item, idx) => (
        <ReleaseNoteItem key={`improvement-${idx}`} icon={Wrench} text={item} type="improvement" />
      ))}
      {fixes.map((item, idx) => (
        <ReleaseNoteItem key={`fix-${idx}`} icon={Bug} text={item} type="fix" />
      ))}
    </motion.ul>
  </motion.div>
);

// Hero Section
const ReleaseNotesHero = () => (
  <section className="relative pt-32 pb-20 lg:pt-48 lg:pb-32 overflow-hidden px-6">
    <div className="absolute inset-0 pointer-events-none">
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] bg-purple-600/20 rounded-full blur-[120px]"></div>
    </div>
    <div className="max-w-4xl mx-auto text-center relative z-10">
      <motion.h1
        initial="hidden"
        whileInView="visible"
        viewport={{ once: true }}
        variants={fadeInUp}
        className="text-5xl lg:text-7xl font-bold text-white mb-6 tracking-tight"
      >
        Release Notes
      </motion.h1>
      <motion.p
        initial="hidden"
        whileInView="visible"
        viewport={{ once: true }}
        variants={fadeInUp}
        className="text-xl text-gray-400 max-w-2xl mx-auto leading-relaxed"
      >
        Stay up to date with the latest features, improvements, and fixes to TradeSignal.
      </motion.p>
    </div>
  </section>
);

// Main Component
const ReleaseNotesPage = () => {
  const releases = [
    {
      version: "2.1.0",
      date: "December 25, 2025",
      features: [
        "Introduced LUNA AI Engine - Unified proprietary analysis replacing legacy pattern detection",
        "Added Forensic Company Reports with automatic price predictions",
        "Implemented dual-model architecture (advanced AI for deep analysis, optimized model for routine tasks)"
      ],
      improvements: [
        "Consolidated redundant API calls into single AI request for better performance",
        "Enhanced AI Insights page with real-time forensic analysis",
        "Optimized database queries for faster data retrieval"
      ],
      fixes: [
        "Fixed Forum endpoints returning 404 (double prefix bug)",
        "Corrected CORS middleware order to prevent request blocking",
        "Resolved import crashes from legacy pattern analysis service"
      ]
    },
    {
      version: "2.0.0",
      date: "December 19, 2025",
      breaking: [
        "Removed legacy Chart Patterns feature in favor of unified LUNA AI analysis"
      ],
      features: [
        "Launched Hybrid Intelligence Architecture ($25 Plan)",
        "Integrated SEC Form 4 scraping with automatic trade enrichment",
        "Added multi-tier subscription system (Free, Pro, Enterprise)"
      ],
      improvements: [
        "Upgraded to FastAPI with async/await for better concurrency",
        "Implemented Redis caching for frequently accessed data",
        "Enhanced alert prioritization with value estimation service"
      ],
      fixes: [
        "Fixed Insider Trades page pagination issues",
        "Resolved 90-day historical data access paywall",
        "Corrected timezone handling for trade timestamps"
      ]
    },
    {
      version: "1.5.0",
      date: "November 2025",
      features: [
        "Added Fed Calendar with interest rate tracking",
        "Implemented Market News aggregation from multiple sources",
        "Launched Community Forums for trader discussions"
      ],
      improvements: [
        "Enhanced dashboard with real-time WebSocket updates",
        "Improved mobile responsiveness across all pages",
        "Added dark mode support throughout the application"
      ],
      fixes: [
        "Fixed API rate limiting issues with external data providers",
        "Resolved memory leaks in Celery background tasks",
        "Corrected stock price calculation discrepancies"
      ]
    }
  ];

  return (
    <div className="min-h-screen bg-gradient-to-b from-gray-900 via-gray-900 to-black">
      <ReleaseNotesHero />

      <section className="px-6 pb-20">
        <motion.div
          variants={staggerContainer}
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true }}
          className="max-w-4xl mx-auto space-y-8"
        >
          {releases.map((release, idx) => (
            <ReleaseVersion key={idx} {...release} />
          ))}
        </motion.div>

        {/* Legend */}
        <motion.div
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true }}
          variants={fadeInUp}
          className="max-w-4xl mx-auto mt-12 p-6 bg-gray-800/30 rounded-xl border border-gray-700/50"
        >
          <h4 className="text-sm font-semibold text-gray-400 mb-4">Legend</h4>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
            <div className="flex items-center gap-2">
              <Sparkles className="w-4 h-4 text-green-400" />
              <span className="text-gray-300">New Feature</span>
            </div>
            <div className="flex items-center gap-2">
              <Wrench className="w-4 h-4 text-blue-400" />
              <span className="text-gray-300">Improvement</span>
            </div>
            <div className="flex items-center gap-2">
              <Bug className="w-4 h-4 text-orange-400" />
              <span className="text-gray-300">Bug Fix</span>
            </div>
            <div className="flex items-center gap-2">
              <AlertCircle className="w-4 h-4 text-red-400" />
              <span className="text-gray-300">Breaking Change</span>
            </div>
          </div>
        </motion.div>
      </section>
    </div>
  );
};

export default ReleaseNotesPage;
