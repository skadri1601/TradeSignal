import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { alertsApi } from "../api/alerts";
import LoadingSpinner from "../components/common/LoadingSpinner";
import { Alert, PaginatedResponse } from "../types";
import AlertList from "../components/alerts/AlertList";
import CreateAlertModal from "../components/alerts/CreateAlertModal";

export default function AlertsPage() {
  const [page, setPage] = useState(1);
  const [isActive, setIsActive] = useState<boolean | undefined>(undefined);
  const [isModalOpen, setIsModalOpen] = useState(false);

  const { data, isLoading, error } = useQuery<PaginatedResponse<Alert>>({
    queryKey: ["alerts", { page, isActive }],
    queryFn: () => alertsApi.getAlerts({ page, is_active: isActive }),
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
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Alerts</h1>
          <p className="mt-2 text-gray-600">
            Manage your insider trading alerts.
          </p>
        </div>
        <button onClick={() => setIsModalOpen(true)} className="btn btn-primary">Create Alert</button>
      </div>

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
