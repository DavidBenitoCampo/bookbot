import type { Metadata } from "next";
import { Plus_Jakarta_Sans } from "next/font/google";
import "./globals.css";
import Sidebar from "@/components/Sidebar";

const plusJakarta = Plus_Jakarta_Sans({
  subsets: ["latin"],
  weight: ["300", "400", "500", "600", "700"],
  variable: "--font-jakarta"
});

export const metadata: Metadata = {
  title: "BookBot - Text Analysis Dashboard",
  description: "Professional text analysis tool for books and documents",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className={plusJakarta.className} suppressHydrationWarning>
        <div className="flex min-h-screen bg-[var(--bg-primary)]">
          <Sidebar />
          <main className="flex-1 min-w-0" style={{ marginLeft: '240px' }}>
            {children}
          </main>
        </div>
      </body>
    </html>
  );
}
