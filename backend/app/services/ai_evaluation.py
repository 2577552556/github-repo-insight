"""
AI Evaluation Service using LangGraph + DeepSeek.

功能：
1. AIScore: 基于规则的快速评分 (0-100)
2. AIAnalysis: DeepSeek 深度分析 (summary/strengths/risks/suggestions)
"""

import logging
from datetime import datetime
from typing import TypedDict

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_deepseek import ChatDeepSeek
from langgraph.graph import StateGraph, END

from app.core.config import settings
from app.schemas.analyze import (
    RepositoryInfo,
    LanguageDistribution,
    AIScore,
    AIAnalysis,
)

logger = logging.getLogger(__name__)


class EvaluationState(TypedDict):
    """LangGraph 状态定义."""
    repository: RepositoryInfo
    languages: LanguageDistribution
    recent_commits: int
    contributors_count: int
    score: int
    grade: str
    summary: str
    strengths: list[str]
    risks: list[str]
    suggestions: list[str]
    iteration: int


SYSTEM_PROMPT = """你是一个专业的 GitHub 仓库评估专家。请对仓库进行深度分析。

分析维度：
1. 项目定位：这个仓库是什么，用什么技术栈，解决什么问题
2. 优势：社区活跃、文档完善、技术成熟、维护及时等
3. 风险：长期未更新、贡献者少、Issue 积压、依赖过时等
4. 建议：如何改进该项目

请用中文回复，始终输出 JSON 格式：

{
  "summary": "项目一句话总结（50字内）",
  "strengths": ["优势1", "优势2", "优势3"],
  "risks": ["风险1", "风险2", "风险3"],
  "suggestions": ["建议1", "建议2", "建议3"]
}

只输出 JSON，不要有其他内容。"""


def build_analysis_prompt(
    repository: RepositoryInfo,
    languages: LanguageDistribution,
    recent_commits: int,
    contributors_count: int,
) -> str:
    """构建分析提示词."""
    lang_str = ", ".join(
        f"{lang} ({pct:.1f}%)" for lang, pct in languages.languages.items()
    ) if languages.languages else "无可用数据"

    return f"""请分析以下 GitHub 仓库：

## 基础信息
仓库名称：{repository.full_name}
描述：{repository.description or "暂无描述"}
主要语言：{repository.language or "未指定"}
星标数：{repository.stars:,}
分支数：{repository.forks:,}
关注者数：{repository.watchers}
开放 Issues：{repository.open_issues}
默认分支：{repository.default_branch}
创建时间：{repository.created_at}
最后更新：{repository.updated_at}
开源协议：{repository.license or "未指定"}
主题标签：{', '.join(repository.topics) if repository.topics else "无"}

## 编程语言分布
{lang_str}

## 活跃度
近30天 Commit 数：{recent_commits}
贡献者数量：{contributors_count}

请分析并给出 JSON 格式的评估结果。"""


def create_analysis_agent() -> StateGraph:
    """创建 LangGraph 分析 Agent."""

    def analyze_node(state: EvaluationState) -> EvaluationState:
        """LLM 分析节点."""
        repo = state["repository"]
        langs = state["languages"]

        llm = ChatDeepSeek(
            model="deepseek-chat",
            api_key=settings.DEEPSEEK_API_KEY or "",
            base_url=settings.DEEPSEEK_API_URL,
            temperature=0.3,
        )

        messages = [
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(content=build_analysis_prompt(
                repo, langs,
                state["recent_commits"],
                state["contributors_count"]
            )),
        ]

        response = llm.invoke(messages)
        content = response.content if hasattr(response, "content") else str(response)

        # 解析 JSON 响应
        summary, strengths, risks, suggestions = parse_analysis_response(content)

        return {
            **state,
            "summary": summary,
            "strengths": strengths,
            "risks": risks,
            "suggestions": suggestions,
            "iteration": state["iteration"] + 1,
        }

    # 构建图
    graph = StateGraph(EvaluationState)
    graph.add_node("analyze", analyze_node)
    graph.set_entry_point("analyze")
    graph.add_edge("analyze", END)

    return graph.compile()


