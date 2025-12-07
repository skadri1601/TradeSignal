/**
 * User Profile Page
 * Allows users to view and edit their profile information
 */

import { useState, FormEvent, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { User, Calendar, Phone, FileText, Image, Save, AlertCircle, CheckCircle2, Crown, XCircle, Pause, Play, HelpCircle } from 'lucide-react';
import { getSubscription, cancelSubscription, pauseSubscription, resumeSubscription } from '../api/billing';
import type { SubscriptionResponse } from '../api/billing';
import { useCustomConfirm } from '../hooks/useCustomConfirm';
import CustomConfirm from '../components/common/CustomConfirm';

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
  const isAdmin = user?.is_superuser || false;
  const { confirmState, showConfirm, hideConfirm } = useCustomConfirm();
  const [isEditing, setIsEditing] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);

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
      const response = await fetch(`${API_URL}/api/v1/auth/profile`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${tokens?.access_token}`
        },
        body: JSON.stringify(profile)
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

  if (!user) {
    return <div className="min-h-screen flex items-center justify-center">Loading...</div>;
  }

  return (
    <div className="min-h-screen bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Profile Settings</h1>
          <p className="mt-2 text-sm text-gray-600">
            Manage your account information and preferences
          </p>
        </div>

        {/* Message Alert */}
        {message && (
          <div className={`mb-6 p-4 rounded-lg flex items-start ${
            message.type === 'success' ? 'bg-green-50 border border-green-200' : 'bg-red-50 border border-red-200'
          }`}>
            {message.type === 'success' ? (
              <CheckCircle2 className="h-5 w-5 text-green-600 mt-0.5 mr-3 flex-shrink-0" />
            ) : (
              <AlertCircle className="h-5 w-5 text-red-600 mt-0.5 mr-3 flex-shrink-0" />
            )}
            <p className={`text-sm ${message.type === 'success' ? 'text-green-800' : 'text-red-800'}`}>
              {message.text}
            </p>
          </div>
        )}

        <div className="space-y-6">
          {/* Profile Information Card */}
          <div className="bg-white shadow rounded-lg">
            <div className="px-6 py-4 border-b border-gray-200 flex justify-between items-center">
              <h2 className="text-lg font-semibold text-gray-900">Profile Information</h2>
              {!isEditing && (
                <button
                  onClick={() => setIsEditing(true)}
                  className="text-sm text-blue-600 hover:text-blue-700 font-medium"
                >
                  Edit Profile
                </button>
              )}
            </div>

            <form onSubmit={handleProfileUpdate} className="p-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {/* Username (Read-only) */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Username
                  </label>
                  <div className="relative">
                    <User className="absolute left-3 top-2.5 h-5 w-5 text-gray-400" />
                    <input
                      type="text"
                      value={user.username}
                      disabled
                      className="w-full pl-10 pr-3 py-2 border border-gray-300 rounded-lg bg-gray-100 text-gray-600"
                    />
                  </div>
                </div>

                {/* Full Name */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Full Name
                  </label>
                  <div className="relative">
                    <User className="absolute left-3 top-2.5 h-5 w-5 text-gray-400" />
                    <input
                      type="text"
                      value={profile.full_name}
                      onChange={(e) => setProfile({ ...profile, full_name: e.target.value })}
                      disabled={!isEditing}
                      className={`w-full pl-10 pr-3 py-2 border border-gray-300 rounded-lg ${
                        isEditing ? 'bg-white' : 'bg-gray-50'
                      }`}
                      placeholder="John Doe"
                    />
                  </div>
                </div>

                {/* Date of Birth */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Date of Birth
                  </label>
                  <div className="relative">
                    <Calendar className="absolute left-3 top-2.5 h-5 w-5 text-gray-400" />
                    <input
                      type="date"
                      value={profile.date_of_birth}
                      onChange={(e) => setProfile({ ...profile, date_of_birth: e.target.value })}
                      disabled={!isEditing}
                      className={`w-full pl-10 pr-3 py-2 border border-gray-300 rounded-lg ${
                        isEditing ? 'bg-white' : 'bg-gray-50'
                      }`}
                    />
                  </div>
                </div>

                {/* Phone Number */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Phone Number
                  </label>
                  <div className="relative">
                    <Phone className="absolute left-3 top-2.5 h-5 w-5 text-gray-400" />
                    <input
                      type="tel"
                      value={profile.phone_number}
                      onChange={(e) => setProfile({ ...profile, phone_number: e.target.value })}
                      disabled={!isEditing}
                      className={`w-full pl-10 pr-3 py-2 border border-gray-300 rounded-lg ${
                        isEditing ? 'bg-white' : 'bg-gray-50'
                      }`}
                      placeholder="+1 (555) 123-4567"
                    />
                  </div>
                </div>

                {/* Avatar URL */}
                <div className="md:col-span-2">
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Avatar URL
                  </label>
                  <div className="relative">
                    <Image className="absolute left-3 top-2.5 h-5 w-5 text-gray-400" />
                    <input
                      type="url"
                      value={profile.avatar_url}
                      onChange={(e) => setProfile({ ...profile, avatar_url: e.target.value })}
                      disabled={!isEditing}
                      className={`w-full pl-10 pr-3 py-2 border border-gray-300 rounded-lg ${
                        isEditing ? 'bg-white' : 'bg-gray-50'
                      }`}
                      placeholder="https://example.com/avatar.jpg"
                    />
                  </div>
                </div>

                {/* Bio */}
                <div className="md:col-span-2">
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Bio
                  </label>
                  <div className="relative">
                    <FileText className="absolute left-3 top-2.5 h-5 w-5 text-gray-400" />
                    <textarea
                      value={profile.bio}
                      onChange={(e) => setProfile({ ...profile, bio: e.target.value })}
                      disabled={!isEditing}
                      rows={4}
                      maxLength={500}
                      className={`w-full pl-10 pr-3 py-2 border border-gray-300 rounded-lg resize-none ${
                        isEditing ? 'bg-white' : 'bg-gray-50'
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
                    className="flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
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
                    className="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50"
                  >
                    Cancel
                  </button>
                </div>
              )}
            </form>
          </div>

          {/* Email Change Card */}
          <div className="bg-white shadow rounded-lg">
            <div className="px-6 py-4 border-b border-gray-200 flex justify-between items-center">
              <div>
                <h2 className="text-lg font-semibold text-gray-900">Email Address</h2>
                <p className="text-sm text-gray-600 mt-1">{user.email}</p>
              </div>
              {!showEmailChange && (
                <button
                  onClick={() => setShowEmailChange(true)}
                  className="text-sm text-blue-600 hover:text-blue-700 font-medium"
                >
                  Change Email
                </button>
              )}
            </div>

            {showEmailChange && (
              <form onSubmit={handleEmailChange} className="p-6 space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    New Email
                  </label>
                  <input
                    type="email"
                    value={newEmail}
                    onChange={(e) => setNewEmail(e.target.value)}
                    required
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                    placeholder="new@example.com"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Confirm Password
                  </label>
                  <input
                    type="password"
                    value={emailPassword}
                    onChange={(e) => setEmailPassword(e.target.value)}
                    required
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                    placeholder="••••••••"
                  />
                </div>
                <div className="flex gap-3">
                  <button
                    type="submit"
                    disabled={isSaving}
                    className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
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
                    className="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50"
                  >
                    Cancel
                  </button>
                </div>
              </form>
            )}
          </div>

          {/* Password Change Card */}
          <div className="bg-white shadow rounded-lg">
            <div className="px-6 py-4 border-b border-gray-200 flex justify-between items-center">
              <h2 className="text-lg font-semibold text-gray-900">Password</h2>
              {!showPasswordChange && (
                <button
                  onClick={() => setShowPasswordChange(true)}
                  className="text-sm text-blue-600 hover:text-blue-700 font-medium"
                >
                  Change Password
                </button>
              )}
            </div>

            {showPasswordChange && (
              <form onSubmit={handlePasswordChange} className="p-6 space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Current Password
                  </label>
                  <input
                    type="password"
                    value={currentPassword}
                    onChange={(e) => setCurrentPassword(e.target.value)}
                    required
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                    placeholder="••••••••"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    New Password
                  </label>
                  <input
                    type="password"
                    value={newPassword}
                    onChange={(e) => setNewPassword(e.target.value)}
                    required
                    minLength={8}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                    placeholder="••••••••"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Confirm New Password
                  </label>
                  <input
                    type="password"
                    value={confirmPassword}
                    onChange={(e) => setConfirmPassword(e.target.value)}
                    required
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                    placeholder="••••••••"
                  />
                </div>
                <div className="flex gap-3">
                  <button
                    type="submit"
                    disabled={isSaving}
                    className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
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
                    className="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50"
                  >
                    Cancel
                  </button>
                </div>
              </form>
            )}
          </div>

          {/* Account Status */}
          <div className="bg-white shadow rounded-lg p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Account Status</h2>
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-600">Account Status</span>
                <span className={`px-3 py-1 rounded-full text-xs font-medium ${
                  user.is_active ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'
                }`}>
                  {user.is_active ? 'Active' : 'Inactive'}
                </span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-600">Email Verification</span>
                <span className={`px-3 py-1 rounded-full text-xs font-medium ${
                  user.is_verified ? 'bg-green-100 text-green-700' : 'bg-yellow-100 text-yellow-700'
                }`}>
                  {user.is_verified ? 'Verified' : 'Not Verified'}
                </span>
              </div>
              {user.is_superuser && (
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-600">Role</span>
                  <span className="px-3 py-1 rounded-full text-xs font-medium bg-purple-100 text-purple-700">
                    Administrator
                  </span>
                </div>
              )}
              {/* Hide subscription info for admins */}
              {!isAdmin && (
                <>
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-gray-600">Subscription Tier</span>
                    {subscriptionLoading ? (
                      <span className="text-xs text-gray-400">Loading...</span>
                    ) : (
                      <span className={`px-3 py-1 rounded-full text-xs font-medium flex items-center ${
                        subscription?.tier === 'enterprise' ? 'bg-purple-100 text-purple-700' :
                        subscription?.tier === 'pro' ? 'bg-blue-100 text-blue-700' :
                        subscription?.tier === 'plus' || subscription?.tier === 'basic' ? 'bg-green-100 text-green-700' :
                        'bg-gray-100 text-gray-700'
                      }`}>
                        {subscription?.tier === 'enterprise' && <Crown className="w-3 h-3 mr-1" />}
                        {subscription?.tier ? subscription.tier.charAt(0).toUpperCase() + subscription.tier.slice(1) : 'Free'}
                      </span>
                    )}
                  </div>
                  {subscription && subscription.is_active && subscription.current_period_end && (
                    <div className="flex items-center justify-between">
                      <span className="text-sm text-gray-600">Renews On</span>
                      <span className="text-xs text-gray-700">
                        {new Date(subscription.current_period_end).toLocaleDateString()}
                      </span>
                    </div>
                  )}
                  {subscription && subscription.cancel_at_period_end && (
                    <div className="flex items-center justify-between">
                      <span className="text-sm text-gray-600">Status</span>
                      <span className="px-3 py-1 rounded-full text-xs font-medium bg-yellow-100 text-yellow-700">
                        Cancels at period end
                      </span>
                    </div>
                  )}
                </>
              )}
            </div>
          </div>

          {/* Membership Management - Only for users with active subscriptions */}
          {!isAdmin && subscription && subscription.is_active && subscription.tier !== 'free' && (
            <div className="bg-white shadow rounded-lg p-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">Membership Management</h2>
              <div className="space-y-4">
                <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                  <div>
                    <h3 className="font-medium text-gray-900">Order History</h3>
                    <p className="text-sm text-gray-600">View your payment history and receipts</p>
                  </div>
                  <button
                    onClick={() => navigate('/orders')}
                    className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                  >
                    View Orders
                  </button>
                </div>

                {subscription.status !== 'paused' && !subscription.cancel_at_period_end && (
                  <>
                    <div className="flex items-center justify-between p-4 bg-yellow-50 rounded-lg border border-yellow-200">
                      <div>
                        <h3 className="font-medium text-gray-900 flex items-center">
                          <Pause className="w-4 h-4 mr-2 text-yellow-600" />
                          Pause Membership
                        </h3>
                        <p className="text-sm text-gray-600">Temporarily pause billing for up to 3 months</p>
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
                        className="px-4 py-2 bg-yellow-600 text-white rounded-lg hover:bg-yellow-700 transition-colors disabled:opacity-50"
                      >
                        {isPausing ? 'Pausing...' : 'Pause'}
                      </button>
                    </div>

                    <div className="flex items-center justify-between p-4 bg-red-50 rounded-lg border border-red-200">
                      <div>
                        <h3 className="font-medium text-gray-900 flex items-center">
                          <XCircle className="w-4 h-4 mr-2 text-red-600" />
                          Cancel Membership
                        </h3>
                        <p className="text-sm text-gray-600">Cancel at the end of your billing period</p>
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
                        className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors disabled:opacity-50"
                      >
                        {isCanceling ? 'Canceling...' : 'Cancel'}
                      </button>
                    </div>
                  </>
                )}

                {subscription.status === 'paused' && (
                  <div className="flex items-center justify-between p-4 bg-green-50 rounded-lg border border-green-200">
                    <div>
                      <h3 className="font-medium text-gray-900 flex items-center">
                        <Play className="w-4 h-4 mr-2 text-green-600" />
                        Resume Membership
                      </h3>
                      <p className="text-sm text-gray-600">Resume your paused membership</p>
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
                      className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors disabled:opacity-50"
                    >
                      {isResuming ? 'Resuming...' : 'Resume'}
                    </button>
                  </div>
                )}

                <div className="flex items-center justify-between p-4 bg-blue-50 rounded-lg border border-blue-200">
                  <div>
                    <h3 className="font-medium text-gray-900 flex items-center">
                      <HelpCircle className="w-4 h-4 mr-2 text-blue-600" />
                      Need Help?
                    </h3>
                    <p className="text-sm text-gray-600">Contact our support team for billing questions</p>
                  </div>
                  <button
                    onClick={() => navigate('/contact')}
                    className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                  >
                    Contact Support
                  </button>
                </div>
              </div>
            </div>
          )}
        </div>
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
