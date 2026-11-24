# Testes

Em um ambiente virtual criado conforme o README:

```powershell
.\.venv\Scripts\python -m pip install ".[desktop,test]"
.\.venv\Scripts\python -m pytest -q
```

Para preparar os pacotes de teste em uma máquina conectada, execute `python -m pip wheel --wheel-dir wheelhouse ".[test]"`. Na instalação offline, use `"okami-memorias[test]"` no comando de instalação pelo wheelhouse.

A suíte cria imagens geométricas durante a execução. Verifica descoberta, EXIF, transparência, entradas inválidas e pasta vazia. O pypdf inspeciona tamanho de página, posição, resolução e paginação para uma, quatro e cinco fotos. Os testes cobrem também determinismo, integridade dos originais, cancelamento, falhas de publicação, concorrência e CLI.

Os testes da interface usam o modo `offscreen` do Qt e simulam a seleção nos diálogos. Eles verificam a exportação de cinco fotos, geometria compartilhada com a prévia e bloqueio por arquivos inválidos. Para preparar os wheels da suíte completa, use `".[desktop,test]"`. Com apenas o extra `test`, os testes de interface são pulados.

Os testes dos modelos verificam a compatibilidade do Branco, as margens, as cores e posições dos elementos no PDF, o título acentuado, as proporções das fotografias e a paginação 4 + 1. Os testes Qt exercitam a seleção do modelo e a exportação com título.

Os testes de turma verificam três alunos com 1, 4 e 5 fotos, PDFs de 1, 1 e 2 páginas, margem esquerda de 25 mm e título por aluno. Também cobrem a troca de prévia, pastas vazias, fotos inválidas, destino existente e cancelamento após o primeiro PDF.

Os testes Qt verificam também as linhas de ordem, arquivo e páginas exibidas em **Preparar impressão**. O teste do executável instalado e o roteiro para uma máquina limpa e uma folha física estão no [guia do instalador Windows](WINDOWS_INSTALLER.md).
