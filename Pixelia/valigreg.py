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
        # Chamada técnica à IA Polímnia
        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {
                    "role": "system", 
                    "content": (
                        "Você é o Sistema Polímnia, especialista técnico em padronização de Pixel Art. "
                        "Sua tarefa é converter conceitos em guias práticos. "
                        "Sempre forneça: 1) Paletas em HEX. 2) Regras de iluminação/sombreamento. "
                        "3) Sugestão de resolução (ex: 16x16, 32x32). Seja objetivo e técnico."
                    )
                },
                {"role": "user", "content": pergunta}
            ],
            temperature=0.3
        )
        resposta = completion.choices[0].message.content

        # Salvando a diretriz no PostgreSQL (Persistência)
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