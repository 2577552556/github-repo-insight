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
    ConclusionItem,
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

## 核心原则

1. **数据溯源**：每条结论必须标注数据来源
2. **因果推理**：区分"因果关系"与"相关性"，禁止因果倒置
3. **置信度标注**：每条结论标注置信度（high/medium/low）
4. **类型适配**：根据项目类型调整分析重点

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

## 项目类型说明

| 类型 | 特征 | 分析重点 |
|------|------|----------|
| AI Platform | 集成LLM/RAG/Agent | AI能力成熟度、模型生态 |
| Infrastructure | 高可用/分布式/容器 | 稳定性、SLA、集群规模 |
| SDK/Library | 被依赖、API文档 | 版本管理、API稳定性 |
| Open Core | 核心开源+商业扩展 | 社区版vs商业功能区分 |
| Community OSS | 社区驱动 | 外部贡献者比例、治理效率 |
| Corporate OSS | 企业主导 | 商业支持、员工维护比例 |

## 输出要求

请用中文输出 JSON 格式，始终只输出 JSON，不要有任何其他内容。

每个结论项必须包含：
- text: 结论文本（至少80字）
- source: 数据来源（如 "stars=28k, forks=7k"）
- confidence: 置信度（high/medium/low）
- causation: 因果关系（causation/correlation/unknown）

禁止：
- "PR少 → 社区差"（应为 correlation，因为可能是 Open Core 核心代码走内部）
- "License非OSI → 项目风险高"（应为 correlation，Source Available 也可能是成熟项目）
- "stars高 → 项目优质"（应为 correlation，刷单项目可能高stars低质量）

{
  "summary": "项目一句话总结（50字内）",
  "strengths": [
    {
      "text": "优势描述（至少80字）",
      "source": "数据来源",
      "confidence": "high/medium/low",
      "causation": "causation/correlation/unknown"
    }
  ],
  "risks": [
    {
      "text": "风险描述（至少80字）",
      "source": "数据来源",
      "confidence": "high/medium/low",
      "causation": "causation/correlation/unknown"
    }
  ],
  "suggestions": [
    {
      "text": "建议描述（至少80字）",
      "source": "数据来源",
      "confidence": "high/medium/low",
      "causation": "causation/correlation/unknown"
    }
  ]
}

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

    # 类型检测信息
    type_info = ""
    if health_score.type_detection:
        td = health_score.type_detection
        type_info = f"""
## 项目类型检测
主类型：{td.primary_type.value}（置信度：{td.confidence:.0%}）
次要类型：{', '.join([t.value for t in td.secondary_types]) if td.secondary_types else "无"}
"""
        if td.features:
            features_str = ", ".join([f"{k}={v}" for k, v in td.features.items() if v is not False])
            type_info += f"检测特征：{features_str}"

    # AI 成熟度信息
    ai_maturity_info = ""
    if health_score.ai_maturity:
        am = health_score.ai_maturity
        detected_caps = [c["capability"] for c in am.capabilities if c.get("detected")]
        if detected_caps:
            ai_maturity_info = f"""
## AI 成熟度评分（AI Platform 项目）
总分：{am.total_score}/100
检测到的 AI 能力：{', '.join(detected_caps)}
支持的模型：{', '.join(am.model_support) if am.model_support else "未检测到"}
部署方式：{', '.join(am.deployment_methods) if am.deployment_methods else "未检测到"}
"""

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
{type_info}
{ai_maturity_info}
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
平均 Issue 响应时间：{metrics.issue_response_time_avg or "无数据"}小时（中位数：{metrics.issue_response_time_median or "无数据"}小时）
平均 PR 合并时间：{metrics.pr_merge_time_avg or "无数据"}小时（中位数：{metrics.pr_merge_time_median or "无数据"}小时）

## 分析要求

1. 每条结论必须包含：
   - source: 标注具体数据来源（如 "stars=28k, fork_ratio=0.25"）
   - confidence: high/medium/low
   - causation: causation（因果）/correlation（相关）/unknown（未知）

2. 禁止因果倒置：
   - "PR少 → 社区差" → 应为 correlation（Open Core 核心代码走内部）
   - "License非OSI → 风险高" → 应为 correlation（Source Available 也可能成熟）
   - "stars高 → 优质" → 应为 correlation（刷单项目可能高stars低质量）

3. 类型适配：根据检测到的项目类型调整分析重点

