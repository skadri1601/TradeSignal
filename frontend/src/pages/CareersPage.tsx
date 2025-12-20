import { useState, useContext } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Briefcase, MapPin, Clock, Plus, Trash2, FileText, Send, X, TrendingUp, Users, Globe } from 'lucide-react';
import { jobsApi, type Job, type JobCreate, type JobApplicationCreate } from '../api/jobs';
import { AuthContext } from '../contexts/AuthContext';
import LoadingSpinner from '../components/common/LoadingSpinner';

// Job Application Modal Component
interface JobApplicationModalProps {
  isOpen: boolean;
  onClose: () => void;
  job: Job | null;
}

function JobApplicationModal({ isOpen, onClose, job }: JobApplicationModalProps) {
  const queryClient = useQueryClient();
  const [formData, setFormData] = useState({
    applicant_name: '',
    applicant_email: '',
    applicant_phone: '',
    cover_letter: '',
  });

  const mutation = useMutation({
    mutationFn: (data: JobApplicationCreate) => jobsApi.applyToJob(job!.id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['jobs'] });
      alert('Application submitted successfully! We\'ll be in touch soon.');
      setFormData({ applicant_name: '', applicant_email: '', applicant_phone: '', cover_letter: '' });
      onClose();
    },
    onError: (error: any) => {
      alert(error.response?.data?.detail || 'Failed to submit application. Please try again.');
    },
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    mutation.mutate(formData);
  };

  if (!isOpen || !job) return null;

  return (
    <div className="fixed inset-0 bg-black/80 backdrop-blur-sm flex items-center justify-center z-50 p-4">
      <div className="bg-gray-900 border border-white/10 rounded-2xl shadow-2xl w-full max-w-2xl max-h-[90vh] overflow-y-auto">
        <div className="p-6">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-2xl font-bold text-white">Apply for {job.title}</h2>
            <button onClick={onClose} className="text-gray-400 hover:text-white transition-colors">
              <X className="h-6 w-6" />
            </button>
          </div>

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-1">Full Name *</label>
              <input
                type="text"
                required
                value={formData.applicant_name}
                onChange={(e) => setFormData({ ...formData, applicant_name: e.target.value })}
                className="w-full px-4 py-3 bg-gray-800 border border-gray-700 rounded-xl text-white focus:ring-2 focus:ring-purple-500 focus:border-transparent outline-none transition-all"
                placeholder="John Doe"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-300 mb-1">Email *</label>
              <input
                type="email"
                required
                value={formData.applicant_email}
                onChange={(e) => setFormData({ ...formData, applicant_email: e.target.value })}
                className="w-full px-4 py-3 bg-gray-800 border border-gray-700 rounded-xl text-white focus:ring-2 focus:ring-purple-500 focus:border-transparent outline-none transition-all"
                placeholder="john@example.com"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-300 mb-1">Phone (Optional)</label>
              <input
                type="tel"
                value={formData.applicant_phone}
                onChange={(e) => setFormData({ ...formData, applicant_phone: e.target.value })}
                className="w-full px-4 py-3 bg-gray-800 border border-gray-700 rounded-xl text-white focus:ring-2 focus:ring-purple-500 focus:border-transparent outline-none transition-all"
                placeholder="+1 (555) 123-4567"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-300 mb-1">
                Cover Letter * (Minimum 50 characters)
              </label>
              <textarea
                required
                minLength={50}
                rows={6}
                value={formData.cover_letter}
                onChange={(e) => setFormData({ ...formData, cover_letter: e.target.value })}
                className="w-full px-4 py-3 bg-gray-800 border border-gray-700 rounded-xl text-white focus:ring-2 focus:ring-purple-500 focus:border-transparent outline-none transition-all"
                placeholder="Tell us why you're interested in this position..."
              />
              <p className="text-xs text-gray-500 mt-1 text-right">
                {formData.cover_letter.length} / 50 characters
              </p>
            </div>

            <div className="flex justify-end space-x-3 pt-6 border-t border-gray-800">
              <button
                type="button"
                onClick={onClose}
                className="px-6 py-2.5 border border-gray-600 text-gray-300 rounded-full hover:bg-gray-800 transition-colors font-medium"
              >
                Cancel
              </button>
              <button
                type="submit"
                disabled={mutation.isPending}
                className="flex items-center space-x-2 px-6 py-2.5 bg-white text-black rounded-full hover:bg-gray-200 transition-all font-bold disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <Send className="h-4 w-4" />
                <span>{mutation.isPending ? 'Submitting...' : 'Submit Application'}</span>
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
}

