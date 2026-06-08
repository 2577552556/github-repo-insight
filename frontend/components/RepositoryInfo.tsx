"use client";

import type { RepositoryInfo as RepositoryInfoType } from "@/types";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { MetricCard } from "@/components/MetricCard";
import { formatNumber, formatDate } from "@/lib/utils";
import { Star, GitFork, Eye, AlertCircle, Calendar, GitBranch } from "lucide-react";

interface RepositoryInfoProps {
  repository: RepositoryInfoType;
}

export function RepositoryInfo({ repository }: RepositoryInfoProps) {
  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle className="text-xl">{repository.full_name}</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          {repository.description && (
            <p className="text-muted-foreground">{repository.description}</p>
          )}
          <div className="flex flex-wrap gap-2">
            {repository.language && (
              <span className="px-2 py-1 bg-secondary rounded text-sm">
                {repository.language}
              </span>
            )}
            <span className="px-2 py-1 bg-secondary rounded text-sm">
              默认分支：{repository.default_branch}
            </span>
          </div>
          <div className="text-sm text-muted-foreground">
            创建时间：{formatDate(repository.created_at)} • 更新时间：{formatDate(repository.updated_at)}
          </div>
        </CardContent>
      </Card>

      <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
        <MetricCard
          title="星标数"
          value={formatNumber(repository.stars)}
          icon={Star}
        />
        <MetricCard
          title="分支数"
          value={formatNumber(repository.forks)}
          icon={GitFork}
        />
        <MetricCard
          title="关注者数"
          value={formatNumber(repository.watchers)}
          icon={Eye}
        />
        <MetricCard
          title="开放 Issues"
          value={formatNumber(repository.open_issues)}
          icon={AlertCircle}
        />
        <MetricCard
          title="仓库年龄"
          value={formatDate(repository.created_at)}
          icon={Calendar}
        />
      </div>
    </div>
  );
}