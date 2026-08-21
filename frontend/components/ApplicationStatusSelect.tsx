"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { APPLICATION_STATUSES } from "@/lib/types";
import { updateApplicationStatus } from "@/lib/api";

export function ApplicationStatusSelect({
  applicationId,
  currentStatus,
}: {
  applicationId: number;
  currentStatus: string;
}) {
  const router = useRouter();
  const [updating, setUpdating] = useState(false);

  async function handleChange(e: React.ChangeEvent<HTMLSelectElement>) {
    setUpdating(true);
    try {
      await updateApplicationStatus(applicationId, e.target.value);
      router.refresh();
    } finally {
      setUpdating(false);
    }
  }

  return (
    <select
      defaultValue={currentStatus}
      onChange={handleChange}
      disabled={updating}
      className="rounded-md border border-gray-300 px-3 py-1.5 text-sm font-medium disabled:opacity-50"
    >
      {APPLICATION_STATUSES.map((s) => (
        <option key={s} value={s}>
          {s}
        </option>
      ))}
    </select>
  );
}
