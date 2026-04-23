from google import genai
import os

# 1. Configuração
# Dica: Você também pode definir uma variável de ambiente chamada GEMINI_API_KEY
CHAVE_API = "AIzaSyDULHl3mAzJoYPY42mWETsoQDVaUMRzMgM"
client = genai.Client(api_key=CHAVE_API)

def testar_comunicacao():
    try:
        print("Enviando requisição (SDK Novo)...")
        
        # 2. Chamada simplificada
        response = client.models.generate_content(
            model="gemini-1.5-flash", 
            contents="Responda apenas: Conexão 2.0 estabelecida!"
        )
        
        # 3. Exibir o retorno
        print("\n--- Resposta da API ---")
        print(response.text)
        print("-----------------------")
        
    except Exception as e:
        print(f"Erro ao conectar na API: {e}")

if __name__ == "__main__":
    testar_comunicacao()