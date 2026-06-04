import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "BUCC AI Assistant",
  description: "Your Babcock University Computer Science academic assistant",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
