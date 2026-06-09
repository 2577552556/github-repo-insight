"use client";

import { useState, useCallback, useEffect } from "react";
import type { AnalysisRecordSummary, AnalyzeResponse } from "@/types";
import {
  getAnalysisHistory,
  getAnalysisRecord,
  deleteAnalysisRecord,
} from "@/services/api";

interface UseWorkspaceReturn {
  // History state
  history: AnalysisRecordSummary[];
  isLoadingHistory: boolean;

  // Active record state
  activeRecord: AnalyzeResponse | null;
  activeId: string | null;

  // Operations
  loadHistory: () => void;
  loadRecord: (id: string) => void;
  clearActiveRecord: () => void;
  deleteRecord: (id: string) => Promise<void>;
  refreshHistory: () => void;
}

export function useWorkspace(): UseWorkspaceReturn {
  const [history, setHistory] = useState<AnalysisRecordSummary[]>([]);
  const [isLoadingHistory, setIsLoadingHistory] = useState(false);
  const [activeRecord, setActiveRecord] = useState<AnalyzeResponse | null>(null);
  const [activeId, setActiveId] = useState<string | null>(null);

  // Load history on mount
  const loadHistory = useCallback(() => {
    setIsLoadingHistory(true);
    getAnalysisHistory(0, 50)
      .then((records) => {
        setHistory(records);
      })
      .catch((err) => {
        console.error("Failed to load history:", err);
      })
      .finally(() => {
        setIsLoadingHistory(false);
      });
  }, []);

  // Load a single record from SQLite (fast, no AI re-call)
  const loadRecord = useCallback((id: string) => {
    getAnalysisRecord(id)
      .then((record) => {
        if (record.result_json) {
          setActiveRecord(record.result_json);
          setActiveId(id);
        }
      })
      .catch((err) => {
        console.error("Failed to load record:", err);
      });
  }, []);

  // Clear active record
  const clearActiveRecord = useCallback(() => {
    setActiveRecord(null);
    setActiveId(null);
  }, []);

  // Delete a record
  const deleteRecord = useCallback(async (id: string) => {
    await deleteAnalysisRecord(id);
    setHistory((prev) => prev.filter((r) => r.id !== id));
    if (activeId === id) {
      setActiveRecord(null);
      setActiveId(null);
    }
  }, [activeId]);

  // Refresh history after new analysis
  const refreshHistory = useCallback(() => {
    loadHistory();
  }, [loadHistory]);

  // Initial load
  useEffect(() => {
    loadHistory();
  }, [loadHistory]);

  return {
    history,
    isLoadingHistory,
    activeRecord,
    activeId,
    loadHistory,
    loadRecord,
    clearActiveRecord,
    deleteRecord,
    refreshHistory,
  };
}