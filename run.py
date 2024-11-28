from flask import Flask, request, jsonify
from pymongo import MongoClient

app = Flask(__name__)

# URL de conexão com o MongoDB Atlas
MONGO_URI = "mongodb+srv://medicalize:QbMsr5u38WP5zpxU@medicalize.6s4wv.mongodb.net/?retryWrites=true&w=majority&appName=Medicalize"
client = MongoClient(MONGO_URI)
db = client['medications']  # Nome do banco de dados
interactions_collection = db['interactions']  # Nome da coleção de interações

@app.route('/check-interactions', methods=['POST'])
def check_interactions():
    data = request.get_json()

    # Validação da entrada
    if not data or "medications" not in data:
        return jsonify({"error": "O campo 'medications' é obrigatório."}), 400
    
    medications = data["medications"]

    if not isinstance(medications, list) or len(medications) < 2 or len(medications) > 5:
        return jsonify({
            "error": "Por favor, insira entre 2 e 5 medicamentos."
        }), 400

    # Verificar interações no MongoDB
    interactions = []
    for i in range(len(medications)):
        for j in range(i + 1, len(medications)):
            # Normalizar os nomes dos medicamentos para evitar erros de capitalização
            med1 = medications[i].strip().title()  # Capitalizando e removendo espaços
            med2 = medications[j].strip().title()  # Capitalizando e removendo espaços

            # Buscar no MongoDB o registro do primeiro medicamento
            med1_record = interactions_collection.find_one({"medicamento": med1})
            if med1_record:  # Se o medicamento foi encontrado
                # Verificar se med2 está nas interações de med1
                if med2 in med1_record["interacoes"]:
                    interactions.append({"pair": [med1, med2]})

            # Buscar no MongoDB o registro do segundo medicamento
            med2_record = interactions_collection.find_one({"medicamento": med2})
            if med2_record:  # Se o medicamento foi encontrado
                # Verificar se med1 está nas interações de med2
                if med1 in med2_record["interacoes"]:
                    interactions.append({"pair": [med1, med2]})

    # Retornar resposta com ou sem interações
    if not interactions:
        return jsonify({"message": "Nenhuma interação de risco encontrada."})

    return jsonify({
        "message": "Interações de risco identificadas.",
        "interactions": interactions
    })

if __name__ == '__main__':
   app.run(debug=True, host='0.0.0.0', port=8080)
