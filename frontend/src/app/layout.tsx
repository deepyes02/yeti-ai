import type { Metadata } from "next";
import { Nunito_Sans } from "next/font/google";
import "./globals.scss";

const nunitoSans = Nunito_Sans({
  subsets: ["latin"],
  display: "swap",
});

export const metadata: Metadata = {
  title: "Yeti | AI Agent",
  description: "Superintelligence from the base of Mount Everest",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" suppressHydrationWarning className={nunitoSans.className}>
      <body style={{ margin: 0 }}>
        {children}
      </body>
    </html>
  );
}
