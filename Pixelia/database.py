import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

def get_connection():
    return psycopg2.connect(
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT")
    )

def configurar_banco():
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS interacoes (
                id SERIAL PRIMARY KEY,
                usuario VARCHAR(50),
                pergunta TEXT,
                resposta TEXT,
                data_hora TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        ''')
        
        conn.commit()
        cursor.close()
        conn.close()
        print("✅ Banco Postgres conectado e tabelas criadas!")
    except Exception as e:
        print(f"❌ Erro no Postgres: {e}")

if __name__ == "__main__":
    configurar_banco()