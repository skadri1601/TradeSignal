import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { alertsApi } from "../api/alerts";
import LoadingSpinner from "../components/common/LoadingSpinner";
import { Alert, PaginatedResponse, AlertStats } from "../types";
import AlertList from "../components/alerts/AlertList";
import CreateAlertModal from "../components/alerts/CreateAlertModal";
import { LegalDisclaimer } from "../components/LegalDisclaimer";
import { Bell, BellRing, BellOff, Send, AlertTriangle } from "lucide-react";

export default function AlertsPage() {
  const [page, setPage] = useState(1);
  const [isActive, setIsActive] = useState<boolean | undefined>(undefined);
  const [isModalOpen, setIsModalOpen] = useState(false);

  const { data, isLoading, error } = useQuery<PaginatedResponse<Alert>>({
    queryKey: ["alerts", { page, isActive }],
    queryFn: () => alertsApi.getAlerts({ page, is_active: isActive }),
  });

  // Fetch alert statistics
  const { data: stats } = useQuery<AlertStats>({
    queryKey: ["alertStats"],
    queryFn: () => alertsApi.getAlertStats(),
  });

  if (error) {
    return (
      <div className="text-center py-12">
        <p className="text-red-600">Error loading alerts. Please try again.</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <LegalDisclaimer />

      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Alerts</h1>
          <p className="mt-2 text-gray-600">
            Manage your insider trading alerts.
          </p>
        </div>
        <button onClick={() => setIsModalOpen(true)} className="btn btn-primary">Create Alert</button>
      </div>

      {/* Alert Statistics */}
      {stats && (
        <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
          <div className="bg-white p-4 rounded-lg shadow-sm border">
            <div className="flex items-center gap-2">
              <Bell className="h-5 w-5 text-blue-600" />
              <span className="text-sm text-gray-600">Total Alerts</span>
            </div>
            <p className="text-2xl font-bold text-gray-900 mt-1">{stats.total_alerts}</p>
          </div>
          <div className="bg-white p-4 rounded-lg shadow-sm border">
            <div className="flex items-center gap-2">
              <BellRing className="h-5 w-5 text-green-600" />
              <span className="text-sm text-gray-600">Active</span>
            </div>
            <p className="text-2xl font-bold text-green-600 mt-1">{stats.active_alerts}</p>
          </div>
          <div className="bg-white p-4 rounded-lg shadow-sm border">
            <div className="flex items-center gap-2">
              <BellOff className="h-5 w-5 text-gray-400" />
              <span className="text-sm text-gray-600">Inactive</span>
            </div>
            <p className="text-2xl font-bold text-gray-500 mt-1">{stats.inactive_alerts}</p>
          </div>
          <div className="bg-white p-4 rounded-lg shadow-sm border">
            <div className="flex items-center gap-2">
              <Send className="h-5 w-5 text-indigo-600" />
              <span className="text-sm text-gray-600">Sent (24h)</span>
            </div>
            <p className="text-2xl font-bold text-indigo-600 mt-1">{stats.notifications_last_24h}</p>
          </div>
          <div className="bg-white p-4 rounded-lg shadow-sm border">
            <div className="flex items-center gap-2">
              <AlertTriangle className="h-5 w-5 text-red-500" />
              <span className="text-sm text-gray-600">Failed (24h)</span>
            </div>
            <p className="text-2xl font-bold text-red-500 mt-1">{stats.failed_notifications_last_24h}</p>
          </div>
        </div>
      )}

      <div className="card">
        <div className="flex justify-end space-x-4 mb-4">
          <button
            onClick={() => setIsActive(undefined)}
            className={`btn ${
              isActive === undefined ? "btn-primary" : "btn-secondary"
            }`}
          >
            All
          </button>
          <button
            onClick={() => setIsActive(true)}
            className={`btn ${
              isActive === true ? "btn-primary" : "btn-secondary"
            }`}
          >
            Active
          </button>
          <button
            onClick={() => setIsActive(false)}
            className={`btn ${
              isActive === false ? "btn-primary" : "btn-secondary"
            }`}
          >
            Inactive
          </button>
        </div>

        {isLoading ? (
          <div className="flex items-center justify-center h-64">
            <LoadingSpinner />
          </div>
        ) : (
          <>
            <AlertList alerts={data?.items || []} />

            {data && data.pages > 1 && (
              <div className="flex items-center justify-between mt-6 pt-6 border-t">
                <div className="text-sm text-gray-600">
                  Page {data.page} of {data.pages} ({data.total} total alerts)
                </div>
                <div className="flex space-x-2">
                  <button
                    onClick={() => setPage((p) => Math.max(1, p - 1))}
                    disabled={!data.has_prev}
                    className="btn btn-secondary disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    Previous
                  </button>
                  <button
                    onClick={() => setPage((p) => p + 1)}
                    disabled={!data.has_next}
                    className="btn btn-secondary disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    Next
                  </button>
                </div>
              </div>
            )}
          </>
        )}
      </div>
      <CreateAlertModal isOpen={isModalOpen} onClose={() => setIsModalOpen(false)} />
    </div>
  );
}
