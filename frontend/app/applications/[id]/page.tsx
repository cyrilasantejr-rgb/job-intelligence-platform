import Link from "next/link";
import { fetchApplication, fetchApplicationEvents, fetchEventTypes } from "@/lib/api";
import { EventTimeline } from "@/components/EventTimeline";
import { LogEventForm } from "@/components/LogEventForm";
import { ApplicationStatusSelect } from "@/components/ApplicationStatusSelect";

export default async function ApplicationDetailPage({ params }: { params: { id: string } }) {
  const applicationId = Number(params.id);

  const [application, events, eventTypes] = await Promise.all([
    fetchApplication(applicationId),
    fetchApplicationEvents(applicationId),
    fetchEventTypes(),
  ]);

  return (
    <main className="mx-auto max-w-3xl px-4 py-10">
      <Link href="/applications" className="text-sm text-gray-500 hover:text-gray-700">
        ← Back to tracker
      </Link>

      <header className="mt-3 mb-8 flex items-start justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">{application.job.title}</h1>
          <p className="mt-1 text-sm text-gray-600">
            {application.job.company_name}
            {application.job.location ? ` · ${application.job.location}` : ""}
          </p>
        </div>
        <ApplicationStatusSelect
          applicationId={application.id}
          currentStatus={application.current_status}
        />
      </header>

      <div className="mb-6">
        <LogEventForm applicationId={application.id} eventTypes={eventTypes} />
      </div>

      <h2 className="mb-3 text-sm font-semibold text-gray-700">Timeline</h2>
      <EventTimeline events={events} />
    </main>
  );
}
