import { fetchApplications } from "@/lib/api";
import { KanbanBoard } from "@/components/KanbanBoard";

export default async function ApplicationsPage() {
  const applications = await fetchApplications();

  return (
    <main className="mx-auto max-w-7xl px-4 py-10">
      <header className="mb-8">
        <h1 className="text-2xl font-bold text-gray-900">Application Tracker</h1>
        <p className="mt-1 text-sm text-gray-600">
          {applications.length} tracked application{applications.length === 1 ? "" : "s"}
        </p>
      </header>

      <KanbanBoard initialApplications={applications} />
    </main>
  );
}
