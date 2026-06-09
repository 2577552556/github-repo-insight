"use client";

import { useState, useCallback } from "react";
import type { AnalyzeResponse, AnalysisStatus } from "@/types";
import { analyzeRepository } from "@/services/api";

export type LoadingPhase = "idle" | "loading" | "success" | "error";

interface UseAnalysisReturn {
  status: LoadingPhase;
  result: AnalyzeResponse | null;
  error: string | null;
  analyze: (url: string) => Promise<void>;
  reset: () => void;
}

export function useAnalysis(): UseAnalysisReturn {
  const [status, setStatus] = useState<LoadingPhase>("idle");
  const [result, setResult] = useState<AnalyzeResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  const analyze = useCallback(async (url: string) => {
    setStatus("loading");
    setError(null);
    setResult(null);

    try {
      const data = await analyzeRepository(url);
      setResult(data);
      setStatus("success");
    } catch (err) {
      setError(err instanceof Error ? err.message : "An unexpected error occurred");
      setStatus("error");
    }
  }, []);

  const reset = useCallback(() => {
    setStatus("idle");
    setResult(null);
    setError(null);
  }, []);

  return { status, result, error, analyze, reset };
}