# Deploy AWS compartilhado

O workflow `.github/workflows/deploy-application.yml` e o ponto de entrada
compartilhado das APIs Kairos. Ele delega build, verificacao e deploy ao
`kairos-infra`, mantendo a identidade do repositorio chamador.

Cada API instala seu `deploy.yml` e chama:

```yaml
uses: KairosApplication/.github/.github/workflows/deploy-application.yml@main
```

O arquivo completo do chamador esta em
[examples/mobile-api/deploy.yml](https://github.com/KairosApplication/kairos-infra/blob/main/examples/mobile-api/deploy.yml).
O workflow executa depois da CI aprovada em main ou por execucao manual.

## Configuracao

- Cadastrar a API habilitada no services.json do infra.
- Configurar AWS_ACCOUNT_ID, AWS_REGION, EKS_CLUSTER_NAME, AWS_PUBLISHER_ROLE_ARN,
  AWS_DEPLOYER_ROLE_ARN, API_HOST e API_CERTIFICATE_ARN como Variables da API.
- Criar o Environment production restrito a main.
- Para chaves AWS, configurar AWS_ACCESS_KEY_ID e AWS_SECRET_ACCESS_KEY em Secrets
  da API e permitir ao principal assumir as roles; AWS_SESSION_TOKEN e opcional
  para credenciais temporarias. Sem esses Secrets, usar OIDC.
- Ativar KAIROS_DEPLOY_ENABLED=true somente depois de provisionar a AWS e a plataforma.

O cadastro permite apenas servicos aprovados da KairosApplication. A Action
verifica se o release existe e se seu manifesto precisa ser atualizado, publica
imagens imutaveis e usa rollout gradual com verificacoes e rollback Helm.

Para solicitar a verificacao de todos os servicos cadastrados, executar
**Deploy connected services** no kairos-infra. Ela tambem e disparada apos um
provisionamento bem-sucedido em main. O resultado de cada deploy aparece no
Actions da API correspondente.

Integrar o infra primeiro, este workflow depois, e por ultimo os chamadores.
Os detalhes de IAM, runner privado, Secrets, Variables e triggers estao no
[guia de automacao](https://github.com/KairosApplication/kairos-infra/blob/main/docs/automation.md).
