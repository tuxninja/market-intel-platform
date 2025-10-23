/**
 * Root Layout Component
 */

import type { Metadata } from "next";
import "./globals.css";
import Header from "@/components/layout/Header";

export const metadata: Metadata = {
  title: "TradeTheHype",
  description: "AI-powered trading signals from breaking news",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="bg-background min-h-screen">
        <Header />
        <main>{children}</main>
      </body>
    </html>
  );
}
