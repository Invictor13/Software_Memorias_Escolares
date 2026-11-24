"""Erros apresentados pela aplicação."""

class PhotoError(Exception):
    """A origem ou uma fotografia não pôde ser processada."""


class ExportError(Exception):
    """O PDF não pôde ser publicado no destino."""


class OperationCancelled(Exception):
    """A operação foi interrompida antes da publicação."""
