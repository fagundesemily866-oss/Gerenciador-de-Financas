import os, random, sys, tempfile, unittest
from datetime import date
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from models.database import Database
from dao.usuario_dao import UsuarioDAO
from dao.lancamento_dao import LancamentoDAO
from dao.meta_dao import MetaDAO
from dao.categoria_dao import CategoriaDAO
from services.financas_aleatorias import GeradorFinancasAleatorias
from services.simulador_cenarios import simular, frase_meta
from services.resumo_executivo import gerar_resumo


class TestSimuladorEResumo(unittest.TestCase):
    def setUp(self):
        self.path = tempfile.mktemp(suffix=".db")
        self.db = Database(self.path)
        self.uid = UsuarioDAO(self.db).inserir("U", "u@x.com", "1")
        GeradorFinancasAleatorias(self.db, random.Random(4), date.today()).gerar(self.uid)
        self.l = LancamentoDAO(self.db).listar_todos(self.uid)
        self.m = MetaDAO(self.db).listar_todas(self.uid)

    def tearDown(self):
        self.db.close(); os.remove(self.path)

    def test_cenarios_ordenados_e_metas(self):
        r = simular(self.l, self.m, 12, 10, 0, 0)
        c = r["cenarios"]
        self.assertGreater(c["otimista"]["saldo_final"], c["planejado"]["saldo_final"])
        self.assertGreater(c["planejado"]["saldo_final"], c["pessimista"]["saldo_final"])
        self.assertEqual(len(c["planejado"]["metas"]), len(self.m))
        for k in c:
            for meta in c[k]["metas"]:
                self.assertIn(meta["status"], ("antes", "no_prazo", "atrasada", "sem_prazo", "sem_aporte"))
                self.assertTrue(frase_meta(meta, k).startswith("Neste cenário"))
        # melhor cenário nunca demora mais para atingir a meta
        for mo, mp in zip(c["otimista"]["metas"], c["pessimista"]["metas"]):
            if mo["meses"] and mp["meses"]:
                self.assertLessEqual(mo["meses"], mp["meses"])

    def test_sem_dados_nao_inventa_numeros(self):
        self.assertIsNone(simular([], [], 12, 0, 0, 0))
        self.assertIsNone(gerar_resumo([], []))

    def test_resumo_bate_com_lancamentos(self):
        r = gerar_resumo(self.l, CategoriaDAO(self.db).listar_todas(self.uid))
        pref = f"{r['ano']:04d}-{r['mes']:02d}"
        rec = sum(x["value"] for x in self.l if x["type"] == "Receita" and x["date"].startswith(pref))
        self.assertAlmostEqual(r["receitas"], rec, places=2)
        self.assertAlmostEqual(r["saldo"], r["receitas"] - r["despesas"], places=2)


if __name__ == "__main__":
    unittest.main()
