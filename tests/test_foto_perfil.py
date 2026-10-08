"""Testes de regressão da foto do perfil, sem depender de MySQL e de GUI."""
from tempfile import TemporaryDirectory
from pathlib import Path
from unittest.mock import Mock, patch
import unittest
from PIL import Image
from services import foto_perfil as fotos


class TestFotoPerfil(unittest.TestCase):
    def setUp(self):
        self.temp = TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.raiz = Path(self.temp.name)
        self.patch_raiz = patch.object(fotos, 'RAIZ_PROJETO', self.raiz)
        self.patch_pasta = patch.object(fotos, 'PASTA_FOTOS', self.raiz / 'data/perfis')
        self.patch_raiz.start(); self.patch_pasta.start()
        self.addCleanup(self.patch_raiz.stop); self.addCleanup(self.patch_pasta.stop)
        self.origem = self.raiz / 'minha_foto.png'
        Image.new('RGB', (1200, 350), (40, 120, 220)).save(self.origem)

    def test_salva_reabre_apos_nova_sessao(self):
        dao = Mock()
        dao.atualizar_foto.return_value = True
        caminho, img = fotos.salvar_foto(7, str(self.origem), dao)
        self.assertTrue(caminho.startswith('data/perfis/usuario_7_'))
        self.assertEqual(img.size, (512, 512))
        dao.atualizar_foto.assert_called_once_with(7, caminho)
        foto_reaberta = fotos.carregar_foto(caminho)
        self.assertIsNotNone(foto_reaberta)
        self.assertEqual(foto_reaberta.size, (512, 512))
        # Mesmo após apagar a imagem original, a foto salva permanece.
        self.origem.unlink()
        self.assertIsNotNone(fotos.carregar_foto(caminho))

    def test_erro_no_mysql_nao_deixa_foto_orfa(self):
        dao = Mock()
        dao.atualizar_foto.side_effect = RuntimeError('Banco indisponível')
        with self.assertRaises(RuntimeError):
            fotos.salvar_foto(5, str(self.origem), dao)
        self.assertEqual(list(fotos.PASTA_FOTOS.glob('*')), [])

    def test_usuario_inexistente_nao_salva(self):
        with self.assertRaises(ValueError):
            fotos.salvar_foto(0, str(self.origem), Mock())

    def test_arredondamento_mantem_proporcao_e_transparencia(self):
        avatar = fotos.avatar_circular(Image.open(self.origem), 72)
        self.assertEqual(avatar.size, (144, 144))
        self.assertEqual(avatar.getpixel((0, 0))[3], 0)
        self.assertEqual(avatar.getpixel((72, 72))[3], 255)

    def test_foto_terceiro_persiste(self):
        dao = Mock()
        dao.atualizar_foto.return_value = True
        caminho = fotos.salvar_foto_terceiro(12, str(self.origem), dao)
        self.assertTrue(caminho.startswith('data/terceiros/terceiro_12_'))
        dao.atualizar_foto.assert_called_once_with(12, caminho)
        self.assertIsNotNone(fotos.carregar_foto(caminho))

    def test_foto_terceiro_erro_mysql_nao_deixa_arquivo(self):
        dao = Mock()
        dao.atualizar_foto.return_value = False
        with self.assertRaises(RuntimeError):
            fotos.salvar_foto_terceiro(12, str(self.origem), dao)
        self.assertEqual(list((self.raiz/'data/terceiros').glob('*')), [])

    def test_foto_faltando_nao_quebra_tela(self):
        self.assertIsNone(fotos.carregar_foto('data/perfis/nao_existe.png'))
        self.assertIsNone(fotos.carregar_foto(None))

    def test_recusa_foto_maior_que_limite(self):
        with patch.object(fotos, 'TAMANHO_ARQUIVO_MAXIMO', 10):
            with self.assertRaises(ValueError):
                fotos.preparar_foto(str(self.origem))


if __name__ == '__main__':
    unittest.main()
