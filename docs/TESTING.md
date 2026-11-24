# Testes

Em um ambiente virtual criado conforme o README:

```powershell
.\.venv\Scripts\python -m pip install ".[test]"
.\.venv\Scripts\python -m pytest -q
```

Para preparar os pacotes de teste em uma máquina conectada, execute `python -m pip wheel --wheel-dir wheelhouse ".[test]"`. Na instalação offline, use `"okami-memorias[test]"` no comando de instalação pelo wheelhouse.

A suíte cria imagens geométricas durante a execução. Verifica descoberta, EXIF, transparência, entradas inválidas e pasta vazia. O pypdf inspeciona tamanho de página, posição, resolução e paginação para uma, quatro e cinco fotos. Os testes cobrem também determinismo, integridade dos originais, cancelamento, falhas de publicação, concorrência e CLI.
