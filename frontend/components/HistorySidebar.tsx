"use client";

import type { AnalysisRecordSummary } from "@/types";
import { HistoryItem } from "@/components/HistoryItem";
import { Loader2, History } from "lucide-react";

interface HistorySidebarProps {
  history: AnalysisRecordSummary[];
  isLoading: boolean;
  activeId: string | null;
  onSelect: (id: string) => void;
  onDelete: (id: string) => void;
  onNewAnalysis: () => void;
}

export function HistorySidebar({
  history,
  isLoading,
  activeId,
  onSelect,
  onDelete,
  onNewAnalysis,
}: HistorySidebarProps) {
  return (
    <aside className="w-72 border-r flex flex-col bg-background h-full">
      {/* Header */}
      <div className="p-4 border-b flex items-center justify-between">
        <div className="flex items-center gap-2">
          <History className="w-5 h-5" />
          <h2 className="font-semibold">分析历史</h2>
        </div>
        <span className="text-xs text-muted-foreground">{history.length} 条</span>
      </div>

      {/* New Analysis Button */}
      <div className="p-3 border-b">
        <button
          onClick={onNewAnalysis}
          className="w-full px-3 py-2 text-sm font-medium rounded-md bg-primary text-primary-foreground hover:bg-primary/90 transition-colors"
        >
          新建分析
        </button>
      </div>

      {/* History List */}
      <div className="flex-1 overflow-y-auto">
        {isLoading ? (
          <div className="flex items-center justify-center py-8">
            <Loader2 className="w-6 h-6 animate-spin text-muted-foreground" />
          </div>
        ) : history.length === 0 ? (
          <div className="text-center py-8 text-muted-foreground">
            <p className="text-sm">暂无分析记录</p>
            <p className="text-xs mt-1">开始分析一个仓库吧</p>
          </div>
        ) : (
          <div className="divide-y">
            {history.map((record) => (
              <HistoryItem
                key={record.id}
                record={record}
                isActive={activeId === record.id}
                onClick={() => onSelect(record.id)}
                onDelete={() => onDelete(record.id)}
              />
            ))}
          </div>
        )}
      </div>
    </aside>
  );
}