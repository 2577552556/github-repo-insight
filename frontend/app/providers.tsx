"use client";

import { ReactNode } from "react";
import { SettingsProvider } from "@/contexts/SettingsContext";

export function Providers({ children }: { children: ReactNode }) {
  return (
    <SettingsProvider>{children}</SettingsProvider>
  );
}