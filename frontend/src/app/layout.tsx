
import type { Metadata } from "next";
import { AuthProvider } from "@/components/providers/auth-provider";

import "./globals.css";
import { QueryProvider } from "@/providers/query-provider";

export const metadata: Metadata = {
  title: {
    default: "TerraMind Next",
    template: "%s | TerraMind Next",
  },
  description:
    "Geospatial exploration, data collection and AI-assisted analysis platform.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body>
         <AuthProvider>
             <QueryProvider>{children}</QueryProvider>
         </AuthProvider>
      </body>
    </html>
  );
}
