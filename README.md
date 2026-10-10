# Automação de documentação da KairosApplication

O workflow `.github/workflows/documentation-bot.yml` centraliza a sincronização dos repositórios da organização. Não altera o perfil em `profile/README.md`.

## Garantia de isolamento por repositório

Cada job recebe `repository`, `branch` e `wiki` da API do GitHub. O código confere o remote do checkout com esse alvo e confere o remote da wiki com **o mesmo alvo**, acrescido de `.wiki.git`. Uma divergência interrompe a execução.

- O README é atualizado em uma PR no **repositório alvo**, na branch `chore/automated-documentation`, sem auto-merge.
- A wiki é atualizada no Git separado **`https://github.com/<organização>/<repositório-alvo>.wiki.git`**.
- Links da wiki apontam para arquivos e branch do próprio alvo, nunca para o hub `.github`.
- A wiki é sincronizada antes de gerar alterações para a PR: recebe apenas documentação já integrada na branch padrão.
- Conteúdo manual do README e da Home é preservado fora de `<!-- docs-bot:start -->` / `<!-- docs-bot:end -->`. Páginas existentes não são apagadas. Páginas geradas usam `Bot-README` e `Bot-Doc-<caminho-em-hexadecimal>`; colisões com conteúdo não gerenciado são rejeitadas.

## O que é atualizado

Para qualquer stack: índice dos arquivos Markdown de `docs/` no README existente e cópias do README e desses guias na wiki atual. Não reescreve explicações técnicas por IA nem executa scripts do repositório alvo. Sem README Markdown ou guias, não inventa conteúdo.

Para a API Kairos com controllers em `src/main/java/com/kairos/kairosapipostgres/controller`, gera também `docs/api-endpoints.md` e versões Java/Spring Boot a partir do `pom.xml`. Mapeamentos Java não suportados falham explicitamente para evitar publicar rotas incorretas.

## Ativação

1. Integre esta branch à branch padrão de `KairosApplication/.github`. Publicar só a branch não ativa o agendamento.
2. Configure o secret de organização **`DOCS_BOT_TOKEN`**, disponível ao repo `.github`. O token precisa ler os repositórios cobertos e escrever conteúdo/wiki e PRs neles. Um token fine-grained requer acesso aos repos escolhidos, **Contents: read/write**, **Pull requests: read/write** e Metadata/read. Valide também o acesso Git à wiki e as políticas/SSO da organização. O `GITHUB_TOKEN` de `.github` não dá acesso de escrita aos outros repositórios.
3. Execute manualmente `Organization documentation bot` e confira um repositório antes de depender do agendamento.
4. Habilite e inicialize a wiki de cada alvo com uma página `Home.md`. Wikis desabilitadas são ignoradas; wikis inacessíveis falham com diagnóstico (não se troca o destino por outro repo).

A descoberta é dinâmica: cobre repositórios acessíveis ao token, ativos, não-forks e não-vazios; exclui `.github`. Novos repositórios entram automaticamente **se o token tiver acesso a eles**. Até 256 alvos por execução, limite da matriz do GitHub Actions.

## Frequência e após merge

O agendamento é diário às 12:17 UTC com uma condição que permite execução a cada **três dias corridos**, contados de 10/10/2026; não usa `*/3` no dia do mês, que quebra o intervalo na virada do mês. O GitHub pode atrasar execuções agendadas. Execução manual ignora o intervalo.

Para disparar também após cada merge/push em `main`, instale `workflow-templates/documentation-sync.yml` em `.github/workflows/` de cada repo e disponibilize o secret ao chamador (inclusive acesso Contents/write a `.github` para `repository_dispatch`). Ajuste a branch se a principal não for `main`. O template apenas notifica o hub com `github.repository`; a descoberta central valida que o alvo pertence à organização.

**Workflows no repo `.github` não são herdados automaticamente pelos demais repos.** O polling a cada três dias é central e não exige chamadores; o disparo imediato após merge exige instalar o chamador ou uma integração GitHub App/webhook. O template não é instalado nos outros repos por esta alteração.

## Verificação local

```sh
python -m unittest discover -s .github/scripts -p 'test_*.py' -v
```

Os testes cobrem rejeição de checkout/wiki trocados, alvo fora da organização, preservação de texto manual e que links e páginas pertençam ao mesmo repositório.
