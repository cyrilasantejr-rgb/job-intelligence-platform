"use client";

import { useState } from "react";
import Link from "next/link";
import { Application, APPLICATION_STATUSES } from "@/lib/types";
import { updateApplicationStatus } from "@/lib/api";

const TERMINAL_STATUSES = new Set(["Rejected", "Withdrawn"]);
const PIPELINE_STATUSES = APPLICATION_STATUSES.filter((s) => !TERMINAL_STATUSES.has(s));

function ApplicationCard({
  application,
  onStatusChange,
}: {
  application: Application;
  onStatusChange: (id: number, newStatus: string) => void;
}) {
  const [updating, setUpdating] = useState(false);

  async function handleChange(e: React.ChangeEvent<HTMLSelectElement>) {
    const newStatus = e.target.value;
    setUpdating(true);
    try {
      await updateApplicationStatus(application.id, newStatus);
      onStatusChange(application.id, newStatus);
    } finally {
      setUpdating(false);
    }
  }

  return (
    <div className="rounded-lg border border-gray-200 bg-white p-3 shadow-sm">
      <Link
        href={`/applications/${application.id}`}
        className="text-sm font-semibold text-gray-900 hover:text-blue-600"
      >
        {application.job.title}
      </Link>
      <p className="mt-0.5 text-xs text-gray-500">
        {application.job.company_name}
        {application.job.location ? ` · ${application.job.location}` : ""}
      </p>

      <select
        value={application.current_status}
        onChange={handleChange}
        disabled={updating}
        className="mt-2 w-full rounded-md border border-gray-300 px-2 py-1 text-xs disabled:opacity-50"
      >
        {APPLICATION_STATUSES.map((s) => (
          <option key={s} value={s}>
            {s}
          </option>
        ))}
      </select>
    </div>
  );
}

export function KanbanBoard({ initialApplications }: { initialApplications: Application[] }) {
  const [applications, setApplications] = useState(initialApplications);

  function handleStatusChange(id: number, newStatus: string) {
    setApplications((prev) =>
      prev.map((a) => (a.id === id ? { ...a, current_status: newStatus } : a))
    );
  }

  if (applications.length === 0) {
    return (
      <div className="rounded-lg border border-dashed border-gray-300 bg-white p-10 text-center text-gray-500">
        No tracked applications yet. Go to the job listings and click{" "}
        <span className="font-medium">"+ Add to tracker"</span> on a job you're applying to.
      </div>
    );
  }

  return (
    <div className="flex gap-4 overflow-x-auto pb-4">
      {PIPELINE_STATUSES.map((status) => {
        const columnApps = applications.filter((a) => a.current_status === status);
        return (
          <div key={status} className="w-64 flex-shrink-0">
            <div className="mb-2 flex items-center justify-between px-1">
              <h3 className="text-sm font-semibold text-gray-700">{status}</h3>
              <span className="text-xs text-gray-400">{columnApps.length}</span>
            </div>
            <div className="space-y-2">
              {columnApps.map((app) => (
                <ApplicationCard key={app.id} application={app} onStatusChange={handleStatusChange} />
              ))}
            </div>
          </div>
        );
      })}

      {/* Rejected / Withdrawn shown as a single collapsed column at the end */}
      <div className="w-64 flex-shrink-0">
        <div className="mb-2 flex items-center justify-between px-1">
          <h3 className="text-sm font-semibold text-gray-500">Rejected / Withdrawn</h3>
          <span className="text-xs text-gray-400">
            {applications.filter((a) => TERMINAL_STATUSES.has(a.current_status)).length}
          </span>
        </div>
        <div className="space-y-2">
          {applications
            .filter((a) => TERMINAL_STATUSES.has(a.current_status))
            .map((app) => (
              <ApplicationCard key={app.id} application={app} onStatusChange={handleStatusChange} />
            ))}
        </div>
      </div>
    </div>
  );
}
