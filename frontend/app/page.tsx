"use client";

import { GithubIcon, Activity } from "lucide-react";
import { RepositoryInput } from "@/components/RepositoryInput";
import { AnalysisDashboard } from "@/components/AnalysisDashboard";
import { LoadingState } from "@/components/LoadingState";
import { ErrorState } from "@/components/ErrorState";
import { useAnalysis } from "@/hooks/useAnalysis";

export default function Home() {
  const { status, result, error, analyze, reset } = useAnalysis();

  return (
    <div className="min-h-screen bg-gradient-to-b from-background to-muted/20">
      <div className="container mx-auto px-4 py-12 max-w-6xl">
        <header className="text-center mb-12 space-y-4">
          <div className="flex items-center justify-center gap-3">
            <GithubIcon className="w-10 h-10" />
            <h1 className="text-4xl font-bold tracking-tight">GitHub Repository Health Check</h1>
          </div>
          <p className="text-muted-foreground text-lg max-w-2xl mx-auto">
            Enter a GitHub repository URL to analyze its health, metrics, and get AI-powered evaluation
          </p>
        </header>

        <main className="space-y-8">
          <RepositoryInput
            onSubmit={analyze}
            isLoading={status === "loading"}
          />

          <div className="mt-8">
            {status === "idle" && (
              <div className="text-center py-12 text-muted-foreground">
                <Activity className="w-12 h-12 mx-auto mb-4 opacity-50" />
                <p>Enter a GitHub repository URL to see the analysis</p>
              </div>
            )}

            {status === "loading" && <LoadingState />}

            {status === "error" && (
              <ErrorState
                message={error || "An unexpected error occurred"}
                onRetry={reset}
              />
            )}

            {status === "success" && result && (
              <AnalysisDashboard result={result} />
            )}
          </div>
        </main>

        <footer className="mt-16 pt-8 border-t text-center text-sm text-muted-foreground">
          <p>Built with Next.js, FastAPI, and AI-powered analysis</p>
        </footer>
      </div>
    </div>
  );
}