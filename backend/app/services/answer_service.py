import time

from google.genai.errors import ServerError

from app.services.llm_services import generate_answer


def generate_answer_with_retry(
    question: str,
    context_chunks: list[str],
    max_retry: int = 3
) -> str:

    for attempt in range(max_retry):
        try:
            return generate_answer(
                question=question,
                context_chunks=context_chunks
            )

        except ServerError:
            if attempt == max_retry - 1:
                raise

            time.sleep(2)