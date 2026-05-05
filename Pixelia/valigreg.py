import os
import sys
from groq import Groq
from dotenv import load_dotenv

# 1. Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

# 2. Pega a chave de forma segura (sem expor no código)
CHAVE_GROQ = os.getenv("GROQ_API_KEY")

def validar_polimnia():
    print("--- CONEXÃO POLÍMNIA (VIA GROQ CLOUD 2026) ---")
    
    if not CHAVE_GROQ:
        print("\n ERRO: Chave API não encontrada no arquivo .env!")
        print("Crie um arquivo chamado .env e coloque: GROQ_API_KEY=sua_chave")
        return

    try:
        # Inicializa o cliente com a chave protegida
        client = Groq(api_key=CHAVE_GROQ)
        
        print("Solicitando resposta da IA...")
        
        # Chamada ao modelo que validamos anteriormente
        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {
                    "role": "user", 
                    "content": "Confirme a conexão: Sistema Polímnia 2026 Online via Groq!"
                }
            ],
            temperature=0.5
        )

        print("\n[RESPOSTA RECEBIDA]:")
        print(f">>> {completion.choices[0].message.content}")
        print("\n-------------------------------------------------")
        print("STATUS: CONEXÃO VALIDADA E SEGURA!")

    except Exception as e:
        print(f"\n Erro técnico ao conectar: {e}")

def salvar_no_postgres(pergunta, resposta):
    try:
        # Importe a função de conexão do database.py ou use direto aqui
        from database import get_connection
        conn = get_connection()
        cursor = conn.cursor()
        
        # ITEM 3: Inserção de dados
        sql = "INSERT INTO interacoes (usuario, pergunta, resposta) VALUES (%s, %s, %s)"
        cursor.execute(sql, ("Ana/Luana", pergunta, resposta))
        
        conn.commit()
        cursor.close()
        conn.close()
        print("Log salvo no PostgreSQL!")
    except Exception as e:
        print(f"Erro ao salvar: {e}")

if __name__ == "__main__":
    validar_polimnia()

    