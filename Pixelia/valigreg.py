import os
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv

from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate

from database import get_connection, configurar_banco

load_dotenv()
configurar_banco()

app = Flask(__name__)

# MODELO GROQ
llm = ChatGroq(
    temperature=0.4,
    model_name="llama-3.1-8b-instant",
    api_key=os.getenv("GROQ_API_KEY")
)

# PROMPT PRINCIPAL
prompt_template = ChatPromptTemplate.from_messages([
    ("system", (
        "Você é o Sistema Polímnia, especialista em Pixel Art criativa.\n\n"

        "OBJETIVO PRINCIPAL:\n"
        "O usuário descreve o que deseja criar e você sugere automaticamente:\n"
        "- estilo visual\n"
        "- tamanho ideal\n"
        "- paleta de cores\n"
        "- função de cada cor\n"
        "- grid numérico da pixel art\n\n"

        "REGRAS IMPORTANTES:\n"
        "1. Nunca use tabelas Markdown.\n"
        "2. Use apenas texto puro.\n"
        "3. Se o usuário não definir tamanho, escolha automaticamente um tamanho pequeno.\n"
        "4. O grid deve conter apenas números e espaços.\n"
        "5. Seja criativo e artístico.\n\n"

        "ESTRUTURA DA RESPOSTA:\n\n"

        "IDEIA VISUAL:\n"
        "Explique rapidamente como será a pixel art.\n\n"

        "PALETA SUGERIDA:\n"
        "Liste as cores HEX e explique para que serve cada cor.\n\n"

        "GRID:\n"
        "Mostre o mapa numérico alinhado.\n\n"

    )),

    ("user",
     "Ideia: {pergunta}\n"
     "Tamanho opcional: {tamanho}\n"
     "Paleta opcional: {paleta}\n"
     "Significados opcionais: {significado}")
])

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/perguntar', methods=['POST'])
def perguntar():

    dados = request.json

    pergunta = dados.get('pergunta')

    tamanho = dados.get('tamanho') or "Não definido"
    paleta = dados.get('paleta') or "Não definida"
    significado = dados.get('significado') or "Não definido"

    try:

        chain = prompt_template | llm

        response = chain.invoke({
            "pergunta": pergunta,
            "tamanho": tamanho,
            "paleta": paleta,
            "significado": significado
        })

        resposta = response.content

        # SALVAR NO BANCO
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO interacoes
            (usuario, pergunta, resposta)
            VALUES (%s, %s, %s)
            """,
            ("Equipe Polímnia", pergunta, resposta)
        )

        conn.commit()

        cursor.close()
        conn.close()

        return jsonify({
            "resposta": resposta
        })

    except Exception as e:
        return jsonify({
            "erro": str(e)
        }), 500

if __name__ == '__main__':
    app.run(debug=True)

    #eu quero que a pessoa possa escolher o tamanho da pixel arte que ela queixa tipo 10x10 3x3 8x8 etc, ela possa mandar a paleta de cores dela e ele guarde a paleta dela, ele criei o grid com base na tabela de cores, que a pessoa possa especificar tambem o que cada cor da tabela dela serve exemplo
 #F2D6B3 cor serve para pele, dar a grid exemplo cor #00000 é = 1 #ffffff =2 etc com as cores da paleta dela, paleta do site Poliminia #8C1F33
#D95276

#F2DAAC

#F2D6B3

#F28585