/**
 * Lessons Page - Educational Content About Insider Trading
 */

import { BookOpen, GraduationCap, Target, TrendingUp, AlertCircle, CheckCircle } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { useCustomAlert } from '../hooks/useCustomAlert';
import CustomAlert from '../components/common/CustomAlert';

export default function LessonsPage() {
  const navigate = useNavigate();
  const { alertState, showAlert, hideAlert } = useCustomAlert();

  const lessons = [
    {
      id: 1,
      title: 'Introduction to Insider Trading',
      description: 'Learn the basics of legal insider trading and why it matters for investors',
      duration: '10 min',
      level: 'Beginner',
      icon: BookOpen,
      color: 'blue',
      completed: false
    },
    {
      id: 2,
      title: 'Understanding SEC Form 4 Filings',
      description: 'Deep dive into how to read and interpret SEC Form 4 insider trading reports',
      duration: '15 min',
      level: 'Beginner',
      icon: GraduationCap,
      color: 'green',
      completed: false
    },
    {
      id: 3,
      title: 'Identifying Significant Trades',
      description: 'Learn how to spot trades that could indicate important market movements',
      duration: '12 min',
      level: 'Intermediate',
      icon: Target,
      color: 'purple',
      completed: false
    },
    {
      id: 4,
      title: 'Building a Trading Strategy',
      description: 'Use insider trading data to inform your investment decisions',
      duration: '20 min',
      level: 'Advanced',
      icon: TrendingUp,
      color: 'orange',
      completed: false
    },
  ];

  const colorMap: Record<string, string> = {
    blue: 'from-blue-500 to-blue-600',
    green: 'from-green-500 to-green-600',
    purple: 'from-purple-500 to-purple-600',
    orange: 'from-orange-500 to-orange-600',
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900 flex items-center">
          <GraduationCap className="w-8 h-8 mr-3 text-blue-600" />
          Trading Lessons
        </h1>
        <p className="text-gray-600 mt-2">
          Master the art of insider trading analysis with our educational content
        </p>
      </div>

      {/* Progress Overview */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-white rounded-xl p-6 border border-gray-200">
          <div className="flex items-center justify-between mb-2">
            <p className="text-gray-600 text-sm">Lessons Completed</p>
            <CheckCircle className="w-5 h-5 text-green-500" />
          </div>
          <p className="text-3xl font-bold text-gray-900">0/{lessons.length}</p>
        </div>

        <div className="bg-white rounded-xl p-6 border border-gray-200">
          <div className="flex items-center justify-between mb-2">
            <p className="text-gray-600 text-sm">Total Learning Time</p>
            <BookOpen className="w-5 h-5 text-blue-500" />
          </div>
          <p className="text-3xl font-bold text-gray-900">
            {lessons.reduce((acc, l) => acc + parseInt(l.duration), 0)} min
          </p>
        </div>

        <div className="bg-white rounded-xl p-6 border border-gray-200">
          <div className="flex items-center justify-between mb-2">
            <p className="text-gray-600 text-sm">Your Level</p>
            <Target className="w-5 h-5 text-purple-500" />
          </div>
          <p className="text-3xl font-bold text-gray-900">Beginner</p>
        </div>
      </div>

      {/* Lessons Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {lessons.map((lesson) => {
          const Icon = lesson.icon;
          return (
            <div
              key={lesson.id}
              className="bg-white rounded-2xl shadow-sm border border-gray-200 overflow-hidden hover:shadow-md transition-shadow cursor-pointer"
            >
              <div className={`h-32 bg-gradient-to-br ${colorMap[lesson.color]} p-6 flex items-center justify-center`}>
                <Icon className="w-16 h-16 text-white" />
              </div>
              <div className="p-6">
                <div className="flex items-start justify-between mb-3">
                  <h3 className="font-bold text-lg text-gray-900">{lesson.title}</h3>
                  <span className={`px-3 py-1 rounded-full text-xs font-medium ${
                    lesson.level === 'Beginner' ? 'bg-green-100 text-green-700' :
                    lesson.level === 'Intermediate' ? 'bg-blue-100 text-blue-700' :
                    'bg-purple-100 text-purple-700'
                  }`}>
                    {lesson.level}
                  </span>
                </div>
                <p className="text-gray-600 text-sm mb-4">{lesson.description}</p>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-500">{lesson.duration}</span>
                  <button 
                    onClick={() => {
                      // For now, show a message that lessons are coming soon
                      // In the future, this could navigate to /lessons/{lesson.id} or open a modal
                      showAlert(
                        `"${lesson.title}" lesson is coming soon! We're working on interactive content for this lesson.`,
                        { type: 'info', title: 'TradeSignal' }
                      );
                    }}
                    className="px-4 py-2 bg-blue-600 text-white rounded-lg text-sm font-medium hover:bg-blue-700 transition-colors"
                  >
                    Start Lesson
                  </button>
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Coming Soon Banner */}
      <div className="bg-gradient-to-br from-yellow-50 to-orange-50 rounded-2xl p-8 border border-yellow-200">
        <div className="flex items-start space-x-4">
          <div className="w-12 h-12 bg-yellow-100 rounded-lg flex items-center justify-center flex-shrink-0">
            <AlertCircle className="w-6 h-6 text-yellow-600" />
          </div>
          <div>
            <h3 className="text-xl font-bold text-gray-900 mb-2">Interactive Lessons Coming Soon!</h3>
            <p className="text-gray-600 mb-4">
              We're creating comprehensive video tutorials, quizzes, and hands-on exercises to help you become an expert in insider trading analysis.
            </p>
            <button
              onClick={() => navigate('/trades')}
              className="px-6 py-3 bg-yellow-600 text-white rounded-lg font-medium hover:bg-yellow-700 transition-colors"
            >
              Start Analyzing Trades Now →
            </button>
          </div>
        </div>
      </div>

      {/* Custom Alert Modal */}
      <CustomAlert
        show={alertState.show}
        message={alertState.message}
        title={alertState.title || 'TradeSignal'}
        type={alertState.type}
        onClose={hideAlert}
      />
    </div>
  );
}
