"use client";

import { useState, type FormEvent } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { cn } from "@/lib/utils";

interface RepositoryInputProps {
  url: string;
  onUrlChange: (url: string) => void;
  onSubmit: (url: string) => void;
  isLoading: boolean;
}

const GITHUB_URL_REGEX = /^https?:\/\/(www\.)?github\.com\/[^/]+\/[^/]+\/?$/;

export function RepositoryInput({ url, onUrlChange, onSubmit, isLoading }: RepositoryInputProps) {
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault();
    setError(null);

    if (!url.trim()) {
      setError("请输入 GitHub 仓库 URL");
      return;
    }

    if (!GITHUB_URL_REGEX.test(url.trim())) {
      setError("无效的 GitHub URL 格式。示例：https://github.com/owner/repo");
      return;
    }

    onSubmit(url.trim());
  };

  return (
    <form onSubmit={handleSubmit} className="w-full max-w-2xl mx-auto space-y-4">
      <div className="space-y-2">
        <Label htmlFor="repo-url" className="text-lg font-semibold">
          GitHub 仓库 URL
        </Label>
        <Input
          id="repo-url"
          type="text"
          placeholder="https://github.com/owner/repo"
          value={url}
          onChange={(e) => onUrlChange(e.target.value)}
          className={cn("h-12 text-lg", error && "border-destructive")}
          disabled={isLoading}
        />
        {error && (
          <p className="text-sm text-destructive">{error}</p>
        )}
      </div>
      <Button
        type="submit"
        size="lg"
        className="w-full"
        disabled={isLoading}
      >
        {isLoading ? "分析中..." : "分析仓库"}
      </Button>
    </form>
  );
}