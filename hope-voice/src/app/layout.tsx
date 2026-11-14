import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "HOPE Voice | Emergency Support",
  description: "HOPE emergency voice support and coordination interface.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
