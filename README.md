# OKAMI Memórias Escolares

O OKAMI transforma uma pasta de fotografias em um mosaico PDF A4 para impressão. O processamento acontece no computador, com quatro espaços por página e margem esquerda para encadernação.

## Instalar no Windows x64

Execute `OKAMI-Memorias-0.5.0-Windows-x64.exe` e abra **OKAMI Memórias Escolares 0.5.0** pelo menu Iniciar. O instalador inclui as dependências e funciona offline sem Python instalado. Para gerar o arquivo ou reproduzir a validação, consulte o [guia do instalador](docs/WINDOWS_INSTALLER.md).

## Interface desktop

No PowerShell, a partir da raiz do projeto, com Python 3.11 ou superior:

```powershell
python -m venv .venv
.\.venv\Scripts\python -m pip install ".[desktop]"
.\.venv\Scripts\python -m okami_memorias.desktop
```

Escolha a pasta de fotos e selecione **Branco**, **Caderno azul** ou **Jardim da turma**. Digite um título se quiser repeti-lo em todas as páginas. Ajuste as margens observando a prévia da primeira página, escolha onde salvar e clique em **Gerar PDF**. Os modelos decorativos mantêm os fundos e molduras dentro das margens e reservam espaço para as fotos inteiras.

Se houver arquivos inválidos, a interface exibe a contagem e dá acesso aos nomes. Corrija os arquivos e selecione a pasta novamente. O botão **Cancelar** interrompe a operação no próximo ponto seguro. Uma foto grande ou a gravação final do PDF pode atrasar a resposta ao cancelamento.

### Exportar uma turma

Organize uma pasta com uma subpasta por aluno, como `Turma 5A/Ana`, `Turma 5A/João` e `Turma 5A/Luísa`. Coloque as fotos no nível imediato de cada subpasta.

1. Selecione **Turma — PDFs por aluno** e escolha a pasta da turma. Use **Ver lista da turma** para conferir contagens, pastas vazias e arquivos inválidos.
2. Escolha um aluno para visualizar a primeira página. Modelo e margens valem para toda a turma. Você pode deixar o título vazio, digitar um título comum ou usar o nome da subpasta como título de cada PDF.
3. Escolha uma pasta de destino existente e clique em **Exportar turma**. Confira os arquivos gerados, falhas e pendências em **Ver resultado do lote**.

Cada PDF recebe o nome da subpasta do aluno. Pastas vazias ou com arquivos inválidos são ignoradas. Se um PDF já existir, o lote registra a falha e continua com os demais alunos. Cancelar mantém os PDFs concluídos e descarta a exportação em andamento. Corrija as entradas e selecione novamente a pasta da turma para atualizar a validação.

### Preparar a impressão

Após exportar um álbum ou uma turma, clique em **Preparar impressão** para conferir a ordem dos PDFs e as páginas por arquivo. Abra o PDF selecionado ou a pasta de destino. No leitor de PDF, selecione A4, retrato e escala de **100% (Tamanho real)**. Imprima uma folha de teste e confira a margem de encadernação com uma régua.

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
