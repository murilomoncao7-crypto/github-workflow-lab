# Verificação automática da documentação

O laboratório cresceu e a conferência de links e blocos de código era apenas manual. O [verificador local](../scripts/check_docs.py) permite repetir parte dessa revisão antes do commit e no GitHub, sem instalar pacotes Python nem acessar URLs durante a análise.

## Executar localmente

Requer Python 3.11 ou mais recente. Na raiz deste clone, confira o interpretador e rode os mesmos comandos usados pelo workflow:

```sh
python --version
python -B -m unittest discover -s tests -v
python -B scripts/check_docs.py
```

No Windows, se o comando disponível for o Python Launcher, use `py -3` no lugar de `python`. Um atalho da Microsoft Store sem Python instalado não é um interpretador; interrompa e prepare um Python válido antes de depender do resultado. Os comandos usam o interpretador, sem precisar executar arquivos `.ps1` ou alterar políticas do PowerShell.

O verificador localiza a raiz a partir do próprio arquivo; também aceita `--root` com uma pasta de documentação para testes. A saída informa o arquivo e a linha do problema, por exemplo:

```text
README.md:3: link local inexistente: docs/arquivo-ausente.md
```

O código de saída é `0` quando a análise passa e `1` quando encontra problemas. No PowerShell, confira `$LASTEXITCODE` imediatamente após cada comando. Os [testes](../tests/test_check_docs.py) criam exemplos temporários dentro do clone e os removem ao terminar; esses exemplos não são alterações para publicar.

## O que é verificado

- Leitura UTF-8 dos arquivos `.md` da raiz e de `docs/`, incluindo subpastas.
- Fechamento de blocos com três ou mais acentos graves ou tils, respeitando o tipo e o tamanho do marcador.
- Existência de destinos locais de links e imagens no formato inline, como `[Guia](arquivo.md)`.
- Caminhos relativos resolvidos a partir do documento, incluindo espaços codificados como `%20` ou destinos entre `<` e `>`.
- Destinos que saem da raiz do repositório ou usam caminhos absolutos são rejeitados.

Links dentro de exemplos cercados por marcadores de código e trechos de código inline são ignorados. URLs HTTP/HTTPS e links de e-mail ou telefone não são acessados. Fragmentos `#secao` não têm seu título de destino validado.

Este é um verificador pequeno para os formatos usados no laboratório. Não é um parser Markdown completo: links por referência, HTML, URLs locais com parênteses não escapados, código indentado e construções complexas não são cobertos integralmente. Também não executa comandos dos tutoriais, não verifica ortografia e não substitui revisão de conteúdo ou de dados sensíveis.

## Verificação no GitHub

O [workflow Documentacao](../.github/workflows/documentacao.yml) executa os testes e a análise em PRs para `main`, em pushes para `main` e na branch de implementação desta melhoria. Depois do merge, também poderá ser iniciado manualmente em **Actions**.

O job **Documentacao / verificar** usa Python 3.13, permissão de leitura do conteúdo e não faz commits ou push. As actions são fixadas por SHA, com as versões identificadas em comentários. O checkout não persiste credenciais. Não há instalação de dependências de aplicação.

Antes do merge, confirme que o job existe e terminou com sucesso na versão atual do PR. Ausência de execução, aprovação pendente, falha ou bloqueio não equivalem a sucesso. Não desative verificações para integrar. Este workflow não altera as proteções de branch nem se torna obrigatório automaticamente.

## Como corrigir uma falha

1. Abra o arquivo e a linha indicados.
2. Confira a intenção do link ou do bloco de código e faça a correção útil.
3. Execute testes, análise e `git diff --check` novamente.
4. Leia o diff completo, incluindo arquivos novos, antes de publicar na mesma branch.
5. Aguarde o resultado atualizado no PR.

Mantenha mudanças relacionadas no mesmo PR. A finalidade da automação é detectar regressões na documentação, independentemente de Achievements.

## Referências

- [Workflow syntax](https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax)
- [Action checkout](https://github.com/actions/checkout)
- [Action setup-python](https://github.com/actions/setup-python)

[Voltar ao README](../README.md)
