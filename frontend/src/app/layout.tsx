import type { Metadata } from "next";
import { Lexend_Deca } from "next/font/google";
import "./globals.scss";

const lexendDeca = Lexend_Deca({
  variable: "--font-lexend-deca",
  subsets: ["latin"],
});


export const metadata: Metadata = {
  title: "Agentic AI",
  description: "Bringing our AI to life",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className={`${lexendDeca.variable}`}>
        {children}
      </body>
    </html>
  );
}
