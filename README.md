# Kairos · Padrões da organização

Este repositório concentra a apresentação da [KairosApplication](https://github.com/KairosApplication) e os padrões compartilhados de colaboração. Não contém as aplicações do produto, não substitui a documentação técnica dos projetos e não executa o deploy das APIs.

O Kairos apoia a gestão de gôndolas em supermercados. A visão do produto, a arquitetura de referência e o mapa dos projetos estão no [perfil da organização](profile/README.md). A [wiki](https://github.com/KairosApplication/.github/wiki) reúne orientações complementares deste repositório.

## Organização dos arquivos

| Caminho | Responsabilidade |
| --- | --- |
| [profile/README.md](profile/README.md) | Apresentação pública da organização e mapa dos projetos. |
| [README.md](README.md) | Objetivo e navegação deste repositório. |
| [CONTRIBUTING.md](CONTRIBUTING.md) | Convenções de branches, commits, validação e revisão. |
| [SECURITY.md](SECURITY.md) | Relato responsável e privado de vulnerabilidades. |
| [.github/ISSUE_TEMPLATE/](.github/ISSUE_TEMPLATE/) | Formulários de bug, funcionalidade e tarefa técnica. |
| [.github/pull_request_template.md](.github/pull_request_template.md) | Template compartilhado de pull requests. |
| [.github/workflows/](.github/workflows/) | Validações executadas neste repositório. |
| [.github/scripts/validate.py](.github/scripts/validate.py) e [.github/validation.md](.github/validation.md) | Validação estrutural e seus limites. |
| [.github/copilot-instructions.md](.github/copilot-instructions.md) | Orientações de revisão específicas deste repositório. |
| [docs/aws-deploy.md](docs/aws-deploy.md) | Direcionamento para a automação centralizada no `kairos-infra`. |
| [.github/workflows/documentation-bot.yml](.github/workflows/documentation-bot.yml) | Sincronização centralizada de documentação dos repositórios elegíveis. |
| [workflow-templates/documentation-sync.yml](workflow-templates/documentation-sync.yml) | Chamador opcional para notificar o bot após push na branch principal. |
| [LICENSE](LICENSE) | Licença deste repositório; não define a licença dos demais projetos. |

## Como os padrões são aplicados

O GitHub utiliza os arquivos comunitários compatíveis deste repositório público, presentes na branch padrão, como padrão para os repositórios da organização que não tenham um arquivo próprio correspondente. Templates locais de PR e configurações/formulários locais de issues têm prioridade; não são sobrescritos por estes padrões.

- O perfil utiliza `profile/README.md`; o README da raiz descreve o repositório.
- Os padrões não são copiados para o clone ou histórico Git dos projetos.
- Templates orientam novas issues e PRs; não reescrevem descrições já publicadas.
- Workflows e instruções do Copilot **não são herdados automaticamente** pelos outros repositórios.
- Labels, assignees, revisores, rulesets e checks obrigatórios exigem configuração própria; o template não os aplica.
- Licenças continuam sendo definidas em cada repositório.

Veja a [referência oficial sobre arquivos comunitários padrão](https://docs.github.com/en/communities/setting-up-your-project-for-healthy-contributions/creating-a-default-community-health-file).

## Contribuição e pull requests

Leia o [guia de contribuição](CONTRIBUTING.md) e a [política de segurança](SECURITY.md) antes de contribuir. Use branches como `feat/`, `fix/`, `chore/`, `docs/`, `refactor/` e `test/`; não use `codex/`. Escreva commits em inglês no formato `type(scope): description`, com escopo opcional, e separe mudanças por responsabilidade.

Preencha o [template de PR](.github/pull_request_template.md) com informações correspondentes ao diff:

- **Tipo de PR:** marque os tipos de mudança realmente realizados.
- **Descrição:** explique o objetivo e o problema resolvido.
- **Card:** vincule o card do Jira ou a issue quando existir; não invente um vínculo.
- **Alterações:** liste as mudanças relevantes, sem incluir funcionalidades que não foram alteradas.
- **Validação:** informe comandos e resultados, distinguindo testes executados de limitações.
- **Observações:** registre impactos, compatibilidade, migrações e implantação/rollback quando aplicáveis.
- **Checklist:** confirme as verificações realizadas antes de solicitar revisão.

Aplique labels pelo conteúdo: `documentation` para documentação, `chore` para manutenção, `github_actions` para workflows e `security` para mudanças de segurança, quando disponíveis. Este repositório não precisa de labels de linguagem das aplicações.

Revisão automática não substitui revisão humana nem os checks exigidos nas configurações do GitHub. Não publique credenciais, cookies, dados pessoais ou vulnerabilidades em issues públicas.

## Validação e deploy

Os workflows em [.github/workflows/](.github/workflows/) validam a sintaxe e a estrutura dos artefatos versionados, verificam workflows com actionlint em versão fixa e checksum e executam secret scan com Gitleaks e saída mascarada. Esses checks não executam aplicações, testes das APIs, bancos de dados ou deploy AWS.

Antes de enviar alterações, revise o Markdown, confirme os links e execute `git diff --check`. Para executar a validação estrutural da raiz do repositório:

```sh
python -m pip install PyYAML==6.0.2 sqlglot==26.33.0
python .github/scripts/validate.py
```

Use um ambiente Python isolado e acompanhe os checks da PR. Validação sintática não deve ser apresentada como teste de aplicação. Consulte [.github/validation.md](.github/validation.md) para os limites dessas verificações; a exigência de cada check depende das configurações do GitHub.

O build e o deploy AWS são responsabilidade exclusiva do [kairos-infra](https://github.com/KairosApplication/kairos-infra). A implementação centralizada está descrita na [PR #4 de infraestrutura](https://github.com/KairosApplication/kairos-infra/pull/4). Este repositório fornece os padrões da organização e não participa da execução do deploy. Não configure Secrets AWS, runners ou workflows de deploy aqui para esse fluxo. Consulte o [guia de direcionamento](docs/aws-deploy.md) e a [wiki de infraestrutura](https://github.com/KairosApplication/kairos-infra/wiki).

## Automação de documentação

O workflow `.github/workflows/documentation-bot.yml` centraliza a sincronização dos repositórios da organização. Não altera o perfil em `profile/README.md`.

### Garantia de isolamento por repositório

Cada job recebe `repository`, `branch` e `wiki` da API do GitHub. O código confere o remote do checkout com esse alvo e confere o remote da wiki com **o mesmo alvo**, acrescido de `.wiki.git`. Uma divergência interrompe a execução.

- O README é atualizado em uma PR no **repositório alvo**, na branch `chore/automated-documentation`, sem auto-merge.
- A wiki é atualizada no Git separado **`https://github.com/<organização>/<repositório-alvo>.wiki.git`**.
- Links da wiki apontam para arquivos e branch do próprio alvo, nunca para o hub `.github`.
- A wiki é sincronizada antes de gerar alterações para a PR: recebe apenas documentação já integrada na branch padrão.
- Conteúdo manual do README e da Home é preservado fora de `<!-- docs-bot:start -->` / `<!-- docs-bot:end -->`. Páginas existentes não são apagadas. Páginas geradas usam `Bot-README` e `Bot-Doc-<caminho-em-hexadecimal>`; colisões com conteúdo não gerenciado são rejeitadas.

### O que é atualizado

Para qualquer stack: índice dos arquivos Markdown de `docs/` no README existente e cópias do README e desses guias na wiki atual. Não reescreve explicações técnicas por IA nem executa scripts do repositório alvo. Sem README Markdown ou guias, não inventa conteúdo.

Para a API Kairos com controllers em `src/main/java/com/kairos/kairosapipostgres/controller`, gera também `docs/api-endpoints.md` e versões Java/Spring Boot a partir do `pom.xml`. Mapeamentos Java não suportados falham explicitamente para evitar publicar rotas incorretas.

### Ativação

1. O workflow deve estar integrado à branch padrão de `KairosApplication/.github`. Publicar só uma branch de desenvolvimento não ativa o agendamento.
2. Configure o secret de organização **`DOCS_BOT_TOKEN`**, disponível ao repo `.github`. O token precisa ler os repositórios cobertos e escrever conteúdo/wiki e PRs neles. Um token fine-grained requer acesso aos repos escolhidos, **Contents: read/write**, **Pull requests: read/write** e Metadata/read. Valide também o acesso Git à wiki e as políticas/SSO da organização. O `GITHUB_TOKEN` de `.github` não dá acesso de escrita aos outros repositórios.
3. Execute manualmente `Organization documentation bot` e confira um repositório antes de depender do agendamento.
4. Habilite e inicialize a wiki de cada alvo com uma página `Home.md`. Wikis desabilitadas são ignoradas; wikis inacessíveis, vazias ou sem Home geram aviso e não impedem a PR do README. Falhas na publicação da wiki também geram aviso. O resumo da execução indica o que ficou pendente; divergências de identidade ou conteúdo inválido continuam interrompendo o job.

A descoberta é dinâmica: cobre repositórios acessíveis ao token, ativos, não-forks e não-vazios, com README Markdown na raiz ou pasta `docs/`; exclui `.github`. Repositórios sem documentação são informados no resumo e ignorados antes do checkout. Assim, um repo sem documentação e com submódulo incompleto não bloqueia o bot. O submódulo precisa ser corrigido no repo de origem antes de habilitar seu checkout. Novos repositórios entram automaticamente **se o token tiver acesso a eles e houver documentação para sincronizar**. Até 256 alvos por execução, limite da matriz do GitHub Actions.

A PR inclui somente os arquivos permitidos que realmente foram alterados e existem no checkout: o README com seu nome real e, quando gerada, `docs/api-endpoints.md`. Não são passadas alternativas inexistentes de maiúsculas/minúsculas ao Git. Sem alterações, a etapa de criação da PR é ignorada.

### Frequência e após merge

O agendamento é diário às 12:17 UTC com uma condição que permite execução a cada **três dias corridos**, contados de 10/10/2026; não usa `*/3` no dia do mês, que quebra o intervalo na virada do mês. O GitHub pode atrasar execuções agendadas. Execução manual ignora o intervalo.

Para disparar também após cada merge/push em `main`, instale [workflow-templates/documentation-sync.yml](workflow-templates/documentation-sync.yml) em `.github/workflows/` de cada repo e disponibilize o secret ao chamador (inclusive acesso Contents/write a `.github` para `repository_dispatch`). Ajuste a branch se a principal não for `main`. O template apenas notifica o hub com `github.repository`; a descoberta central valida que o alvo pertence à organização.

**Workflows no repo `.github` não são herdados automaticamente pelos demais repos.** O polling a cada três dias é central e não exige chamadores; o disparo imediato após merge exige instalar o chamador ou uma integração GitHub App/webhook. O template não é instalado nos outros repos por esta alteração.

### Verificação local

```sh
python -m unittest discover -s .github/scripts -p 'test_*.py' -v
```

Os testes cobrem rejeição de checkout/wiki trocados, alvo fora da organização, preservação de texto manual e que links e páginas pertençam ao mesmo repositório.

## Manutenção

Mantenha o README, a wiki e os arquivos referenciados alinhados. Ao integrar mudanças, atualize os links e remova informações de revisão que deixaram de ser atuais. Preserve um único template compartilhado de PR e evite nomes de checks duplicados ao consolidar workflows. Não afirme que uma regra, workflow ou implantação está ativo apenas porque seu arquivo foi adicionado.