请生成 JSON 格式的解读报告。"""


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
) -> tuple[str, list[dict], list[dict], list[dict]]:
    """解析 LLM 响应为解读结果。

    返回 (summary, strengths, risks, suggestions)
    其中每个列表项是包含 text/source/confidence/causation 的字典
    """
    # 尝试提取 JSON -优先匹配 markdown 代码块内的 JSON
    json_match = re.search(r'```json\s*(\{[\s\S]*?\})\s*```', content, re.DOTALL)
    if not json_match:
        # 尝试使用 raw_decode 自动提取 JSON
        start_idx = content.find('{')
        if start_idx >= 0:
            try:
                # raw_decode 会返回解析后的对象和结束位置
                parsed_json, _ = json.JSONDecoder().raw_decode(content[start_idx:])
                json_match = type('obj', (object,), {'group': lambda self: json.dumps(parsed_json)})()
            except (json.JSONDecodeError, ValueError):
                json_match = None

    if not json_match:
        # 返回默认值
        default_item = {
            "text": f"仓库 '{repository.full_name}' 数据不足以生成分析",
            "source": "N/A",
            "confidence": "low",
            "causation": "unknown"
        }
        return (
            f"仓库 '{repository.full_name}' 的健康评估",
            [default_item],
            [default_item],
            [default_item],
        )

    try:
        data = json.loads(json_match.group())
        summary = data.get("summary", f"仓库 '{repository.full_name}' 的健康评估")

        # 解析 strengths/risks/suggestions，每个项包含 text/source/confidence/causation
        def parse_items(items: list, field_name: str) -> list[dict]:
            result = []
            for item in items:
                if isinstance(item, dict):
                    result.append({
                        "text": item.get("text", f"数据不足以生成{field_name}"),
                        "source": item.get("source", "N/A"),
                        "confidence": item.get("confidence", "medium"),
                        "causation": item.get("causation", "unknown"),
                    })
                elif isinstance(item, str):
                    # 兼容旧格式（纯字符串）
                    result.append({
                        "text": item,
                        "source": "N/A",
                        "confidence": "medium",
                        "causation": "unknown",
                    })
            return result if result else [{
                "text": f"数据不足以生成{field_name}",
                "source": "N/A",
                "confidence": "low",
                "causation": "unknown"
            }]

        strengths = parse_items(data.get("strengths", []), "优势分析")
        risks = parse_items(data.get("risks", []), "风险分析")
        suggestions = parse_items(data.get("suggestions", []), "改进建议")

        return summary, strengths, risks, suggestions
    except (json.JSONDecodeError, KeyError) as e:
        default_item = {
            "text": f"解析失败: {str(e)[:50]}",
            "source": "N/A",
            "confidence": "low",
            "causation": "unknown"
        }
        return (
            f"仓库 '{repository.full_name}' 的健康评估",
            [default_item],
            [default_item],
            [default_item],
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
            max_tokens=4096,  # 增加 token 限制以支持更复杂的 JSON 输出
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
                if strengths and strengths[0].get("text") != "数据不足以生成优势分析":
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
        default_item = {
            "text": f"AI 解读服务暂时不可用，请稍后重试",
            "source": "N/A",
            "confidence": "low",
            "causation": "unknown"
        }
        return {
            **state,
            "summary": f"仓库 '{repo.full_name}' 的健康评估",
            "strengths": [default_item],
            "risks": [default_item],
            "suggestions": [default_item],
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

            # 将 dict 格式转换为 ConclusionItem
            def to_conclusion_items(items: list[dict]) -> list[dict]:
                return [
                    ConclusionItem(
                        text=item.get("text", ""),
                        source=item.get("source", "N/A"),
                        confidence=item.get("confidence", "medium"),
                        causation=item.get("causation", "unknown"),
                    )
                    for item in items
                ]

            return AIAnalysis(
                summary=result["summary"] or f"这是一个名为 {repository.name} 的 GitHub 仓库",
                strengths=to_conclusion_items(result["strengths"]),
                risks=to_conclusion_items(result["risks"]),
                suggestions=to_conclusion_items(result["suggestions"]),
                ai_used=True,
            )
        except Exception as e:
            logger.error(f"AI 解读失败: {e}")
            raise NetworkError(f"AI 解读服务调用失败: {str(e)}")


ai_evaluation_service = AIEvaluationService()