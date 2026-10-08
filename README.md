# Kairos · Padrões da organização

Repositório de apresentação e padrões compartilhados da [KairosApplication](https://github.com/KairosApplication).

O Kairos é uma plataforma de gestão de gôndolas para supermercados, com alertas de reposição, histórico operacional e análise de dados. A apresentação do projeto está em [profile/README.md](profile/README.md).

## Objetivo deste repositório

Centralizar as orientações de colaboração e os modelos usados nos repositórios da organização. O nome especial `.github` permite que o GitHub utilize arquivos de comunidade como padrão quando um repositório não possui uma versão própria.

## Organização dos arquivos

| Caminho | Finalidade |
| --- | --- |
| `README.md` | Documentação deste repositório. |
| `profile/README.md` | Apresentação exibida no perfil da organização. |
| `.github/PULL_REQUEST_TEMPLATE.md` | Caminho do template compartilhado de PR, após sua integração na branch padrão. |
| `LICENSE` | Licença deste repositório. |

## Padrão de pull request

O template organiza a descrição de cada alteração em cinco seções:

| Seção | Como preencher |
| --- | --- |
| **Tipo de PR** | Marque todas as opções aplicáveis: Bug Fix, Feature, Refactor, Performance Improvement, Documentation, Style, Test, Chore ou Revert. |
| **Descrição** | Explique o objetivo da alteração e o problema que ela resolve. |
| **Card** | Informe o link do card no Jira. Se não houver card, indique isso. |
| **Alterações** | Liste as principais mudanças realizadas. |
| **Observações** | Inclua os testes realizados, cuidados no deploy e informações úteis para a revisão, quando aplicável. |

### Como o template é aplicado

1. O template precisa estar integrado na branch padrão deste repositório público.
2. Ao abrir uma nova PR em um repositório da organização sem template próprio, o GitHub utiliza o modelo compartilhado.
3. O autor preenche as seções e marca os tipos de alteração antes de solicitar a revisão.

Um template próprio no repositório de destino tem prioridade. O modelo compartilhado não é copiado para o histórico Git desses repositórios e não altera as descrições de PRs já abertas.

O template orienta o preenchimento. Verificações obrigatórias, aprovação de revisores e proteção de branches são configuradas por workflows e regras do GitHub.

## Como contribuir

1. Crie uma branch a partir da branch padrão.
2. Edite o arquivo correspondente: a apresentação da organização fica em `profile/README.md`; a documentação do repositório fica neste README.
3. Revise o Markdown, os links e a clareza das instruções.
4. Abra uma PR descrevendo a mudança e aguarde as verificações exigidas pelo repositório.

Alterações em arquivos compartilhados podem afetar vários repositórios. Explique esse impacto na descrição da PR.

## Referência

O comportamento dos arquivos compartilhados está descrito na [documentação oficial do GitHub](https://docs.github.com/en/communities/setting-up-your-project-for-healthy-contributions/creating-a-default-community-health-file).
