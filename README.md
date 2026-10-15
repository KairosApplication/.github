# Padrões da organização Kairos

Este repositório concentra a apresentação da organização e os padrões compartilhados de colaboração. Não contém a aplicação Kairos nem substitui a documentação técnica dos projetos.

## Conteúdo

- [Perfil da organização](profile/README.md): visão do produto, arquitetura de referência e mapa de repositórios.
- [Guia de contribuição](CONTRIBUTING.md): branches, commits, validação e revisão.
- [Política de segurança](SECURITY.md): relato responsável e privado de vulnerabilidades.
- [Template de pull request](.github/pull_request_template.md).
- [Formulários de issues](.github/ISSUE_TEMPLATE): bug, funcionalidade e tarefa técnica.

## Como os padrões são usados

Após o merge na `main`, o GitHub utiliza os arquivos comunitários deste repositório público como padrão nos repositórios da organização que não tenham um arquivo próprio correspondente. Templates locais de PR e configurações/formulários locais de issues têm prioridade; não são sobrescritos por estes padrões.

O arquivo `profile/README.md` compõe a apresentação pública da organização. Os padrões não são copiados para o histórico ou para o clone dos outros projetos.

Workflows **não** são herdados automaticamente. Esta alteração não adiciona workflows reutilizáveis, não altera CI e não modifica rulesets. Licenças continuam sendo definidas em cada repositório.

Referência: [arquivos comunitários padrão no GitHub](https://docs.github.com/en/communities/setting-up-your-project-for-healthy-contributions/creating-a-default-community-health-file).
