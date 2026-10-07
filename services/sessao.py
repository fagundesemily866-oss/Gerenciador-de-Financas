"""
Sessão do usuário logado.
=========================

As views e DAOs do sistema não recebem o usuário por parâmetro; por isso a
aplicação mantém aqui, em um único lugar, o ID do usuário atualmente logado.

Os DAOs usam ``resolver_usuario`` para, quando nenhum ``usuario_id`` é informado
explicitamente, filtrar/gravar os dados do usuário da sessão. Sem sessão ativa
(por exemplo, nos testes automatizados) o comportamento anterior é mantido:
``None`` significa "sem filtro por usuário".
"""
from typing import Optional


class Sessao:
    """Guarda o usuário logado (estado global simples e explícito)."""

    _usuario_id: Optional[int] = None

    @classmethod
    def definir(cls, usuario_id: Optional[int]) -> None:
        cls._usuario_id = int(usuario_id) if usuario_id is not None else None

    @classmethod
    def limpar(cls) -> None:
        cls._usuario_id = None

    @classmethod
    def usuario_id(cls) -> Optional[int]:
        return cls._usuario_id


def resolver_usuario(usuario_id: Optional[int] = None) -> Optional[int]:
    """Retorna o ID informado ou, se ausente, o do usuário logado (pode ser None)."""
    return usuario_id if usuario_id is not None else Sessao.usuario_id()
