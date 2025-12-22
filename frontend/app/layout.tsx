import type { Metadata } from "next";
import "./globals.css";
import { ToastProvider } from "@/components/ui";
import { AuthProvider } from "@/lib/auth";
import { MainLayout } from "@/components/layout";

export const metadata: Metadata = {
  title: "VEETSSUITES",
  description: "Multi-subsite platform for education and professional services",
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
          <ToastProvider>
            <MainLayout>{children}</MainLayout>
          </ToastProvider>
        </AuthProvider>
      </body>
    </html>
  );
}
