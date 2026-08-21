import { Job } from "@/lib/types";
import { TrackApplicationButton } from "./TrackApplicationButton";

function formatSalary(min: number | null, max: number | null): string | null {
  if (min === null && max === null) return null;
  const fmt = (n: number) =>
    n >= 1000 ? `$${Math.round(n / 1000)}k` : `$${n}`;
  if (min !== null && max !== null) return `${fmt(min)} – ${fmt(max)}`;
  return fmt((min ?? max) as number);
}

export function JobCard({ job }: { job: Job }) {
  const salary = formatSalary(job.salary_min, job.salary_max);

  return (
    <div className="rounded-lg border border-gray-200 bg-white p-5 shadow-sm transition hover:shadow-md">
      <div className="flex items-start justify-between gap-4">
        <div>
          <h3 className="text-lg font-semibold text-gray-900">{job.title}</h3>
          <p className="text-sm text-gray-600">{job.company.name}</p>
        </div>
        {job.employment_type && (
          <span className="whitespace-nowrap rounded-full bg-blue-50 px-3 py-1 text-xs font-medium text-blue-700">
            {job.employment_type}
          </span>
        )}
      </div>

      <div className="mt-3 flex flex-wrap gap-2 text-sm text-gray-500">
        {job.location && <span>{job.location}</span>}
        {job.work_mode && (
          <>
            <span className="text-gray-300">·</span>
            <span>{job.work_mode}</span>
          </>
        )}
        {salary && (
          <>
            <span className="text-gray-300">·</span>
            <span>{salary}</span>
          </>
        )}
      </div>

      {job.category && (
        <p className="mt-3 inline-block rounded-full bg-gray-100 px-3 py-1 text-xs font-medium text-gray-600">
          {job.category}
        </p>
      )}

      {job.description && (
        <p className="mt-3 line-clamp-2 text-sm text-gray-600">{job.description}</p>
      )}

      <div className="mt-4 flex items-center justify-between gap-3">
        {job.application_url && (
          <a
            href={job.application_url}
            target="_blank"
            rel="noopener noreferrer"
            className="text-sm font-medium text-blue-600 hover:text-blue-800"
          >
            View posting →
          </a>
        )}
        <TrackApplicationButton jobId={job.id} />
      </div>
    </div>
  );
}