// Create/Edit Job Modal Component (Admin Only)
interface JobFormModalProps {
  isOpen: boolean;
  onClose: () => void;
  job: Job | null;
}

function JobFormModal({ isOpen, onClose, job }: JobFormModalProps) {
  const queryClient = useQueryClient();
  const [formData, setFormData] = useState<JobCreate>({
    title: job?.title || '',
    department: job?.department || '',
    location: job?.location || '',
    employment_type: job?.employment_type || 'Full-time',
    description: job?.description || '',
    requirements: job?.requirements || '',
    salary_range: job?.salary_range || '',
    is_active: job?.is_active ?? true,
  });

  const createMutation = useMutation({
    mutationFn: (data: JobCreate) => jobsApi.createJob(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['jobs-admin'] });
      alert('Job created successfully!');
      onClose();
    },
    onError: (error: any) => {
      console.error('Error creating job:', error);
      const errorMessage = error?.response?.data?.error || 
                          error?.response?.data?.detail || 
                          error?.message || 
                          'Failed to create job. Please try again.';
      alert(`Error: ${errorMessage}`);
    },
  });

  const updateMutation = useMutation({
    mutationFn: (data: JobCreate) => jobsApi.updateJob(job!.id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['jobs-admin'] });
      alert('Job updated successfully!');
      onClose();
    },
    onError: (error: any) => {
      console.error('Error updating job:', error);
      const errorMessage = error?.response?.data?.error || 
                          error?.response?.data?.detail || 
                          error?.message || 
                          'Failed to update job. Please try again.';
      alert(`Error: ${errorMessage}`);
    },
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (job) {
      updateMutation.mutate(formData);
    } else {
      createMutation.mutate(formData);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black/80 backdrop-blur-sm flex items-center justify-center z-50 p-4">
      <div className="bg-gray-900 border border-white/10 rounded-2xl shadow-2xl w-full max-w-3xl max-h-[90vh] overflow-y-auto">
        <div className="p-6">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-2xl font-bold text-white">
              {job ? 'Edit Job' : 'Create New Job'}
            </h2>
            <button onClick={onClose} className="text-gray-400 hover:text-white transition-colors">
              <X className="h-6 w-6" />
            </button>
          </div>

          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-1">Job Title *</label>
                <input
                  type="text"
                  required
                  value={formData.title}
                  onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                  className="w-full px-4 py-2.5 bg-gray-800 border border-gray-700 rounded-xl text-white focus:ring-2 focus:ring-purple-500 outline-none"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-300 mb-1">Department *</label>
                <input
                  type="text"
                  required
                  value={formData.department}
                  onChange={(e) => setFormData({ ...formData, department: e.target.value })}
                  className="w-full px-4 py-2.5 bg-gray-800 border border-gray-700 rounded-xl text-white focus:ring-2 focus:ring-purple-500 outline-none"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-300 mb-1">Location *</label>
                <input
                  type="text"
                  required
                  value={formData.location}
                  onChange={(e) => setFormData({ ...formData, location: e.target.value })}
                  className="w-full px-4 py-2.5 bg-gray-800 border border-gray-700 rounded-xl text-white focus:ring-2 focus:ring-purple-500 outline-none"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-300 mb-1">Employment Type *</label>
                <select
                  required
                  value={formData.employment_type}
                  onChange={(e) => setFormData({ ...formData, employment_type: e.target.value })}
                  className="w-full px-4 py-2.5 bg-gray-800 border border-gray-700 rounded-xl text-white focus:ring-2 focus:ring-purple-500 outline-none"
                >
                  <option value="Full-time">Full-time</option>
                  <option value="Part-time">Part-time</option>
                  <option value="Contract">Contract</option>
                  <option value="Internship">Internship</option>
                </select>
              </div>

              <div className="md:col-span-2">
                <label className="block text-sm font-medium text-gray-300 mb-1">Salary Range (Optional)</label>
                <input
                  type="text"
                  value={formData.salary_range || ''}
                  onChange={(e) => setFormData({ ...formData, salary_range: e.target.value })}
                  className="w-full px-4 py-2.5 bg-gray-800 border border-gray-700 rounded-xl text-white focus:ring-2 focus:ring-purple-500 outline-none"
                  placeholder="e.g., $80k-$120k"
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-300 mb-1">Description *</label>
              <textarea
                required
                rows={4}
                value={formData.description}
                onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                className="w-full px-4 py-2.5 bg-gray-800 border border-gray-700 rounded-xl text-white focus:ring-2 focus:ring-purple-500 outline-none"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-300 mb-1">Requirements *</label>
              <textarea
                required
                rows={4}
                value={formData.requirements}
                onChange={(e) => setFormData({ ...formData, requirements: e.target.value })}
                className="w-full px-4 py-2.5 bg-gray-800 border border-gray-700 rounded-xl text-white focus:ring-2 focus:ring-purple-500 outline-none"
                placeholder="One requirement per line"
              />
            </div>

            <div className="flex items-center space-x-2">
              <input
                type="checkbox"
                id="is_active"
                checked={formData.is_active}
                onChange={(e) => setFormData({ ...formData, is_active: e.target.checked })}
                className="rounded border-gray-600 bg-gray-800 text-purple-600 focus:ring-purple-500"
              />
              <label htmlFor="is_active" className="text-sm font-medium text-gray-300">
                Active (accepting applications)
              </label>
            </div>

            <div className="flex justify-end space-x-3 pt-6 border-t border-gray-800">
              <button
                type="button"
                onClick={onClose}
                className="px-4 py-2 border border-gray-600 text-gray-300 rounded-lg hover:bg-gray-800 transition-colors"
              >
                Cancel
              </button>
              <button
                type="submit"
                disabled={createMutation.isPending || updateMutation.isPending}
                className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors disabled:opacity-50 font-medium"
              >
                {job ? 'Update Job' : 'Create Job'}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
}

