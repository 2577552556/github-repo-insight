"use client";

import type { AnalysisRecordSummary } from "@/types";
import { cn } from "@/lib/utils";
import { Star, Trash2 } from "lucide-react";

interface HistoryItemProps {
  record: AnalysisRecordSummary;
  isActive: boolean;
  onClick: () => void;
  onDelete: () => void;
}

function formatTimeAgo(dateStr: string | null): string {
  if (!dateStr) return "未知";

  const date = new Date(dateStr);
  const now = new Date();
  const diffMs = now.getTime() - date.getTime();
  const diffMins = Math.floor(diffMs / 60000);
  const diffHours = Math.floor(diffMins / 60);
  const diffDays = Math.floor(diffHours / 24);

  if (diffMins < 1) return "刚刚";
  if (diffMins < 60) return `${diffMins}分钟前`;
  if (diffHours < 24) return `${diffHours}小时前`;
  if (diffDays < 30) return `${diffDays}天前`;
  return date.toLocaleDateString("zh-CN");
}

function getGradeColor(grade: string | null): string {
  switch (grade) {
    case "A":
      return "text-green-500";
    case "B":
      return "text-emerald-500";
    case "C":
      return "text-yellow-500";
    case "D":
      return "text-orange-500";
    case "E":
      return "text-red-500";
    case "F":
      return "text-red-600";
    default:
      return "text-muted-foreground";
  }
}

export function HistoryItem({
  record,
  isActive,
  onClick,
  onDelete,
}: HistoryItemProps) {
  return (
    <div
      className={cn(
        "group relative p-3 cursor-pointer transition-colors hover:bg-muted/50",
        isActive && "bg-muted/80 border-l-2 border-primary"
      )}
      onClick={onClick}
    >
      {/* Header: name + score */}
      <div className="flex items-center justify-between">
        <span className="font-medium text-sm truncate max-w-[120px]">
          {record.repository_name}
        </span>
        {record.score !== null && (
          <span className={cn("text-sm font-bold", getGradeColor(record.grade))}>
            ({record.score})
          </span>
        )}
      </div>

      {/* Secondary: grade + time */}
      <div className="flex items-center justify-between mt-1">
        <span className="text-xs text-muted-foreground">
          {record.grade ? `${record.grade}级` : "无评分"} · {formatTimeAgo(record.created_at)}
        </span>
      </div>

      {/* Status indicator */}
      <div className="flex items-center mt-1">
        {record.status === "processing" && (
          <span className="flex items-center text-xs text-blue-500">
            <span className="w-1.5 h-1.5 rounded-full bg-blue-500 animate-pulse mr-1" />
            进行中
          </span>
        )}
        {record.status === "completed" && (
          <span className="flex items-center text-xs text-green-500">
            <Star className="w-3 h-3 mr-1" />
            已完成
          </span>
        )}
        {record.status === "failed" && (
          <span className="flex items-center text-xs text-red-500">
            <span className="w-1.5 h-1.5 rounded-full bg-red-500 mr-1" />
            失败
          </span>
        )}
      </div>

      {/* Delete button */}
      <button
        className="absolute top-2 right-2 opacity-0 group-hover:opacity-100 p-1 rounded hover:bg-destructive/10 text-muted-foreground hover:text-destructive transition-colors"
        onClick={(e) => {
          e.stopPropagation();
          onDelete();
        }}
        title="删除记录"
      >
        <Trash2 className="w-4 h-4" />
      </button>
    </div>
  );
}