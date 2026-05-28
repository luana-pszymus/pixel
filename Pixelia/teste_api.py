import os

from dotenv import load_dotenv
from langchain_groq import ChatGroq

load_dotenv()

llm = ChatGroq(
    temperature=0.5,
    model_name="llama-3.3-70b-versatile",
    api_key=os.getenv("GROQ_API_KEY")
)

try:

    resposta = llm.invoke(
        "Diga apenas: conexão realizada com sucesso"
    )

    print("✅ API conectada!")

    print("\nResposta:\n")

    print(resposta.content)

except Exception as e:

    print("Erro:", e)