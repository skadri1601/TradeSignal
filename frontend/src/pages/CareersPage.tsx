import { useState, useContext } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Briefcase, MapPin, Clock, Plus, Edit, Trash2, FileText, Send, X } from 'lucide-react';
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
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg shadow-xl w-full max-w-2xl max-h-[90vh] overflow-y-auto">
        <div className="p-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-2xl font-bold text-gray-900">Apply for {job.title}</h2>
            <button onClick={onClose} className="text-gray-400 hover:text-gray-600">
              <X className="h-6 w-6" />
            </button>
          </div>

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Full Name *</label>
              <input
                type="text"
                required
                value={formData.applicant_name}
                onChange={(e) => setFormData({ ...formData, applicant_name: e.target.value })}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Email *</label>
              <input
                type="email"
                required
                value={formData.applicant_email}
                onChange={(e) => setFormData({ ...formData, applicant_email: e.target.value })}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Phone (Optional)</label>
              <input
                type="tel"
                value={formData.applicant_phone}
                onChange={(e) => setFormData({ ...formData, applicant_phone: e.target.value })}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="+1 (555) 123-4567"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Cover Letter * (Minimum 50 characters)
              </label>
              <textarea
                required
                minLength={50}
                rows={8}
                value={formData.cover_letter}
                onChange={(e) => setFormData({ ...formData, cover_letter: e.target.value })}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="Tell us why you're interested in this position and what makes you a great fit..."
              />
              <p className="text-xs text-gray-500 mt-1">
                {formData.cover_letter.length} / 50 characters minimum
              </p>
            </div>

            <div className="flex justify-end space-x-3 pt-4 border-t">
              <button
                type="button"
                onClick={onClose}
                className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
              >
                Cancel
              </button>
              <button
                type="submit"
                disabled={mutation.isPending}
                className="flex items-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
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
  });

  const updateMutation = useMutation({
    mutationFn: (data: JobCreate) => jobsApi.updateJob(job!.id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['jobs-admin'] });
      alert('Job updated successfully!');
      onClose();
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
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg shadow-xl w-full max-w-3xl max-h-[90vh] overflow-y-auto">
        <div className="p-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-2xl font-bold text-gray-900">
              {job ? 'Edit Job' : 'Create New Job'}
            </h2>
            <button onClick={onClose} className="text-gray-400 hover:text-gray-600">
              <X className="h-6 w-6" />
            </button>
          </div>

          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Job Title *</label>
                <input
                  type="text"
                  required
                  value={formData.title}
                  onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Department *</label>
                <input
                  type="text"
                  required
                  value={formData.department}
                  onChange={(e) => setFormData({ ...formData, department: e.target.value })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Location *</label>
                <input
                  type="text"
                  required
                  value={formData.location}
                  onChange={(e) => setFormData({ ...formData, location: e.target.value })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Employment Type *</label>
                <select
                  required
                  value={formData.employment_type}
                  onChange={(e) => setFormData({ ...formData, employment_type: e.target.value })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                >
                  <option value="Full-time">Full-time</option>
                  <option value="Part-time">Part-time</option>
                  <option value="Contract">Contract</option>
                  <option value="Internship">Internship</option>
                </select>
              </div>

              <div className="md:col-span-2">
                <label className="block text-sm font-medium text-gray-700 mb-1">Salary Range (Optional)</label>
                <input
                  type="text"
                  value={formData.salary_range || ''}
                  onChange={(e) => setFormData({ ...formData, salary_range: e.target.value })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  placeholder="e.g., $80k-$120k"
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Description *</label>
              <textarea
                required
                rows={4}
                value={formData.description}
                onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Requirements *</label>
              <textarea
                required
                rows={4}
                value={formData.requirements}
                onChange={(e) => setFormData({ ...formData, requirements: e.target.value })}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                placeholder="One requirement per line"
              />
            </div>

            <div className="flex items-center space-x-2">
              <input
                type="checkbox"
                id="is_active"
                checked={formData.is_active}
                onChange={(e) => setFormData({ ...formData, is_active: e.target.checked })}
                className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
              />
              <label htmlFor="is_active" className="text-sm font-medium text-gray-700">
                Active (accepting applications)
              </label>
            </div>

            <div className="flex justify-end space-x-3 pt-4 border-t">
              <button
                type="button"
                onClick={onClose}
                className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50"
              >
                Cancel
              </button>
              <button
                type="submit"
                disabled={createMutation.isPending || updateMutation.isPending}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
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
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Careers</h1>
          <p className="mt-2 text-gray-600">
            Join us in building the future of insider trading intelligence
          </p>
        </div>
        {isSuperAdmin && (
          <button
            onClick={handleCreateJob}
            className="flex items-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            <Plus className="h-5 w-5" />
            <span>Post New Job</span>
          </button>
        )}
      </div>

      {/* Company Culture */}
      <div className="card bg-gradient-to-r from-blue-50 to-indigo-50 border-blue-200">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">Why TradeSignal?</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <h3 className="font-semibold text-gray-900 mb-2">Mission-Driven</h3>
            <p className="text-gray-700 text-sm">
              We're democratizing access to insider trading data, giving retail investors the same information as institutions.
            </p>
          </div>
          <div>
            <h3 className="font-semibold text-gray-900 mb-2">Remote-First</h3>
            <p className="text-gray-700 text-sm">
              Work from anywhere. We're a distributed team with flexible hours and a focus on results, not hours.
            </p>
          </div>
          <div>
            <h3 className="font-semibold text-gray-900 mb-2">Growth Opportunities</h3>
            <p className="text-gray-700 text-sm">
              Join a fast-growing startup with equity options, competitive salary, and opportunities to shape the product.
            </p>
          </div>
        </div>
      </div>

      {/* Open Positions */}
      <div>
        <h2 className="text-2xl font-semibold text-gray-900 mb-4">
          Open Positions {jobs.length > 0 && `(${jobs.length})`}
        </h2>

        {isLoading ? (
          <div className="flex justify-center py-12">
            <LoadingSpinner />
          </div>
        ) : jobs.length === 0 ? (
          <div className="card text-center py-12">
            <Briefcase className="h-12 w-12 text-gray-400 mx-auto mb-4" />
            <p className="text-gray-600">No open positions at the moment</p>
            <p className="text-sm text-gray-500 mt-2">
              Check back soon or send us your resume for future opportunities
            </p>
          </div>
        ) : (
          <div className="space-y-4">
            {jobs.map((job) => (
              <div key={job.id} className="card hover:shadow-lg transition-shadow">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center space-x-2 mb-2">
                      <h3 className="text-xl font-semibold text-gray-900">{job.title}</h3>
                      <span className="px-2 py-1 bg-blue-100 text-blue-800 text-xs font-semibold rounded">
                        {job.department}
                      </span>
                      {!job.is_active && (
                        <span className="px-2 py-1 bg-gray-100 text-gray-800 text-xs font-semibold rounded">
                          INACTIVE
                        </span>
                      )}
                      {isSuperAdmin && (
                        <span className="px-2 py-1 bg-green-100 text-green-800 text-xs font-semibold rounded">
                          {job.application_count} application{job.application_count !== 1 ? 's' : ''}
                        </span>
                      )}
                    </div>
                    <p className="text-gray-700 mb-4">{job.description}</p>

                    <div className="flex flex-wrap items-center gap-4 mb-4 text-sm text-gray-600">
                      <div className="flex items-center space-x-1">
                        <MapPin className="h-4 w-4" />
                        <span>{job.location}</span>
                      </div>
                      <div className="flex items-center space-x-1">
                        <Clock className="h-4 w-4" />
                        <span>{job.employment_type}</span>
                      </div>
                      {job.salary_range && (
                        <div className="flex items-center space-x-1">
                          <FileText className="h-4 w-4" />
                          <span>{job.salary_range}</span>
                        </div>
                      )}
                    </div>

                    <div>
                      <h4 className="font-semibold text-gray-900 mb-2">Requirements:</h4>
                      <div className="text-gray-700 text-sm whitespace-pre-line">
                        {job.requirements}
                      </div>
                    </div>
                  </div>
                </div>

                <div className="mt-4 pt-4 border-t border-gray-200 flex items-center justify-between">
                  <button
                    onClick={() => handleApply(job)}
                    disabled={!job.is_active}
                    className="flex items-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    <span>{job.is_active ? 'Apply Now' : 'Not Accepting Applications'}</span>
                  </button>

                  {isSuperAdmin && (
                    <div className="flex items-center space-x-2">
                      <button
                        onClick={() => handleEditJob(job)}
                        className="flex items-center space-x-1 px-3 py-2 border border-gray-300 rounded-lg hover:bg-gray-50"
                      >
                        <Edit className="h-4 w-4" />
                        <span>Edit</span>
                      </button>
                      <button
                        onClick={() => handleDeleteJob(job.id, job.title)}
                        className="flex items-center space-x-1 px-3 py-2 border border-red-300 text-red-600 rounded-lg hover:bg-red-50"
                      >
                        <Trash2 className="h-4 w-4" />
                        <span>Delete</span>
                      </button>
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
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
