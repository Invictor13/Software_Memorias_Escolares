# Instalador Windows x64

## Instalar e usar

Execute o instalador e abra **OKAMI Memórias Escolares 0.5.0** no menu Iniciar. A instalação é por usuário e inclui o interpretador e as bibliotecas. O aplicativo gera PDFs offline. Para remover o programa, use **Aplicativos instalados** nas configurações do Windows. Os arquivos exportados e os arquivos pessoais fora da lista instalada permanecem no disco.

## Gerar o instalador

É necessário Windows x64, Python x64 com o extra de build e o compilador [NSIS 3](https://nsis.sourceforge.io/Download). A estação de build precisa dos pacotes preparados localmente ou de acesso ao índice de pacotes. Exemplo no PowerShell, a partir da raiz do repositório:

```powershell
python -m venv .venv
.\.venv\Scripts\python -m pip install ".[desktop,windows-build,test]"
.\.venv\Scripts\python scripts/windows/build_installer.py --makensis "C:\Ferramentas\NSIS\makensis.exe"
```

A saída fica em `dist/windows/`, com o instalador e o arquivo `.sha256`. O build empacota o aplicativo com PyInstaller em modo pasta, mantendo DLLs e extensões Qt substituíveis. O NSIS instala essa pasta e gera um desinstalador que remove os caminhos registrados no build. A pasta `Licencas` no aplicativo reúne avisos, versões e referências de código-fonte. Os binários desta etapa são locais e sem assinatura Authenticode.

O empacotamento limita os caminhos usados para descobrir DLLs e usa a versão mais recente do runtime Visual C++ já incluída pelas dependências. Isso evita misturar bibliotecas de outros programas da estação de build.

## Verificar a instalação

O teste automatizado abaixo usa uma pasta temporária dentro de `build/windows/`. Ele instala silenciosamente para a conta atual, verifica o atalho, inicia o executável com PATH restrito ao Windows, inspeciona um lote sintético e desinstala. Também verifica a preservação de um arquivo particular colocado na pasta durante o teste. Execute em uma conta onde a versão sob teste ainda não esteja instalada:

```powershell
.\scripts\windows\test_installer.ps1 -Installer .\dist\windows\OKAMI-Memorias-0.5.0-Windows-x64.exe -TestPython .\.venv\Scripts\python.exe
```

Para o aceite em outra máquina, copie o instalador para um Windows x64 sem Python, desconecte a rede e instale. Abra pelo menu Iniciar, exporte uma turma fictícia com 1, 4 e 5 fotos e confira a ordem e as 1, 1 e 2 páginas na janela de impressão. Use o modelo Caderno azul com margem esquerda de 25 mm. Imprima uma folha A4 em retrato a 100% e meça da borda esquerda do papel até o início do fundo azul para verificar os 25 mm. Drivers e impressoras podem impor margens físicas próprias.

Para distribuir o instalador fora da equipe, disponibilize também o código-fonte correspondente das bibliotecas Qt/PySide/Shiboken do build conforme os termos aplicáveis. As versões e referências registradas auxiliam a montar esse conjunto. Consulte [licenças de terceiros](THIRD_PARTY_LICENSES.md).