def parse_analysis_response(content: str) -> tuple[str, list[str], list[str], list[str]]:
    """解析 LLM 响应为分析结果."""
    import json
    import re

    # 尝试提取 JSON
    json_match = re.search(r'\{[\s\S]*\}', content)
    if not json_match:
        return content, [], [], []

    try:
        data = json.loads(json_match.group())
        summary = data.get("summary", content[:100])
        strengths = data.get("strengths", [])
        risks = data.get("risks", [])
        suggestions = data.get("suggestions", [])
        return summary, strengths, risks, suggestions
    except json.JSONDecodeError:
        return content[:100], [], [], []


def calculate_rule_score(
    repository: RepositoryInfo,
    recent_commits: int,
    contributors_count: int,
) -> tuple[int, str]:
    """基于规则计算评分 (Fallback)."""
    stars = repository.stars
    forks = repository.forks
    issues = repository.open_issues
    language_count = len(repository.topics)

    score = 0
    grade = "F"

    # 基础评分
    if stars > 100000:
        score = 85
        grade = "A"
    elif stars > 50000:
        score = 78
        grade = "B"
    elif stars > 10000:
        score = 72
        grade = "B"
    elif stars > 1000:
        score = 60
        grade = "C"
    elif stars > 100:
        score = 45
        grade = "D"
    else:
        score = 25
        grade = "F"

    # 调整
    if language_count >= 3:
        score = min(100, score + 5)
    if contributors_count >= 10:
        score = min(100, score + 5)
    if issues > 0:
        issue_ratio = issues / max(stars, 1)
        if issue_ratio > 0.5:
            score = max(0, score - 10)

    return score, grade


