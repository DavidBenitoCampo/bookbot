"use client";

import { useState } from "react";
import Link from "next/link";
import {
    BookOpen,
    LayoutDashboard,
    Search,
    FileText,
    Settings,
    ChevronDown
} from "lucide-react";

interface FileItem {
    name: string;
    status: "raw" | "analyzed";
}

export default function Sidebar() {
    const [files, setFiles] = useState<FileItem[]>([
        { name: "Hamlet.txt", status: "raw" },
        { name: "Macbeth.txt", status: "analyzed" },
        { name: "Romeo.txt", status: "analyzed" },
        { name: "Othello.txt", status: "analyzed" },
    ]);

    return (
        <aside className="fixed left-0 top-0 h-screen w-[240px] bg-[#0a0d12] border-r border-[var(--border-color)] flex flex-col shadow-xl shadow-black/20">
            {/* Logo */}
            <div className="p-4 flex items-center gap-2">
                <div className="w-8 h-8 bg-[var(--accent-cyan)] rounded flex items-center justify-center font-bold text-black">
                    B
                </div>
                <span className="text-lg font-semibold">BookBot</span>
            </div>

            {/* Project Selector */}
            <div className="px-3 mb-4">
                <div className="text-xs text-[var(--text-muted)] uppercase tracking-wider mb-2">
                    Project
                </div>
                <button className="w-full flex items-center gap-2 p-2 rounded-lg bg-[var(--bg-tertiary)] hover:bg-[var(--bg-hover)] transition">
                    <div className="w-8 h-8 bg-gradient-to-br from-purple-500 to-blue-500 rounded-lg flex items-center justify-center">
                        <BookOpen size={16} />
                    </div>
                    <div className="flex-1 text-left">
                        <div className="text-sm font-medium">BookBot</div>
                        <div className="text-xs text-[var(--accent-green)]">v1.0.0 • Active</div>
                    </div>
                    <ChevronDown size={16} className="text-[var(--text-muted)]" />
                </button>
            </div>

            {/* Navigation */}
            <div className="px-3 mb-4">
                <div className="text-xs text-[var(--text-muted)] uppercase tracking-wider mb-2">
                    Navigation
                </div>
                <nav className="space-y-1">
                    <Link
                        href="/"
                        className="flex items-center gap-3 px-3 py-2 rounded-lg bg-[var(--accent-cyan)]/10 text-[var(--accent-cyan)]"
                    >
                        <LayoutDashboard size={18} />
                        <span className="text-sm">Overview</span>
                    </Link>
                    <Link
                        href="/analyze"
                        className="flex items-center gap-3 px-3 py-2 rounded-lg text-[var(--text-secondary)] hover:bg-[var(--bg-hover)] transition"
                    >
                        <Search size={18} />
                        <span className="text-sm">Deep Analysis</span>
                    </Link>
                </nav>
            </div>

            {/* Source Files */}
            <div className="px-3 flex-1 overflow-y-auto">
                <div className="text-xs text-[var(--text-muted)] uppercase tracking-wider mb-2">
                    Source Files
                </div>
                <div className="space-y-1">
                    {files.map((file) => (
                        <button
                            key={file.name}
                            className="w-full flex items-center gap-2 px-3 py-2 rounded-lg text-[var(--text-secondary)] hover:bg-[var(--bg-hover)] transition text-left"
                        >
                            <FileText size={16} />
                            <span className="text-sm flex-1">{file.name}</span>
                            {file.status === "raw" && (
                                <span className="text-[10px] px-1.5 py-0.5 bg-[var(--bg-hover)] rounded text-[var(--text-muted)]">
                                    RAW
                                </span>
                            )}
                        </button>
                    ))}
                </div>
            </div>

            {/* Settings */}
            <div className="p-3 border-t border-[var(--border-color)]">
                <button className="w-full flex items-center gap-3 px-3 py-2 rounded-lg text-[var(--text-secondary)] hover:bg-[var(--bg-hover)] transition">
                    <Settings size={18} />
                    <span className="text-sm">Settings</span>
                </button>
            </div>
        </aside>
    );
}
