"use client";

import {
    BarChart,
    Bar,
    XAxis,
    YAxis,
    Tooltip,
    ResponsiveContainer,
    CartesianGrid
} from "recharts";

interface CharFrequencyChartProps {
    data: Record<string, number>;
}

export default function CharFrequencyChart({ data }: CharFrequencyChartProps) {
    // Convert to array and take top 15
    const chartData = Object.entries(data)
        .slice(0, 15)
        .map(([char, count]) => ({
            char: char.toUpperCase(),
            count,
        }));

    return (
        <div className="bg-[var(--bg-tertiary)] rounded-xl p-6 border border-[var(--border-color)]">
            <div className="flex items-center justify-between mb-4">
                <div>
                    <h3 className="text-lg font-semibold">Character Frequency Distribution</h3>
                    <p className="text-sm text-[var(--text-muted)]">Letter occurrence across all analyzed texts</p>
                </div>
                <select className="bg-[var(--bg-hover)] border border-[var(--border-color)] rounded-lg px-3 py-1.5 text-sm">
                    <option>A-Z</option>
                </select>
            </div>

            <div className="h-[300px]">
                <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={chartData} margin={{ top: 10, right: 10, left: -10, bottom: 0 }}>
                        <CartesianGrid strokeDasharray="3 3" stroke="var(--border-color)" vertical={false} />
                        <XAxis
                            dataKey="char"
                            axisLine={false}
                            tickLine={false}
                            tick={{ fill: 'var(--text-muted)', fontSize: 12 }}
                        />
                        <YAxis
                            axisLine={false}
                            tickLine={false}
                            tick={{ fill: 'var(--text-muted)', fontSize: 12 }}
                        />
                        <Tooltip
                            contentStyle={{
                                backgroundColor: 'var(--bg-secondary)',
                                border: '1px solid var(--border-color)',
                                borderRadius: '8px',
                                color: 'var(--text-primary)',
                            }}
                        />
                        <Bar
                            dataKey="count"
                            fill="#79c0ff"
                            radius={[4, 4, 0, 0]}
                            maxBarSize={40}
                        />
                    </BarChart>
                </ResponsiveContainer>
            </div>
        </div>
    );
}
