import os
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate

from database import get_connection, configurar_banco

load_dotenv()
configurar_banco()

app = Flask(__name__)

llm = ChatGroq(
    temperature=0.4, 
    model_name="llama-3.1-8b-instant",
    api_key=os.getenv("GROQ_API_KEY")
)

# PROMPT REFORÇADO: Bloqueia tabelas Markdown e foca em texto puro
prompt_template = ChatPromptTemplate.from_messages([
    ("system", (
        "Você é o Sistema Polímnia, especialista em Pixel Art técnica para o site ArtLif.\n\n"
        "REGRAS DE FORMATO (CRUCIAL):\n"
        "1. PROIBIDO usar tabelas Markdown (ex: |---|).\n"
        "2. Se o usuário não definiu nada, sugira um tamanho pequeno (máximo 16x16) para não travar o site.\n"
        "3. MAPA DE GRID: Deve ser um bloco de código de texto puro contendo apenas NÚMEROS e ESPAÇOS.\n\n"
        "ESTRUTURA DA RESPOSTA:\n"
        "1) PARÂMETROS TÉCNICOS: (Tamanho sugerido, Paleta de 5 cores HEX e funções).\n"
        "2) MAPA DE GRID: Bloco de código com o desenho numérico.\n"
        "3) GUIA MAKER: Dicas para usar EVA/Biscuit."
    )),
    ("user", "Ideia: {pergunta}. Técnica Atual: [Tamanho: {tamanho}, Paleta: {paleta}, Significados: {significado}]")
])

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/perguntar', methods=['POST'])
def perguntar():
    dados = request.json
    pergunta = dados.get('pergunta')
    
    # Se os campos estiverem vazios no front, passamos 'Não definido' para a IA sugerir
    tamanho = dados.get('tamanho') or "Não definido (sugira algo pequeno)"
    paleta = dados.get('paleta') or "Não definida (sugira 5 cores)"
    significado = dados.get('significado') or "Não definido"

    try:
        chain = prompt_template | llm
        response = chain.invoke({
            "tamanho": tamanho,
            "paleta": paleta,
            "significado": significado,
            "pergunta": pergunta
        })
        resposta = response.content

        # Salva no banco de dados
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO interacoes (usuario, pergunta, resposta) VALUES (%s, %s, %s)", 
            ("Equipe Polímnia", pergunta, resposta)
        )
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({'resposta': resposta})
    except Exception as e:
        return jsonify({'erro': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)