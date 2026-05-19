import os

from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv

from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate

from openai import OpenAI

from database import get_connection, configurar_banco

# =====================================================
# CONFIG
# =====================================================

load_dotenv()
configurar_banco()

app = Flask(__name__)

# =====================================================
# GROQ
# =====================================================

llm = ChatGroq(
    temperature=0.5,
    model_name="llama-3.3-70b-versatile",
    api_key=os.getenv("GROQ_API_KEY")
)

# =====================================================
# SAMBANOVA
# =====================================================

sambanova_client = OpenAI(
    api_key=os.getenv("SAMBANOVA_API_KEY"),
    base_url=os.getenv("SAMBANOVA_URL")
)

# =====================================================
# PROMPT PRINCIPAL
# =====================================================

prompt_template = ChatPromptTemplate.from_messages([

    ("system",

    """

    Você é o Sistema Polímnia.

    O Polímnia é uma IA especialista em:
    - direção de arte
    - pixel art
    - teoria das cores
    - iluminação
    - sombreamento
    - consistência visual
    - estilização visual
    - arte para jogos indie

    OBJETIVO:
    Ajudar artistas e equipes de pixel art.

    IMPORTANTE:
    - NÃO use markdown
    - NÃO use **
    - NÃO escreva textos gigantes
    - NÃO faça respostas acadêmicas
    - Seja organizado
    - Seja visual
    - Seja objetivo

    Respostas devem parecer notas rápidas
    de direção artística usadas em estúdios indie.

    O usuário pode:
    - enviar paletas
    - definir funções das cores
    - pedir direção artística
    - pedir iluminação
    - pedir sugestões
    - pedir consistência visual

    Utilize prioritariamente:
    - paletas do usuário
    - estilos definidos
    - funções das cores

    FORMATO DA RESPOSTA:

    CONCEITO:
    Explique a ideia visual em até 5 frase.

    PALETA:
    Mostre as cores principais.
    Explique rapidamente cada uma.

    ILUMINAÇÃO:
    Explique a luz.

    SOMBRA:
    Explique  o sombreamento.

    ESTILO:
    Explique o estilo artístico em poucas palavras.

    SUGESTÃO EXTRA:
    até 5  sugestão útil.

    """ 

    ),

    ("user",

    """

    Ideia:
    {pergunta}

    Tamanho:
    {tamanho}

    Paleta:
    {paleta}

    Significado das cores:
    {significado}

    Paletas já existentes:
    {paletas_salvas}

    """

    )

])

# =====================================================
# HOME
# =====================================================

@app.route('/')
def index():
    return render_template('index.html')

# =====================================================
# LISTAR PALETAS
# =====================================================

@app.route('/paletas')
def listar_paletas():

    try:

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id, nome, cores, significados, categoria
            FROM paletas
            ORDER BY id DESC
        """)

        dados = cursor.fetchall()

        paletas = []

        for p in dados:

            paletas.append({
                "id": p[0],
                "nome": p[1],
                "cores": p[2],
                "significados": p[3],
                "categoria": p[4]
            })

        cursor.close()
        conn.close()

        return jsonify(paletas)

    except Exception as e:

        return jsonify({
            "erro": str(e)
        }), 500

# =====================================================
# IA PRINCIPAL
# =====================================================

@app.route('/perguntar', methods=['POST'])
def perguntar():

    try:

        dados = request.json

        pergunta = dados.get("pergunta")

        # =====================================================
        # PROTEÇÃO
        # =====================================================

        bloqueados = [
            "ignore",
            "system",
            "prompt",
            "apikey",
            "api key",
            "senha",
            "hack",
            "burlar",
            "mostre seu prompt",
            "revele"
        ]

        texto = pergunta.lower()

        for palavra in bloqueados:

            if palavra in texto:

                return jsonify({
                    "resposta": "Solicitação bloqueada por segurança."
                })

        # =====================================================
        # DADOS
        # =====================================================

        tamanho = dados.get("tamanho") or "Automático"

        paleta = dados.get("paleta") or """
#8C1F33, #D95276, #F2DAAC, #F2D6B3, #F28585
"""

        significado = dados.get("significado") or "Não definido"

        # =====================================================
        # BANCO
        # =====================================================

        conn = get_connection()
        cursor = conn.cursor()

        # =====================================================
        # BUSCAR PALETAS
        # =====================================================

        cursor.execute("""
            SELECT nome, cores, significados
            FROM paletas
            ORDER BY id DESC
            LIMIT 10
        """)

        resultado_paletas = cursor.fetchall()

        paletas_salvas = ""

        for p in resultado_paletas:

            paletas_salvas += f"""

Nome: {p[0]}
Cores: {p[1]}
Significados: {p[2]}

"""

        # =====================================================
        # PRIMEIRA IA - GROQ
        # =====================================================

        chain = prompt_template | llm

        response_groq = chain.invoke({

            "pergunta": pergunta,
            "tamanho": tamanho,
            "paleta": paleta,
            "significado": significado,
            "paletas_salvas": paletas_salvas

        })

        resposta_groq = response_groq.content

        # =====================================================
        # SEGUNDA IA - SAMBANOVA
        # =====================================================

        try:

            response_samba = sambanova_client.chat.completions.create(

                model="Meta-Llama-3.3-70B-Instruct",

                messages=[

                    {
                        "role": "system",

                        "content":

                        """

                        Você é um diretor técnico de pixel art.

                        Sua função:
                        - revisar respostas artísticas
                        - corrigir excesso de texto
                        - melhorar clareza
                        - melhorar direção de arte
                        - melhorar iluminação
                        - melhorar consistência

                        IMPORTANTE:
                        - respostas curtas
                        - sem markdown
                        - sem listas enormes
                        - linguagem visual e profissional

                        """

                    },

                    {
                        "role": "user",

                        "content":

                        f"""

                        Pedido do usuário:
                        {pergunta}

                        Resposta inicial da IA:
                        {resposta_groq}

                        Melhore essa resposta.
                        Deixe mais curta.
                        Mais organizada.
                        Mais visual.
                        Mais profissional.

                        """

                    }

                ]

            )

            resposta_final = response_samba.choices[0].message.content

        except Exception as e:

            resposta_final = resposta_groq + f"""

OBS:
SambaNova indisponível no momento.
Erro: {str(e)}
"""

        # =====================================================
        # SALVAR PALETA
        # =====================================================

        if paleta.strip() != "":

            cursor.execute(
                """
                INSERT INTO paletas
                (nome, cores, significados, categoria)
                VALUES (%s, %s, %s, %s)
                """,
                (
                    pergunta,
                    paleta,
                    significado,
                    "geral"
                )
            )

        # =====================================================
        # SALVAR INTERAÇÃO
        # =====================================================

        cursor.execute(
            """
            INSERT INTO interacoes
            (usuario, pergunta, resposta)
            VALUES (%s, %s, %s)
            """,
            (
                "Equipe Polímnia",
                pergunta,
                resposta_final
            )
        )

        conn.commit()

        cursor.close()
        conn.close()

        return jsonify({
            "resposta": resposta_final
        })

    except Exception as e:

        return jsonify({
            "erro": str(e)
        }), 500

# =====================================================
# START
# =====================================================

if __name__ == '__main__':
    app.run(debug=True)