/**
 * User Profile Page - Dark Mode
 * Allows users to view and edit their profile information
 */

import { useState, FormEvent, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { User, Calendar, Phone, FileText, Image, Save, AlertCircle, CheckCircle2, Crown, XCircle, Pause, Play, HelpCircle, Webhook as WebhookIcon, Key, Plus, Trash2, Eye, Copy } from 'lucide-react';
import { getSubscription, cancelSubscription, pauseSubscription, resumeSubscription } from '../api/billing';
import type { SubscriptionResponse } from '../api/billing';
import { useCustomConfirm } from '../hooks/useCustomConfirm';
import CustomConfirm from '../components/common/CustomConfirm';
import { webhooksApi, type Webhook, type WebhookDelivery } from '../api/webhooks';
import { apiKeysApi, type APIKey, type APIKeyCreated, type APIKeyUsageStats } from '../api/apiKeys';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

interface ProfileData {
  full_name?: string;
  date_of_birth?: string;
  phone_number?: string;
  bio?: string;
  avatar_url?: string;
}

export default function ProfilePage() {
  const { user, tokens } = useAuth();
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const isAdmin = user?.is_superuser || false;
  const { confirmState, showConfirm, hideConfirm } = useCustomConfirm();
  const [activeTab, setActiveTab] = useState<any>('profile');
  const [isEditing, setIsEditing] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);
  
  // Webhooks state
  const [showCreateWebhook, setShowCreateWebhook] = useState(false);
  const [selectedWebhookId, setSelectedWebhookId] = useState<number | null>(null);
  const [newWebhookUrl, setNewWebhookUrl] = useState('');
  const [newWebhookEvents, setNewWebhookEvents] = useState<string[]>([]);

  // API Keys state
  const [showCreateAPIKey, setShowCreateAPIKey] = useState(false);
  const [selectedAPIKeyId, setSelectedAPIKeyId] = useState<number | null>(null);
  const [newAPIKeyName, setNewAPIKeyName] = useState('');
  const [newAPIKeyDescription, setNewAPIKeyDescription] = useState('');
  const [newAPIKeyRateLimit, setNewAPIKeyRateLimit] = useState(1000);
  const [createdAPIKey, setCreatedAPIKey] = useState<APIKeyCreated | null>(null);

  // Profile form state
  const [profile, setProfile] = useState<ProfileData>({
    full_name: user?.full_name || '',
    date_of_birth: user?.date_of_birth || '',
    phone_number: user?.phone_number || '',
    bio: user?.bio || '',
    avatar_url: user?.avatar_url || ''
  });

  // Password change state
  const [showPasswordChange, setShowPasswordChange] = useState(false);
  const [currentPassword, setCurrentPassword] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');

  // Email change state
  const [showEmailChange, setShowEmailChange] = useState(false);
  const [newEmail, setNewEmail] = useState('');
  const [emailPassword, setEmailPassword] = useState('');

  // Subscription state
  const [subscription, setSubscription] = useState<SubscriptionResponse | null>(null);
  const [subscriptionLoading, setSubscriptionLoading] = useState(true);
  const [isCanceling, setIsCanceling] = useState(false);
  const [isPausing, setIsPausing] = useState(false);
  const [isResuming, setIsResuming] = useState(false);

  useEffect(() => {
    if (user) {
      setProfile({
        full_name: user.full_name || '',
        date_of_birth: user.date_of_birth || '',
        phone_number: user.phone_number || '',
        bio: user.bio || '',
        avatar_url: user.avatar_url || ''
      });
    }
  }, [user]);

  useEffect(() => {
    // Fetch subscription information (skip for admins)
    const fetchSubscription = async () => {
      if (isAdmin) {
        // Admins don't need subscription info
        setSubscriptionLoading(false);
        return;
      }
      
      try {
        setSubscriptionLoading(true);
        const sub = await getSubscription();
        setSubscription(sub);
      } catch (error: any) {
        console.error('Error fetching subscription:', error);
        // Set default free tier if error
        setSubscription({
          tier: 'free',
          status: 'inactive',
          is_active: false,
          current_period_start: null,
          current_period_end: null,
          cancel_at_period_end: false
        });
      } finally {
        setSubscriptionLoading(false);
      }
    };

    if (user) {
      fetchSubscription();
    }
  }, [user, isAdmin]);

  const handleProfileUpdate = async (e: FormEvent) => {
    e.preventDefault();
    setIsSaving(true);
    setMessage(null);

    try {
      // Filter out empty strings and convert them to null for optional fields
      const profileData: any = {};
      if (profile.full_name && profile.full_name.trim()) {
        profileData.full_name = profile.full_name.trim();
      }
      if (profile.date_of_birth && profile.date_of_birth.trim()) {
        profileData.date_of_birth = profile.date_of_birth.trim();
      } else if (profile.date_of_birth !== undefined) {
        profileData.date_of_birth = null;
      }
      if (profile.phone_number && profile.phone_number.trim()) {
        profileData.phone_number = profile.phone_number.trim();
      }
      if (profile.bio && profile.bio.trim()) {
        profileData.bio = profile.bio.trim();
      }
      if (profile.avatar_url && profile.avatar_url.trim()) {
        profileData.avatar_url = profile.avatar_url.trim();
      }

      const response = await fetch(`${API_URL}/api/v1/auth/profile`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${tokens?.access_token}`
        },
        body: JSON.stringify(profileData)
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Failed to update profile');
      }

      setMessage({ type: 'success', text: 'Profile updated successfully!' });
      setIsEditing(false);

      // Refresh page to update user context
      setTimeout(() => window.location.reload(), 1500);
    } catch (error: any) {
      setMessage({ type: 'error', text: error.message });
    } finally {
      setIsSaving(false);
    }
  };

  const handlePasswordChange = async (e: FormEvent) => {
    e.preventDefault();

    if (newPassword !== confirmPassword) {
      setMessage({ type: 'error', text: 'Passwords do not match' });
      return;
    }

    if (newPassword.length < 8) {
      setMessage({ type: 'error', text: 'Password must be at least 8 characters' });
      return;
    }

    setIsSaving(true);
    setMessage(null);

    try {
      const response = await fetch(`${API_URL}/api/v1/auth/change-password`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${tokens?.access_token}`
        },
        body: JSON.stringify({
          current_password: currentPassword,
          new_password: newPassword
        })
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Failed to change password');
      }

      setMessage({ type: 'success', text: 'Password changed successfully!' });
      setShowPasswordChange(false);
      setCurrentPassword('');
      setNewPassword('');
      setConfirmPassword('');
    } catch (error: any) {
      setMessage({ type: 'error', text: error.message });
    } finally {
      setIsSaving(false);
    }
  };

  const handleEmailChange = async (e: FormEvent) => {
    e.preventDefault();
    setIsSaving(true);
    setMessage(null);

    try {
      const response = await fetch(`${API_URL}/api/v1/auth/email`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${tokens?.access_token}`
        },
        body: JSON.stringify({
          new_email: newEmail,
          password: emailPassword
        })
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Failed to update email');
      }

      const result = await response.json();
      setMessage({ type: 'success', text: result.message });
      setShowEmailChange(false);
      setNewEmail('');
      setEmailPassword('');

      // Refresh page after 2 seconds
      setTimeout(() => window.location.reload(), 2000);
    } catch (error: any) {
      setMessage({ type: 'error', text: error.message });
    } finally {
      setIsSaving(false);
    }
  };

  // Webhooks queries
  const { data: webhooks, isLoading: loadingWebhooks } = useQuery<Webhook[]>({
    queryKey: ['webhooks'],
    queryFn: () => webhooksApi.getWebhooks(),
    enabled: activeTab === 'webhooks',
  });

  const { data: webhookDeliveries } = useQuery<WebhookDelivery[]>({
    queryKey: ['webhook-deliveries', selectedWebhookId],
    queryFn: () => webhooksApi.getDeliveries(selectedWebhookId!),
    enabled: activeTab === 'webhooks' && selectedWebhookId !== null,
  });

  const createWebhookMutation = useMutation({
    mutationFn: (data: { url: string; event_types?: string[] }) =>
      webhooksApi.createWebhook(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['webhooks'] });
      setShowCreateWebhook(false);
      setNewWebhookUrl('');
      setNewWebhookEvents([]);
      setMessage({ type: 'success', text: 'Webhook created successfully!' });
    },
    onError: (error: any) => {
      setMessage({ type: 'error', text: error.message || 'Failed to create webhook' });
    },
  });

  const testWebhookMutation = useMutation({
    mutationFn: (webhookId: number) => webhooksApi.testWebhook(webhookId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['webhook-deliveries'] });
      setMessage({ type: 'success', text: 'Test webhook sent!' });
    },
    onError: (error: any) => {
      setMessage({ type: 'error', text: error.message || 'Failed to send test webhook' });
    },
  });

  // API Keys queries
  const { data: apiKeys, isLoading: loadingAPIKeys } = useQuery<APIKey[]>({
    queryKey: ['api-keys'],
    queryFn: () => apiKeysApi.getKeys(),
    enabled: activeTab === 'api-keys',
  });

  const { data: apiKeyUsage } = useQuery<APIKeyUsageStats>({
    queryKey: ['api-key-usage', selectedAPIKeyId],
    queryFn: () => apiKeysApi.getUsage(selectedAPIKeyId!),
    enabled: activeTab === 'api-keys' && selectedAPIKeyId !== null,
  });

  const createAPIKeyMutation = useMutation({
    mutationFn: (data: { name: string; description?: string; rate_limit_per_hour?: number }) =>
      apiKeysApi.createKey(data),
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ['api-keys'] });
      setShowCreateAPIKey(false);
      setNewAPIKeyName('');
      setNewAPIKeyDescription('');
      setNewAPIKeyRateLimit(1000);
      setCreatedAPIKey(data);
      setMessage({ type: 'success', text: 'API key created! Save it now - it won\'t be shown again.' });
    },
    onError: (error: any) => {
      setMessage({ type: 'error', text: error.message || 'Failed to create API key' });
    },
  });

  const revokeAPIKeyMutation = useMutation({
    mutationFn: (keyId: number) => apiKeysApi.revokeKey(keyId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['api-keys'] });
      setSelectedAPIKeyId(null);
      setMessage({ type: 'success', text: 'API key revoked successfully' });
    },
    onError: (error: any) => {
      setMessage({ type: 'error', text: error.message || 'Failed to revoke API key' });
    },
  });

  if (!user) {
    return <div className="min-h-screen flex items-center justify-center bg-[#0a0a0a] text-white">Loading...</div>;
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-white">Profile Settings</h1>
        <p className="mt-2 text-sm text-gray-400">
          Manage your account information and preferences
        </p>
      </div>

      {/* Tabs */}
      <div className="border-b border-white/10">
        <nav className="flex space-x-8">
          <button
            onClick={() => setActiveTab('profile')}
            className={`py-4 px-1 border-b-2 font-medium text-sm transition-colors ${
              activeTab === 'profile'
                ? 'border-purple-500 text-purple-400'
                : 'border-transparent text-gray-400 hover:text-gray-200 hover:border-gray-700'
            }`}
          >
            Profile
          </button>
          {!isAdmin && (
            <button
              onClick={() => setActiveTab('subscription')}
              className={`py-4 px-1 border-b-2 font-medium text-sm transition-colors ${
                activeTab === 'subscription'
                  ? 'border-purple-500 text-purple-400'
                  : 'border-transparent text-gray-400 hover:text-gray-200 hover:border-gray-700'
              }`}
            >
              Subscription
            </button>
          )}
          <button
            onClick={() => setActiveTab('webhooks')}
            className={`py-4 px-1 border-b-2 font-medium text-sm transition-colors ${
              activeTab === 'webhooks'
                ? 'border-purple-500 text-purple-400'
                : 'border-transparent text-gray-400 hover:text-gray-200 hover:border-gray-700'
            }`}
          >
            Webhooks
          </button>
          <button
            onClick={() => setActiveTab('api-keys')}
            className={`py-4 px-1 border-b-2 font-medium text-sm transition-colors ${
              activeTab === 'api-keys'
                ? 'border-purple-500 text-purple-400'
                : 'border-transparent text-gray-400 hover:text-gray-200 hover:border-gray-700'
            }`}
          >
            API Keys
          </button>
        </nav>
      </div>

      {/* Message Alert */}
      {message && (
        <div className={`mb-6 p-4 rounded-lg flex items-start ${
          message.type === 'success' ? 'bg-green-900/20 border border-green-500/30' : 'bg-red-900/20 border border-red-500/30'
        }`}>
          {message.type === 'success' ? (
            <CheckCircle2 className="h-5 w-5 text-green-400 mt-0.5 mr-3 flex-shrink-0" />
          ) : (
            <AlertCircle className="h-5 w-5 text-red-400 mt-0.5 mr-3 flex-shrink-0" />
          )}
          <p className={`text-sm ${message.type === 'success' ? 'text-green-300' : 'text-red-300'}`}>
            {message.text}
          </p>
        </div>
      )}

      <div className="space-y-6">
        {/* Profile Tab */}
        {activeTab === 'profile' && (
          <>
        {/* Profile Information Card */}
        <div className="bg-gray-900/50 backdrop-blur-sm shadow-lg rounded-2xl border border-white/10">
          <div className="px-6 py-4 border-b border-white/10 flex justify-between items-center">
            <h2 className="text-lg font-semibold text-white">Profile Information</h2>
            {!isEditing && (
              <button
                onClick={() => setIsEditing(true)}
                className="text-sm text-blue-400 hover:text-blue-300 font-medium transition-colors"
              >
                Edit Profile
              </button>
            )}
          </div>

          <form onSubmit={handleProfileUpdate} className="p-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* Username (Read-only) */}
              <div>
                <label className="block text-sm font-medium text-gray-400 mb-2">
                  Username
                </label>
                <div className="relative">
                  <User className="absolute left-3 top-2.5 h-5 w-5 text-gray-500" />
                  <input
                    type="text"
                    value={user.username}
                    disabled
                    className="w-full pl-10 pr-3 py-2 border border-white/10 rounded-lg bg-black/30 text-gray-500 cursor-not-allowed"
                  />
                </div>
              </div>

              {/* Full Name */}
              <div>
                <label className="block text-sm font-medium text-gray-400 mb-2">
                  Full Name
                </label>
                <div className="relative">
                  <User className="absolute left-3 top-2.5 h-5 w-5 text-gray-500" />
                  <input
                    type="text"
                    value={profile.full_name}
                    onChange={(e) => setProfile({ ...profile, full_name: e.target.value })}
                    disabled={!isEditing}
                    className={`w-full pl-10 pr-3 py-2 border border-white/10 rounded-lg text-white placeholder-gray-600 focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all ${
                      isEditing ? 'bg-black/50' : 'bg-black/30 text-gray-400'
                    }`}
                    placeholder="John Doe"
                  />
                </div>
              </div>

              {/* Date of Birth */}
              <div>
                <label className="block text-sm font-medium text-gray-400 mb-2">
                  Date of Birth
                </label>
                <div className="relative">
                  <Calendar className="absolute left-3 top-2.5 h-5 w-5 text-gray-500" />
                  <input
                    type="date"
                    value={profile.date_of_birth}
                    onChange={(e) => setProfile({ ...profile, date_of_birth: e.target.value })}
                    disabled={!isEditing}
                    className={`w-full pl-10 pr-3 py-2 border border-white/10 rounded-lg text-white placeholder-gray-600 focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all ${
                      isEditing ? 'bg-black/50' : 'bg-black/30 text-gray-400'
                    }`}
                  />
                </div>
              </div>

              {/* Phone Number */}
              <div>
                <label className="block text-sm font-medium text-gray-400 mb-2">
                  Phone Number
                </label>
                <div className="relative">
                  <Phone className="absolute left-3 top-2.5 h-5 w-5 text-gray-500" />
                  <input
                    type="tel"
                    value={profile.phone_number}
                    onChange={(e) => setProfile({ ...profile, phone_number: e.target.value })}
                    disabled={!isEditing}
                    className={`w-full pl-10 pr-3 py-2 border border-white/10 rounded-lg text-white placeholder-gray-600 focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all ${
                      isEditing ? 'bg-black/50' : 'bg-black/30 text-gray-400'
                    }`}
                    placeholder="+1 (555) 123-4567"
                  />
                </div>
              </div>

              {/* Avatar URL */}
              <div className="md:col-span-2">
                <label className="block text-sm font-medium text-gray-400 mb-2">
                  Avatar URL
                </label>
                <div className="relative">
                  <Image className="absolute left-3 top-2.5 h-5 w-5 text-gray-500" />
                  <input
                    type="url"
                    value={profile.avatar_url}
                    onChange={(e) => setProfile({ ...profile, avatar_url: e.target.value })}
                    disabled={!isEditing}
                    className={`w-full pl-10 pr-3 py-2 border border-white/10 rounded-lg text-white placeholder-gray-600 focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all ${
                      isEditing ? 'bg-black/50' : 'bg-black/30 text-gray-400'
                    }`}
                    placeholder="https://example.com/avatar.jpg"
                  />
                </div>
              </div>

              {/* Bio */}
              <div className="md:col-span-2">
                <label className="block text-sm font-medium text-gray-400 mb-2">
                  Bio
                </label>
                <div className="relative">
                  <FileText className="absolute left-3 top-2.5 h-5 w-5 text-gray-500" />
                  <textarea
                    value={profile.bio}
                    onChange={(e) => setProfile({ ...profile, bio: e.target.value })}
                    disabled={!isEditing}
                    rows={4}
                    maxLength={500}
                    className={`w-full pl-10 pr-3 py-2 border border-white/10 rounded-lg resize-none text-white placeholder-gray-600 focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all ${
                      isEditing ? 'bg-black/50' : 'bg-black/30 text-gray-400'
                    }`}
                    placeholder="Tell us about yourself..."
                  />
                </div>
                <p className="mt-1 text-xs text-gray-500">
                  {profile.bio?.length || 0}/500 characters
                </p>
              </div>
            </div>

            {/* Action Buttons */}
            {isEditing && (
              <div className="mt-6 flex gap-3">
                <button
                  type="submit"
                  disabled={isSaving}
                  className="flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-500 transition-colors disabled:opacity-50 font-medium"
                >
                  <Save className="h-4 w-4 mr-2" />
                  {isSaving ? 'Saving...' : 'Save Changes'}
                </button>
                <button
                  type="button"
                  onClick={() => {
                    setIsEditing(false);
                    setProfile({
                      full_name: user.full_name || '',
                      date_of_birth: user.date_of_birth || '',
                      phone_number: user.phone_number || '',
                      bio: user.bio || '',
                      avatar_url: user.avatar_url || ''
                    });
                  }}
                  className="px-4 py-2 border border-white/20 text-gray-300 rounded-lg hover:bg-white/10 transition-colors font-medium"
                >
                  Cancel
                </button>
              </div>
            )}
          </form>
        </div>

        {/* Email Change Card */}
        <div className="bg-gray-900/50 backdrop-blur-sm shadow-lg rounded-2xl border border-white/10">
          <div className="px-6 py-4 border-b border-white/10 flex justify-between items-center">
            <div>
              <h2 className="text-lg font-semibold text-white">Email Address</h2>
              <p className="text-sm text-gray-400 mt-1">{user.email}</p>
            </div>
            {!showEmailChange && (
              <button
                onClick={() => setShowEmailChange(true)}
                className="text-sm text-blue-400 hover:text-blue-300 font-medium transition-colors"
              >
                Change Email
              </button>
            )}
          </div>

          {showEmailChange && (
            <form onSubmit={handleEmailChange} className="p-6 space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-400 mb-2">
                  New Email
                </label>
                <input
                  type="email"
                  value={newEmail}
                  onChange={(e) => setNewEmail(e.target.value)}
                  required
                  className="w-full px-3 py-2 bg-black/50 border border-white/10 rounded-lg text-white focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all"
                  placeholder="new@example.com"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-400 mb-2">
                  Confirm Password
                </label>
                <input
                  type="password"
                  value={emailPassword}
                  onChange={(e) => setEmailPassword(e.target.value)}
                  required
                  className="w-full px-3 py-2 bg-black/50 border border-white/10 rounded-lg text-white focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all"
                  placeholder="••••••••"
                />
              </div>
              <div className="flex gap-3">
                <button
                  type="submit"
                  disabled={isSaving}
                  className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-500 transition-colors disabled:opacity-50 font-medium"
                >
                  {isSaving ? 'Updating...' : 'Update Email'}
                </button>
                <button
                  type="button"
                  onClick={() => {
                    setShowEmailChange(false);
                    setNewEmail('');
                    setEmailPassword('');
                  }}
                  className="px-4 py-2 border border-white/20 text-gray-300 rounded-lg hover:bg-white/10 transition-colors font-medium"
                >
                  Cancel
                </button>
              </div>
            </form>
          )}
        </div>

        {/* Password Change Card */}
        <div className="bg-gray-900/50 backdrop-blur-sm shadow-lg rounded-2xl border border-white/10">
          <div className="px-6 py-4 border-b border-white/10 flex justify-between items-center">
            <h2 className="text-lg font-semibold text-white">Password</h2>
            {!showPasswordChange && (
              <button
                onClick={() => setShowPasswordChange(true)}
                className="text-sm text-blue-400 hover:text-blue-300 font-medium transition-colors"
              >
                Change Password
              </button>
            )}
          </div>

          {showPasswordChange && (
            <form onSubmit={handlePasswordChange} className="p-6 space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-400 mb-2">
                  Current Password
                </label>
                <input
                  type="password"
                  value={currentPassword}
                  onChange={(e) => setCurrentPassword(e.target.value)}
                  required
                  className="w-full px-3 py-2 bg-black/50 border border-white/10 rounded-lg text-white focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all"
                  placeholder="••••••••"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-400 mb-2">
                  New Password
                </label>
                <input
                  type="password"
                  value={newPassword}
                  onChange={(e) => setNewPassword(e.target.value)}
                  required
                  minLength={8}
                  className="w-full px-3 py-2 bg-black/50 border border-white/10 rounded-lg text-white focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all"
                  placeholder="••••••••"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-400 mb-2">
                  Confirm New Password
                </label>
                <input
                  type="password"
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                  required
                  className="w-full px-3 py-2 bg-black/50 border border-white/10 rounded-lg text-white focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all"
                  placeholder="••••••••"
                />
              </div>
              <div className="flex gap-3">
                <button
                  type="submit"
                  disabled={isSaving}
                  className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-500 transition-colors disabled:opacity-50 font-medium"
                >
                  {isSaving ? 'Changing...' : 'Change Password'}
                </button>
                <button
                  type="button"
                  onClick={() => {
                    setShowPasswordChange(false);
                    setCurrentPassword('');
                    setNewPassword('');
                    setConfirmPassword('');
                  }}
                  className="px-4 py-2 border border-white/20 text-gray-300 rounded-lg hover:bg-white/10 transition-colors font-medium"
                >
                  Cancel
                </button>
              </div>
            </form>
          )}
        </div>

        {/* Account Status */}
        <div className="bg-gray-900/50 backdrop-blur-sm shadow-lg rounded-2xl border border-white/10 p-6">
          <h2 className="text-lg font-semibold text-white mb-4">Account Status</h2>
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-400">Account Status</span>
              <span className={`px-3 py-1 rounded-full text-xs font-medium ${
                user.is_active ? 'bg-green-500/20 text-green-300 border border-green-500/30' : 'bg-red-500/20 text-red-300 border border-red-500/30'
              }`}>
                {user.is_active ? 'Active' : 'Inactive'}
              </span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-400">Email Verification</span>
              <span className={`px-3 py-1 rounded-full text-xs font-medium ${
                user.is_verified ? 'bg-green-500/20 text-green-300 border border-green-500/30' : 'bg-yellow-500/20 text-yellow-300 border border-yellow-500/30'
              }`}>
                {user.is_verified ? 'Verified' : 'Not Verified'}
              </span>
            </div>
            {user.is_superuser && (
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-400">Role</span>
                <span className="px-3 py-1 rounded-full text-xs font-medium bg-purple-500/20 text-purple-300 border border-purple-500/30">
                  Administrator
                </span>
              </div>
            )}
            {/* Hide subscription info for admins */}
            {!isAdmin && (
              <>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-400">Subscription Tier</span>
                  {subscriptionLoading ? (
                    <span className="text-xs text-gray-500">Loading...</span>
                  ) : (
                    <span className={`px-3 py-1 rounded-full text-xs font-medium flex items-center ${
                      subscription?.tier === 'enterprise' ? 'bg-purple-500/20 text-purple-300 border border-purple-500/30' :
                      subscription?.tier === 'pro' ? 'bg-blue-500/20 text-blue-300 border border-blue-500/30' :
                      subscription?.tier === 'plus' || subscription?.tier === 'basic' ? 'bg-green-500/20 text-green-300 border border-green-500/30' :
                      'bg-gray-800 text-gray-400 border border-gray-700'
                    }`}>
                      {subscription?.tier === 'enterprise' && <Crown className="w-3 h-3 mr-1" />}
                      {subscription?.tier ? subscription.tier.charAt(0).toUpperCase() + subscription.tier.slice(1) : 'Free'}
                    </span>
                  )}
                </div>
                {subscription && subscription.is_active && subscription.current_period_end && (
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-gray-400">Renews On</span>
                    <span className="text-xs text-gray-300">
                      {new Date(subscription.current_period_end).toLocaleDateString()}
                    </span>
                  </div>
                )}
                {subscription && subscription.cancel_at_period_end && (
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-gray-400">Status</span>
                    <span className="px-3 py-1 rounded-full text-xs font-medium bg-yellow-500/20 text-yellow-300 border border-yellow-500/30">
                      Cancels at period end
                    </span>
                  </div>
                )}
              </>
            )}
          </div>
        </div>

        {/* Membership Management - Only for users with active subscriptions */}
        {activeTab === 'subscription' && !isAdmin && subscription && subscription.is_active && subscription.tier !== 'free' && (
          <div className="bg-gray-900/50 backdrop-blur-sm shadow-lg rounded-2xl border border-white/10 p-6">
            <h2 className="text-lg font-semibold text-white mb-4">Membership Management</h2>
            <div className="space-y-4">
              <div className="flex items-center justify-between p-4 bg-white/5 rounded-lg border border-white/5">
                <div>
                  <h3 className="font-medium text-white">Order History</h3>
                  <p className="text-sm text-gray-400">View your payment history and receipts</p>
                </div>
                <button
                  onClick={() => navigate('/orders')}
                  className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-500 transition-colors font-medium"
                >
                  View Orders
                </button>
              </div>

              {subscription.status !== 'paused' && !subscription.cancel_at_period_end && (
                <>
                  <div className="flex items-center justify-between p-4 bg-yellow-900/20 rounded-lg border border-yellow-500/30">
                    <div>
                      <h3 className="font-medium text-yellow-200 flex items-center">
                        <Pause className="w-4 h-4 mr-2 text-yellow-400" />
                        Pause Membership
                      </h3>
                      <p className="text-sm text-yellow-200/70">Temporarily pause billing for up to 3 months</p>
                    </div>
                    <button
                      onClick={async () => {
                        showConfirm(
                          'Are you sure you want to pause your membership? Billing will resume automatically after 3 months.',
                          async () => {
                            try {
                          setIsPausing(true);
                          await pauseSubscription();
                          setMessage({ type: 'success', text: 'Membership paused successfully' });
                          // Refresh subscription
                          const sub = await getSubscription();
                          setSubscription(sub);
                        } catch (error: any) {
                          setMessage({ type: 'error', text: error.message || 'Failed to pause membership' });
                        } finally {
                              setIsPausing(false);
                            }
                          },
                          { type: 'warning', title: 'TradeSignal' }
                        );
                      }}
                      disabled={isPausing}
                      className="px-4 py-2 bg-yellow-600/80 text-white rounded-lg hover:bg-yellow-600 transition-colors disabled:opacity-50 font-medium"
                    >
                      {isPausing ? 'Pausing...' : 'Pause'}
                    </button>
                  </div>

                  <div className="flex items-center justify-between p-4 bg-red-900/20 rounded-lg border border-red-500/30">
                    <div>
                      <h3 className="font-medium text-red-200 flex items-center">
                        <XCircle className="w-4 h-4 mr-2 text-red-400" />
                        Cancel Membership
                      </h3>
                      <p className="text-sm text-red-200/70">Cancel at the end of your billing period</p>
                    </div>
                    <button
                      onClick={async () => {
                        showConfirm(
                          'Are you sure you want to cancel your membership? You will retain access until the end of your billing period.',
                          async () => {
                            try {
                          setIsCanceling(true);
                          await cancelSubscription();
                          setMessage({ type: 'success', text: 'Membership will be canceled at the end of your billing period' });
                          // Refresh subscription
                          const sub = await getSubscription();
                          setSubscription(sub);
                        } catch (error: any) {
                          setMessage({ type: 'error', text: error.message || 'Failed to cancel membership' });
                        } finally {
                              setIsCanceling(false);
                            }
                          },
                          { type: 'warning', title: 'TradeSignal' }
                        );
                      }}
                      disabled={isCanceling}
                      className="px-4 py-2 bg-red-600/80 text-white rounded-lg hover:bg-red-600 transition-colors disabled:opacity-50 font-medium"
                    >
                      {isCanceling ? 'Canceling...' : 'Cancel'}
                    </button>
                  </div>
                </>
              )}

              {subscription.status === 'paused' && (
                <div className="flex items-center justify-between p-4 bg-green-900/20 rounded-lg border border-green-500/30">
                  <div>
                    <h3 className="font-medium text-green-200 flex items-center">
                      <Play className="w-4 h-4 mr-2 text-green-400" />
                      Resume Membership
                    </h3>
                    <p className="text-sm text-green-200/70">Resume your paused membership</p>
                  </div>
                  <button
                    onClick={async () => {
                      try {
                        setIsResuming(true);
                        await resumeSubscription();
                        setMessage({ type: 'success', text: 'Membership resumed successfully' });
                        // Refresh subscription
                        const sub = await getSubscription();
                        setSubscription(sub);
                      } catch (error: any) {
                        setMessage({ type: 'error', text: error.message || 'Failed to resume membership' });
                      } finally {
                        setIsResuming(false);
                      }
                    }}
                    disabled={isResuming}
                    className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-500 transition-colors disabled:opacity-50 font-medium"
                  >
                    {isResuming ? 'Resuming...' : 'Resume'}
                  </button>
                </div>
              )}

              <div className="flex items-center justify-between p-4 bg-blue-900/20 rounded-lg border border-blue-500/30">
                <div>
                  <h3 className="font-medium text-blue-200 flex items-center">
                    <HelpCircle className="w-4 h-4 mr-2 text-blue-400" />
                    Need Help?
                  </h3>
                  <p className="text-sm text-blue-200/70">Contact our support team for billing questions</p>
                </div>
                <button
                  onClick={() => navigate('/contact')}
                  className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-500 transition-colors font-medium"
                >
                  Contact Support
                </button>
              </div>
            </div>
          </div>
        )}
          </>
        )}

        {/* Webhooks Tab */}
        {activeTab === 'webhooks' && (
          <div className="bg-gray-900/50 backdrop-blur-sm shadow-lg rounded-2xl border border-white/10 p-6">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-lg font-semibold text-white">Webhooks</h2>
              <button
                onClick={() => setShowCreateWebhook(true)}
                className="px-4 py-2 bg-purple-600 hover:bg-purple-700 rounded-lg flex items-center gap-2 transition-colors"
              >
                <Plus className="w-4 h-4" />
                Create Webhook
              </button>
            </div>

            {loadingWebhooks ? (
              <div className="text-center py-8 text-gray-400">Loading webhooks...</div>
            ) : webhooks && webhooks.length > 0 ? (
              <div className="space-y-4">
                {webhooks.map((webhook) => (
                  <div
                    key={webhook.id}
                    className="bg-white/5 border border-white/10 rounded-lg p-4 hover:bg-white/10 transition-colors cursor-pointer"
                    onClick={() => setSelectedWebhookId(selectedWebhookId === webhook.id ? null : webhook.id)}
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex-1">
                        <div className="flex items-center gap-3 mb-2">
                          <h3 className="font-semibold">{webhook.url}</h3>
                          <span
                            className={`px-2 py-1 rounded text-xs ${
                              webhook.is_active
                                ? 'bg-green-500/20 text-green-400'
                                : 'bg-gray-500/20 text-gray-400'
                            }`}
                          >
                            {webhook.is_active ? 'Active' : 'Inactive'}
                          </span>
                        </div>
                        <p className="text-sm text-gray-400">
                          Events: {webhook.event_types?.join(', ') || 'All events'}
                        </p>
                        <p className="text-xs text-gray-500 mt-1">
                          Created: {new Date(webhook.created_at).toLocaleDateString()}
                        </p>
                      </div>
                      <div className="flex gap-2">
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            testWebhookMutation.mutate(webhook.id);
                          }}
                          disabled={testWebhookMutation.isPending}
                          className="p-2 hover:bg-white/10 rounded transition-colors"
                          title="Test Webhook"
                        >
                          <Eye className="w-5 h-5" />
                        </button>
                      </div>
                    </div>

                    {/* Delivery History (expanded) */}
                    {selectedWebhookId === webhook.id && webhookDeliveries && (
                      <div className="mt-4 pt-4 border-t border-white/10">
                        <h4 className="font-semibold mb-3">Delivery History</h4>
                        {webhookDeliveries.length > 0 ? (
                          <div className="space-y-2">
                            {webhookDeliveries.slice(0, 10).map((delivery) => (
                              <div
                                key={delivery.id}
                                className="flex items-center justify-between p-2 bg-white/5 rounded text-sm"
                              >
                                <div>
                                  <span className="font-medium">{delivery.event_type}</span>
                                  <span className="text-gray-400 ml-2">
                                    {new Date(delivery.created_at).toLocaleString()}
                                  </span>
                                </div>
                                <span
                                  className={`px-2 py-1 rounded text-xs ${
                                    delivery.status === 'delivered'
                                      ? 'bg-green-500/20 text-green-400'
                                      : delivery.status === 'failed'
                                      ? 'bg-red-500/20 text-red-400'
                                      : 'bg-yellow-500/20 text-yellow-400'
                                  }`}
                                >
                                  {delivery.status} {delivery.response_code && `(${delivery.response_code})`}
                                </span>
                              </div>
                            ))}
                          </div>
                        ) : (
                          <p className="text-gray-400 text-sm">No deliveries yet</p>
                        )}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-12">
                <WebhookIcon className="w-12 h-12 text-gray-500 mx-auto mb-4" />
                <p className="text-gray-400 mb-4">No webhooks configured</p>
                <button
                  onClick={() => setShowCreateWebhook(true)}
                  className="px-4 py-2 bg-purple-600 hover:bg-purple-700 rounded-lg transition-colors"
                >
                  Create Your First Webhook
                </button>
              </div>
            )}

            {/* Create Webhook Modal */}
            {showCreateWebhook && (
              <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
                <div className="bg-[#1a1a1a] border border-white/10 rounded-lg p-6 max-w-md w-full mx-4">
                  <h3 className="text-xl font-bold mb-4">Create Webhook</h3>
                  <div className="space-y-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-400 mb-2">Webhook URL</label>
                      <input
                        type="url"
                        value={newWebhookUrl}
                        onChange={(e) => setNewWebhookUrl(e.target.value)}
                        placeholder="https://example.com/webhook"
                        className="w-full px-3 py-2 bg-black/50 border border-white/10 rounded-lg text-white focus:ring-2 focus:ring-purple-500"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-400 mb-2">Event Types (optional)</label>
                      <input
                        type="text"
                        value={newWebhookEvents.join(', ')}
                        onChange={(e) => setNewWebhookEvents(e.target.value.split(',').map(s => s.trim()).filter(Boolean))}
                        placeholder="trade_alert, conversion, subscription_updated"
                        className="w-full px-3 py-2 bg-black/50 border border-white/10 rounded-lg text-white focus:ring-2 focus:ring-purple-500"
                      />
                      <p className="text-xs text-gray-500 mt-1">Leave empty for all events</p>
                    </div>
                    <div className="flex gap-3 justify-end">
                      <button
                        onClick={() => {
                          setShowCreateWebhook(false);
                          setNewWebhookUrl('');
                          setNewWebhookEvents([]);
                        }}
                        className="px-4 py-2 border border-white/20 hover:bg-white/10 rounded-lg transition-colors"
                      >
                        Cancel
                      </button>
                      <button
                        onClick={() => {
                          if (newWebhookUrl) {
                            createWebhookMutation.mutate({
                              url: newWebhookUrl,
                              event_types: newWebhookEvents.length > 0 ? newWebhookEvents : undefined,
                            });
                          }
                        }}
                        disabled={!newWebhookUrl || createWebhookMutation.isPending}
                        className="px-4 py-2 bg-purple-600 hover:bg-purple-700 rounded-lg transition-colors disabled:opacity-50"
                      >
                        {createWebhookMutation.isPending ? 'Creating...' : 'Create'}
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            )}
          </div>
        )}

        {/* API Keys Tab */}
        {activeTab === 'api-keys' && (
          <div className="bg-gray-900/50 backdrop-blur-sm shadow-lg rounded-2xl border border-white/10 p-6">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-lg font-semibold text-white">API Keys</h2>
              <button
                onClick={() => setShowCreateAPIKey(true)}
                className="px-4 py-2 bg-purple-600 hover:bg-purple-700 rounded-lg flex items-center gap-2 transition-colors"
              >
                <Plus className="w-4 h-4" />
                Create API Key
              </button>
            </div>

            {/* Show created key modal (one-time display) */}
            {createdAPIKey && (
              <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
                <div className="bg-[#1a1a1a] border border-white/10 rounded-lg p-6 max-w-md w-full mx-4">
                  <h3 className="text-xl font-bold mb-4 text-yellow-400">⚠️ Save Your API Key</h3>
                  <p className="text-gray-400 mb-4 text-sm">
                    This is the only time you'll see this key. Copy it now and store it securely!
                  </p>
                  <div className="bg-black/50 border border-white/10 rounded-lg p-4 mb-4">
                    <code className="text-sm text-white break-all">{createdAPIKey.key}</code>
                  </div>
                  <div className="flex gap-3">
                    <button
                      onClick={() => {
                        navigator.clipboard.writeText(createdAPIKey.key);
                        setMessage({ type: 'success', text: 'API key copied to clipboard!' });
                      }}
                      className="flex-1 px-4 py-2 bg-purple-600 hover:bg-purple-700 rounded-lg transition-colors flex items-center justify-center gap-2"
                    >
                      <Copy className="w-4 h-4" />
                      Copy Key
                    </button>
                    <button
                      onClick={() => setCreatedAPIKey(null)}
                      className="px-4 py-2 border border-white/20 hover:bg-white/10 rounded-lg transition-colors"
                    >
                      I've Saved It
                    </button>
                  </div>
                </div>
              </div>
            )}

            {loadingAPIKeys ? (
              <div className="text-center py-8 text-gray-400">Loading API keys...</div>
            ) : apiKeys && apiKeys.length > 0 ? (
              <div className="space-y-4">
                {apiKeys.map((key) => (
                  <div
                    key={key.id}
                    className="bg-white/5 border border-white/10 rounded-lg p-4 hover:bg-white/10 transition-colors cursor-pointer"
                    onClick={() => setSelectedAPIKeyId(selectedAPIKeyId === key.id ? null : key.id)}
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex-1">
                        <div className="flex items-center gap-3 mb-2">
                          <h3 className="font-semibold">{key.name}</h3>
                          <span className="text-sm text-gray-400 font-mono">{key.key_prefix}...</span>
                          <span
                            className={`px-2 py-1 rounded text-xs ${
                              key.is_active
                                ? 'bg-green-500/20 text-green-400'
                                : 'bg-gray-500/20 text-gray-400'
                            }`}
                          >
                            {key.is_active ? 'Active' : 'Revoked'}
                          </span>
                        </div>
                        {key.description && (
                          <p className="text-sm text-gray-400 mb-2">{key.description}</p>
                        )}
                        <div className="flex gap-4 text-sm text-gray-400">
                          <span>Rate Limit: {key.rate_limit_per_hour}/hour</span>
                          {key.last_used_at && (
                            <span>Last Used: {new Date(key.last_used_at).toLocaleDateString()}</span>
                          )}
                          {key.expires_at && (
                            <span className={new Date(key.expires_at) < new Date() ? 'text-red-400' : ''}>
                              Expires: {new Date(key.expires_at).toLocaleDateString()}
                            </span>
                          )}
                        </div>
                      </div>
                      {key.is_active && (
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            if (window.confirm('Are you sure you want to revoke this API key?')) {
                              revokeAPIKeyMutation.mutate(key.id);
                            }
                          }}
                          disabled={revokeAPIKeyMutation.isPending}
                          className="p-2 hover:bg-red-500/20 rounded transition-colors"
                          title="Revoke Key"
                        >
                          <Trash2 className="w-5 h-5 text-red-400" />
                        </button>
                      )}
                    </div>

                    {/* Usage Stats (expanded) */}
                    {selectedAPIKeyId === key.id && apiKeyUsage && (
                      <div className="mt-4 pt-4 border-t border-white/10">
                        <h4 className="font-semibold mb-3">Usage Statistics (Last {apiKeyUsage.days} days)</h4>
                        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                          <div>
                            <p className="text-sm text-gray-400">Total Requests</p>
                            <p className="text-xl font-bold">{apiKeyUsage.total_requests}</p>
                          </div>
                          <div>
                            <p className="text-sm text-gray-400">Successful</p>
                            <p className="text-xl font-bold text-green-400">{apiKeyUsage.successful_requests}</p>
                          </div>
                          <div>
                            <p className="text-sm text-gray-400">Failed</p>
                            <p className="text-xl font-bold text-red-400">{apiKeyUsage.failed_requests}</p>
                          </div>
                          <div>
                            <p className="text-sm text-gray-400">Avg Response</p>
                            <p className="text-xl font-bold">{apiKeyUsage.avg_response_time_ms.toFixed(0)}ms</p>
                          </div>
                        </div>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-12">
                <Key className="w-12 h-12 text-gray-500 mx-auto mb-4" />
                <p className="text-gray-400 mb-4">No API keys created</p>
                <button
                  onClick={() => setShowCreateAPIKey(true)}
                  className="px-4 py-2 bg-purple-600 hover:bg-purple-700 rounded-lg transition-colors"
                >
                  Create Your First API Key
                </button>
              </div>
            )}

            {/* Create API Key Modal */}
            {showCreateAPIKey && (
              <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
                <div className="bg-[#1a1a1a] border border-white/10 rounded-lg p-6 max-w-md w-full mx-4">
                  <h3 className="text-xl font-bold mb-4">Create API Key</h3>
                  <div className="space-y-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-400 mb-2">Name</label>
                      <input
                        type="text"
                        value={newAPIKeyName}
                        onChange={(e) => setNewAPIKeyName(e.target.value)}
                        placeholder="My API Key"
                        className="w-full px-3 py-2 bg-black/50 border border-white/10 rounded-lg text-white focus:ring-2 focus:ring-purple-500"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-400 mb-2">Description (optional)</label>
                      <input
                        type="text"
                        value={newAPIKeyDescription}
                        onChange={(e) => setNewAPIKeyDescription(e.target.value)}
                        placeholder="Used for production integration"
                        className="w-full px-3 py-2 bg-black/50 border border-white/10 rounded-lg text-white focus:ring-2 focus:ring-purple-500"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-400 mb-2">Rate Limit (requests/hour)</label>
                      <input
                        type="number"
                        value={newAPIKeyRateLimit}
                        onChange={(e) => setNewAPIKeyRateLimit(Number(e.target.value))}
                        min={1}
                        max={10000}
                        className="w-full px-3 py-2 bg-black/50 border border-white/10 rounded-lg text-white focus:ring-2 focus:ring-purple-500"
                      />
                    </div>
                    <div className="flex gap-3 justify-end">
                      <button
                        onClick={() => {
                          setShowCreateAPIKey(false);
                          setNewAPIKeyName('');
                          setNewAPIKeyDescription('');
                          setNewAPIKeyRateLimit(1000);
                        }}
                        className="px-4 py-2 border border-white/20 hover:bg-white/10 rounded-lg transition-colors"
                      >
                        Cancel
                      </button>
                      <button
                        onClick={() => {
                          if (newAPIKeyName) {
                            createAPIKeyMutation.mutate({
                              name: newAPIKeyName,
                              description: newAPIKeyDescription || undefined,
                              rate_limit_per_hour: newAPIKeyRateLimit,
                            });
                          }
                        }}
                        disabled={!newAPIKeyName || createAPIKeyMutation.isPending}
                        className="px-4 py-2 bg-purple-600 hover:bg-purple-700 rounded-lg transition-colors disabled:opacity-50"
                      >
                        {createAPIKeyMutation.isPending ? 'Creating...' : 'Create'}
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Custom Confirm Modal */}
      <CustomConfirm
        show={confirmState.show}
        message={confirmState.message}
        title={confirmState.title || 'TradeSignal'}
        type={confirmState.type}
        confirmText={confirmState.confirmText}
        cancelText={confirmState.cancelText}
        onConfirm={confirmState.onConfirm || (() => {})}
        onCancel={hideConfirm}
      />
    </div>
  );
}