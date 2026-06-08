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
            <h1 className="text-4xl font-bold tracking-tight">GitHub 仓库健康检查</h1>
          </div>
          <p className="text-muted-foreground text-lg max-w-2xl mx-auto">
            输入 GitHub 仓库 URL，分析其健康状况、指标和 AI 评估
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
                <p>输入 GitHub 仓库 URL 查看分析结果</p>
              </div>
            )}

            {status === "loading" && <LoadingState />}

            {status === "error" && (
              <ErrorState
                message={error || "发生未知错误"}
                onRetry={reset}
              />
            )}

            {status === "success" && result && (
              <AnalysisDashboard result={result} />
            )}
          </div>
        </main>

        <footer className="mt-16 pt-8 border-t text-center text-sm text-muted-foreground">
          <p>使用 Next.js、FastAPI 和 AI 分析构建</p>
        </footer>
      </div>
    </div>
  );
}