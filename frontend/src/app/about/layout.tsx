import type { Metadata } from "next";
import "../globals.scss";

export const metadata: Metadata = {
  title: "About Agentic AI",
  description: "Bringing our AI to life",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body>
        {children}
      </body>
    </html>
  );
}
