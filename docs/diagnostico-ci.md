# Diagnosticar uma falha de CI

Um check vermelho informa que a execução não terminou como esperado; a causa aparece no contexto do log. Este guia complementa a [verificação de documentação](verificacao-documentacao.md), que descreve os requisitos e os limites do verificador, e o [fluxo de contribuição](../CONTRIBUTING.md), que orienta revisão e publicação.

## Workflow, job e step neste laboratório

Veja a configuração real em [documentacao.yml](../.github/workflows/documentacao.yml):

| Nível | Configuração | Papel |
| --- | --- | --- |
| Workflow | `name: Documentacao` | Define eventos, permissões e jobs da automação |
| Job | Chave `verificar`, nome `Documentacao / verificar` | Executa em `ubuntu-latest`, com limite de cinco minutos |
| Step | `Obter este repositorio` | Faz checkout usando a action fixada por SHA |
| Step | `Preparar Python` | Seleciona Python 3.13 usando a action fixada por SHA |
| Step | `Testar o verificador` | Executa a suíte unittest |
| Step | `Conferir a documentacao` | Executa a análise dos documentos do clone |

Os steps deste job seguem a ordem acima; uma falha normalmente impede os seguintes de executar. GitHub também acrescenta etapas de preparação e conclusão do job. Não confunda um step posterior ignorado com a origem da falha.

O workflow roda em PRs para `main`, em pushes para `main` e `ci/verificacao-documentacao`, e por disparo manual. A ausência de execução após um push em outra branch não prova defeito no workflow: confira o evento e os filtros. Ter uma execução bem-sucedida não configura automaticamente uma proteção de branch.

## Encontre a execução e a primeira causa relevante

1. Abra **Checks** no PR ou **Actions**, selecione **Documentacao** e abra a execução correspondente. Confira branch, evento, SHA e tentativa; uma execução antiga não valida commits novos.
2. Abra o job **Documentacao / verificar** e o primeiro step que falhou. Expanda os logs desse step; a busca de logs considera os steps expandidos.
3. Leia desde o comando executado até o primeiro diagnóstico que explica a falha. `Process completed with exit code 1` apenas resume o resultado: procure antes dele o arquivo e linha, uma asserção ou uma exceção.
4. Se a falha ocorreu antes do Python, leia os steps de checkout, preparação do runner e seleção do interpretador. Não atribua ao Markdown um erro que aconteceu antes de sua análise.
5. Registre a URL da execução, o step e o trecho mínimo relevante, sem copiar dados privados, credenciais ou caminhos pessoais. Se os logs não estiverem acessíveis, informe essa limitação; não invente a causa.

## Reproduza os comandos locais

Na raiz do clone, com Python 3.11 ou posterior disponível, execute um comando por vez:

```sh
python --version
python -B -m unittest discover -s tests -v
python -B scripts/check_docs.py
```

No PowerShell, capture `$LASTEXITCODE` imediatamente depois de cada programa. Pare após uma falha; não confunda o retorno do comando seguinte com o do comando que falhou. Se o interpretador não estiver instalado, siga a [preparação do ambiente](../CONTRIBUTING.md).

O CI usa Python 3.13 em Linux. Passar no Windows com outra versão suportada ajuda a investigar, mas não substitui o check remoto. Confira também maiúsculas e minúsculas dos caminhos: o Windows pode aceitar um link cuja capitalização difere do arquivo, enquanto o Linux o rejeita.

## Interprete a mensagem emitida

As mensagens abaixo vêm do [código do verificador](../scripts/check_docs.py). O diagnóstico geralmente contém `arquivo:linha: mensagem`; problemas de leitura podem não ter linha.

| Mensagem ou trecho real | O que conferir |
| --- | --- |
| `link local inexistente: ...` | Destino relativo ao documento de origem, arquivo versionado e capitalização correta |
| `bloco de codigo sem fechamento` | Linha de abertura indicada; fechar com o mesmo marcador e tamanho suficiente |
| `link sai da raiz do repositorio` | Caminho resolve para fora da raiz analisada; corrigir o destino, sem ampliar o escopo para ocultar o problema |
| `use um caminho relativo com barras /` | Link usa caminho absoluto ou barras invertidas |
| `nao foi possivel ler o arquivo como UTF-8` | Codificação do arquivo e possibilidade de leitura |
| `Nenhum arquivo Markdown encontrado` | Raiz escolhida e presença de `.md` na raiz ou em `docs/` |
| `Raiz de documentacao inexistente` | Valor de `--root`, se utilizado |

`FALHOU: ...` é o resumo; cada linha anterior aponta um diagnóstico. Retorno `1` indica problema encontrado e `0` indica análise aprovada. Erros de uso da linha de comando ou exceções do Python podem produzir outras saídas: não classifique qualquer retorno diferente de zero como link quebrado. URLs externas e fragmentos de títulos não são validados; consulte os [limites da análise](verificacao-documentacao.md).

## Exercício local: falhar, diagnosticar e corrigir

