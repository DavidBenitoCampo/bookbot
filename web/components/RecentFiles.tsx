"use client";

import { FileText, Download } from "lucide-react";

interface FileItem {
    filename: string;
    date: string;
    size: string;
    status: "analyzed" | "pending" | "error";
}

interface RecentFilesProps {
    files: FileItem[];
}

export default function RecentFiles({ files }: RecentFilesProps) {
    const statusColors = {
        analyzed: "text-[var(--accent-green)]",
        pending: "text-[var(--accent-orange)]",
        error: "text-[var(--accent-red)]",
    };

    const statusLabels = {
        analyzed: "● Analyzed",
        pending: "○ Pending",
        error: "✕ Error",
    };

    return (
        <div className="bg-[var(--bg-tertiary)] rounded-xl border border-[var(--border-color)]">
            <div className="flex items-center justify-between p-6 border-b border-[var(--border-color)]">
                <h3 className="text-lg font-semibold">Recent Files Processed</h3>
                <button className="text-sm text-[var(--accent-cyan)] hover:underline">
                    View All
                </button>
            </div>

            <div className="overflow-x-auto">
                <table className="w-full">
                    <thead>
                        <tr className="border-b border-[var(--border-color)]">
                            <th className="text-left text-xs text-[var(--text-muted)] uppercase tracking-wider px-6 py-3">
                                Filename
                            </th>
                            <th className="text-left text-xs text-[var(--text-muted)] uppercase tracking-wider px-6 py-3">
                                Date
                            </th>
                            <th className="text-left text-xs text-[var(--text-muted)] uppercase tracking-wider px-6 py-3">
                                Size
                            </th>
                            <th className="text-left text-xs text-[var(--text-muted)] uppercase tracking-wider px-6 py-3">
                                Status
                            </th>
                            <th className="text-left text-xs text-[var(--text-muted)] uppercase tracking-wider px-6 py-3">
                                Actions
                            </th>
                        </tr>
                    </thead>
                    <tbody>
                        {files.map((file, index) => (
                            <tr
                                key={index}
                                className="border-b border-[var(--border-color)] hover:bg-[var(--bg-hover)] transition"
                            >
                                <td className="px-6 py-4">
                                    <div className="flex items-center gap-3">
                                        <FileText size={18} className="text-[var(--text-muted)]" />
                                        <span className="font-medium">{file.filename}</span>
                                    </div>
                                </td>
                                <td className="px-6 py-4 text-[var(--text-secondary)]">
                                    {file.date}
                                </td>
                                <td className="px-6 py-4 text-[var(--text-secondary)]">
                                    {file.size}
                                </td>
                                <td className="px-6 py-4">
                                    <span className={statusColors[file.status]}>
                                        {statusLabels[file.status]}
                                    </span>
                                </td>
                                <td className="px-6 py-4">
                                    <button className="p-2 text-[var(--text-muted)] hover:text-[var(--text-primary)] transition">
                                        <Download size={18} />
                                    </button>
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>
        </div>
    );
}
