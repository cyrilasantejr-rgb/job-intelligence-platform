"use client";

import { useRouter, useSearchParams } from "next/navigation";
import { useState } from "react";
import { CATEGORIES, EMPLOYMENT_TYPES, WORK_MODES } from "@/lib/types";

export function JobFilters() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const [searchInput, setSearchInput] = useState(searchParams.get("search") ?? "");

  function updateParam(key: string, value: string) {
    const params = new URLSearchParams(searchParams.toString());
    if (value) {
      params.set(key, value);
    } else {
      params.delete(key);
    }
    params.delete("page");
    router.push(`/?${params.toString()}`);
  }

  function handleSearchSubmit(e: React.FormEvent) {
    e.preventDefault();
    updateParam("search", searchInput);
  }

  function clearAll() {
    setSearchInput("");
    router.push("/");
  }

  const hasActiveFilters = Array.from(searchParams.keys()).some((k) => k !== "page");

  return (
    <div className="flex flex-wrap items-center gap-3 rounded-lg border border-gray-200 bg-white p-4">
      <form onSubmit={handleSearchSubmit} className="flex-1 min-w-[200px]">
        <input
          type="text"
          value={searchInput}
          onChange={(e) => setSearchInput(e.target.value)}
          placeholder="Search title or description..."
          className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none"
        />
      </form>

      <select
        value={searchParams.get("category") ?? ""}
        onChange={(e) => updateParam("category", e.target.value)}
        className="rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none"
      >
        <option value="">All categories</option>
        {CATEGORIES.map((c) => (
          <option key={c} value={c}>
            {c}
          </option>
        ))}
      </select>

      <select
        value={searchParams.get("employment_type") ?? ""}
        onChange={(e) => updateParam("employment_type", e.target.value)}
        className="rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none"
      >
        <option value="">Internship or New Grad</option>
        {EMPLOYMENT_TYPES.map((t) => (
          <option key={t} value={t}>
            {t}
          </option>
        ))}
      </select>

      <select
        value={searchParams.get("work_mode") ?? ""}
        onChange={(e) => updateParam("work_mode", e.target.value)}
        className="rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none"
      >
        <option value="">Any work mode</option>
        {WORK_MODES.map((w) => (
          <option key={w} value={w}>
            {w}
          </option>
        ))}
      </select>

      {hasActiveFilters && (
        <button
          onClick={clearAll}
          className="text-sm font-medium text-gray-500 hover:text-gray-700"
        >
          Clear filters
        </button>
      )}
    </div>
  );
}
