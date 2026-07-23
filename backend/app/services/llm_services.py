import os
from dotenv import load_dotenv
from google import genai
from google.genai.errors import ServerError
import time


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
Sen ScholarMind AI adlı akademik araştırma asistanısın.

Görevin yalnızca sana verilen kaynak metinlerini kullanarak soruyu cevaplamaktır.

Kurallar:

1. Asla kendi bilgini kullanma.
2. Yalnızca verilen kaynaklardan çıkarım yap.
3. Kaynaklarda cevap yoksa şu ifadeyi kullan:
   "Bu bilgi yüklenen dokümanlarda bulunamadı."

4. Bilgiden emin değilsen tahmin yürütme.

5. Cevabı açık, teknik ve akademik bir dille yaz.

6. Gerekirse maddeler halinde açıkla.

7. Gereksiz tekrar yapma.

8. Kaynaklarda çelişki varsa bunu belirt.

9. Kaynak metnini aynen kopyalama; kendi cümlelerinle özetleyerek açıkla.

10. Soru Türkçeyse Türkçe, İngilizceyse İngilizce cevap ver.

-----------------------------
KAYNAK METİNLER
-----------------------------

{context}

-----------------------------
SORU
-----------------------------

{question}

-----------------------------
CEVAP
-----------------------------
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

def generate_search_queries(
    question: str,
    query_count: int = 3
) -> list[str]:

    prompt = f"""
Sen akademik dokümanlarda arama yapmak için sorgu üreten bir asistansın.

Görevin kullanıcının sorusunu cevaplamak değil.
Görevin, aynı bilgiyi bulabilecek farklı arama sorguları üretmektir.

Kurallar:
- Toplam {query_count} sorgu üret.
- İlk sorgu kullanıcının orijinal sorusu olsun.
- Diğer sorgular aynı anlamı farklı ifadelerle anlatsın.
- Kısaltmalar varsa açık hâlini kullanabilirsin.
- Gereksiz açıklama yazma.
- Numara veya madde işareti kullanma.
- Her satıra yalnızca bir sorgu yaz.

KULLANICI SORUSU:
{question}
"""

    response = client.models.generate_content(
        model="gemini-3.5-flash",
        contents=prompt
    )

    response_text = response.text.strip()

    generated_queries = [
        line.strip()
        for line in response_text.splitlines()
        if line.strip()
    ]

    queries = [question]

    for query in generated_queries:
        if query.lower() != question.lower():
            queries.append(query)

        if len(queries) == query_count:
            break

    return queries