// Main CareersPage Component
export default function CareersPage() {
  const authContext = useContext(AuthContext);
  const user = authContext?.user;
  const isSuperAdmin = user?.is_superuser || user?.role === 'super_admin';

  const queryClient = useQueryClient();
  const [selectedJob, setSelectedJob] = useState<Job | null>(null);
  const [showApplicationModal, setShowApplicationModal] = useState(false);
  const [showJobFormModal, setShowJobFormModal] = useState(false);
  const [editingJob, setEditingJob] = useState<Job | null>(null);

  // Fetch jobs (admin sees all, public sees only active)
  const { data: jobsData, isLoading } = useQuery({
    queryKey: isSuperAdmin ? ['jobs-admin'] : ['jobs'],
    queryFn: () => isSuperAdmin ? jobsApi.getAllJobsAdmin() : jobsApi.getJobs(),
  });

  const deleteMutation = useMutation({
    mutationFn: (jobId: number) => jobsApi.deleteJob(jobId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['jobs-admin'] });
      alert('Job deleted successfully!');
    },
  });

  const handleApply = (job: Job) => {
    setSelectedJob(job);
    setShowApplicationModal(true);
  };

  const handleCreateJob = () => {
    setEditingJob(null);
    setShowJobFormModal(true);
  };

  const handleEditJob = (job: Job) => {
    setEditingJob(job);
    setShowJobFormModal(true);
  };

  const handleDeleteJob = (jobId: number, jobTitle: string) => {
    if (window.confirm(`Are you sure you want to delete "${jobTitle}"? This will also delete all applications.`)) {
      deleteMutation.mutate(jobId);
    }
  };

  const jobs = jobsData?.data?.jobs || [];

  return (
    <div className="min-h-screen bg-black text-white selection:bg-purple-500 selection:text-white font-sans overflow-x-hidden pb-20">
      
      {/* Hero Section */}
      <section className="relative pt-32 pb-20 overflow-hidden">
        {/* Abstract Background */}
        <div className="absolute top-0 right-0 w-[600px] h-[600px] bg-blue-600/20 rounded-full blur-[120px] -z-10" />
        <div className="absolute bottom-0 left-0 w-[600px] h-[600px] bg-purple-600/20 rounded-full blur-[120px] -z-10" />
        
        <div className="max-w-7xl mx-auto px-6 text-center relative z-10">
          <h1 className="text-4xl lg:text-6xl font-bold mb-6">
            Join the <br />
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-purple-400">
              TradeSignal Revolution
            </span>
          </h1>
          <p className="text-xl text-gray-400 max-w-2xl mx-auto mb-10">
            We're building the future of financial intelligence. Help us democratize insider trading data for everyone.
          </p>
          
          {isSuperAdmin && (
            <button
              onClick={handleCreateJob}
              className="inline-flex items-center gap-2 px-6 py-3 bg-white text-black font-semibold rounded-full hover:bg-gray-200 transition-all hover:scale-105"
            >
              <Plus className="h-5 w-5" />
              <span>Post New Position</span>
            </button>
          )}
        </div>
      </section>

      <div className="max-w-7xl mx-auto px-6 space-y-20">
        
        {/* Company Culture */}
        <div className="grid md:grid-cols-3 gap-8">
          {[
            {
              icon: <TrendingUp className="w-6 h-6" />,
              title: "Mission-Driven",
              desc: "We're democratizing access to financial intelligence. Help us train LUNA, our advanced AI, to give retail investors the same edge as institutions."
            },
            {
              icon: <Globe className="w-6 h-6" />,
              title: "Remote-First",
              desc: "Work from anywhere. We're a distributed team with flexible hours and a focus on results, not hours."
            },
            {
              icon: <Users className="w-6 h-6" />,
              title: "Growth Culture",
              desc: "Join a fast-growing startup with equity options, competitive salary, and opportunities to shape the product."
            }
          ].map((item, i) => (
            <div key={i} className="bg-white/5 border border-white/10 p-8 rounded-2xl hover:bg-white/10 transition-colors">
              <div className="w-12 h-12 bg-gradient-to-br from-blue-500/20 to-purple-500/20 rounded-xl flex items-center justify-center text-purple-400 mb-6">
                {item.icon}
              </div>
              <h3 className="text-xl font-bold text-white mb-3">{item.title}</h3>
              <p className="text-gray-400 leading-relaxed">{item.desc}</p>
            </div>
          ))}
        </div>

        {/* Perks & Benefits */}
        <div>
          <h2 className="text-3xl font-bold text-white mb-8 text-center">Perks & Benefits</h2>
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {[
              { title: "Competitive Salary", desc: "Top-tier compensation packages that rival big tech." },
              { title: "Equity Options", desc: "Own a piece of the company you're helping to build." },
              { title: "100% Remote", desc: "Work from home, a co-working space, or a beach in Bali." },
              { title: "Health & Wellness", desc: "Comprehensive medical, dental, and vision coverage." },
              { title: "Home Office Stipend", desc: "$1,500 budget to set up your dream workspace." },
              { title: "Unlimited PTO", desc: "Take time off when you need it. We trust you." },
            ].map((perk, i) => (
              <div key={i} className="flex items-start gap-4 p-6 rounded-xl bg-gray-900/30 border border-white/5">
                <div className="w-2 h-2 mt-2 rounded-full bg-green-400 shrink-0 shadow-[0_0_10px_rgba(74,222,128,0.5)]"></div>
                <div>
                  <h3 className="font-bold text-white mb-1">{perk.title}</h3>
                  <p className="text-sm text-gray-400">{perk.desc}</p>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Open Positions */}
        <div>
          <div className="flex items-end justify-between mb-8 border-b border-white/10 pb-4">
            <h2 className="text-3xl font-bold text-white">
              Open Positions
            </h2>
            <span className="text-gray-400 font-medium">{jobs.length} roles available</span>
          </div>

          {isLoading ? (
            <div className="flex justify-center py-20">
              <LoadingSpinner />
            </div>
          ) : jobs.length === 0 ? (
            <div className="text-center py-20 bg-white/5 rounded-3xl border border-white/10">
              <div className="w-16 h-16 bg-gray-800 rounded-full flex items-center justify-center mx-auto mb-4">
                <Briefcase className="h-8 w-8 text-gray-500" />
              </div>
              <h3 className="text-xl font-semibold text-white mb-2">No open positions</h3>
              <p className="text-gray-400">Check back soon or follow us for updates.</p>
            </div>
          ) : (
            <div className="space-y-4">
              {jobs.map((job) => (
                <div 
                  key={job.id} 
                  className="group bg-gray-900/50 border border-white/10 rounded-2xl p-6 hover:border-purple-500/50 transition-all duration-300 relative overflow-hidden"
                >
                  <div className="absolute inset-0 bg-gradient-to-r from-purple-500/0 via-purple-500/0 to-purple-500/5 opacity-0 group-hover:opacity-100 transition-opacity" />
                  
                  <div className="relative z-10 flex flex-col md:flex-row md:items-start md:justify-between gap-6">
                    <div className="flex-1">
                      <div className="flex flex-wrap items-center gap-3 mb-3">
                        <h3 className="text-2xl font-bold text-white group-hover:text-purple-400 transition-colors">
                          {job.title}
                        </h3>
                        <span className="px-3 py-1 bg-blue-500/20 text-blue-300 text-xs font-bold uppercase tracking-wider rounded-full">
                          {job.department}
                        </span>
                        {!job.is_active && (
                          <span className="px-3 py-1 bg-gray-700 text-gray-300 text-xs font-bold uppercase tracking-wider rounded-full">
                            Closed
                          </span>
                        )}
                      </div>
                      
                      <p className="text-gray-400 mb-6 max-w-3xl line-clamp-2">
                        {job.description}
                      </p>

                      <div className="flex flex-wrap items-center gap-6 text-sm text-gray-500">
                        <div className="flex items-center gap-2">
                          <MapPin className="h-4 w-4 text-purple-500" />
                          <span>{job.location}</span>
                        </div>
                        <div className="flex items-center gap-2">
                          <Clock className="h-4 w-4 text-purple-500" />
                          <span>{job.employment_type}</span>
                        </div>
                        {job.salary_range && (
                          <div className="flex items-center gap-2">
                            <FileText className="h-4 w-4 text-purple-500" />
                            <span>{job.salary_range}</span>
                          </div>
                        )}
                      </div>
                    </div>

                    <div className="flex flex-col gap-3 min-w-[140px]">
                      <button
                        onClick={() => handleApply(job)}
                        disabled={!job.is_active}
                        className="w-full px-6 py-3 bg-white text-black font-bold rounded-xl hover:bg-gray-200 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
                      >
                        {job.is_active ? 'Apply Now' : 'Closed'} 
                        {job.is_active && <Send className="w-4 h-4" />}
                      </button>

                      {isSuperAdmin && (
                        <div className="flex gap-2">
                          <button
                            onClick={() => handleEditJob(job)}
                            className="flex-1 px-3 py-2 border border-gray-700 text-gray-300 rounded-lg hover:bg-gray-800 transition-colors text-sm"
                          >
                            Edit
                          </button>
                          <button
                            onClick={() => handleDeleteJob(job.id, job.title)}
                            className="px-3 py-2 border border-red-900/50 text-red-500 rounded-lg hover:bg-red-900/20 transition-colors"
                          >
                            <Trash2 className="h-4 w-4" />
                          </button>
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Modals */}
      <JobApplicationModal
        isOpen={showApplicationModal}
        onClose={() => {
          setShowApplicationModal(false);
          setSelectedJob(null);
        }}
        job={selectedJob}
      />

      <JobFormModal
        isOpen={showJobFormModal}
        onClose={() => {
          setShowJobFormModal(false);
          setEditingJob(null);
        }}
        job={editingJob}
      />
    </div>
  );
}
