# Kairos · Padrões da organização

Repositório de apresentação e padrões compartilhados da [KairosApplication](https://github.com/KairosApplication). Não contém as aplicações do produto nem executa o deploy das APIs.

O Kairos apoia a gestão de gôndolas em supermercados. A visão do produto e o mapa dos projetos estão no [perfil da organização](https://github.com/KairosApplication/.github/blob/main/profile/README.md). A [wiki](https://github.com/KairosApplication/.github/wiki) reúne as orientações deste repositório.

## Estado da documentação

Na revisão de 10/10/2026, a `main` contém o perfil e a licença. Os padrões, este README e as validações abaixo estão em PRs abertas; só ficam disponíveis na branch principal após o merge.

| PR | Escopo |
| --- | --- |
| [#2](https://github.com/KairosApplication/.github/pull/2) | Guia de contribuição, segurança, formulários de issues, template de PR e validação estrutural. |
| [#4](https://github.com/KairosApplication/.github/pull/4) | Alternativa de template compartilhado de PR. |
| [#6](https://github.com/KairosApplication/.github/pull/6) | README deste repositório. |
| [#7](https://github.com/KairosApplication/.github/pull/7) | Validação de workflows com actionlint, secret scan e guia do deploy centralizado. |

As PRs #2 e #6 alteram o README; #2 e #4 adicionam templates com nomes que diferem em maiúsculas/minúsculas; #2 e #7 adicionam secret scan e um check chamado **Validate organization templates**. Consolidar os arquivos e evitar checks duplicados antes dos merges.

## Organização dos arquivos

Os caminhos abaixo identificam o conteúdo existente ou proposto nas PRs indicadas:

| Caminho | Responsabilidade |
| --- | --- |
| `profile/README.md` | Apresentação pública da organização, já na main. |
| `README.md` | Objetivo, estado e navegação deste repositório. |
| `CONTRIBUTING.md` e `SECURITY.md` | Contribuição e relato privado de vulnerabilidades (#2). |
| `.github/ISSUE_TEMPLATE/` | Formulários de bug, funcionalidade e tarefa técnica (#2). |
| `.github/pull_request_template.md` | Template da #2; consolidar com `.github/PULL_REQUEST_TEMPLATE.md` da #4. |
| `.github/workflows/` | Checks deste repositório (#2 e #7). |
| `.github/scripts/validate.py` e `.github/validation.md` | Validação estrutural e seus limites (#2). |
| `docs/aws-deploy.md` | Direcionamento para a automação em kairos-infra (#7). |
| `LICENSE` | Licença deste repositório; não define a licença dos demais projetos. |

## Como os padrões são aplicados

Arquivos comunitários compatíveis deste repositório público podem servir como padrão para os outros repositórios da organização depois de integrados na branch padrão. Um arquivo equivalente próprio no projeto de destino tem prioridade.

- O perfil utiliza `profile/README.md`; o README da raiz descreve o repositório.
- Os padrões não são copiados para o clone ou histórico Git dos projetos.
- Templates orientam novas issues/PRs; não reescrevem descrições já publicadas.
- Workflows e instruções do Copilot **não são herdados automaticamente**.
- Labels, assignees, revisores, rulesets e checks obrigatórios exigem configuração própria; o template não os aplica.

Veja a [referência oficial sobre arquivos comunitários padrão](https://docs.github.com/en/communities/setting-up-your-project-for-healthy-contributions/creating-a-default-community-health-file).

## Contribuição e pull requests

Use branches como `feat/`, `fix/`, `chore/`, `docs/`, `refactor/` e `test/`; não use `codex/`. Escreva commits em inglês no formato `type(scope): description`, com escopo opcional, e separe mudanças por responsabilidade.

Uma PR deve conter **Tipo de PR**, **Descrição**, **Card**, **Alterações** e **Observações**. Informe também a validação realizada, preferencialmente em uma seção **Validação**, distinguindo testes executados de limitações. Vincule o card do Jira quando existir; não invente um vínculo.

Aplique labels pelo conteúdo: `documentation` para documentação, `chore` para manutenção, `github_actions` para workflows e `security` para mudanças de segurança. Este repositório não precisa de labels de linguagem das aplicações. Revisão automática não substitui revisão humana nem os checks exigidos nas configurações do GitHub.

Leia o [guia de contribuição proposto](https://github.com/KairosApplication/.github/blob/chore/repository-validation/CONTRIBUTING.md) e a [política de segurança proposta](https://github.com/KairosApplication/.github/blob/chore/repository-validation/SECURITY.md). Não publique credenciais, cookies, dados pessoais ou vulnerabilidades em issues públicas.

## Validação e deploy

A #2 propõe validação sintática/estrutural dos artefatos versionados. A #7 valida workflows com actionlint em versão fixa e checksum. O secret scan usa Gitleaks com saída mascarada. Esses checks não executam aplicações, testes das APIs, bancos de dados ou deploy AWS.

Antes de enviar alterações, revise o Markdown, confirme os links e execute `git diff --check`. Acompanhe os checks da PR; validação sintática não deve ser apresentada como teste de aplicação.

O build e o deploy AWS ficam exclusivamente no [kairos-infra](https://github.com/KairosApplication/kairos-infra), cuja implementação central está na [PR #4](https://github.com/KairosApplication/kairos-infra/pull/4). Não configure Secrets AWS, runners ou workflows de deploy neste repositório para esse fluxo. Consulte a [wiki de infraestrutura](https://github.com/KairosApplication/kairos-infra/wiki) e o [guia de automação em revisão](https://github.com/KairosApplication/kairos-infra/blob/feat/automated-infrastructure/docs/automation.md).

## Manutenção

Ao integrar as PRs, atualize a seção de estado, consolide os templates/workflows e ajuste os links de branches de revisão para a main. Mantenha README e wiki alinhados sem afirmar que um workflow ou regra já está ativo apenas porque seu arquivo foi proposto.
