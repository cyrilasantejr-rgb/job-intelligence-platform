import { ApplicationEvent } from "@/lib/types";

function formatDateTime(iso: string): string {
  return new Date(iso).toLocaleString(undefined, {
    month: "short",
    day: "numeric",
    hour: "numeric",
    minute: "2-digit",
  });
}

export function EventTimeline({ events }: { events: ApplicationEvent[] }) {
  if (events.length === 0) {
    return (
      <div className="rounded-lg border border-dashed border-gray-300 bg-white p-6 text-center text-sm text-gray-500">
        No events logged yet.
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {events.map((event) => (
        <div key={event.id} className="flex gap-3">
          <div className="mt-1.5 h-2 w-2 flex-shrink-0 rounded-full bg-blue-500" />
          <div className="flex-1 rounded-lg border border-gray-200 bg-white p-3">
            <div className="flex items-start justify-between gap-2">
              <p className="text-sm font-medium text-gray-900">{event.event_type.display_name}</p>
              <p className="whitespace-nowrap text-xs text-gray-400">
                {formatDateTime(event.event_date)}
              </p>
            </div>

            {(event.sender || event.subject) && (
              <p className="mt-1 text-xs text-gray-500">
                {event.sender && <span>{event.sender}</span>}
                {event.sender && event.subject && <span> · </span>}
                {event.subject && <span>{event.subject}</span>}
              </p>
            )}

            {event.notes && <p className="mt-1.5 text-sm text-gray-600">{event.notes}</p>}

            {event.next_action && (
              <p className="mt-1.5 text-xs font-medium text-amber-700">
                Next: {event.next_action}
              </p>
            )}
          </div>
        </div>
      ))}
    </div>
  );
}
