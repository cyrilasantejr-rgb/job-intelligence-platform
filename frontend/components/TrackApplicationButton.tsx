"use client";

import { useState } from "react";
import { createApplication } from "@/lib/api";

export function TrackApplicationButton({ jobId }: { jobId: number }) {
  const [status, setStatus] = useState<"idle" | "loading" | "done" | "error">("idle");

  async function handleClick() {
    setStatus("loading");
    try {
      await createApplication(jobId);
      setStatus("done");
    } catch {
      setStatus("error");
    }
  }

  if (status === "done") {
    return (
      <span className="text-sm font-medium text-green-600">✓ Added to tracker</span>
    );
  }

  return (
    <button
      onClick={handleClick}
      disabled={status === "loading"}
      className="text-sm font-medium text-gray-600 hover:text-gray-900 disabled:opacity-50"
    >
      {status === "loading" ? "Adding..." : status === "error" ? "Try again" : "+ Add to tracker"}
    </button>
  );
}
