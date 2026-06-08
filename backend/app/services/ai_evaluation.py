"""
AI Evaluation Service using LangGraph + DeepSeek.

功能：
- AI 解读：基于规则引擎的评分结果，生成项目总结/优势/风险/建议

注意：
- AI 只负责解读，不做评分
- 评分由规则引擎（health_score_service）计算
- 无 DEEPSEEK_API_KEY 时抛出异常
"""

import logging
import json
import re
from pathlib import Path
from typing import TypedDict

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_deepseek import ChatDeepSeek
from langgraph.graph import StateGraph, END

from app.core.config import settings
from app.core.exceptions import NetworkError
from app.schemas.analyze import (
    RepositoryInfo,
    LanguageDistribution,
    RepositoryMetrics,
    HealthScore,
    AIAnalysis,
)


def _load_deepseek_key_from_file() -> str | None:
    """从 settings.json 加载 DeepSeek API Key"""
    settings_file = Path(__file__).parent.parent.parent / "data" / "settings.json"
    if settings_file.exists():
        data = json.loads(settings_file.read_text(encoding="utf-8"))
        return data.get("deepseek_api_key")
    return None

logger = logging.getLogger(__name__)


class InterpretationState(TypedDict):
    """LangGraph 状态定义."""
    repository: RepositoryInfo
    languages: LanguageDistribution
    metrics: RepositoryMetrics
    health_score: HealthScore
    summary: str
    strengths: list[str]
    risks: list[str]
    suggestions: list[str]
    iteration: int


SYSTEM_PROMPT = """你是一名资深开源项目架构师、技术负责人和代码审查专家。

你的任务是根据规则引擎的评分结果，对 GitHub 仓库进行深度解读，生成专业的"体检报告"。

## 规则引擎评分（满分100分）

| 维度 | 满分 | 说明 |
|------|------|------|
| Popularity（流行度）| 25 | Stars/Forks/Watchers |
| Activity（活跃度）| 25 | Commit频率/更新时间 |
| Community（社区）| 15 | Contributors/Issue处理 |
| Issue Governance（Issue治理）| 10 | Issue响应时间/关闭率 |
| PR Governance（PR治理）| 10 | PR合并时间/合并率 |
| Engineering（工程化）| 10 | License/README/Topics |
| Release/Maintenance（发布维护）| 5 | 发布节奏/维护风险 |

等级划分：A≥90, B≥80, C≥70, D≥60, E≥50, F<50

## 输出要求

请用中文输出 JSON 格式，始终只输出 JSON，不要有任何其他内容。

每个优势、风险、建议必须至少80 字，提供详细、专业的分析：

{
  "summary": "项目一句话总结（50字内）",
  "strengths": [
    "优势1（至少80字，详细说明优势的具体表现、对项目的影响程度）",
    "优势2（至少80字，详细说明优势的具体表现、对项目的影响程度）",
    "优势3（至少80字，详细说明优势的具体表现、对项目的影响程度）"
  ],
  "risks": [
    "风险1（至少80字，详细说明风险的具体影响、可能造成的后果）",
    "风险2（至少80字，详细说明风险的具体影响、可能造成的后果）",
    "风险3（至少80字，详细说明风险的具体影响、可能造成的后果）"
  ],
  "suggestions": [
    "建议1（至少80字，提供可操作的改进方案，包括具体步骤）",
    "建议2（至少80字，提供可操作的改进方案，包括具体步骤）",
    "建议3（至少80字，提供可操作的改进方案，包括具体步骤）"
  ]
}

重点分析方向：
1. 项目定位与影响力
2. 活跃度与维护状态
3. 社区健康度与贡献者分布
4. Issue/PR 治理效率
5. 工程规范与文档完善度
6. 潜在风险与改进空间

只输出 JSON，不要有其他内容。"""


def build_interpretation_prompt(
    repository: RepositoryInfo,
    languages: LanguageDistribution,
    metrics: RepositoryMetrics,
    health_score: HealthScore,
) -> str:
    """构建解读提示词."""
    lang_str = ", ".join(
        f"{lang} ({pct:.1f}%)" for lang, pct in languages.languages.items()
    ) if languages.languages else "无可用数据"

    dims = health_score.dimensions
    total = health_score.score

    return f"""请分析以下 GitHub 仓库并解读：

## 基础信息
仓库名称：{repository.full_name}
描述：{repository.description or "暂无描述"}
主要语言：{repository.language or "未指定"}
星标数：{repository.stars:,}
分支数：{repository.forks:,}
开放 Issues：{repository.open_issues}
默认分支：{repository.default_branch}
创建时间：{repository.created_at}
最后更新：{repository.updated_at}
开源协议：{repository.license or "未指定"}
主题标签：{', '.join(repository.topics) if repository.topics else "无"}

## 语言分布
{lang_str}

## 规则引擎评分结果（满分100分）

总分：{total}分（等级：{calculate_grade_for_ai(total)}）

各维度得分：
- Popularity（流行度）: {dims.popularity}/25分
- Activity（活跃度）: {dims.activity}/25分
- Community（社区）: {dims.community}/15分
- Issue Governance（Issue治理）: {dims.issue_governance}/10分
- PR Governance（PR治理）: {dims.pr_governance}/10分
- Engineering（工程化）: {dims.engineering}/10分
- Release/Maintenance（发布维护）: {dims.release_maintenance}/5分

## 扩展指标
近30天 Commits：{metrics.recent_commits_30d}
近90天 Commits：{metrics.recent_commits_90d}
贡献者数量：{metrics.contributors_count}
开放 Issues：{metrics.open_issues_count}
30天关闭 Issues：{metrics.closed_issues_30d}
开放 PRs：{metrics.open_prs_count}
30天合并 PRs：{metrics.merged_prs_30d}
发布次数：{metrics.releases_count}
最近发布：{metrics.latest_release_date or "无"}
平均 Issue 响应时间：{metrics.issue_response_time_avg or "无数据"}小时
平均 PR 合并时间：{metrics.pr_merge_time_avg or "无数据"}小时

请基于以上评分结果，生成 JSON 格式的解读报告。要求每个优势、风险、建议至少50字，提供详细的分析。"""


