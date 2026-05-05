import os
from flask import Flask, render_template, request, jsonify
from groq import Groq
from dotenv import load_dotenv
from database import get_connection, configurar_banco

load_dotenv()
configurar_banco()

app = Flask(__name__)
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

PALETA = "#8C1F33, #D95276, #F2DAAC, #F2D6B3, #F28585"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/perguntar', methods=['POST'])
def perguntar():
    pergunta = request.json.get('pergunta')
    try:
        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {
                    "role": "system", 
                    "content": (
                        "Você é o Sistema Polímnia. Sua paleta é: " + PALETA + ". "
                        "Responda com: 1) LEGENDA NUMERADA. 2) MAPA DE GRID (numérico). 3) GUIA TÉCNICO. "
                        "Mantenha o grid alinhado."
                    )
                },
                {"role": "user", "content": pergunta}
            ],
            temperature=0.3
        )
        resposta = completion.choices[0].message.content
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO interacoes (usuario, pergunta, resposta) VALUES (%s, %s, %s)", ("Equipe Polímnia", pergunta, resposta))
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({'resposta': resposta})
    except Exception as e:
        return jsonify({'erro': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)