# Arquitetura

| Módulo | Responsabilidade |
| --- | --- |
| `__main__` | Interpretar a CLI e mapear falhas para códigos de saída. |
| `core` | Validar layout, destino e fotos antes de iniciar a exportação. |
| `imaging` | Ordenar e ler JPEG e PNG, corrigir EXIF e normalizar para RGB. |
| `layouts` | Calcular posições em milímetros, com origem no canto inferior esquerdo, e ajustar por `contain`. |
| `decoration` | Compor a folha em milímetros com preenchimentos vetoriais, áreas das fotos e título. |
| `export` | Converter milímetros em pontos, paginar, reduzir imagens e publicar o PDF. |
| `errors` | Representar falhas de leitura e exportação. |
| `operation` | Reportar progresso e sinalizar cancelamento cooperativo sem depender de Qt. |
| `batch` | Validar a estrutura da turma, chamar a exportação individual e registrar o resultado de cada aluno. |
| `desktop` | Selecionar arquivos, exibir a primeira página e iniciar tarefas de validação e exportação em uma thread separada. |

`Mosaic.slots()` fornece quatro retângulos em ordem de leitura. `compose_page()` calcula o espaço do modelo dentro das margens e entrega um `PageDesign` com as formas, molduras, áreas úteis das fotos e, quando preenchido, o título. A prévia Qt e a renderização ReportLab desenham essa composição usando suas respectivas unidades. Os temas internos são definidos em código e permanecem disponíveis offline.

A validação abre uma fotografia por vez. A exportação relê as imagens após validar o conjunto. Mantenha a pasta estável durante a execução. O ReportLab acumula recursos do PDF em memória até o fim, de modo que o consumo cresce com o álbum.

O exportador grava um temporário na pasta de destino e publica por renomeação no Windows ou por link físico em POSIX. A publicação recusa destinos que surgirem durante a geração. Em POSIX, o destino exige um sistema de arquivos com suporte a links físicos.

A interface armazena até quatro miniaturas em memória e recalcula a composição quando o modelo, o título ou as margens mudam. Ambos os renderizadores usam `Rect.contain()` para posicionar as fotos. Molduras são desenhadas apenas nas posições ocupadas. A exportação valida novamente a pasta antes de renderizar. O cancelamento é checado entre fotografias e antes da publicação do PDF.

No modo Turma, a validação lê os arquivos de cada aluno e armazena contagens e problemas. As miniaturas são carregadas sob demanda apenas para o aluno selecionado. O lote usa a mesma exportação individual para cada subpasta apta, com cancelamento compartilhado e progresso por aluno. Cada PDF é publicado separadamente e o resultado registra arquivos gerados, falhas, alunos ignorados na validação e alunos pendentes após cancelamento.
