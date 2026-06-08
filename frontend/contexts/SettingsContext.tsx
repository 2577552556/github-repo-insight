"use client";

import { createContext, useContext, useState, useCallback, ReactNode } from "react";
import type { SettingsStatus } from "@/types";
import { getSettings, updateSettings } from "@/services/settingsApi";

interface SettingsContextValue {
  isOpen: boolean;
  settings: SettingsStatus | null;
  loading: boolean;
  error: string | null;
  openDrawer: () => void;
  closeDrawer: () => void;
  loadSettings: () => Promise<void>;
  saveSettings: (deepseekKey: string, githubToken: string) => Promise<void>;
}

const SettingsContext = createContext<SettingsContextValue | null>(null);

export function SettingsProvider({ children }: { children: ReactNode }) {
  const [isOpen, setIsOpen] = useState(false);
  const [settings, setSettings] = useState<SettingsStatus | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const openDrawer = useCallback(() => {
    setIsOpen(true);
  }, []);

  const closeDrawer = useCallback(() => {
    setIsOpen(false);
    setError(null);
  }, []);

  const loadSettings = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await getSettings();
      setSettings(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load settings");
    } finally {
      setLoading(false);
    }
  }, []);

  const saveSettings = useCallback(async (deepseekKey: string, githubToken: string) => {
    setLoading(true);
    setError(null);
    try {
      const data = await updateSettings({
        deepseek_api_key: deepseekKey || null,
        github_token: githubToken || null,
      });
      setSettings(data);
      setIsOpen(false);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to save settings");
    } finally {
      setLoading(false);
    }
  }, []);

  return (
    <SettingsContext.Provider
      value={{
        isOpen,
        settings,
        loading,
        error,
        openDrawer,
        closeDrawer,
        loadSettings,
        saveSettings,
      }}
    >
      {children}
    </SettingsContext.Provider>
  );
}

export function useSettings(): SettingsContextValue {
  const context = useContext(SettingsContext);
  if (!context) {
    throw new Error("useSettings must be used within SettingsProvider");
  }
  return context;
}