"use client";

import { CheckCircle, Circle, Loader2 } from "lucide-react";
import type { ProgressiveResult } from "@/services/api";

interface StreamingProgressProps {
  result: ProgressiveResult;
  isStreaming: boolean;
}

const STEPS = [
  { key: "repository", label: "仓库信息", description: "获取仓库基础信息" },
  { key: "languages", label: "语言分布", description: "分析编程语言" },
  { key: "metrics", label: "扩展指标", description: "计算活跃度指标" },
  { key: "healthScore", label: "健康评分", description: "评估仓库健康度" },
  { key: "aiScore", label: "AI评分", description: "生成AI评分" },
  { key: "aiAnalysis", label: "AI分析", description: "深度解读仓库" },
] as const;

type StepKey = typeof STEPS[number]["key"];

function getStepStatus(
  key: StepKey,
  result: ProgressiveResult,
  isStreaming: boolean
): "completed" | "processing" | "pending" {
  const hasData = result[key] !== null;

  if (hasData) {
    return "completed";
  }

  // Find the first pending step
  const stepIndex = STEPS.findIndex((s) => s.key === key);
  const firstPendingIndex = STEPS.findIndex((s) => result[s.key] === null);

  if (stepIndex === firstPendingIndex && isStreaming) {
    return "processing";
  }

  return "pending";
}

export function StreamingProgress({ result, isStreaming }: StreamingProgressProps) {
  // Find current processing step
  const currentStepIndex = STEPS.findIndex((s) => result[s.key] === null);
  const currentStep = currentStepIndex >= 0 ? STEPS[currentStepIndex] : null;

  return (
    <div className="mb-6">
      {/* 进度条 */}
      <div className="mb-3">
        <div className="flex justify-between text-xs text-muted-foreground mb-1">
          <span>
            {currentStep ? `正在分析: ${currentStep.description}` : "分析完成"}
          </span>
          <span>
            {STEPS.filter((s) => result[s.key] !== null).length} / {STEPS.length}
          </span>
        </div>
        <div className="h-2 bg-muted rounded-full overflow-hidden">
          <div
            className="h-full bg-primary transition-all duration-300 ease-out"
            style={{
              width: `${(STEPS.filter((s) => result[s.key] !== null).length / STEPS.length) * 100}%`,
            }}
          />
        </div>
      </div>

      {/* 步骤列表 */}
      <div className="grid grid-cols-3 md:grid-cols-6 gap-2">
        {STEPS.map((step) => {
          const status = getStepStatus(step.key, result, isStreaming);

          return (
            <div
              key={step.key}
              className={`
                flex items-center gap-2 px-3 py-2 rounded-lg border text-xs
                ${
                  status === "completed"
                    ? "bg-green-500/10 border-green-500/30 text-green-600"
                    : status === "processing"
                      ? "bg-blue-500/10 border-blue-500/30 text-blue-600 animate-pulse"
                      : "bg-muted/50 border-muted text-muted-foreground"
                }
              `}
            >
              {status === "completed" ? (
                <CheckCircle className="w-3 h-3 flex-shrink-0" />
              ) : status === "processing" ? (
                <Loader2 className="w-3 h-3 flex-shrink-0 animate-spin" />
              ) : (
                <Circle className="w-3 h-3 flex-shrink-0" />
              )}
              <span className="truncate">{step.label}</span>
            </div>
          );
        })}
      </div>
    </div>
  );
}
