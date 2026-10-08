"""Verificações de integração de navegação sem abrir Tkinter nem tocar no MySQL."""
import ast
from pathlib import Path
import unittest

RAIZ = Path(__file__).resolve().parent.parent


class TestNavegacaoEstatica(unittest.TestCase):
    def test_dez_telas_possuem_classes_definidas(self):
        mapa = {
            'painel_real_view.py': ['DashboardRealView', 'RelatorioRealView'],
            'saude_financeira_view.py': ['SaudeFinanceiraView'],
            'assistente_ia_view.py': ['AssistenteIAView'],
            'lancamento_view.py': ['LancamentoView'],
            'meta_view.py': ['MetaView'],
            'simulador_view.py': ['SimuladorView'],
            'terceiro_view.py': ['TerceiroView'],
            'categoria_view.py': ['CategoriaView'],
            'usuario_view.py': ['UsuarioView'],
        }
        for arquivo, classes in mapa.items():
            tree = ast.parse((RAIZ / 'views' / arquivo).read_text(encoding='utf-8'))
            definidos = {n.name for n in tree.body if isinstance(n, ast.ClassDef)}
            self.assertTrue(set(classes).issubset(definidos), arquivo)

    def test_menu_tem_entrada_de_saude_separada(self):
        code = (RAIZ / 'views/menu_view.py').read_text(encoding='utf-8')
        self.assertIn('"dashboard": ("views.painel_real_view", "DashboardRealView")', code)
        self.assertIn('"saude": ("views.saude_financeira_view", "SaudeFinanceiraView")', code)

    def test_simulador_permita_carregar_cenarios(self):
        arvore = ast.parse((RAIZ / 'views/simulador_view.py').read_text(encoding='utf-8'))
        classe = next(n for n in arvore.body if isinstance(n, ast.ClassDef) and n.name == 'SimuladorView')
        metodo = next(n for n in classe.body if isinstance(n, ast.FunctionDef) and n.name == '_carregar_cenario')
        self.assertGreater(len(metodo.body), 1)
        self.assertIn('listar_todas', ast.unparse(metodo))

    def test_foto_carregada_ao_abrir_app(self):
        menu = (RAIZ / 'views/menu_view.py').read_text(encoding='utf-8')
        perfil = (RAIZ / 'views/usuario_view.py').read_text(encoding='utf-8')
        self.assertIn('carregar_foto(self.usuario_logado.get("foto_perfil"))', menu)
        self.assertIn('carregar_foto(self.usuario_atual.get("foto_perfil"))', perfil)


if __name__ == '__main__':
    unittest.main()
