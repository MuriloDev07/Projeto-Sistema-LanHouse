from banco import Conexao

def transform_dic(tupla):
    dic = {}
    dic['id'] = tupla[0]
    dic['nome'] = tupla[1]
    return dic

class CategoriaRepositorio:

    def __init__(self, conexao: Conexao):
        self.cursor = conexao.cursor
        self.conexao = conexao.conexao

    def inserir_categoria(self, nome: str):
        self.cursor.execute("INSERT INTO categorias (nome) VALUES (?)", (nome,))

        self.conexao.commit()
        return self.cursor.lastrowid

    def listar_categorias(self):
        self.cursor.execute("SELECT * FROM categorias")

        resultados = self.cursor.fetchall()
        dados = []
        for resultado in resultados:
            dic = transform_dic(resultado)
            dados.append(dic)
        return dados

    def buscar_categoria_por_id(self, id):
        self.cursor.execute("SELECT * FROM categorias WHERE id = ?", (id,))

        resultado = self.cursor.fetchone()

        if resultado is not None:
            dados = transform_dic(resultado)
            return dados