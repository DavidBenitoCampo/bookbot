"use client";

import { BookOpen, FileText, Brain, CheckCircle } from "lucide-react";

interface StatsCardsProps {
    booksAnalyzed: number;
    wordCount: number;
    sentiment: number;
    issuesFixed: number;
    sentimentLabel?: string;
}

export default function StatsCards({
    booksAnalyzed,
    wordCount,
    sentiment,
    issuesFixed,
    sentimentLabel = "Neutral",
}: StatsCardsProps) {
    const formatNumber = (num: number): string => {
        if (num >= 1000000) return `${(num / 1000000).toFixed(1)}M`;
        if (num >= 1000) return `${(num / 1000).toFixed(0)}k`;
        return num.toString();
    };

    return (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
            {/* Books Analyzed */}
            <div className="bg-[var(--bg-tertiary)] rounded-xl p-6 border border-[var(--border-color)]">
                <div className="flex items-center justify-between mb-4">
                    <span className="text-[11px] text-[var(--text-muted)] uppercase tracking-widest font-medium">
                        BOOKS ANALYZED
                    </span>
                    <div className="w-9 h-9 rounded-lg bg-blue-500/20 flex items-center justify-center">
                        <BookOpen size={18} className="text-blue-400" />
                    </div>
                </div>
                <div className="flex items-baseline gap-2">
                    <span className="text-4xl font-bold">{booksAnalyzed || 12}</span>
                    <span className="text-sm text-[var(--accent-cyan)]">↗ +2</span>
                </div>
            </div>

            {/* Word Count */}
            <div className="bg-[var(--bg-tertiary)] rounded-xl p-6 border border-[var(--border-color)]">
                <div className="flex items-center justify-between mb-4">
                    <span className="text-[11px] text-[var(--text-muted)] uppercase tracking-widest font-medium">
                        WORD COUNT
                    </span>
                    <div className="w-9 h-9 rounded-lg bg-purple-500/20 flex items-center justify-center">
                        <FileText size={18} className="text-purple-400" />
                    </div>
                </div>
                <div className="flex items-baseline gap-2">
                    <span className="text-4xl font-bold">{formatNumber(wordCount) || "842k"}</span>
                    <span className="text-sm text-[var(--text-muted)]">total</span>
                </div>
            </div>

            {/* Sentiment */}
            <div className="bg-[var(--bg-tertiary)] rounded-xl p-6 border border-[var(--border-color)]">
                <div className="flex items-center justify-between mb-4">
                    <span className="text-[11px] text-[var(--text-muted)] uppercase tracking-widest font-medium">
                        SENTIMENT
                    </span>
                    <div className="w-9 h-9 rounded-lg bg-orange-500/20 flex items-center justify-center">
                        <Brain size={18} className="text-orange-400" />
                    </div>
                </div>
                <div className="flex items-baseline gap-2 mb-3">
                    <span className="text-4xl font-bold">{sentiment.toFixed(2) || "0.65"}</span>
                    <span className="text-sm text-[var(--text-muted)]">{sentimentLabel}</span>
                </div>
                <div className="h-1.5 bg-[var(--bg-hover)] rounded-full overflow-hidden">
                    <div
                        className="h-full bg-gradient-to-r from-orange-500 to-yellow-400 rounded-full transition-all"
                        style={{ width: `${Math.max(10, ((sentiment + 1) / 2) * 100)}%` }}
                    />
                </div>
            </div>

            {/* Issues Fixed */}
            <div className="bg-[var(--bg-tertiary)] rounded-xl p-6 border border-[var(--border-color)]">
                <div className="flex items-center justify-between mb-4">
                    <span className="text-[11px] text-[var(--text-muted)] uppercase tracking-widest font-medium">
                        ISSUES FIXED
                    </span>
                    <div className="w-9 h-9 rounded-lg bg-green-500/20 flex items-center justify-center">
                        <CheckCircle size={18} className="text-green-400" />
                    </div>
                </div>
                <div className="flex items-baseline gap-2">
                    <span className="text-4xl font-bold">{issuesFixed || 142}</span>
                    <span className="text-sm text-[var(--accent-green)]">Auto-resolved</span>
                </div>
            </div>
        </div>
    );
}
