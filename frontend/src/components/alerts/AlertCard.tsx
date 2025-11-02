import { useState } from "react";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { alertsApi } from "../../api/alerts";
import { Alert } from "../../types";
import EditAlertModal from "./EditAlertModal";

interface AlertCardProps {
  alert: Alert;
}

export default function AlertCard({ alert }: AlertCardProps) {
  const queryClient = useQueryClient();
  const [isEditModalOpen, setIsEditModalOpen] = useState(false);

  const deleteMutation = useMutation({
    mutationFn: () => alertsApi.deleteAlert(alert.id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["alerts"] });
    },
  });

  const handleDelete = () => {
    if (window.confirm("Are you sure you want to delete this alert?")) {
      deleteMutation.mutate();
    }
  };

  return (
    <>
      <div className="card">
        <div className="flex justify-between items-center">
          <div>
            <h2 className="text-lg font-semibold">{alert.name}</h2>
            <p className="text-sm text-gray-500">{alert.alert_type}</p>
          </div>
          <div className="flex items-center space-x-4">
            <span
              className={`badge ${
                alert.is_active ? "badge-success" : "badge-error"
              }`}
            >
              {alert.is_active ? "Active" : "Inactive"}
            </span>
            <button
              onClick={() => setIsEditModalOpen(true)}
              className="btn btn-secondary"
            >
              Edit
            </button>
            <button
              onClick={handleDelete}
              className="btn btn-danger"
              disabled={deleteMutation.isPending}
            >
              {deleteMutation.isPending ? "Deleting..." : "Delete"}
            </button>
          </div>
        </div>
      </div>
      <EditAlertModal
        isOpen={isEditModalOpen}
        onClose={() => setIsEditModalOpen(false)}
        alert={alert}
      />
    </>
  );
}
