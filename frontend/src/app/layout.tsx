import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import Link from "next/link";
import "./globals.css";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "AI Hiring Assistant",
  description: "Voice AI screening + people search & reachout",
};

export default function RootLayout({ children }: LayoutProps<"/">) {
  return (
    <html
      lang="en"
      className={`${geistSans.variable} ${geistMono.variable} h-full antialiased`}
    >
      <body className="min-h-full flex flex-col bg-zinc-50">
        <header className="border-b bg-white">
          <nav className="mx-auto flex max-w-5xl items-center gap-6 px-6 py-4">
            <Link href="/" className="font-semibold">
              AI Hiring Assistant
            </Link>
            <Link href="/screening" className="text-sm text-zinc-600 hover:text-zinc-950">
              Screening Call
            </Link>
            <Link href="/reachout" className="text-sm text-zinc-600 hover:text-zinc-950">
              People Search & Reachout
            </Link>
            <Link href="/dashboard" className="text-sm text-zinc-600 hover:text-zinc-950">
              Dashboard
            </Link>
          </nav>
        </header>
        <main className="mx-auto w-full max-w-5xl flex-1 px-6 py-10">{children}</main>
      </body>
    </html>
  );
}
