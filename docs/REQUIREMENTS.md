# Requisitos P0 e P1

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
