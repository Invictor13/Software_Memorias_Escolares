# Licenças de terceiros

| Componente | Uso | Licença |
| --- | --- | --- |
| [Pillow](https://github.com/python-pillow/Pillow/blob/main/LICENSE) | Execução | Permissiva derivada do PIL. O wheel 12.3.0 declara MIT-CMU. Confira o texto da versão distribuída. |
| [ReportLab](https://docs.reportlab.com/developerfaqs/) | Execução | BSD de 3 cláusulas |
| [charset-normalizer](https://pypi.org/project/charset-normalizer/) | Dependência do ReportLab | MIT |
| [pytest](https://github.com/pytest-dev/pytest/blob/main/LICENSE) | Testes | MIT |
| [pypdf](https://pypi.org/project/pypdf/) | Testes | BSD de 3 cláusulas |
| [iniconfig](https://pypi.org/project/iniconfig/) e [pluggy](https://pypi.org/project/pluggy/) | Dependências de teste | MIT |
| [colorama](https://pypi.org/project/colorama/) | Dependência de teste no Windows | BSD de 3 cláusulas |
| [packaging](https://pypi.org/project/packaging/) | Dependência de teste | Apache-2.0 ou BSD de 2 cláusulas |
| [Pygments](https://pypi.org/project/Pygments/) | Dependência de teste | BSD de 2 cláusulas |
| [setuptools](https://pypi.org/project/setuptools/) | Build | MIT |
| [PySide6-Essentials e shiboken6](https://doc.qt.io/qtforpython-6/) | Interface desktop opcional | Qt for Python Community, LGPLv3 ou GPLv3, com avisos de terceiros. |
| Bitstream Vera Sans Bold | Título opcional no PDF e na prévia | Licença Bitstream Vera, distribuída pelo ReportLab em `reportlab/fonts/bitstream-vera-license.txt`. |
| [CPython](https://docs.python.org/3/license.html) | Interpretador no instalador | PSF e avisos de componentes distribuídos no instalador oficial. |
| [PyInstaller](https://www.pyinstaller.org/en/stable/license.html) | Build Windows | GPL com exceção de empacotamento. Arquivos específicos sob Apache-2.0. |
| [NSIS](https://nsis.sourceforge.io/License) | Build e desinstalador Windows | zlib/libpng para o instalador com compressão zlib, com avisos do projeto. |

Ao redistribuir um instalador ou wheelhouse, preserve os textos completos das licenças, os avisos de copyright e as exclusões de garantia das versões incluídas. Respeite as restrições de endosso das licenças BSD e os avisos e condições dos componentes nativos dos wheels, como os codecs do Pillow. Se o pacote incluir o interpretador Python, preserve a licença PSF e seus avisos correspondentes. Revise as dependências transitivas por plataforma e versão antes de empacotar.

A interface usa Qt Core, Gui e Widgets do wheel Essentials para limitar as dependências. Para redistribuir Qt/PySide/Shiboken sob LGPLv3, mantenha as bibliotecas separadas e substituíveis, informe seu uso e preserve os textos e avisos aplicáveis. Disponibilize o código-fonte correspondente dos componentes redistribuídos conforme a licença, incluindo eventuais modificações, e preserve o direito de engenharia reversa para depurar modificações nessas bibliotecas. Consulte os [avisos de Qt for Python](https://doc.qt.io/qtforpython-6/licenses.html) ao empacotar.

O título usa a fonte `VeraBd.ttf` já presente no ReportLab e incorpora um subconjunto no PDF. Na redistribuição do aplicativo com essa fonte, preserve os avisos e o texto da licença que acompanham o wheel. A licença permite incorporar a fonte e restringe sua venda isolada e o uso dos nomes Bitstream e Vera em versões modificadas.

O build Windows coleta os textos de licença das dependências, os avisos do Python, a licença do NSIS e as referências às versões de Qt/PySide/Shiboken. Mantenha o código-fonte correspondente disponível aos destinatários do binário conforme a LGPLv3, incluindo eventuais modificações. Preserve também os avisos do runtime do Visual C++ redistribuível que acompanha o CPython.
