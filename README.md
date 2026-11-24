# OKAMI Memórias Escolares

O OKAMI transforma uma pasta de fotografias em um mosaico PDF A4 para impressão. O processamento acontece no computador, com quatro espaços por página e margem esquerda para encadernação.

## Interface desktop

No PowerShell, a partir da raiz do projeto, com Python 3.11 ou superior:

```powershell
python -m venv .venv
.\.venv\Scripts\python -m pip install ".[desktop]"
.\.venv\Scripts\python -m okami_memorias.desktop
```

Escolha a pasta de fotos e selecione **Branco**, **Caderno azul** ou **Jardim da turma**. Digite um título se quiser repeti-lo em todas as páginas. Ajuste as margens observando a prévia da primeira página, escolha onde salvar e clique em **Gerar PDF**. Os modelos decorativos mantêm os fundos e molduras dentro das margens e reservam espaço para as fotos inteiras.

Se houver arquivos inválidos, a interface exibe a contagem e dá acesso aos nomes. Corrija os arquivos e selecione a pasta novamente. O botão **Cancelar** interrompe a operação no próximo ponto seguro. Uma foto grande ou a gravação final do PDF pode atrasar a resposta ao cancelamento.

Para instalar sem rede, prepare o wheelhouse com `python -m pip wheel --wheel-dir wheelhouse ".[desktop]"` e instale `"okami-memorias[desktop]"` usando `--no-index --find-links wheelhouse`. Se o pip indicar caminhos longos no Windows, crie o ambiente virtual em um caminho curto, como `C:\venvs\okami` em uma pasta na qual você tenha acesso de escrita, e use o executável desse ambiente.

## Instalação da CLI

Requer Python 3.11 ou superior. No PowerShell, a partir da raiz do projeto:

```powershell
python -m venv .venv
.\.venv\Scripts\python -m pip install .
```

Em Linux ou macOS, use `.venv/bin/python` no lugar do executável do Windows. Para instalar em uma máquina desconectada, prepare os pacotes em uma máquina com acesso ao índice, com o mesmo sistema, arquitetura e versão do Python, e transfira o diretório `wheelhouse`:

```powershell
python -m pip wheel --wheel-dir wheelhouse .
.\.venv\Scripts\python -m pip install --no-index --find-links wheelhouse okami-memorias
```

## Gerar um mosaico

```powershell
.\.venv\Scripts\python -m okami_memorias --input ./fotos --output ./album.pdf --photos-per-page 4 --binding-margin-mm 20
```

O comando lê JPG, JPEG e PNG da pasta indicada, em ordem alfabética por nome de arquivo, e recusa arquivos ilegíveis e destinos já existentes. O diretório de destino deve existir. Para um exemplo sem fotografias reais:

```powershell
.\.venv\Scripts\python scripts/gerar_fotos_sinteticas.py ./qa-p0/fotos
.\.venv\Scripts\python -m okami_memorias --input ./qa-p0/fotos --output ./qa-p0/album.pdf --binding-margin-mm 25
```

As margens direita, superior e inferior têm 10 mm por padrão. Use `--right-margin-mm`, `--top-margin-mm` e `--bottom-margin-mm` para ajustá-las. O espaçamento de 5 mm pode ser alterado com `--gap-mm`. Na impressão, selecione papel A4 e escala de 100% para manter as medidas do PDF.

Consulte a [arquitetura](docs/ARCHITECTURE.md), os [requisitos](docs/REQUIREMENTS.md), os [testes](docs/TESTING.md), a [privacidade](docs/PRIVACY.md), as [licenças](docs/THIRD_PARTY_LICENSES.md) e o [roteiro](docs/ROADMAP.md).