class AIEvaluationService:
    """AI 评估服务."""

    def __init__(self):
        self._agent = None

    @property
    def agent(self):
        """延迟初始化 Agent."""
        if self._agent is None:
            self._agent = create_analysis_agent()
        return self._agent

    async def evaluate_quick(
        self,
        repository: RepositoryInfo,
        recent_commits: int = 0,
        contributors_count: int = 0,
    ) -> AIScore:
        """快速评分 (规则或 AI)."""
        if settings.DEEPSEEK_API_KEY:
            return await self._evaluate_quick_with_ai(
                repository, recent_commits, contributors_count
            )
        return self._evaluate_with_rules(repository, recent_commits, contributors_count)

    async def analyze(
        self,
        repository: RepositoryInfo,
        languages: LanguageDistribution,
        recent_commits: int = 0,
        contributors_count: int = 0,
    ) -> AIAnalysis:
        """深度 AI 分析."""
        if settings.DEEPSEEK_API_KEY:
            return await self._analyze_with_agent(
                repository, languages, recent_commits, contributors_count
            )
        return self._analyze_with_rules(repository, languages, recent_commits, contributors_count)

    async def _evaluate_quick_with_ai(
        self,
        repository: RepositoryInfo,
        recent_commits: int,
        contributors_count: int,
    ) -> AIScore:
        """使用 AI 快速评分."""
        try:
            initial_state: EvaluationState = {
                "repository": repository,
                "languages": LanguageDistribution(languages={}),
                "recent_commits": recent_commits,
                "contributors_count": contributors_count,
                "score": 50,
                "grade": "C",
                "summary": "",
                "strengths": [],
                "risks": [],
                "suggestions": [],
                "iteration": 0,
            }

            result = await self.agent.ainvoke(initial_state)

            # 根据分析结果计算分数
            score = max(0, min(100, result["score"]))
            grade = result["grade"]

            return AIScore(
                score=score,
                grade=grade,
                summary=result["summary"] or f"仓库 '{repository.full_name}' 的 AI 评分",
                ai_used=True,
            )
        except Exception as e:
            logger.warning(f"AI 快速评分失败: {e}")
            return self._evaluate_with_rules(repository, recent_commits, contributors_count)

    async def _analyze_with_agent(
        self,
        repository: RepositoryInfo,
        languages: LanguageDistribution,
        recent_commits: int,
        contributors_count: int,
    ) -> AIAnalysis:
        """使用 DeepSeek Agent 进行深度分析."""
        try:
            initial_state: EvaluationState = {
                "repository": repository,
                "languages": languages,
                "recent_commits": recent_commits,
                "contributors_count": contributors_count,
                "score": 50,
                "grade": "C",
                "summary": "",
                "strengths": [],
                "risks": [],
                "suggestions": [],
                "iteration": 0,
            }

            result = await self.agent.ainvoke(initial_state)

            return AIAnalysis(
                summary=result["summary"] or f"这是一个名为 {repository.name} 的 GitHub 仓库",
                strengths=result["strengths"],
                risks=result["risks"],
                suggestions=result["suggestions"],
                ai_used=True,
            )
        except Exception as e:
            logger.warning(f"DeepSeek API 调用失败: {e}")
            return self._analyze_with_rules(repository, languages, recent_commits, contributors_count)

    def _evaluate_with_rules(
        self,
        repository: RepositoryInfo,
        recent_commits: int,
        contributors_count: int,
    ) -> AIScore:
        """基于规则的评分 Fallback."""
        score, grade = calculate_rule_score(repository, recent_commits, contributors_count)

        grade_text = "优秀" if score >= 85 else "良好" if score >= 70 else "一般" if score >= 50 else "较差" if score >= 30 else "需关注"

        return AIScore(
            score=score,
            grade=grade,
            summary=f"仓库 '{repository.full_name}' 拥有 {repository.stars:,} 星标和 {repository.forks:,} 分支。综合评估：{grade_text}。",
            ai_used=False,
        )

    def _analyze_with_rules(
        self,
        repository: RepositoryInfo,
        languages: LanguageDistribution,
        recent_commits: int,
        contributors_count: int,
    ) -> AIAnalysis:
        """基于规则的深度分析 Fallback."""
        strengths = []
        risks = []
        suggestions = []

        # 分析优势
        if repository.stars >= 10000:
            strengths.append("非常受欢迎的项目，Stars 数量超过 10k")
        elif repository.stars >= 1000:
            strengths.append("有一定用户基础的项目")

        if repository.language:
            strengths.append(f"主要使用 {repository.language} 开发")

        if repository.topics:
            strengths.append(f"项目定位清晰：{', '.join(repository.topics[:3])}")

        if recent_commits >= 10:
            strengths.append("近期活跃度高，有持续的 commits")

        # 分析风险
        if repository.stars < 100:
            risks.append("Stars 数量较低，项目可能不够成熟")

        if contributors_count <= 1:
            risks.append("贡献者数量少，存在单点故障风险")

        if repository.open_issues > repository.stars * 0.2:
            risks.append("Issue 积压较多，维护压力较大")

        try:
            updated = datetime.fromisoformat(repository.updated_at.replace("Z", "+00:00"))
            days_since_update = (datetime.now(updated.tzinfo) - updated).days
            if days_since_update > 365:
                risks.append(f"已超过 {days_since_update} 天未更新，可能被放弃")
            elif days_since_update > 180:
                risks.append(f"已超过半年未更新，维护活跃度下降")
        except Exception:
            pass

        # 建议
        if not repository.license:
            suggestions.append("建议添加开源协议，明确项目授权")
        if not repository.description:
            suggestions.append("建议添加项目描述，让用户快速了解项目")
        if not repository.topics:
            suggestions.append("建议添加 Topics，帮助用户发现项目")
        if contributors_count <= 1:
            suggestions.append("建议吸引更多贡献者，降低项目维护风险")

        return AIAnalysis(
            summary=f"仓库 '{repository.full_name}' 是一个{'活跃的' if recent_commits > 10 else '需要关注维护的'}项目",
            strengths=strengths[:3],
            risks=risks[:3],
            suggestions=suggestions[:3],
            ai_used=False,
        )


ai_evaluation_service = AIEvaluationService()