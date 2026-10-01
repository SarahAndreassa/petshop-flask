"""Tudo que fala com o MySQL fica aqui.

As outras partes do projeto só chamam as funções abaixo, sem se
preocupar em abrir/fechar conexão.
"""
import os

import mysql.connector
from dotenv import load_dotenv

# Lê o arquivo .env e deixa os valores disponíveis em os.environ.
# Assim a senha NÃO fica escrita dentro do código.
load_dotenv()


def _config(com_banco=True):
    dados = {
        "host": os.environ.get("DB_HOST", "localhost"),
        "user": os.environ.get("DB_USER", "root"),
        "password": os.environ.get("DB_PASSWORD", ""),
    }
    if com_banco:
        dados["database"] = os.environ.get("DB_NAME", "petshop")
    return dados


def conectar():
    """Abre uma conexão com o banco 'petshop'."""
    return mysql.connector.connect(**_config())


def buscar_todos(sql, valores=()):
    """Roda um SELECT e devolve uma lista de dicionários.

    Exemplo de linha: {"id": 1, "nome": "Ana", "telefone": "1199..."}
    Por isso nos templates usamos cliente.nome em vez de cliente[1].
    """
    conexao = conectar()
    cursor = conexao.cursor(dictionary=True)
    cursor.execute(sql, valores)
    linhas = cursor.fetchall()
    cursor.close()
    conexao.close()
    return linhas


def buscar_um(sql, valores=()):
    """Roda um SELECT e devolve só a primeira linha (ou None)."""
    linhas = buscar_todos(sql, valores)
    return linhas[0] if linhas else None


def executar(sql, valores=()):
    """Roda INSERT / UPDATE / DELETE e salva (commit) no banco."""
    conexao = conectar()
    cursor = conexao.cursor()
    cursor.execute(sql, valores)
    conexao.commit()
    novo_id = cursor.lastrowid
    cursor.close()
    conexao.close()
    return novo_id


def criar_tabelas():
    """Cria o banco e as tabelas (se ainda não existirem) lendo o schema.sql."""
    caminho = os.path.join(os.path.dirname(__file__), "schema.sql")
    with open(caminho, encoding="utf-8") as arquivo:
        comandos = arquivo.read().split(";")

    conexao = mysql.connector.connect(**_config(com_banco=False))
    cursor = conexao.cursor()
    for comando in comandos:
        # tira as linhas de comentário (-- ...) antes de rodar
        linhas = [l for l in comando.splitlines() if not l.strip().startswith("--")]
        comando = "\n".join(linhas).strip()
        if comando:
            cursor.execute(comando)
    conexao.commit()
    cursor.close()
    conexao.close()
