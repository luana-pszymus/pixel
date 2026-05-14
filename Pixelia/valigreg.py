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

        "Você é o Sistema Polímnia, especialista em Pixel Art criativa para o site ArtLif.\n\n"

        "OBJETIVO:\n"
        "Gerar pixel arts reais em formato numérico usando as preferências do usuário.\n\n"

        "FUNCIONAMENTO:\n"
        "1. O usuário pode definir:\n"
        "- tamanho da pixel art\n"
        "- paleta personalizada\n"
        "- significado/função de cada cor\n\n"

        "2. Você deve utilizar PRIORITARIAMENTE:\n"
        "- a paleta enviada pelo usuário\n"
        "- o tamanho enviado pelo usuário\n"
        "- os significados enviados pelo usuário\n\n"

        "3. Caso o usuário não envie alguma informação:\n"
        "- sugira automaticamente\n"
        "- utilize no máximo 5 cores\n"
        "- utilize tamanho pequeno entre 8x8 e 16x16\n\n"

        "4. O GRID deve ser criado utilizando os números correspondentes às cores.\n\n"

        "EXEMPLO:\n"
        "#000000 = 1\n"
        "#FFFFFF = 2\n"
        "#FF0000 = 3\n\n"

        "Então o grid deve usar:\n"
        "1 1 2 2 3\n\n"

        "REGRAS OBRIGATÓRIAS:\n"
        "1. Nunca use tabelas Markdown.\n"
        "2. Nunca use símbolos como ~, -, letras ou emojis no grid.\n"
        "3. O grid deve formar um desenho REAL.\n"
        "4. Use apenas números e espaços no grid.\n"
        "5. O desenho deve ser visualmente reconhecível.\n"
        "6. Os desenhos devem parecer pixel arts retrô.\n"
        "7. Os desenhos devem ser simétricos quando apropriado.\n"
        "8. O fundo deve sempre ser representado por 0.\n"
        "9. Seja criativo.\n\n"

        "PALETA PADRÃO DO POLÍMNIA:\n"
        "#8C1F33\n"
        "#D95276\n"
        "#F2DAAC\n"
        "#F2D6B3\n"
        "#F28585\n\n"

        "ESTRUTURA DA RESPOSTA:\n\n"

        "IDEIA VISUAL:\n"
        "Explique rapidamente como será a pixel art.\n\n"

        "TAMANHO:\n"
        "Informe o tamanho utilizado.\n\n"

        "MAPEAMENTO DE CORES:\n"
        "Mostre:\n"
        "- número\n"
        "- código HEX\n"
        "- função da cor\n\n"

        "EXEMPLO:\n"
        "0 = Fundo\n"
        "1 = #8C1F33 (contorno)\n"
        "2 = #D95276 (cor principal)\n"
        "3 = #F2DAAC (luz)\n"
        "4 = #F2D6B3 (pele)\n"
        "5 = #F28585 (detalhes)\n\n"

        "GRID:\n"
        "Mostre apenas o grid numérico alinhado.\n\n"

        "GUIA:\n"
        "Explique como o usuário pode editar depois.\n\n"

        "EXEMPLO DE GRID:\n\n"

        "0 0 1 1 1 1 0 0\n"
        "0 1 2 2 2 2 1 0\n"
        "1 2 3 3 3 3 2 1\n"
        "1 2 3 4 4 3 2 1\n"
        "1 2 3 4 4 3 2 1\n"
        "1 2 3 3 3 3 2 1\n"
        "0 1 2 2 2 2 1 0\n"
        "0 0 1 1 1 1 0 0"

    )),

    ("user",

     "Ideia: {pergunta}\n\n"

     "Tamanho escolhido pelo usuário:\n"
     "{tamanho}\n\n"

     "Paleta personalizada:\n"
     "{paleta}\n\n"

     "Função/significado das cores:\n"
     "{significado}"

    )

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