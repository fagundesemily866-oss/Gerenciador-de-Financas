"""
Modelo representando uma Simulação Financeira Salva.
===================================================

Permite que o usuário preserve cenários hipotéticos, compare diferentes
projeções ao longo do tempo e recupere parâmetros previamente testados.
"""
import json
from datetime import datetime
from typing import Optional, Dict, Any


class Simulacao:
    """Entidade que encapsula os parâmetros e resultados de uma simulação."""

    def __init__(
        self,
        id: Optional[int] = None,
        usuario_id: Optional[int] = None,
        nome: str = "",
        descricao: str = "",
        parametros_json: str = "{}",
        resultados_json: str = "{}",
        data_criacao: Optional[str] = None,
    ):
        self._id = id
        self._usuario_id = usuario_id
        self._nome = nome
        self._descricao = descricao
        self._parametros_json = parametros_json or "{}"
        self._resultados_json = resultados_json or "{}"
        self._data_criacao = data_criacao or datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    @property
    def id(self) -> Optional[int]:
        return self._id

    @id.setter
    def id(self, valor: Optional[int]):
        self._id = valor

    @property
    def usuario_id(self) -> Optional[int]:
        return self._usuario_id

    @usuario_id.setter
    def usuario_id(self, valor: Optional[int]):
        self._usuario_id = valor

    @property
    def nome(self) -> str:
        return self._nome

    @nome.setter
    def nome(self, valor: str):
        self._nome = valor.strip()

    @property
    def descricao(self) -> str:
        return self._descricao

    @descricao.setter
    def descricao(self, valor: str):
        self._descricao = valor.strip()

    @property
    def parametros_json(self) -> str:
        return self._parametros_json

    @parametros_json.setter
    def parametros_json(self, valor: str):
        self._parametros_json = valor

    @property
    def resultados_json(self) -> str:
        return self._resultados_json

    @resultados_json.setter
    def resultados_json(self, valor: str):
        self._resultados_json = valor

    @property
    def data_criacao(self) -> str:
        return self._data_criacao

    def get_parametros(self) -> Dict[str, Any]:
        """Desserializa o JSON de parâmetros para dicionário Python."""
        try:
            return json.loads(self._parametros_json)
        except (ValueError, TypeError):
            return {}

    def set_parametros(self, params: Dict[str, Any]) -> None:
        """Serializa o dicionário de parâmetros para JSON."""
        self._parametros_json = json.dumps(params, ensure_ascii=False)

    def get_resultados(self) -> Dict[str, Any]:
        """Desserializa o JSON de resultados para dicionário Python."""
        try:
            return json.loads(self._resultados_json)
        except (ValueError, TypeError):
            return {}

    def set_resultados(self, resultados: Dict[str, Any]) -> None:
        """Serializa o dicionário de resultados para JSON."""
        self._resultados_json = json.dumps(resultados, ensure_ascii=False)

    def to_dict(self) -> Dict[str, Any]:
        """Converte a entidade para dicionário."""
        return {
            "id": self._id,
            "usuario_id": self._usuario_id,
            "nome": self._nome,
            "descricao": self._descricao,
            "parametros": self.get_parametros(),
            "resultados": self.get_resultados(),
            "data_criacao": self._data_criacao,
        }
