"""所有 SmartHire Agent 的基类，集成 LLM。"""

import json
import re
from abc import ABC, abstractmethod
from typing import Any

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnableSequence
from loguru import logger
from pydantic import BaseModel, ValidationError

from app.config import settings


class BaseAgent(ABC):
    """抽象基类，提供共享的 LLM 和提示词基础设施。"""

    def __init__(self, name: str, system_prompt: str):
        self.name = name
        self.system_prompt = system_prompt
        self._llm: ChatOpenAI | None = None

    def _get_api_key(self) -> str:
        return settings.DEEPSEEK_API_KEY

    def _get_llm(self) -> ChatOpenAI:
        """惰性初始化并返回 DeepSeek LLM。"""
        if self._llm is not None:
            return self._llm

        api_key = settings.DEEPSEEK_API_KEY
        base_url = settings.DEEPSEEK_API_BASE
        model = "deepseek-chat"

        if not api_key:
            logger.warning(f"Agent '{self.name}': DeepSeek API key not set. Using stub mode.")

        self._llm = ChatOpenAI(
            model=model,
            api_key=api_key or "stub",
            base_url=base_url,
            temperature=0.1,
            max_tokens=4096,
        )
        logger.info(f"Agent '{self.name}' initialized with {provider} ({model})")
        return self._llm

    async def _call_llm_structured(
        self,
        output_schema: type[BaseModel],
        user_prompt: str,
        rag_query: str | None = None,
    ) -> BaseModel:
        """手动调用 LLM → 解析 JSON → 验证 Schema，不依赖 with_structured_output。"""
        enriched_prompt = user_prompt

        if not self._get_api_key():
            logger.warning(f"Agent '{self.name}': No API key — returning stub.")
            return output_schema()

        llm = self._get_llm()

        # 构建要求 JSON 输出的提示词
        schema_json = output_schema.model_json_schema()
        schema_str = json.dumps(schema_json, ensure_ascii=False, indent=2)
        json_prompt = (
            "你必须以 JSON 格式返回结果，严格遵循以下 JSON Schema：\n"
            f"{schema_str}\n\n"
            f"请分析以下内容并按照上述 Schema 返回 JSON（不要包含 markdown 代码块标记）：\n\n{enriched_prompt}"
        )
        messages = [
            SystemMessage(content=self.system_prompt),
            HumanMessage(content=json_prompt),
        ]
        logger.debug(f"Agent '{self.name}' requesting structured JSON output")

        for attempt in range(2):
            try:
                llm = self._get_llm()
                response = await llm.ainvoke(messages)
                text = response.content.strip()

                # 提取 JSON（兼容可能的 markdown 代码块）
                json_str = text
                for marker in ["```json", "```"]:
                    if marker in text:
                        parts = text.split(marker)
                        if len(parts) >= 3:
                            json_str = parts[1].strip()
                        break

                parsed = json.loads(json_str)
                result = output_schema.model_validate(parsed)
                logger.debug(f"Agent '{self.name}' parsed structured output successfully")
                return result

            except (json.JSONDecodeError, ValidationError) as e:
                logger.warning(f"Agent '{self.name}' attempt {attempt + 1} - parse failed: {e}")
                if attempt == 1:
                    logger.error(f"Agent '{self.name}' returning fallback after 2 failures")
                    return output_schema()
            except Exception as e:
                logger.error(f"Agent '{self.name}' LLM call failed: {e}")
                return output_schema()

    @abstractmethod
    async def run(self, **kwargs) -> dict[str, Any]:
        """执行 Agent 的核心逻辑。"""
        ...

    def _create_chain(self, template: str) -> RunnableSequence:
        """从提示词模板创建 LangChain RunnableSequence。"""
        prompt = PromptTemplate(
            template=template,
            input_variables=list(self._extract_variables(template)),
        )
        return prompt | self._get_llm()

    @staticmethod
    def _extract_variables(template: str) -> set[str]:
        """从提示词模板字符串中提取模板变量名。"""
        return set(re.findall(r"\{(\w+)\}", template))

    @staticmethod
    def _model_to_dict(model: BaseModel | None) -> dict[str, Any]:
        """安全地将 Pydantic 模型转换为字典，失败时返回空字典。"""
        if model is None:
            return {}
        return model.model_dump()
