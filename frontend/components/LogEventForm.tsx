"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { EventType } from "@/lib/types";
import { createApplicationEvent } from "@/lib/api";

export function LogEventForm({
  applicationId,
  eventTypes,
}: {
  applicationId: number;
  eventTypes: EventType[];
}) {
  const router = useRouter();
  const [open, setOpen] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [eventTypeCode, setEventTypeCode] = useState(eventTypes[0]?.code ?? "");
  const [sender, setSender] = useState("");
  const [subject, setSubject] = useState("");
  const [notes, setNotes] = useState("");

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setSubmitting(true);
    try {
      await createApplicationEvent(applicationId, {
        event_type_code: eventTypeCode,
        sender: sender || undefined,
        subject: subject || undefined,
        notes: notes || undefined,
        source: "manual",
      });
      setSender("");
      setSubject("");
      setNotes("");
      setOpen(false);
      router.refresh();
    } finally {
      setSubmitting(false);
    }
  }

  if (!open) {
    return (
      <button
        onClick={() => setOpen(true)}
        className="rounded-md border border-gray-300 px-3 py-1.5 text-sm font-medium text-gray-700 hover:bg-gray-50"
      >
        + Log an event
      </button>
    );
  }

  return (
    <form onSubmit={handleSubmit} className="rounded-lg border border-gray-200 bg-white p-4">
      <div className="grid gap-3 sm:grid-cols-2">
        <select
          value={eventTypeCode}
          onChange={(e) => setEventTypeCode(e.target.value)}
          className="rounded-md border border-gray-300 px-3 py-2 text-sm sm:col-span-2"
        >
          {eventTypes.map((et) => (
            <option key={et.code} value={et.code}>
              {et.display_name}
            </option>
          ))}
        </select>

        <input
          type="text"
          value={sender}
          onChange={(e) => setSender(e.target.value)}
          placeholder="Sender (optional)"
          className="rounded-md border border-gray-300 px-3 py-2 text-sm"
        />
        <input
          type="text"
          value={subject}
          onChange={(e) => setSubject(e.target.value)}
          placeholder="Subject (optional)"
          className="rounded-md border border-gray-300 px-3 py-2 text-sm"
        />
        <textarea
          value={notes}
          onChange={(e) => setNotes(e.target.value)}
          placeholder="Notes (optional)"
          rows={2}
          className="rounded-md border border-gray-300 px-3 py-2 text-sm sm:col-span-2"
        />
      </div>

      <div className="mt-3 flex gap-2">
        <button
          type="submit"
          disabled={submitting}
          className="rounded-md bg-blue-600 px-3 py-1.5 text-sm font-medium text-white hover:bg-blue-700 disabled:opacity-50"
        >
          {submitting ? "Saving..." : "Save event"}
        </button>
        <button
          type="button"
          onClick={() => setOpen(false)}
          className="rounded-md px-3 py-1.5 text-sm font-medium text-gray-500 hover:text-gray-700"
        >
          Cancel
        </button>
      </div>
    </form>
  );
}
