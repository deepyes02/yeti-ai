import type { Metadata } from "next";
import "./globals.scss";

export const metadata: Metadata = {
  title: "Agentic AI",
  description: "Bringing our AI to life",
  keywords: ["seo keyword for this page", "can be more than one"]
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body>
        {children}
      </body>
    </html>
  );
}
