# Contribuindo com o Kairos

Estas são as convenções padrão da organização. O README, o guia de contribuição e as instruções específicas do repositório têm prioridade quando definirem requisitos próprios.

## Antes de começar

1. Escolha o repositório responsável pela mudança e leia seu README.
2. Procure issues e PRs existentes para evitar duplicação. Vincule o card do Jira quando houver.
3. Defina escopo e critérios de aceite. Mudanças de contrato entre API, mobile e frontend devem ser coordenadas.
4. Parta da branch principal atualizada. Preserve alterações locais de outras tarefas.

## Branches

Use nomes curtos, em inglês, separados por hífens:

| Prefixo | Uso | Exemplo |
|---|---|---|
| `feat/` | Nova funcionalidade | `feat/customer-registration` |
| `fix/` | Correção de comportamento | `fix/session-expiration` |
| `chore/` | Dependências, CI e manutenção | `chore/community-standards` |
| `docs/` | Documentação | `docs/mobile-authentication` |
| `refactor/` | Reorganização sem mudar o comportamento esperado | `refactor/customer-mapper` |
| `test/` | Testes | `test/session-renewal` |

Não use `codex/` como prefixo das branches de contribuição. Não force push na branch principal e não contorne proteções para concluir uma tarefa.

## Commits

Escreva mensagens em inglês no formato `type(scope): description`, com escopo opcional. Use uma descrição objetiva no imperativo, sem afirmar mudanças que não ocorreram.

```text
feat(auth): authenticate customers after registration
fix(customer): validate company before creating a customer
chore(ci): add repository validation
docs: document contribution guidelines
test(auth): cover expired Redis sessions
```

Separe mudanças por responsabilidade, mantendo cada commit coerente. Não inclua segredos, `.env`, dumps, dados pessoais ou artefatos gerados. Confira `git diff --staged` antes de commitar.

## Validação por projeto

Execute os comandos a partir da raiz do respectivo repositório, após seguir seu setup. Os workflows e o README de cada projeto são a referência final.

| Projeto | Validação |
|---|---|
| API Spring Boot | `./mvnw --batch-mode --no-transfer-progress clean verify`; perfil PostgreSQL: `./mvnw -Ppostgres-tests clean verify` |
| Servlet | `./mvnw --batch-mode --no-transfer-progress clean verify` |
| Mobile Android | `./gradlew --no-daemon testDebugUnitTest lintDebug assembleDebug` |
| Frontend React | `npm ci`, `npm run lint` e `npm run build` |
| Landing page | Verificação sintática dos scripts JavaScript e dos arquivos estruturados no CI |
| IA | Validação sintática Python/notebooks; não execute `test.py` como teste unitário: ele é um cliente interativo com serviços externos |
| BI, data, docs, infraestrutura e `.github` | Valide os artefatos presentes; repositórios sem aplicação ainda não possuem build ou testes de aplicação |

No Windows, use `mvnw.cmd` para Maven e `gradlew.bat` para Gradle. Use bancos isolados, emuladores e credenciais de teste. Não execute testes contra produção nem chame provedores pagos de IA sem autorização. Testes instrumentados Android exigem dispositivo/emulador e não são substituídos pelos testes unitários.

Se um workflow ainda estiver em uma PR aberta, suas novas validações não estarão disponíveis na branch principal antes do merge. Diga explicitamente o que foi e o que não foi executado.

## Pull requests e revisão

- Use o template: tipo, descrição, card, alterações, validação e observações.
- Mantenha a PR focada. Descreva migrações, compatibilidade e implantação quando necessário.
- Para mudanças visuais, inclua evidências sem dados pessoais.
- Preserve o padrão de services, controllers, repositories e mappers do projeto.
- Aguarde os checks obrigatórios e as aprovações exigidas pelo ruleset; atualmente, os repositórios usam três aprovações.
- O Copilot auxilia na revisão, mas não substitui validações nem revisão humana. Sua execução depende de acesso e quota disponíveis.
- Resolva conflitos e comentários antes do merge. Renomear a branch de origem pode fechar a PR; preserve os commits e documente qualquer PR substituta.

## Segurança

Não publique vulnerabilidades nos formulários de bug. Siga a [política de segurança](https://github.com/KairosApplication/.github/blob/main/SECURITY.md). Mascare logs, tokens, cookies e identificadores pessoais em qualquer evidência.