Execute os dois blocos na ordem, na mesma sessão Windows PowerShell 5.1 ou PowerShell 7, começando na raiz do clone. Requer Python instalado e `$env:TEMP` disponível. O exercício cria somente uma pasta de fixtures, sem inicializar Git nem configurar remoto; não edita os documentos do laboratório, não cria commits e não publica uma execução com falha.

### 1. Crie a fixture e confira a falha esperada

```powershell
# diagnostico: falhar
$verificador = Join-Path (Get-Location).Path 'scripts/check_docs.py'
if (-not (Test-Path -LiteralPath $verificador -PathType Leaf)) { throw 'Comece na raiz do clone.' }
if (-not $env:TEMP -or -not (Test-Path -LiteralPath $env:TEMP -PathType Container)) { throw 'TEMP indisponivel.' }
$fixture = Join-Path $env:TEMP ('github-ci-diagnostico-' + [guid]::NewGuid().ToString('N'))
if (Test-Path -LiteralPath $fixture) { throw 'Pasta existente; nao a reutilize.' }
New-Item -ItemType Directory -Path $fixture -ErrorAction Stop | Out-Null
$utf8 = New-Object System.Text.UTF8Encoding($false)
[IO.File]::WriteAllText((Join-Path $fixture 'README.md'), "# Fixture`n`n[Guia](docs/guia.md)`n", $utf8)
$saidaFalha = @(python -B "$verificador" --root "$fixture")
$codigoFalha = $LASTEXITCODE
$saidaFalha | Write-Output
if ($codigoFalha -ne 1) { throw 'Era esperado retorno 1. Confira interpretador e saida.' }
if ($saidaFalha -notcontains 'README.md:3: link local inexistente: docs/guia.md') {
    throw 'O diagnostico esperado nao apareceu.'
}
```

Resultado esperado: a mensagem identifica README, linha 3 e destino ausente; o resumo é `FALHOU: 1 problema(s) em 1 arquivo(s).` e `$codigoFalha` vale `1`. A falha é deliberada somente nesta fixture local. Não altere o workflow para aceitar esse retorno.

### 2. Crie o destino correto e confirme aprovação

```powershell
# diagnostico: corrigir
New-Item -ItemType Directory -Path (Join-Path $fixture 'docs') -ErrorAction Stop | Out-Null
[IO.File]::WriteAllText((Join-Path $fixture 'docs/guia.md'), "# Guia de exemplo`n", $utf8)
$saidaCorreta = @(python -B "$verificador" --root "$fixture")
$codigoCorreto = $LASTEXITCODE
$saidaCorreta | Write-Output
if ($codigoCorreto -ne 0) { throw 'A correcao nao passou.' }
if ($saidaCorreta -notcontains 'OK: 2 arquivos Markdown; links locais e blocos conferidos.') {
    throw 'Resumo inesperado apos a correcao.'
}
Write-Output "Fixture preservada em: $fixture"
```

Agora o mesmo link encontra seu destino: dois documentos aprovados, retorno `0`. Não houve troca da regra do verificador para mascarar a falha. A pasta permanece para inspeção; se não precisar mais dela, confira seu conteúdo e remova manualmente somente a pasta `github-ci-diagnostico-...` identificada. Não há limpeza automática.

## Separe o tipo de falha antes de agir

| Evidência | Classificação inicial | Próximo passo |
| --- | --- | --- |
| Step `Conferir a documentacao` aponta arquivo/linha | Conteúdo analisado | Corrigir caminho, bloco ou codificação; repetir a análise local |
| Step `Testar o verificador` mostra `FAIL` ou `ERROR`, nome do teste e traceback | Falha de teste | Ler expectativa e resultado no teste; investigar código, fixture e ambiente antes de mudar qualquer asserção |
| Runner indisponível, download de action falhou ou erro de rede antes da análise | Possível infraestrutura | Ler a mensagem específica, confirmar alcance do problema e aguardar recuperação quando necessário |

Uma exceção de teste também pode ter causa ambiental; a tabela orienta a investigação, não prova a causa. Os [testes existentes](../tests/test_check_docs.py) já cobrem link ausente e códigos de saída. Não é necessário acrescentar um teste que apenas procure frases neste guia.

Executar novamente com os mesmos arquivos não corrige um link quebrado ou uma asserção incorreta. Uma nova tentativa pode ajudar após uma indisponibilidade transitória comprovada; registre por que ela é apropriada e evite loops de execução. Falhas persistentes de configuração ou permissão exigem diagnóstico, não tentativas repetidas nem desativação de checks.

Depois de corrigir uma causa real, execute a suíte e o verificador, revise o diff e publique na mesma branch do PR. Aguarde a execução correspondente à nova versão antes do merge. Para consulta de API indisponível ou resultado de gravação incerto, siga o [procedimento de confirmação remota](../CONTRIBUTING.md), sem repetir push ou merge automaticamente.

## Referência

- [Logs de execuções de workflow](https://docs.github.com/en/actions/how-tos/monitor-workflows/use-workflow-run-logs), documentação oficial consultada em 29/10/2026.

[Voltar ao fluxo de contribuição](../CONTRIBUTING.md)
