from banco import Conexao

def transform_dic(tupla):
    dic = {}
    dic['id'] = tupla[0]
    dic['nome'] = tupla[1]
    dic['preço'] = tupla[2]
    dic['estoque'] = tupla[3]
    dic['categoria_id'] = tupla[4]
    return dic

class ProdutoRepositorio:

    def __init__(self, conexao: Conexao):
        self.cursor = conexao.cursor
        self.conexao = conexao.conexao

    def inserir_produto(self, nome, preco, estoque, categoria_id):
        self.cursor.execute(
            "INSERT INTO produtos (nome, preco, estoque, categoria_id) VALUES (?, ?, ?, ?)",
            (nome, preco, estoque, categoria_id)
            )
        
        self.conexao.commit()
        return self.cursor.lastrowid

    def listar_produtos(self):
        self.cursor.execute("SELECT * FROM produtos")

        resultados = self.cursor.fetchall()
        dados = []
        for resultado in resultados:
            dic = transform_dic(resultado)
            dados.append(dic)
        return dados

    def buscar_produto_por_id(self, id):
        self.cursor.execute("SELECT * FROM produtos WHERE id = ?", (id,))

        resultado = self.cursor.fetchone()

        if resultado is not None:
            dados = transform_dic(resultado)
            return dados