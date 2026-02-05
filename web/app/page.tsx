"use client";

import { useState } from "react";
import { Play, Circle } from "lucide-react";
import StatsCards from "@/components/StatsCards";
import RawInputStream from "@/components/RawInputStream";
import CharFrequencyChart from "@/components/CharFrequencyChart";
import RecentFiles from "@/components/RecentFiles";
import FileUpload from "@/components/FileUpload";

interface AnalysisResult {
  filename: string;
  title: string;
  statistics: {
    word_count: number;
    unique_word_count: number;
    character_count: number;
    sentence_count: number;
    paragraph_count: number;
    average_word_length: number;
    average_sentence_length: number;
    vocabulary_richness: number;
    reading_time_minutes: number;
  };
  char_frequency: Record<string, number>;
  top_words: [string, number][];
  sentiment?: {
    overall: {
      polarity: number;
      subjectivity: number;
      label: string;
      positive: number;
      negative: number;
      neutral: number;
    };
  };
  file_size?: number;
  analyzed_at?: string;
}

// Sample data matching reference design
const sampleCharFrequency: Record<string, number> = {
  'A': 8500, 'B': 2100, 'C': 3200, 'D': 4800, 'E': 13500,
  'F': 2800, 'G': 2400, 'H': 7200, 'I': 7800, 'J': 300,
  'K': 900, 'L': 4500, 'M': 2700, 'N': 7200, 'O': 8100
};

const sampleFiles = [
  { filename: "Hamlet.txt", date: "Oct 24, 2023", size: "182 KB", status: "analyzed" as const },
  { filename: "Macbeth.txt", date: "Oct 23, 2023", size: "140 KB", status: "analyzed" as const },
];

export default function Dashboard() {
  const [result, setResult] = useState<AnalysisResult | null>(null);
  const [files, setFiles] = useState(sampleFiles);
  const [showUploadModal, setShowUploadModal] = useState(false);

  const handleAnalysisComplete = (data: AnalysisResult) => {
    setResult(data);

    const newFile = {
      filename: data.filename,
      date: new Date().toLocaleDateString("en-US", {
        month: "short",
        day: "numeric",
        year: "numeric"
      }),
      size: data.file_size ? `${Math.round(data.file_size / 1024)} KB` : "N/A",
      status: "analyzed" as const,
    };
    setFiles(prev => [newFile, ...prev.slice(0, 9)]);
    setShowUploadModal(false);
  };

  return (
    <div className="min-h-screen bg-[var(--bg-primary)]">
      {/* Header */}
      <header className="sticky top-0 z-10 bg-[var(--bg-primary)]/95 backdrop-blur border-b border-[var(--border-color)] px-6 py-3">
        <div className="flex items-center justify-between">
          <nav className="flex items-center gap-2 text-sm">
            <span className="text-[var(--text-muted)]">Projects</span>
            <span className="text-[var(--text-muted)]">/</span>
            <span className="text-[var(--text-muted)]">Shakespeare Collection</span>
            <span className="text-[var(--text-muted)]">/</span>
            <span className="text-[var(--text-primary)] font-medium">Overview</span>
          </nav>

          <div className="flex items-center gap-4">
            <div className="flex items-center gap-2 text-sm">
              <Circle size={8} className="fill-[#3fb950] text-[#3fb950]" />
              <span className="text-[var(--text-muted)]">System Online</span>
            </div>
            <button
              onClick={() => setShowUploadModal(true)}
              className="flex items-center gap-2 px-4 py-2 bg-[#58a6ff] text-black font-semibold rounded-lg hover:bg-[#79c0ff] transition-colors"
            >
              <Play size={14} fill="currentColor" />
              Start Analysis
            </button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <div className="pl-16 pr-12 pt-10 pb-16">
        {/* Page Title */}
        <div className="mb-8">
          <h1 className="text-[28px] font-bold tracking-tight">Project Overview</h1>
          <p className="text-[var(--text-muted)] text-sm mt-1">
            Real-time analysis of input streams and processed metrics.
          </p>
        </div>

        {/* Top Section: Stream + Stats in row */}
        <div className="grid grid-cols-1 xl:grid-cols-[360px_1fr] gap-10 mb-20">
          <RawInputStream
            title="Raw Input Stream"
            content=""
            issuesCount={3}
          />
          <StatsCards
            booksAnalyzed={result ? files.length : 12}
            wordCount={result?.statistics.word_count || 842000}
            sentiment={result?.sentiment?.overall.polarity || 0.65}
            issuesFixed={142}
            sentimentLabel={result?.sentiment?.overall.label || "Neutral+"}
          />
        </div>

        {/* Chart Section */}
        <div className="mb-16">
          <CharFrequencyChart data={result?.char_frequency || sampleCharFrequency} />
        </div>

        {/* Recent Files */}
        <RecentFiles files={files} />
      </div>

      {/* Upload Modal */}
      {showUploadModal && (
        <div className="fixed inset-0 bg-black/70 flex items-center justify-center z-50">
          <div className="bg-[var(--bg-secondary)] rounded-2xl p-8 max-w-xl w-full mx-4 border border-[var(--border-color)]">
            <h2 className="text-xl font-bold mb-4">Upload File for Analysis</h2>
            <FileUpload onAnalysisComplete={handleAnalysisComplete} />
            <button
              onClick={() => setShowUploadModal(false)}
              className="mt-4 w-full py-2 text-[var(--text-muted)] hover:text-[var(--text-primary)] transition"
            >
              Cancel
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
