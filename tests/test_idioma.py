"""Testa idioma, tradução de rótulos e persistência sem acesso ao MySQL."""
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import idioma


class TestIdiomaInterface(unittest.TestCase):
    def setUp(self):
        self.antigo = idioma.obter_idioma()
        idioma.definir_idioma("pt_BR", salvar=False)

    def tearDown(self):
        idioma.definir_idioma(self.antigo, salvar=False)

    def test_portugues_e_o_padrao(self):
        with tempfile.TemporaryDirectory() as pasta, patch.object(
            idioma, "_CONFIG_IDIOMA", Path(pasta) / "interface.json"
        ):
            self.assertEqual(idioma.carregar_idioma_preferido(), "pt_BR")
        self.assertEqual(idioma.IDIOMA_PADRAO, "pt_BR")

    def test_rotulos_sao_portugueses_por_padrao(self):
        self.assertEqual(idioma.traduzir("🎯  Metas"), "🎯  Metas")
        self.assertEqual(idioma.traduzir("Criar Minha Conta"), "Criar Minha Conta")
        self.assertEqual(idioma.traduzir("PAGO"), "PAGO")

    def test_ingles_e_opcional(self):
        idioma.definir_idioma("en_US", salvar=False)
        self.assertEqual(idioma.traduzir("🎯  Metas"), "🎯  Goals")
        self.assertEqual(idioma.traduzir("👤  Meu Perfil"), "👤  My Profile")
        self.assertEqual(idioma.traduzir("＋  Salvar Lançamento"), "＋  Save Transaction")
        self.assertEqual(idioma.traduzir("PAGO"), "PAID")
        self.assertEqual(idioma.traduzir("PF - Pessoa Física"), "PF - Individual")

    def test_trocar_de_volta_para_portugues(self):
        idioma.definir_idioma("en_US", salvar=False)
        idioma.definir_idioma("pt_BR", salvar=False)
        self.assertEqual(idioma.traduzir("Aguardando dados"), "Aguardando dados")

    def test_valores_financeiros_e_dados_customizados(self):
        idioma.definir_idioma("en_US", salvar=False)
        self.assertEqual(idioma.traduzir("Minha categoria personalizada"), "Minha categoria personalizada")
        self.assertEqual(idioma.traduzir("R$ 2.345,67"), "R$ 2.345,67")

    def test_salva_idioma_sem_apagar_tema(self):
        with tempfile.TemporaryDirectory() as pasta:
            caminho = Path(pasta) / "interface.json"
            caminho.write_text(json.dumps({"theme": "Light"}), encoding="utf-8")
            with patch.object(idioma, "_CONFIG_IDIOMA", caminho):
                idioma.definir_idioma("en_US")
                self.assertEqual(json.loads(caminho.read_text())["theme"], "Light")
                self.assertEqual(idioma.carregar_idioma_preferido(), "en_US")
                idioma.definir_idioma("pt_BR")
                self.assertEqual(idioma.carregar_idioma_preferido(), "pt_BR")
                self.assertEqual(json.loads(caminho.read_text())["theme"], "Light")

    def test_troca_de_tema_nao_apaga_preferencia_de_idioma(self):
        # Importa somente a implementação de preferências, com CTk simulado.
        import importlib.util
        import sys
        from types import ModuleType
        tema_path = Path(__file__).resolve().parents[1] / "views" / "tema.py"
        fake_ctk = ModuleType("customtkinter")
        fake_ctk.CTkFont = lambda *a, **k: None
        fake_ctk.set_appearance_mode = lambda mode: None
        fake_ctk.get_appearance_mode = lambda: "Dark"
        with patch.dict(sys.modules, {"customtkinter": fake_ctk}):
            spec = importlib.util.spec_from_file_location("tema_preferencias_test", tema_path)
            modulo = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(modulo)
        with tempfile.TemporaryDirectory() as pasta:
            config = Path(pasta) / "interface.json"
            config.write_text(json.dumps({"language": "en_US"}), encoding="utf-8")
            with patch.object(modulo, "_CONFIG_INTERFACE", config):
                modulo.definir_tema_preferido("Light")
            self.assertEqual(json.loads(config.read_text())["language"], "en_US")
            self.assertEqual(json.loads(config.read_text())["theme"], "Light")

    def test_config_corrompida_usa_portugues(self):
        with tempfile.TemporaryDirectory() as pasta:
            caminho = Path(pasta) / "interface.json"
            caminho.write_text("invalid json!", encoding="utf-8")
            with patch.object(idioma, "_CONFIG_IDIOMA", caminho):
                self.assertEqual(idioma.carregar_idioma_preferido(), "pt_BR")

    def test_idioma_invalido_rejeitado(self):
        with self.assertRaises(ValueError):
            idioma.definir_idioma("es_ES", salvar=False)

    def test_catalogo_mantido(self):
        self.assertGreater(len(idioma.TRADUCOES), 300)


if __name__ == "__main__":
    unittest.main()
