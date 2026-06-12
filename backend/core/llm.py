import asyncio
import os

from pydantic import BaseModel, Field


class LLMSnippetResponse(BaseModel):
    title: str = Field(description="보안 설정 제목 (예: UFW를 이용한 SSH 포트 차단)")
    code: str = Field(description="즉시 적용 가능한 설정 코드 또는 쉘 명령어")
    description: str = Field(description="해당 코드가 작동하는 원리 1줄 설명")
    confidence: float = Field(description="해결책 신뢰도 0.0~1.0 (0.8 미만 시 전문가 확인 권장)")


class LLMClient:
    """Gemini 우선 호출, 실패 시 OpenAI로 자동 Fallback"""

    def __init__(self):
        self.gemini_api_key = os.getenv("GEMINI_API_KEY")
        self.openai_api_key = os.getenv("OPENAI_API_KEY")

    def _build_prompt(self, vuln_type: str, vuln_detail: str, server_type: str) -> str:
        return f"""
당신은 서버 보안 전문가입니다.
아래 보안 취약점에 대해 즉시 적용 가능한 설정 코드를 생성하세요.

취약점 유형: {vuln_type}
취약점 설명: {vuln_detail}
서버 환경: {server_type}

규칙:
- 코드는 복사 후 바로 붙여넣을 수 있는 형태로 작성
- 주석 최소화
- 확신이 없는 경우 confidence를 0.8 미만으로 설정
"""

    async def _call_gemini(self, prompt: str) -> LLMSnippetResponse:
        """
        Gemini API 호출. response_schema로 Structured Output을 강제한다.
        Gemini SDK는 동기 호출이므로 asyncio.to_thread로 감싸 이벤트 루프 블로킹을 막는다.
        """
        if not self.gemini_api_key:
            raise RuntimeError("GEMINI_API_KEY가 설정되지 않았습니다.")

        import google.generativeai as genai

        genai.configure(api_key=self.gemini_api_key)
        model = genai.GenerativeModel(
            model_name="gemini-3.1-flash-lite",
            generation_config=genai.GenerationConfig(
                response_mime_type="application/json",
                response_schema=LLMSnippetResponse,
            ),
        )
        response = await asyncio.to_thread(model.generate_content, prompt)
        return LLMSnippetResponse.model_validate_json(response.text)

    async def _call_openai(self, prompt: str) -> LLMSnippetResponse:
        """OpenAI API 호출. response_format으로 Structured Output을 강제한다."""
        if not self.openai_api_key:
            raise RuntimeError("OPENAI_API_KEY가 설정되지 않았습니다.")

        from openai import AsyncOpenAI

        client = AsyncOpenAI(api_key=self.openai_api_key)
        response = await client.beta.chat.completions.parse(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            response_format=LLMSnippetResponse,
        )
        return response.choices[0].message.parsed

    async def generate_snippet(
        self,
        vuln_type: str,
        vuln_detail: str,
        server_type: str,
    ) -> dict:
        prompt = self._build_prompt(vuln_type, vuln_detail, server_type)

        for caller, name in (
            (self._call_gemini, "Gemini"),
            (self._call_openai, "OpenAI"),
        ):
            try:
                result = await caller(prompt)
                return result.model_dump()
            except Exception as exc:
                print(f"[LLM] {name} 호출 실패: {exc}, 다음 모델로 전환")

        return {
            "title": "자동 생성 실패",
            "code": "",
            "description": "",
            "confidence": 0.0,
        }


llm_client = LLMClient()
