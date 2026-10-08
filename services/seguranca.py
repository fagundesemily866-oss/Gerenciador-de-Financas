"""
Segurança de senhas.
====================

Gera e confere hashes de senha com PBKDF2-HMAC-SHA256 (biblioteca padrão,
sem dependências extras). O valor guardado em ``usuario.senha_hash`` tem o
formato::

    pbkdf2_sha256$<iteracoes>$<salt_hex>$<hash_hex>

(cerca de 110 caracteres — cabe no VARCHAR(255) da tabela).

Contas antigas, criadas quando a senha ainda era gravada em texto puro, continuam
funcionando: ``verificar_senha`` aceita o formato legado e ``precisa_atualizar``
indica que o hash deve ser regravado no novo formato após um login válido.
"""
import hashlib
import hmac
import secrets

_ALGORITMO = "pbkdf2_sha256"
_ITERACOES = 200_000


def hash_senha(senha: str) -> str:
    """Retorna o hash (com salt aleatório) de uma senha em texto puro."""
    salt = secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac(
        "sha256", senha.encode("utf-8"), bytes.fromhex(salt), _ITERACOES
    ).hex()
    return f"{_ALGORITMO}${_ITERACOES}${salt}${digest}"


def _eh_hash(valor: str) -> bool:
    return isinstance(valor, str) and valor.startswith(_ALGORITMO + "$")


def verificar_senha(senha: str, armazenado: str) -> bool:
    """Confere a senha digitada contra o valor guardado (hash ou texto legado)."""
    if not armazenado:
        return False
    if not _eh_hash(armazenado):
        # Formato legado: senha em texto puro
        return hmac.compare_digest(senha.encode("utf-8"), armazenado.encode("utf-8"))
    try:
        _, iteracoes, salt, esperado = armazenado.split("$")
        calculado = hashlib.pbkdf2_hmac(
            "sha256", senha.encode("utf-8"), bytes.fromhex(salt), int(iteracoes)
        ).hex()
    except (ValueError, TypeError):
        return False
    return hmac.compare_digest(calculado, esperado)


def precisa_atualizar(armazenado: str) -> bool:
    """True se o valor guardado ainda está no formato legado (texto puro)."""
    return bool(armazenado) and not _eh_hash(armazenado)
