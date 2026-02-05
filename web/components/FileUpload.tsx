"use client";

import { useState, useCallback } from "react";
import { useDropzone } from "react-dropzone";
import { Upload, FileText, Loader2 } from "lucide-react";

interface UploadResult {
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
}

interface FileUploadProps {
    onAnalysisComplete: (result: UploadResult) => void;
}

export default function FileUpload({ onAnalysisComplete }: FileUploadProps) {
    const [isUploading, setIsUploading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const onDrop = useCallback(async (acceptedFiles: File[]) => {
        if (acceptedFiles.length === 0) return;

        const file = acceptedFiles[0];
        setIsUploading(true);
        setError(null);

        try {
            const formData = new FormData();
            formData.append("file", file);
            formData.append("include_sentiment", "true");

            const response = await fetch("/api/analyze", {
                method: "POST",
                body: formData,
            });

            if (!response.ok) {
                const err = await response.json();
                throw new Error(err.detail || "Analysis failed");
            }

            const result = await response.json();
            onAnalysisComplete(result);
        } catch (err) {
            setError(err instanceof Error ? err.message : "Upload failed");
        } finally {
            setIsUploading(false);
        }
    }, [onAnalysisComplete]);

    const { getRootProps, getInputProps, isDragActive } = useDropzone({
        onDrop,
        accept: {
            "text/plain": [".txt", ".md"],
            "application/pdf": [".pdf"],
            "application/epub+zip": [".epub"],
        },
        maxFiles: 1,
    });

    return (
        <div
            {...getRootProps()}
            className={`
        relative border-2 border-dashed rounded-xl p-8 text-center cursor-pointer transition-all
        ${isDragActive
                    ? "border-[var(--accent-cyan)] bg-[var(--accent-cyan)]/10"
                    : "border-[var(--border-color)] hover:border-[var(--accent-cyan)]/50 hover:bg-[var(--bg-hover)]/50"
                }
        ${isUploading ? "pointer-events-none opacity-60" : ""}
      `}
        >
            <input {...getInputProps()} />

            <div className="flex flex-col items-center gap-4">
                {isUploading ? (
                    <Loader2 size={48} className="text-[var(--accent-cyan)] animate-spin" />
                ) : (
                    <Upload size={48} className="text-[var(--text-muted)]" />
                )}

                <div>
                    <p className="text-lg font-medium">
                        {isUploading
                            ? "Analyzing..."
                            : isDragActive
                                ? "Drop file here"
                                : "Drop a file or click to upload"
                        }
                    </p>
                    <p className="text-sm text-[var(--text-muted)] mt-1">
                        Supports TXT, PDF, EPUB files
                    </p>
                </div>
            </div>

            {error && (
                <p className="mt-4 text-sm text-[var(--accent-red)]">{error}</p>
            )}
        </div>
    );
}