def calculate_grade_for_ai(score: int) -> str:
    """根据分数计算等级."""
    if score >= 90:
        return "A"
    if score >= 80:
        return "B"
    if score >= 70:
        return "C"
    if score >= 60:
        return "D"
    if score >= 50:
        return "E"
    return "F"


def parse_interpretation_response(
    content: str,
    repository: RepositoryInfo,
) -> tuple[str, list[str], list[str], list[str]]:
    """解析 LLM 响应为解读结果."""
    # 尝试提取 JSON -优先匹配 markdown 代码块内的 JSON
    json_match = re.search(r'```json\s*(\{[\s\S]*?\})\s*```', content)
    if not json_match:
        # 非贪婪匹配
        json_match = re.search(r'\{[\s\S]*?\}', content)

    if not json_match:
        return (
            f"仓库 '{repository.full_name}' 的健康评估",
            ["数据不足以生成优势分析"],
            ["数据不足以生成风险分析"],
            ["数据不足以生成建议"],
        )

    try:
        data = json.loads(json_match.group())
        summary = data.get("summary", f"仓库 '{repository.full_name}' 的健康评估")
        strengths = data.get("strengths", [])
        risks = data.get("risks", [])
        suggestions = data.get("suggestions", [])
        return summary, strengths, risks, suggestions
    except (json.JSONDecodeError, KeyError):
        return (
            f"仓库 '{repository.full_name}' 的健康评估",
            ["数据不足以生成优势分析"],
            ["数据不足以生成风险分析"],
            ["数据不足以生成建议"],
        )


def create_interpretation_agent(max_retries: int = 2) -> StateGraph:
    """创建 LangGraph 解读 Agent."""

    def interpret_node(state: InterpretationState) -> InterpretationState:
        """LLM 解读节点."""
        repo = state["repository"]
        langs = state["languages"]
        metrics = state["metrics"]
        hs = state["health_score"]

        llm = ChatDeepSeek(
            model="deepseek-chat",
            api_key=_load_deepseek_key_from_file() or settings.DEEPSEEK_API_KEY or "",
            base_url=settings.DEEPSEEK_API_URL,
            temperature=0.3,
            max_tokens=2048,  # 确保完整输出
        )

        messages = [
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(content=build_interpretation_prompt(
                repo, langs, metrics, hs
            )),
        ]

        # 重试机制
        last_error = None
        for attempt in range(max_retries):
            try:
                response = llm.invoke(messages)
                content = response.content if hasattr(response, "content") else str(response)

                # 解析 JSON 响应
                summary, strengths, risks, suggestions = parse_interpretation_response(content, repo)

                # 检查解析结果是否有效（内容非空且非占位符）
                if strengths != ["数据不足以生成优势分析"]:
                    return {
                        **state,
                        "summary": summary,
                        "strengths": strengths,
                        "risks": risks,
                        "suggestions": suggestions,
                        "iteration": state["iteration"] + 1,
                    }
                last_error = "解析结果无效"
            except Exception as e:
                last_error = str(e)
                logger.warning(f"AI解读尝试 {attempt + 1} 失败: {e}")

        # 所有重试都失败，返回占位符
        logger.error(f"AI 解读最终失败: {last_error}")
        return {
            **state,
            "summary": f"仓库 '{repo.full_name}' 的健康评估",
            "strengths": ["数据不足以生成优势分析"],
            "risks": ["数据不足以生成风险分析"],
            "suggestions": ["数据不足以生成建议"],
            "iteration": state["iteration"] + 1,
        }

    # 构建图
    graph = StateGraph(InterpretationState)
    graph.add_node("interpret", interpret_node)
    graph.set_entry_point("interpret")
    graph.add_edge("interpret", END)

    return graph.compile()


class AIEvaluationService:
    """AI 评估服务（仅支持 DeepSeek）- 只负责解读，不做评分"""

    def __init__(self):
        self._agent = None

    @property
    def agent(self):
        """延迟初始化 Agent."""
        if self._agent is None:
            self._agent = create_interpretation_agent()
        return self._agent

    def _check_api_key(self) -> None:
        """检查 API Key 是否配置."""
        deepseek_key = _load_deepseek_key_from_file() or settings.DEEPSEEK_API_KEY
        if not deepseek_key:
            raise ValueError(
                "DEEPSEEK_API_KEY 未配置。"
                "请设置环境变量 DEEPSEEK_API_KEY 或在 .env 文件中配置。"
                "AI 解读功能需要有效的 DeepSeek API Key。"
            )

    async def interpret(
        self,
        repository: RepositoryInfo,
        languages: LanguageDistribution,
        metrics: RepositoryMetrics,
        health_score: HealthScore,
    ) -> AIAnalysis:
        """AI 解读（基于规则引擎的评分结果）"""
        self._check_api_key()

        try:
            initial_state: InterpretationState = {
                "repository": repository,
                "languages": languages,
                "metrics": metrics,
                "health_score": health_score,
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
            logger.error(f"AI 解读失败: {e}")
            raise NetworkError(f"AI 解读服务调用失败: {str(e)}")


ai_evaluation_service = AIEvaluationService()