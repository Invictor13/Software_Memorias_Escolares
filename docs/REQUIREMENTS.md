# Requisitos P0 a P4

- Executar localmente com Python 3.11 ou superior, Pillow e ReportLab.
- Importar JPG, JPEG e PNG do nível imediato da pasta, em ordem de nome sem distinção de caixa, com desempate pelo nome original.
- Corrigir EXIF, recusar entradas ilegíveis e preservar os originais. Compor transparência PNG sobre branco.
- Gerar páginas A4 retrato de 210 × 297 mm, com quatro espaços em ordem de leitura e fotos inteiras, centralizadas sem cortes. Deixar espaços vazios em branco.
- Aceitar margens e espaçamento finitos e não negativos. Usar por padrão 20 mm à esquerda, 10 mm nas demais margens e 5 mm entre espaços.
- Reduzir fotos grandes a aproximadamente 300 ppi no tamanho de impressão, sem ampliar as pequenas. Incorporar JPEG com qualidade 92 e metadados genéricos de documento.
- Gravar em caminho novo com extensão PDF e pasta existente. Limpar o temporário em caso de falha ou interrupção durante a geração.
- Oferecer CLI e testes com imagens sintéticas.
- Na interface desktop, permitir selecionar origem e destino, ver a quantidade de fotos e a lista de arquivos inválidos, ajustar margens e pré-visualizar a primeira página.
- Executar validação e exportação fora da thread da janela. Permitir cancelamento cooperativo até a publicação.
- Oferecer os modelos Branco, Caderno azul e Jardim da turma na interface desktop. O Branco sem título conserva a geometria da P1.
- Permitir um título opcional de uma linha. Dimensionar o texto dentro das margens e informar se ele não couber ou se contiver caracteres ausentes na fonte. Usar a mesma composição na prévia e em todas as páginas do PDF.
- Importar alunos a partir das subpastas imediatas da turma e exibir a contagem de fotos e problemas de cada aluno.
- Usar configurações de layout comuns, prévia por aluno e opções de título comum ou nome da subpasta.
- Exportar um PDF A4 por aluno apto para uma pasta de destino existente. Continuar após falhas individuais, proteger os arquivos existentes e preservar os PDFs concluídos se o lote for cancelado.
- Exibir a ordem e as páginas dos PDFs concluídos e orientar impressão em A4 retrato a 100%.
- Fornecer instalador offline para Windows x64, com atalho e desinstalador por usuário.
