from flask import Flask, jsonify, request
import json

app = Flask(__name__)


# Carregar dados
def load_data(category_name: str) -> list:
    try:
        with open(category_name+'.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError as exception:
        print(f'Error on loading data: {exception}')
        return []
    except Exception as exception:
        print(f'Error on loading data: {exception}')
        return []


# Gravar Dados
def save_data(data: dict, category_name: str) -> bool:
    try:
        with open(category_name+'.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False)
            return True
    except Exception as exception:
        print(f'Error on saving data: {exception}')
        return False


# Rota root
@app.route('/')
def root():
    return 'Hello from School Manager!'


# Todos os estudantes
@app.route('/estudantes', methods=['GET'])
def get_estudantes():
    database = load_data('estudantes')
    return jsonify(database)


# Estudante por codigo
@app.route('/estudante/<int:codigo>', methods=['GET'])
def get_estudante(codigo):
    database = load_data('estudantes')
    for estudante in database:
        if estudante.get('codigo') == codigo:
            return jsonify(estudante)
    return 'Estudante não localizado!'


# Criar novo estudante
@app.route('/estudantes', methods=['POST'])
def add_estudante():
    database = load_data('estudantes')
    new_estudante = request.get_json()
    database.append(new_estudante)
    if save_data(database, 'estudantes'):
        return jsonify(new_estudante)
    return 'Erro ao adicionar o estudante!'


# Excluir estudante
@app.route('/estudantes/<int:codigo>', methods=['DELETE'])
def del_estudante(codigo):
    database = load_data('estudantes')
    for index, estudante in enumerate(database):
        if estudante.get('codigo') == codigo:
            del database[index]
            if save_data(database, 'estudantes'):
                return jsonify(estudante)
        return 'Erro ao excluir o estudante!'


# Editar estudante
@app.route('/estudantes/<int:codigo>', methods=['PUT', 'PATCH'])
def update_estudante(codigo):
    updated_estudante = request.get_json()
    database = load_data('estudantes')
    for index, estudante in enumerate(database):
        if estudante.get('codigo') == codigo:
            database[index].update(updated_estudante)
            save_data(database, 'estudantes')
            return jsonify(database[index])
    return 'Estudante não encontrado!'


# port 500 is already used in macOS
app.run(host='localhost', port=5001, debug=True)
