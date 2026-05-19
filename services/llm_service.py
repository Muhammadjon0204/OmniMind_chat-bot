from openai import AsyncOpenAI


class LLMService:
    def __init__(self, base_url: str, model_name: str):
        self.model_name = model_name
        self.client = AsyncOpenAI(
            base_url=base_url,
            api_key="not-needed"
        )

    async def generate_response(self, messages: list[dict]) -> str:
        try:
            response = await self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                temperature=0.25,
                max_tokens=250,
    extra_body={
        "thinking": False
    }
)
            message = response.choices[0].message

            content = getattr(message, "content", None)
            reasoning = getattr(message, "reasoning_content", None)

            if content and content.strip():
                return content.strip()

            if reasoning and reasoning.strip():
                return (
                    "Модель вернула только reasoning_content, но не final answer.\n\n"
                    "Лучше отключить thinking/reasoning mode в LM Studio или выбрать обычную Instruct-модель."
                )

            return "Модель вернула пустой ответ."

        except Exception as ex:
            print(f"LLM ERROR: {ex}")
            return (
                "Local AI server is unavailable.\n"
                "Please make sure LM Studio or Ollama is running."
            )