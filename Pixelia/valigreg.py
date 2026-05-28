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

    ("""
    Você é o Sistema Polímnia.

    Especialista em:
    - pixel art
    - direção de arte
    - teoria das cores
    - iluminação
    - consistência visual
    - arte para jogos indie

    OBJETIVO:
    Ajudar artistas a manter consistência visual.

    IMPORTANTE:
    - NÃO use markdown
    - NÃO use **
    - NÃO use listas enormes
    - NÃO escreva textos longos
    - NÃO explique demais
    - NÃO aja como professor
    - NÃO aja como chatbot

    As respostas devem parecer:
    - notas rápidas de direção artística
    - documentação visual de estúdio indie
    - guia artístico curto e técnico

    Sempre responda nesse formato:

    CONCEITO
    Máximo 2 linhas.

    PALETA
    Liste apenas:
    HEX → função da cor

    Exemplo:
    #8EB9FC → luz
    #274DEA → sombra

    ILUMINAÇÃO
    Máximo 2 linhas.

    SOMBRA
    Máximo 2 linhas.

    ESTILO
    Máximo 1 linha.

    EXTRA
    Máximo 1 sugestão útil.

    IMPORTANTE:
    Respostas curtas.
    Diretas.
    Visuais.
    Profissionais.
    """),

    ("user",

    """

    Ideia:
    {pergunta}

    Modo:
    {modo_ia}

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

@app.route('/editar_paleta/<int:id>', methods=['PUT'])
def editar_paleta(id):

    try:

        dados = request.json

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            UPDATE paletas
            SET nome=%s,
                cores=%s,
                significados=%s
            WHERE id=%s
            """,
            (
                dados.get("nome"),
                dados.get("cores"),
                dados.get("significados"),
                id
            )
        )

        conn.commit()

        cursor.close()
        conn.close()

        return jsonify({
            "mensagem": "Paleta atualizada!"
        })

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

        modo = dados.get("modo") or "tecnico"

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
        modos = {

            "tecnico":
            "Responda tecnicamente e profissionalmente.",

            "resumido":
            "Responda de forma curta e resumida.",

            "professor":
            "Explique de forma didática como um professor.",

            "detalhado":
            "Explique detalhadamente e profundamente.",

            "suporte":
            "Responda como suporte técnico profissional."
        }


        chain = prompt_template | llm

        response_groq = chain.invoke({

            "pergunta": pergunta,
            "tamanho": tamanho,
            "paleta": paleta,
            "significado": significado,
            "paletas_salvas": paletas_salvas,
            "modo_ia": modos.get(modo)

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
        # SALVAR PALETA GERADA PELA IA
        # =====================================================

        import re

        # procura HEX na resposta
        hex_cores = re.findall(
            r'#[0-9A-Fa-f]{6}',
            resposta_final
        )

        # remove duplicadas
        hex_cores = list(dict.fromkeys(hex_cores))

        # paleta padrão do sistema
        paleta_padrao = [
            "#8C1F33",
            "#D95276",
            "#F2DAAC",
            "#F2D6B3",
            "#F28585"
        ]

        # remove cores padrão
        cores_filtradas = [
            cor for cor in hex_cores
            if cor.upper() not in [p.upper() for p in paleta_padrao]
        ]

        # salva apenas se houver novas cores
        if len(cores_filtradas) > 0:

            cores_geradas = ", ".join(cores_filtradas)

            cursor.execute(
                """
                INSERT INTO paletas
                (nome, cores, significados, categoria)
                VALUES (%s, %s, %s, %s)
                """,
                (
                    pergunta,
                    cores_geradas,
                    significado,
                    "gerada_por_ia"
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