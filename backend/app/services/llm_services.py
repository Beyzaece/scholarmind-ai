import os
from dotenv import load_dotenv
from google import genai
from google.genai.errors import ServerError


load_dotenv()
 

client=genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)
def generate_answer(
    question: str,
    context_chunks: list[str]
) -> str:

    context = "\n\n---\n\n".join(context_chunks)

    prompt = f"""
Sen akademik dokümanlar üzerinde çalışan bir araştırma asistanısın.

Yalnızca aşağıdaki kaynak metinleri kullanarak soruyu cevapla.
Cevap kaynaklarda bulunmuyorsa açıkça:
"Bu bilgi yüklenen dokümanlarda bulunamadı."
de.

KAYNAK METİNLER:
{context}

SORU:
{question}

CEVAP:
"""

    try:
        response = client.models.generate_content(
            model="gemini-3.5-flash",
            contents=prompt
        )

        return response.text

    except ServerError as error:
        if error.code == 503:
            return (
                "Yapay zekâ servisi şu anda yoğun. "
                "Lütfen birkaç saniye sonra tekrar deneyin."
            )

        raise