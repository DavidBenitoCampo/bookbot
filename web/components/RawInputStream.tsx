"use client";

import { Code } from "lucide-react";

interface RawInputStreamProps {
    title: string;
    content: string;
    issuesCount?: number;
}

export default function RawInputStream({
    title,
    content,
    issuesCount = 3
}: RawInputStreamProps) {
    // Sample content matching the reference design
    const sampleLines = [
        { num: 1, text: '// Importing source text...', type: 'comment' },
        { num: 2, text: 'const source = "Hamlet_v1.txt";', type: 'code' },
        { num: 3, text: '', type: 'empty' },
        { num: 4, text: '[STREAM_START]', type: 'keyword' },
        { num: 5, text: 'To be, or not to be, that is the q...', type: 'text' },
        { num: 6, text: '[ERR_Encoding]', type: 'error' },
        { num: 7, text: "Whether 'tis nobler in the mind to...", type: 'text' },
        { num: 8, text: 'suffer the slings and arrows of...', type: 'text' },
        { num: 9, text: '[WARN_Whitespace] outrageous', type: 'warning' },
        { num: 10, text: 'fortune,', type: 'warning-cont' },
        { num: 11, text: 'Or to take arms against a sea of...', type: 'text' },
        { num: 12, text: '', type: 'empty' },
        { num: 13, text: '// Parsing metadata', type: 'comment' },
        { num: 14, text: 'ACT: III', type: 'meta' },
        { num: 15, text: 'SCENE: 1', type: 'meta-value' },
        { num: 16, text: '[ERR_Unexpected_EOF]', type: 'error' },
    ];

    const getLineStyle = (type: string) => {
        switch (type) {
            case 'comment':
                return 'text-[var(--text-muted)]';
            case 'error':
                return 'text-[#f85149] bg-[#f85149]/10 px-1 rounded';
            case 'warning':
            case 'warning-cont':
                return 'text-[#d29922] bg-[#d29922]/10 px-1 rounded';
            case 'keyword':
                return 'text-[var(--accent-cyan)]';
            case 'meta':
                return 'text-[var(--accent-purple)]';
            case 'meta-value':
                return 'text-[var(--accent-cyan)]';
            default:
                return 'text-[var(--text-secondary)]';
        }
    };

    return (
        <div className="bg-[var(--bg-tertiary)] rounded-xl border border-[var(--border-color)] overflow-hidden h-full">
            <div className="flex items-center gap-3 px-4 py-3 border-b border-[var(--border-color)]">
                <Code size={16} className="text-[var(--text-muted)]" />
                <span className="font-medium text-sm">Raw Input Stream</span>
                {issuesCount > 0 && (
                    <span className="px-2.5 py-1 bg-[#d29922]/20 text-[#d29922] text-[10px] font-semibold rounded-full uppercase tracking-wider">
                        {issuesCount} ISSUES FOUND
                    </span>
                )}
            </div>

            <div className="p-4 font-mono text-[13px] overflow-x-auto max-h-[380px] overflow-y-auto leading-relaxed">
                {sampleLines.map((line) => (
                    <div key={line.num} className="flex hover:bg-[var(--bg-hover)]/50 px-2 py-0.5 rounded">
                        <span className="text-[var(--text-muted)] select-none w-8 text-right mr-4 shrink-0">
                            {line.num}
                        </span>
                        <span className={getLineStyle(line.type)}>
                            {line.text || '\u00A0'}
                        </span>
                    </div>
                ))}
            </div>
        </div>
    );
}
