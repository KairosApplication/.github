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

## Manutenção

Mantenha o README, a wiki e os arquivos referenciados alinhados. Ao integrar mudanças, atualize os links e remova informações de revisão que deixaram de ser atuais. Preserve um único template compartilhado de PR e evite nomes de checks duplicados ao consolidar workflows. Não afirme que uma regra, workflow ou implantação está ativo apenas porque seu arquivo foi adicionado.
