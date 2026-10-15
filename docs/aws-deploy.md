# Deploy AWS centralizado

Todo o fluxo de build e deploy fica no
[kairos-infra](https://github.com/KairosApplication/kairos-infra).

Os repositorios das APIs fornecem o codigo cadastrado no services.json.
Nao precisam de chamador de deploy, Secrets AWS ou runner. O repo .github
fornece os templates da organizacao; nao participa da execucao do deploy.

Para configurar ou executar, seguir o
[guia de automacao](https://github.com/KairosApplication/kairos-infra/blob/main/docs/automation.md).
O workflow Deploy connected services no infra consulta a main das APIs,
testa commits novos, publica imagens e reconcilia releases EKS.
