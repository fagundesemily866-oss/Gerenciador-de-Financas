import mysql.connector
import os
from dotenv import load_dotenv


class Database:

    load_dotenv()

    def conectar(self):

        host = os.getenv("DB_HOST")
        port = os.getenv("DB_PORT")
        database = os.getenv("DB_NAME")
        user = os.getenv("DB_USER")
        password = os.getenv("DB_PASSWORD")

        faltando = [
            nome for nome, valor in [
                ("DB_HOST", host),
                ("DB_PORT", port),
                ("DB_NAME", database),
                ("DB_USER", user),
                ("DB_PASSWORD", password),
            ]
            if valor is None
        ]

        if faltando:
            raise RuntimeError(
                "Variáveis de ambiente ausentes no .env: "
                + ", ".join(faltando)
                + ". Verifique se o arquivo .env está na raiz do projeto "
                  "(mesma pasta do main.py) e se todas as chaves estão preenchidas."
            )

        try:
            porta = int(port)
        except ValueError:
            raise RuntimeError(
                f"DB_PORT inválido no .env: '{port}'. Deve ser um número (ex: 3306)."
            )

        try:
            conexao = mysql.connector.connect(
                host=host,
                port=porta,
                database=database,
                user=user,
                password=password
            )
            return conexao

        except mysql.connector.Error as e:
            raise RuntimeError(
                f"Falha ao conectar no banco '{database}' em {host}:{porta} "
                f"como '{user}': {e}"
            )

    def desconectar(self, cursor=None, conexao=None):
        if cursor:
            cursor.close()
        if conexao and conexao.is_connected():
            conexao.close()