# Política de segurança

Esta política é o padrão para os repositórios Kairos que não tenham uma política própria. O projeto está em desenvolvimento: não há compromisso de suporte de longo prazo, prazo de resposta ou programa de recompensa definido por este documento.

## Como reportar uma vulnerabilidade

**Não abra uma issue pública com detalhes da exploração, credenciais ou dados pessoais.**

1. No repositório afetado, procure **Security → Advisories → Report a vulnerability**. Use esse canal privado quando ele estiver habilitado.
2. Se essa opção não estiver disponível, integrantes da equipe devem usar seu canal privado já existente com os mantenedores. Não coloque detalhes em cards do Jira que tenham acesso público ou amplo.
3. Para contribuidores externos sem um canal privado, peça aos mantenedores somente um meio de contato privado, sem descrever a falha ou anexar evidências sensíveis. Aguarde esse canal antes de compartilhar detalhes.

Este arquivo não habilita automaticamente private vulnerability reporting e não inventa um e-mail de segurança. A disponibilidade do canal deve ser verificada no repositório afetado.

## Informações úteis para o relato privado

- Repositório, branch/commit e componente afetado.
- Resumo, impacto esperado e pré-condições da falha.
- Passos mínimos para reprodução em ambiente isolado.
- Evidências com valores sensíveis mascarados.
- Possível correção, se conhecida.

Compartilhe apenas o necessário. Nunca envie senhas, tokens válidos, cookies de sessão, chaves de IA, dados pessoais de clientes ou dumps reais. Utilize valores fictícios e contas de teste.

## Testes responsáveis

Limite os testes a ambientes sob sua autorização. Não acesse dados de terceiros, não altere bancos reais e não faça testes destrutivos, de carga, indisponibilidade ou chamadas pagas sem autorização específica.

Mantenha detalhes de exploração privados até coordenar a divulgação com os mantenedores. Se uma credencial foi exposta, o responsável deve revogá-la ou rotacioná-la; apenas apagar o texto ou fechar a PR não remove a credencial do histórico.
