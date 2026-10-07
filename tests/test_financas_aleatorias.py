import os
import random
import sys
import tempfile
import unittest
from datetime import date

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from models.database import Database
from dao.usuario_dao import UsuarioDAO
from dao.categoria_dao import CategoriaDAO
from dao.lancamento_dao import LancamentoDAO
from dao.meta_dao import MetaDAO
from dao.terceiro_dao import TerceiroDAO
from services.financas_aleatorias import GeradorFinancasAleatorias
from services.sessao import Sessao


class TestFinancasAleatorias(unittest.TestCase):

    def setUp(self):
        Sessao.limpar()
        tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        tmp.close()
        self.path = tmp.name
        self.db = Database(db_path=self.path)
        self.usuarios = UsuarioDAO(self.db)
        self.cats = CategoriaDAO(self.db)
        self.lancs = LancamentoDAO(self.db)
        self.metas = MetaDAO(self.db)
        self.terceiros = TerceiroDAO(self.db)
        self.hoje = date(2026, 10, 6)

    def tearDown(self):
        Sessao.limpar()
        self.db.close()
        os.remove(self.path)

    def _novo_usuario(self, nome="Teste", email="t@x.com", tipo="PF"):
        return self.usuarios.inserir(nome, email, "1234", tipo)

    def _gerar(self, uid, seed):
        g = GeradorFinancasAleatorias(self.db, rng=random.Random(seed), hoje=self.hoje)
        return g.gerar(uid)

    def test_dados_coerentes_entre_si(self):
        uid = self._novo_usuario()
        resumo = self._gerar(uid, 1)

        categorias = self.cats.listar_todas(uid)
        nomes_por_tipo = {(c["nome"], c["tipo"]) for c in categorias}
        self.assertTrue(all(c["usuario_id"] == uid for c in categorias))

        ids_terceiros = {t["id"] for t in self.terceiros.listar_todos(uid)}
        self.assertTrue(all(t["usuario_id"] == uid for t in self.terceiros.listar_todos(uid)))

        lancs = self.lancs.listar_todos(uid)
        self.assertGreater(len(lancs), 40)
        for l in lancs:
            self.assertEqual(l["usuario_id"], uid)
            self.assertIn((l["category"], l["type"]), nomes_por_tipo)   # categoria válida do usuário e do mesmo tipo
            self.assertIn(l["terceiro_id"], ids_terceiros)              # terceiro do mesmo usuário
            self.assertIn(l["status"], ("Pago", "Pendente", "Recebido"))
            self.assertGreater(l["value"], 0)
            self.assertLessEqual(l["date"], self.hoje.strftime("%Y-%m-%d"))

        rec = sum(l["value"] for l in lancs if l["type"] == "Receita")
        desp = sum(l["value"] for l in lancs if l["type"] == "Despesa")
        self.assertAlmostEqual(resumo["saldo"], rec - desp, places=2)
        self.assertGreater(rec, 0)

        # limites de categoria de despesa definidos
        self.assertTrue(all(c["limite_orcamento"] > 0 for c in categorias if c["tipo"] == "Despesa"))
        usuario = self.usuarios.buscar_por_id(uid)
        self.assertEqual(usuario["modo_demo"], 1)
        self.assertEqual(usuario["renda_mensal"], resumo["renda_mensal"])

    def test_metas_matematicamente_coerentes(self):
        uid = self._novo_usuario()
        self._gerar(uid, 7)
        metas = self.metas.listar_todas(uid)
        self.assertTrue(3 <= len(metas) <= 4)
        conn = self.db.get_connection()
        aportes_total = 0.0
        for m in metas:
            soma = conn.execute("SELECT COALESCE(SUM(valor),0) FROM meta_aportes WHERE meta_id=?", (m["id"],)).fetchone()[0]
            aportes_total += soma
            self.assertAlmostEqual(m["valor_atual"], soma, places=2)
            self.assertGreater(m["valor_alvo"], m["valor_atual"])
            self.assertEqual(m["concluida"], 0)
            self.assertTrue(m["prazo"].endswith("meses"))
            self.assertEqual(len(m["data_limite"]), 10)
        lancs = self.lancs.listar_todos(uid)
        saldo = sum(l["value"] if l["type"] == "Receita" else -l["value"] for l in lancs)
        # Aportes em metas nunca excedem o que realmente sobrou
        self.assertLessEqual(aportes_total, max(saldo, 0) + 0.01)

    def test_cada_geracao_gera_exemplos_diferentes(self):
        u1 = self._novo_usuario("A", "a@x.com")
        u2 = self._novo_usuario("B", "b@x.com")
        r1 = self._gerar(u1, 1)
        r2 = self._gerar(u2, 2)
        self.assertNotEqual((r1["renda_mensal"], r1["total_despesas"]), (r2["renda_mensal"], r2["total_despesas"]))

    def test_isolamento_entre_usuarios_e_modo_zero(self):
        demo = self._novo_usuario("Demo", "d@x.com")
        zero = self._novo_usuario("Zero", "z@x.com")
        self._gerar(demo, 3)

        Sessao.definir(zero)
        self.assertEqual(self.lancs.listar_todos(), [])
        self.assertEqual(self.metas.listar_todas(), [])
        self.assertEqual(self.cats.listar_todas(), [])
        self.assertEqual(self.terceiros.listar_todos(), [])
        self.assertFalse(self.lancs.existe_dados())
        self.assertEqual(self.usuarios.buscar_por_id(zero)["modo_demo"], 0)

        Sessao.definir(demo)
        self.assertGreater(len(self.lancs.listar_todos()), 0)

    def test_inserir_usa_usuario_da_sessao(self):
        uid = self._novo_usuario()
        Sessao.definir(uid)
        lid = self.lancs.inserir("Café", 10.0, "Despesa", "Alimentação", "2026-10-01")
        self.assertEqual(self.lancs.buscar_por_id(lid)["usuario_id"], uid)

    def test_perfil_pj_usa_categoria_de_faturamento(self):
        uid = self._novo_usuario("Empresa", "e@x.com", "PJ")
        self._gerar(uid, 5)
        nomes = {c["nome"] for c in self.cats.listar_todas(uid) if c["tipo"] == "Receita"}
        self.assertIn("Faturamento", nomes)

    def test_migracao_atribui_dados_legados_ao_primeiro_usuario(self):
        import sqlite3
        path = self.path + ".legacy"
        conn = sqlite3.connect(path)
        conn.executescript("""
            CREATE TABLE usuarios (id INTEGER PRIMARY KEY AUTOINCREMENT, nome TEXT NOT NULL, email TEXT NOT NULL UNIQUE,
                senha_hash TEXT NOT NULL, tipo_perfil TEXT NOT NULL DEFAULT 'PF', data_criacao TEXT NOT NULL);
            CREATE TABLE transactions (id INTEGER PRIMARY KEY AUTOINCREMENT, description TEXT NOT NULL, value REAL NOT NULL,
                type TEXT NOT NULL, category TEXT NOT NULL, date TEXT NOT NULL);
            INSERT INTO usuarios (nome,email,senha_hash,data_criacao) VALUES ('Velho','v@x.com','1','2026-01-01');
            INSERT INTO usuarios (nome,email,senha_hash,data_criacao) VALUES ('Novo','n@x.com','1','2026-02-01');
            INSERT INTO transactions (description,value,type,category,date) VALUES ('X',5,'Despesa','Outros','2026-01-02');
        """)
        conn.commit(); conn.close()
        db = Database(db_path=path)
        try:
            dao = LancamentoDAO(db)
            self.assertEqual(len(dao.listar_todos(1)), 1)
            self.assertEqual(len(dao.listar_todos(2)), 0)
            db2 = Database(db_path=path)  # segunda abertura não refaz a migração
            db2.close()
        finally:
            db.close()
            os.remove(path)


if __name__ == "__main__":
    unittest.main()
