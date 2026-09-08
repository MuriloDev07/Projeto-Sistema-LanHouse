import sqlite3

class Conexao:
    def __init__(self, nome=":memory:"):
        self.nome = nome if nome == ":memory:" else f"{nome}.db"
        self.conexao = sqlite3.connect(self.nome)
        self.cursor = self.conexao.cursor()

    def criar_tabelas(self):
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS categorias (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL UNIQUE
        )
        """)

        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS produtos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        preco FLOAT NOT NULL,
        estoque INTEGER NOT NULL,
        categoria_id INTEGER NOT NULL,
        FOREIGN KEY (categoria_id) REFERENCES categorias(id)
        )
        """)

        self.conexao.commit()