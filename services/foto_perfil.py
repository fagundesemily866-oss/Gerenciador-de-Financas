"""Persistência e renderização das fotos de perfil.

A foto é copiada para dentro do projeto: não depende mais do arquivo original
escolhido pelo usuário. O banco guarda um caminho relativo, válido após reiniciar
ou mover o projeto junto com a pasta ``data/perfis``.
"""

from pathlib import Path
from uuid import uuid4
import os

from PIL import Image, ImageDraw, ImageOps, UnidentifiedImageError

RAIZ_PROJETO = Path(__file__).resolve().parent.parent
PASTA_FOTOS = RAIZ_PROJETO / "data" / "perfis"
TAMANHO_ARQUIVO_MAXIMO = 10 * 1024 * 1024  # 10 MiB
LIMITE_PIXELS = 24_000_000


def carregar_foto(caminho: str | None) -> Image.Image | None:
    """Abre cópia em memória; aceita novos caminhos relativos e caminhos antigos."""
    if not caminho:
        return None
    origem = Path(caminho)
    if not origem.is_absolute():
        origem = RAIZ_PROJETO / origem
    try:
        if not origem.is_file():
            return None
        with Image.open(origem) as img:
            if img.width * img.height > LIMITE_PIXELS:
                return None
            return ImageOps.exif_transpose(img).convert("RGB")
    except (OSError, ValueError, UnidentifiedImageError):
        return None


def preparar_foto(caminho_original: str) -> Image.Image:
    """Valida, corrige rotação e ajusta a foto para formato quadrado."""
    origem = Path(caminho_original)
    if origem.stat().st_size > TAMANHO_ARQUIVO_MAXIMO:
        raise ValueError("A imagem deve ter no máximo 10 MB.")
    with Image.open(origem) as img:
        if img.width * img.height > LIMITE_PIXELS:
            raise ValueError("Imagem grande demais. Escolha uma foto menor.")
        imagem = ImageOps.exif_transpose(img).convert("RGB")
        return ImageOps.fit(imagem, (512, 512), method=Image.Resampling.LANCZOS)


def avatar_circular(imagem: Image.Image, tamanho: int) -> Image.Image:
    """Faz recorte preenchendo todo o círculo, com bordas suaves e sem deformar."""
    if tamanho <= 0:
        raise ValueError("Tamanho do avatar inválido")
    resolucao = tamanho * 3
    imagem = ImageOps.fit(
        ImageOps.exif_transpose(imagem).convert("RGB"),
        (resolucao, resolucao),
        method=Image.Resampling.LANCZOS,
    ).convert("RGBA")
    mascara = Image.new("L", (resolucao, resolucao), 0)
    ImageDraw.Draw(mascara).ellipse((0, 0, resolucao - 1, resolucao - 1), fill=255)
    imagem.putalpha(mascara)
    return imagem.resize((tamanho * 2, tamanho * 2), Image.Resampling.LANCZOS)


def salvar_foto(usuario_id: int, caminho_original: str, usuario_dao) -> tuple[str, Image.Image]:
    """Salva a cópia no disco e confirma no MySQL antes de atualizar a interface.

    Em erro no banco, remove a nova foto e preserva o caminho anterior.
    """
    uid = int(usuario_id)
    if uid <= 0:
        raise ValueError("Usuário inválido para salvar a foto")
    imagem = preparar_foto(caminho_original)
    PASTA_FOTOS.mkdir(parents=True, exist_ok=True)
    nome = f"usuario_{uid}_{uuid4().hex[:12]}.png"
    destino = PASTA_FOTOS / nome
    temporario = PASTA_FOTOS / (nome + ".tmp")
    try:
        imagem.save(temporario, format="PNG", optimize=True)
        os.replace(temporario, destino)
        caminho_relativo = destino.relative_to(RAIZ_PROJETO).as_posix()
        if not usuario_dao.atualizar_foto(uid, caminho_relativo):
            raise RuntimeError("Não foi possível atualizar a foto no banco de dados")
        return caminho_relativo, imagem
    except Exception:
        temporario.unlink(missing_ok=True)
        destino.unlink(missing_ok=True)
        raise


def salvar_foto_terceiro(terceiro_id: int, caminho_original: str, terceiro_dao) -> str:
    """Persiste foto de um contato sem depender do arquivo escolhido originalmente."""
    tid = int(terceiro_id)
    if tid <= 0:
        raise ValueError("Contato inválido")
    imagem = preparar_foto(caminho_original)
    pasta = RAIZ_PROJETO / "data" / "terceiros"
    pasta.mkdir(parents=True, exist_ok=True)
    nome = f"terceiro_{tid}_{uuid4().hex[:12]}.png"
    destino = pasta / nome
    temporario = pasta / (nome + ".tmp")
    try:
        imagem.save(temporario, format="PNG", optimize=True)
        os.replace(temporario, destino)
        caminho_relativo = destino.relative_to(RAIZ_PROJETO).as_posix()
        if not terceiro_dao.atualizar_foto(tid, caminho_relativo):
            raise RuntimeError("Não foi possível salvar a foto do contato no banco")
        return caminho_relativo
    except Exception:
        temporario.unlink(missing_ok=True)
        destino.unlink(missing_ok=True)
        raise


def limpar_fotos_usuario(usuario_id: int) -> None:
    """Remove apenas arquivos locais de foto criados para esta conta.

    Não segue caminhos informados pelo banco nem apaga arquivos fora de data/perfis.
    A execução é feita somente após a confirmação de exclusão no MySQL.
    """
    uid = int(usuario_id)
    if uid <= 0:
        return
    if PASTA_FOTOS.is_dir():
        for arquivo in PASTA_FOTOS.glob(f"usuario_{uid}_*.png"):
            if arquivo.is_file() and not arquivo.is_symlink():
                arquivo.unlink()


def limpar_fotos_terceiro(terceiro_id: int) -> None:
    """Remove somente fotos deste contato dentro da pasta gerenciada pelo app."""
    tid = int(terceiro_id)
    if tid <= 0:
        return
    pasta = RAIZ_PROJETO / "data" / "terceiros"
    if pasta.is_dir():
        for arquivo in pasta.glob(f"terceiro_{tid}_*.png"):
            if arquivo.is_file() and not arquivo.is_symlink():
                arquivo.unlink()
