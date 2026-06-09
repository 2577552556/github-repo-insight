"use client";

import { useState, useEffect } from "react";
import { GithubIcon, Activity, Settings } from "lucide-react";
import { RepositoryInput } from "@/components/RepositoryInput";
import { AnalysisDashboard } from "@/components/AnalysisDashboard";
import { ErrorState } from "@/components/ErrorState";
import { SettingsDrawer } from "@/components/SettingsDrawer";
import { StreamingProgress } from "@/components/StreamingProgress";
import { HistorySidebar } from "@/components/HistorySidebar";
import { useAnalysis } from "@/hooks/useAnalysis";
import { useSettings } from "@/hooks/useSettings";
import { useWorkspace } from "@/hooks/useWorkspace";
import { Button } from "@/components/ui/button";

export default function Home() {
  const { status, result, error, analyze, reset } = useAnalysis();
  const { openDrawer } = useSettings();
  const {
    history,
    isLoadingHistory,
    activeRecord,
    activeId,
    loadRecord,
    clearActiveRecord,
    deleteRecord,
    refreshHistory,
  } = useWorkspace();

  // Track when a new analysis is saved to refresh history
  const [pendingRefresh, setPendingRefresh] = useState(false);
  // URL input state - lifted from RepositoryInput for control by parent
  const [url, setUrl] = useState("");

  // Handle SSE stream data to detect "saved" event
  useEffect(() => {
    if (status === "success" && pendingRefresh) {
      // Analysis completed and saved, refresh history
      refreshHistory();
      setPendingRefresh(false);
    }
  }, [status, pendingRefresh, refreshHistory]);

  // Handle new analysis - clear active record and start fresh
  const handleNewAnalysis = () => {
    clearActiveRecord();
    reset();
    setUrl(""); // Clear URL input
  };

  // Handle history selection - load from SQLite
  const handleSelectHistory = (id: string) => {
    if (activeId === id) return; // Already selected
    reset(); // Reset current analysis state
    loadRecord(id);
  };

  // Handle delete
  const handleDelete = async (id: string) => {
    if (confirm("确定要删除这条记录吗？")) {
      await deleteRecord(id);
    }
  };

  // Handle analyze - set flag to refresh history on completion
  const handleAnalyze = (url: string) => {
    setPendingRefresh(true);
    analyze(url);
  };

  // Build the progressive result from either activeRecord (from history) or streaming result
  const displayResult = activeRecord
    ? {
        repository: activeRecord.repository,
        languages: activeRecord.languages,
        metrics: activeRecord.metrics,
        healthScore: activeRecord.health_score,
        aiScore: activeRecord.ai_score,
        aiAnalysis: activeRecord.ai_analysis,
      }
    : result;

  const displayStatus = activeRecord
    ? "success"
    : status === "idle" && !activeRecord
    ? "idle"
    : status;

  return (
    <div className="min-h-screen bg-gradient-to-b from-background to-muted/20 flex">
      {/* Left: History Sidebar */}
      <HistorySidebar
        history={history}
        isLoading={isLoadingHistory}
        activeId={activeId}
        onSelect={handleSelectHistory}
        onDelete={handleDelete}
        onNewAnalysis={handleNewAnalysis}
      />

      {/* Right: Main Content */}
      <div className="flex-1 flex flex-col">
        <header className="border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60 sticky top-0 z-10">
          <div className="container mx-auto px-4 py-4 max-w-6xl flex items-center justify-between">
            <div className="flex items-center gap-3">
              <GithubIcon className="w-8 h-8" />
              <h1 className="text-2xl font-bold tracking-tight">GitHub 仓库健康检查</h1>
            </div>
            <Button variant="ghost" size="icon" onClick={openDrawer} title="设置">
              <Settings className="h-5 w-5" />
            </Button>
          </div>
        </header>

        <main className="flex-1 container mx-auto px-4 py-8 max-w-6xl">
          {activeRecord && (
            <div className="mb-4 flex items-center gap-2 text-sm text-muted-foreground">
              <span>查看历史记录:</span>
              <span className="font-medium">{activeRecord.repository.full_name}</span>
              <span className="text-xs px-2 py-0.5 rounded bg-muted">
                {activeRecord.ai_score.grade}级 · {activeRecord.ai_score.score}分
              </span>
            </div>
          )}

          <div className="space-y-8">
            <RepositoryInput
              url={url}
              onUrlChange={setUrl}
              onSubmit={handleAnalyze}
              isLoading={status === "streaming"}
            />

            <div className="mt-8">
              {displayStatus === "idle" && !activeRecord && (
                <div className="text-center py-12 text-muted-foreground">
                  <Activity className="w-12 h-12 mx-auto mb-4 opacity-50" />
                  <p>输入 GitHub 仓库 URL 查看分析结果</p>
                </div>
              )}

              {(displayStatus === "streaming" || displayStatus === "success") && (
                <>
                  <StreamingProgress result={displayResult} isStreaming={displayStatus === "streaming"} />
                  <AnalysisDashboard result={displayResult} isStreaming={displayStatus === "streaming"} />
                </>
              )}

              {displayStatus === "error" && (
                <ErrorState
                  message={error || "发生未知错误"}
                  onRetry={reset}
                />
              )}
            </div>
          </div>
        </main>

        <footer className="mt-auto py-4 border-t text-center text-sm text-muted-foreground">
          <p>使用 Next.js、FastAPI 和 AI 分析构建</p>
        </footer>
      </div>

      <SettingsDrawer />
    </div>
  );
}