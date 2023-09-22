from flask import Flask, jsonify, request
import json

app = Flask(__name__)


# Define uma constante com a estrutura para cada categoria
# O dicionário para cada chave é utilizado para obter os dados
# de forma dinâmica nas funções dados_input e editar_input
ESTRUTURA = {
    'estudantes': {
        'codigo': int,
        'nome': str,
        'cpf': str
    },
    'disciplinas': {
        'codigo': int,
        'nome': str
    },
    'professores': {
        'codigo': int,
        'nome': str,
        'cpf': str
    },
    'turmas': {
        'codigo': int,
        'cod_professor': int,
        'cod_disciplina': int,
    },
    'matriculas': {
        'codigo': int,
        'cod_turma': int,
        'cod_estudante': int
    }
}


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
def save_data(category_name: str, data: dict) -> bool:
    try:
        with open(category_name+'.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
            return True
    except Exception as exception:
        print(f'Error on saving data: {exception}')
        return False


# Essa função gerencia o auto incremento dos códigos em cada uma das categorias
# Esses dados são persistidos em um arquivo 'auto_incr_db.json'
# recebe a string categoria que será utilizada como chave na estrutura de dicionário
def auto_incr(categoria: str) -> int:
    # lê os dados de auto incremento
    database = load_data('auto_incr_db')
    # se o database é uma lista vazia
    if len(database) < 1:
        # inclui um objeto vazio no indice 0
        database.append({})
    # testa se a categoria existe no dicionário
    if categoria in database[0]:
        # incrementa o valor
        database[0][categoria] += 1
    # se a categoria não existe
    else:
        # define a chave/categoria com o valor inicial 1
        database[0][categoria] = 1
    # gravar os dados (database)
    save_data('auto_incr_db', database)
    # retorna o valor que será o próximo código para a categoria
    return database[0][categoria]


# Verifica se um codigo já existe na categoria
def codigo_existe(codigo: int, categoria: str) -> bool:
    database = load_data(categoria)
    for _, entidade in enumerate(database):
        if entidade['codigo'] == codigo:
            return True
    return False


# Verifica se um CPF já existe na categoria
# Exclui-se se for o código atual (caso de edicao)
def cpf_existe(codigo: int, cpf: str, categoria: str) -> bool:
    # lê os dados persistidos para a categoria informada
    database = load_data(categoria)
    # percorre cada um dos itens
    for _, entidade in enumerate(database):
        # se o item corrente for igual ao código passado
        if entidade['codigo'] != codigo and entidade['cpf'] == cpf:
            # retorna {index, nome} se a chave nome existir
            return True
    # Caso o loop for termine sem encontrar o código, retorna o index = -1
    return False


# manipula e verifica se o codigo(valor) existe na categoria dependente
def relacao_existe(categoria: str, codigo: int) -> bool:
    # testa se o código existe na categoria de relacao
    if codigo_existe(codigo, categoria):
        return True
    return False


# inserir um novo registro
# recebe a string categoria para definir em qual estrutura o registro será armazenado
def inserir(categoria: str, dados: dict) -> dict | str:
    entidade_dados = {}
    chaves = ESTRUTURA[categoria].keys()
    database = load_data(categoria)

    for chave in chaves:
        if chave != 'codigo':
            try:
                # se o tipo da chave for int, converte
                if ESTRUTURA[categoria][chave] == int:
                    entidade_dados[chave] = int(dados[chave])
                else:
                    entidade_dados[chave] = dados[chave]
                # Verifica se valor é vazio
                print(chave)
                if len(str(entidade_dados[chave]).strip()) == 0:
                    return f'O valor de [ {chave} ] não pode ser vazio.'
                # Testa duplicidade de CPF
                if chave == 'cpf':
                    if cpf_existe(-1, entidade_dados[chave], categoria):
                        return f'O CPF [ {entidade_dados[chave]} ] já existe!'
                if chave.startswith('cod_'):
                    categoria_relacao = chave.replace(
                        'cod_', '') + ('s' if not chave.endswith('r') else 'es')
                    if not relacao_existe(categoria_relacao, entidade_dados[chave]):
                        return f'Código [ {entidade_dados[chave]} ] não existe em {categoria_relacao}!'

            except KeyError as key:
                entidade_dados = None
                return f'Chave [ {key} ] ausente.'
            except Exception as exception:
                entidade_dados = None
                return f'Erro {exception}'

    if entidade_dados:
        nova_entidade = {}

        nova_entidade['codigo'] = auto_incr(categoria)
        nova_entidade.update(entidade_dados)
        database.append(nova_entidade)
        save_data(categoria, database)
        return nova_entidade
    return 'Erro ao inserir...'


# editar um novo registro
# recebe a string categoria para definir em qual estrutura o registro será armazenado
def editar(categoria: str, codigo: int, dados: dict) -> dict | str:
    entidade_dados = {}
    chaves = ESTRUTURA[categoria].keys()
    database = load_data(categoria)

    for chave in chaves:
        if chave != 'codigo':
            try:
                # se o tipo da chave for int, converte
                if ESTRUTURA[categoria][chave] == int:
                    entidade_dados[chave] = int(dados[chave])
                else:
                    entidade_dados[chave] = dados[chave]
                # Verifica se valor é vazio
                if len(str(entidade_dados[chave]).strip()) == 0:
                    return f'O valor de [ {chave} ] não pode ser vazio.'
                # Testa duplicidade de CPF
                if chave == 'cpf':
                    if cpf_existe(codigo, entidade_dados[chave], categoria):
                        return f'O CPF [ {entidade_dados[chave]} ] já existe!'
                if chave.startswith('cod_'):
                    categoria_relacao = chave.replace(
                        'cod_', '') + ('s' if not chave.endswith('r') else 'es')
                    if not relacao_existe(categoria_relacao, entidade_dados[chave]):
                        return f'Código [ {entidade_dados[chave]} ] não existe em {categoria_relacao}!'

            except KeyError as key:
                entidade_dados = None
                return f'Chave [ {key} ] ausente.'
            except Exception as exception:
                entidade_dados = None
                return f'Erro {exception}'

    if entidade_dados:
        for index, entidade in enumerate(database):
            if entidade['codigo'] == codigo:

                database[index].update(entidade_dados)
                save_data(categoria, database)
                return database[index]
    return 'Erro ao atualizar...'


# listar registros
# recebe a string categoria
def obter_todos(categoria: str) -> list:
    return load_data(categoria)


# obter registro
def obter_registro(categoria: str, codigo: int) -> list:
    database = load_data(categoria)
    for entidade in database:
        if entidade['codigo'] == codigo:
            return entidade
    return []


# excluir um registro
# recebe a string categoria
def excluir(categoria: str, codigo: int) -> None:
    database = load_data(categoria)

    for index, entidade in enumerate(database):
        if entidade['codigo'] == codigo:
            database.pop(index)
            save_data(categoria, database)
            return entidade
    return f'Código [ {codigo} ] não existe!'


# Rota root
@app.route('/')
def root():
    return 'Hello from School Manager!'


# Obter todos os estudantes
@app.route('/estudantes', methods=['GET'])
def get_estudantes():
    return jsonify(obter_todos('estudantes'))


# Estudante por codigo
@app.route('/estudante/<int:codigo>', methods=['GET'])
def get_estudante(codigo):
    return jsonify(obter_registro('estudantes', codigo))


# Criar novo estudante
@app.route('/estudantes', methods=['POST'])
def create_estudante():
    new_estudante = request.get_json()
    return jsonify(inserir('estudantes', new_estudante))


# Excluir estudante
@app.route('/estudante/<int:codigo>', methods=['DELETE'])
def delete_estudante(codigo):
    return excluir('estudantes', codigo)


# Editar estudante
@app.route('/estudante/<int:codigo>', methods=['PUT', 'PATCH'])
def update_estudante(codigo):
    new_estudante = request.get_json()
    return jsonify(editar('estudantes', codigo, new_estudante))


# Professores

# Obter todos os professores
@app.route('/professores', methods=['GET'])
def get_professores():
    return jsonify(obter_todos('professores'))


# professor por codigo
@app.route('/professor/<int:codigo>', methods=['GET'])
def get_professor(codigo):
    return jsonify(obter_registro('professores', codigo))


# Criar novo professor
@app.route('/professores', methods=['POST'])
def create_professor():
    new_professor = request.get_json()
    return jsonify(inserir('professores', new_professor))


# Excluir professor
@app.route('/professor/<int:codigo>', methods=['DELETE'])
def delete_professor(codigo):
    return excluir('professores', codigo)


# Disciplinas

# Obter todos os disciplinas
@app.route('/disciplinas', methods=['GET'])
def get_disciplinas():
    return jsonify(obter_todos('disciplinas'))


# disciplina por codigo
@app.route('/disciplina/<int:codigo>', methods=['GET'])
def get_disciplina(codigo):
    return jsonify(obter_registro('disciplinas', codigo))


# Criar novo disciplina
@app.route('/disciplinas', methods=['POST'])
def create_disciplina():
    new_disciplina = request.get_json()
    return jsonify(inserir('disciplinas', new_disciplina))


# Excluir disciplina
@app.route('/disciplina/<int:codigo>', methods=['DELETE'])
def delete_disciplina(codigo):
    return excluir('disciplinas', codigo)


# Editar disciplina
@app.route('/disciplina/<int:codigo>', methods=['PUT', 'PATCH'])
def update_disciplina(codigo):
    new_disciplina = request.get_json()
    return jsonify(editar('disciplinas', codigo, new_disciplina))


# turmas

# Obter todos os turmas
@app.route('/turmas', methods=['GET'])
def get_turmas():
    return jsonify(obter_todos('turmas'))


# turma por codigo
@app.route('/turma/<int:codigo>', methods=['GET'])
def get_turma(codigo):
    return jsonify(obter_registro('turmas', codigo))


# Criar novo turma
@app.route('/turmas', methods=['POST'])
def create_turma():
    new_turma = request.get_json()
    return jsonify(inserir('turmas', new_turma))


# Excluir turma
@app.route('/turma/<int:codigo>', methods=['DELETE'])
def delete_turma(codigo):
    return excluir('turmas', codigo)


# Editar turma
@app.route('/turma/<int:codigo>', methods=['PUT', 'PATCH'])
def update_turma(codigo):
    new_turma = request.get_json()
    return jsonify(editar('turmas', codigo, new_turma))


# matriculas

# Obter todos os matriculas
@app.route('/matriculas', methods=['GET'])
def get_matriculas():
    return jsonify(obter_todos('matriculas'))


# matricula por codigo
@app.route('/matricula/<int:codigo>', methods=['GET'])
def get_matricula(codigo):
    return jsonify(obter_registro('matriculas', codigo))


# Criar novo matricula
@app.route('/matriculas', methods=['POST'])
def create_matricula():
    new_matricula = request.get_json()
    return jsonify(inserir('matriculas', new_matricula))


# Excluir matricula
@app.route('/matricula/<int:codigo>', methods=['DELETE'])
def delete_matricula(codigo):
    return excluir('matriculas', codigo)


# Editar matricula
@app.route('/matricula/<int:codigo>', methods=['PUT', 'PATCH'])
def update_matricula(codigo):
    new_matricula = request.get_json()
    return jsonify(editar('matriculas', codigo, new_matricula))


# port 500 is already used in macOS
app.run(host='localhost', port=5001, debug=True)
