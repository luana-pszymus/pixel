import os
from flask import Flask, render_template, request, jsonify
from groq import Groq
from dotenv import load_dotenv
from database import get_connection, configurar_banco

load_dotenv()
configurar_banco()

app = Flask(__name__)
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/perguntar', methods=['POST'])
def perguntar():
    pergunta = request.json.get('pergunta')
    
    try:
        # 1. Busca resposta na Groq
        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": pergunta}]
        )
        resposta = completion.choices[0].message.content

        # 2. Salva no Banco de Dados
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO interacoes (usuario, pergunta, resposta) VALUES (%s, %s, %s)",
            ("Ana/Luana", pergunta, resposta)
        )
        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({'resposta': resposta})

    except Exception as e:
        return jsonify({'erro': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)