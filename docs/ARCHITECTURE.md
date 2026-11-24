# Arquitetura

| Módulo | Responsabilidade |
| --- | --- |
| `__main__` | Interpretar a CLI e mapear falhas para códigos de saída. |
| `core` | Validar layout, destino e fotos antes de iniciar a exportação. |
| `imaging` | Ordenar e ler JPEG e PNG, corrigir EXIF e normalizar para RGB. |
| `layouts` | Calcular posições em milímetros, com origem no canto inferior esquerdo, e ajustar por `contain`. |
| `export` | Converter milímetros em pontos, paginar, reduzir imagens e publicar o PDF. |
| `errors` | Representar falhas de leitura e exportação. |
| `operation` | Reportar progresso e sinalizar cancelamento cooperativo sem depender de Qt. |
| `desktop` | Selecionar arquivos, exibir a primeira página e iniciar tarefas de validação e exportação em uma thread separada. |

`Mosaic.slots()` fornece quatro retângulos em ordem de leitura. Um futuro motor de decoração poderá usar essa geometria para posicionar elementos em milímetros, mantendo a composição independente da interface e a geometria independente do PDF.

A validação abre uma fotografia por vez. A exportação relê as imagens após validar o conjunto. Mantenha a pasta estável durante a execução. O ReportLab acumula recursos do PDF em memória até o fim, de modo que o consumo cresce com o álbum.

O exportador grava um temporário na pasta de destino e publica por renomeação no Windows ou por link físico em POSIX. A publicação recusa destinos que surgirem durante a geração. Em POSIX, o destino exige um sistema de arquivos com suporte a links físicos.

A interface armazena até quatro miniaturas em memória e recalcula a prévia com `Mosaic.slots()` e `Rect.contain()` quando as margens mudam. A exportação valida novamente a pasta antes de renderizar. O cancelamento é checado entre fotografias e antes da publicação do PDF.
