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

Ao redistribuir um instalador ou wheelhouse, preserve os textos completos das licenças, os avisos de copyright e as exclusões de garantia das versões incluídas. Respeite as restrições de endosso das licenças BSD e os avisos e condições dos componentes nativos dos wheels, como os codecs do Pillow. Se o pacote incluir o interpretador Python, preserve a licença PSF e seus avisos correspondentes. Revise as dependências transitivas por plataforma e versão antes de empacotar.

A interface usa Qt Core, Gui e Widgets do wheel Essentials para limitar as dependências. Para redistribuir Qt/PySide/Shiboken sob LGPLv3, mantenha as bibliotecas separadas e substituíveis, informe seu uso e preserve os textos e avisos aplicáveis. Disponibilize o código-fonte correspondente dos componentes redistribuídos conforme a licença, incluindo eventuais modificações, e preserve o direito de engenharia reversa para depurar modificações nessas bibliotecas. Consulte os [avisos de Qt for Python](https://doc.qt.io/qtforpython-6/licenses.html) ao empacotar.
