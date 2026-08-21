import Link from "next/link";
import { fetchJobs } from "@/lib/api";
import { JobCard } from "@/components/JobCard";
import { JobFilters } from "@/components/JobFilters";
import { Pagination } from "@/components/Pagination";

interface PageProps {
  searchParams: {
    category?: string;
    employment_type?: string;
    work_mode?: string;
    location?: string;
    search?: string;
    page?: string;
  };
}

export default async function HomePage({ searchParams }: PageProps) {
  const page = Number(searchParams.page ?? "1");

  const data = await fetchJobs({
    category: searchParams.category,
    employment_type: searchParams.employment_type,
    work_mode: searchParams.work_mode,
    location: searchParams.location,
    search: searchParams.search,
    page,
  });

  const totalPages = Math.max(1, Math.ceil(data.total / data.page_size));

  return (
    <main className="mx-auto max-w-5xl px-4 py-10">
      <header className="mb-8 flex items-start justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">
            AI Job Intelligence &amp; Application Tracker
          </h1>
          <p className="mt-1 text-sm text-gray-600">
            {data.total} internship{data.total === 1 ? "" : "s"} and new-grad roles
          </p>
        </div>
        <Link
          href="/applications"
          className="whitespace-nowrap rounded-md border border-gray-300 px-3 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50"
        >
          My Tracker →
        </Link>
      </header>

      <div className="mb-6">
        <JobFilters />
      </div>

      {data.items.length === 0 ? (
        <div className="rounded-lg border border-dashed border-gray-300 bg-white p-10 text-center text-gray-500">
          No jobs match these filters.
        </div>
      ) : (
        <div className="grid gap-4 sm:grid-cols-2">
          {data.items.map((job) => (
            <JobCard key={job.id} job={job} />
          ))}
        </div>
      )}

      <Pagination currentPage={data.page} totalPages={totalPages} />
    </main>
  );
}
