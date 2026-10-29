# Windows PowerShell e privacidade dos commits

Este complemento registra dificuldades reais deste laboratório. O [tutorial inicial](primeiro-pull-request.md) já explica branches, commits, PRs e merge; aqui ficam os cuidados específicos com execução, conectividade, respostas da API e identidade Git.

## O que aconteceu e o que aprendemos

| Situação observada | Diagnóstico e decisão |
| --- | --- |
| O Git do ambiente de automação retornou `Could not resolve host: github.com`, enquanto o PowerShell do usuário conseguiu acessar o remoto. | O acesso varia por ambiente. Preparar e testar o caminho de publicação no terminal que realmente tem acesso antes de abrir o PR. |
| Um conector publicou commits com o endereço pessoal padrão da conta. | A configuração do clone não controla um serviço externo. Exigir controle explícito de autor e committer, conferir os objetos antes do push e verificar novamente no remoto. |
| A leitura de uma lista vazia de rulesets foi interpretada como um item no Windows PowerShell. | Normalizar a enumeração da resposta antes de contar. Uma falha de leitura da API deve interromper o fluxo, nunca ser tratada como lista vazia. |
| Houve diferença de interpretação de datas e de acentos entre ambientes PowerShell. | Não depender de conversões implícitas entre versões. Usar codificação explícita e conferir o resultado. |
| O primeiro PR foi integrado depois do intervalo pretendido. | A integração útil continua válida. Preparar o fluxo antes da abertura e priorizar revisão; não criar tentativas repetitivas por um selo. |

## 1. Identifique o terminal e execute arquivos com caminhos claros

Windows PowerShell 5.1 (`powershell.exe`) e PowerShell 7 (`pwsh.exe`) são ambientes diferentes. Veja a versão e as políticas vigentes sem alterá-las:

```powershell
$PSVersionTable.PSVersion
Get-ExecutionPolicy -List
Get-Command git
```

Para um script local revisado chamado `preflight.ps1`, execute o caminho real com o operador `&`:

```powershell
if (-not (Test-Path -LiteralPath '.\preflight.ps1' -PathType Leaf)) {
    throw 'Arquivo não encontrado. Confira a pasta atual.'
}
& '.\preflight.ps1'
```

Um caminho entre aspas sozinho é apenas texto. Não copie os prefixos `PS C:\...>` ou `>>` exibidos no terminal. Se aparecer `>>` por um comando incompleto, cancele com Ctrl+C e confira aspas, parênteses e chaves antes de tentar novamente. Prefira comandos curtos a continuações com acento grave, que falham se houver espaços depois do caractere de continuação.

Se uma política bloquear o script, registre a mensagem e pare. Não use `Bypass`, não altere políticas de usuário/máquina e não desbloqueie arquivos indiscriminadamente para cumprir um prazo. Use um caminho permitido pela política vigente; políticas corporativas podem exigir assinatura ou intervenção do responsável.

## 2. Separe teste de rede de gravação remota

Este comando apenas consulta a branch principal do laboratório:

```powershell
git ls-remote https://github.com/murilomoncao7-crypto/github-workflow-lab.git refs/heads/main
if ($LASTEXITCODE -ne 0) {
    throw 'A consulta Git falhou. Não abra o PR ainda.'
}
```

`$ErrorActionPreference = 'Stop'` ajuda com cmdlets, mas no Windows PowerShell 5.1 não substitui a conferência de `$LASTEXITCODE` após cada programa nativo, como Git. Não execute o próximo passo depois de um erro.

Uma API acessível não prova que o transporte Git funciona, nem que há permissão de push. Antes de abrir o PR, publique a branch de documentação, confirme seu SHA remoto e faça o ensaio do comando de merge com `git push --dry-run`. O ensaio não garante que o envio posterior passará: autenticação pode expirar e o remoto pode mudar.

Não contorne uma falha de DNS usando IP fixo, desativando TLS, mudando credenciais ou alterando configurações globais. Se for necessário usar o terminal do usuário, aguarde ele estar pronto antes de iniciar a etapa com prazo.

## 3. Leia respostas da API sem inventar resultados

No Windows PowerShell, uma coleção retornada por `Invoke-RestMethod` pode ser encaminhada como um único objeto. A forma de contar deve ser testada com zero, um e vários itens. Um padrão para uma resposta de lista já obtida é:

```powershell
# $resposta contém somente o resultado de uma consulta GET bem-sucedida.
$itens = @($resposta | Write-Output)
$quantidade = $itens.Count
```

Esse padrão é para endpoints de lista, como rulesets. Uma resposta de checks é um objeto com a propriedade `check_runs`; enumere essa propriedade, não o objeto inteiro. Para listas paginadas, confira se há outras páginas; se o procedimento não souber completá-las, interrompa sem concluir que não há regras.

Em scripts, use `-ErrorAction Stop` e um tempo limite nas consultas HTTP. Erros HTTP, autenticação, limite de requisições ou uma resposta inesperada devem interromper a operação. Não substitua esses erros por `@()`.

Ausência de status não é o mesmo que status pendente: o endpoint de status combinado pode indicar `pending` com `total_count` igual a zero. Confira também os check runs e as regras aplicáveis. Se houver verificações pendentes, falhas, proteção ou exigência de revisão, respeite-as.

## 4. Configure e confira a identidade no repositório certo

Obtenha seu no-reply em [Settings → Emails](https://github.com/settings/emails). Não o deduza de um exemplo. Para configurar apenas o clone atual, leia o endereço no terminal e use escopo local:

```powershell
$noreply = Read-Host 'Cole seu endereço no-reply confirmado no GitHub'
if ($noreply -notmatch '^[^\s<>]+@users\.noreply\.github\.com$') {
    throw 'Formato inesperado. Confira o endereço na página do GitHub.'
}
git config --local user.email "$noreply"
if ($LASTEXITCODE -ne 0) { throw 'Falha ao configurar este clone.' }
```

A validação de formato não confirma que o endereço pertence à conta; a confirmação vem da página do GitHub. Não coloque o endereço pessoal em exemplos, logs compartilhados ou descrições de PR.

Um commit tem autor e committer. Antes de publicar, confira os dois sem imprimir um endereço inesperado:

```powershell
$enderecos = @(git show -s --format='%ae%n%ce' HEAD)
if ($LASTEXITCODE -ne 0 -or $enderecos.Count -ne 2) {
    throw 'Não foi possível conferir a identidade do commit.'
}
if (@($enderecos | Where-Object { $_ -cne $noreply }).Count -gt 0) {
    throw 'Autor ou committer divergente. Não publique.'
}
'Autor e committer conferidos com o no-reply esperado.'
```

Confira todos os commits novos, não apenas o último. Variáveis de ambiente de identidade e integrações externas podem produzir metadados diferentes do esperado. Não presuma que o método de merge do site ou de um conector usa a mesma configuração do clone.

## 5. Codificação, datas e preparação do merge

Windows PowerShell 5.1 pode interpretar scripts UTF-8 sem BOM como uma codificação legada. Para scripts com acentos que precisem funcionar nele e no PowerShell 7, salve explicitamente em UTF-8 com BOM. Documentos Markdown podem continuar em UTF-8 sem BOM. Não use redirecionamento sem verificar a codificação ao escrever arquivos usados para calcular hashes Git.

Prefira timestamps ISO 8601 com fuso explícito ou segundos Unix. Versões diferentes de `ConvertFrom-Json` podem tratar datas de forma diferente; não use uma conversão de texto dependente da cultura do Windows para decidir se dois instantes são iguais.

Um merge local permite verificar autor, committer, pais e árvore antes do envio. O push normal de um merge que inclui os commits da branch pode fazer o GitHub reconhecer o PR como integrado. Entretanto, esse reconhecimento indireto não deve ser usado para contornar regras: se houver proteção, rulesets ou requisitos não atendidos, interrompa e use o fluxo exigido pelo repositório.

Mudar a identidade para novos commits não corrige commits anteriores. Neste laboratório a correção do histórico exigiu aprovação específica. Não repita reescritas como rotina; cópias, caches ou referências antigas podem continuar existindo.

## Checklist antes de abrir um PR

- [ ] A melhoria preenche uma lacuna real e o diff inteiro foi revisado.
- [ ] Links relativos, comandos e Markdown foram conferidos.
- [ ] O terminal correto executa os scripts sob as políticas vigentes.
- [ ] O transporte Git e as leituras da API funcionam nesse terminal.
- [ ] A branch foi publicada e o SHA remoto foi confirmado.
- [ ] Todos os commits novos e o merge preparado usam o no-reply nos dois campos.
- [ ] Proteções, regras e verificações foram inspecionadas sem contorno.
- [ ] O comando de merge está pronto; se depender de outra pessoa, ela está com o terminal pronto.

Somente então abra um único PR para a melhoria. Confira novamente seu diff e requisitos, integre quando permitido e registre `created_at`, `closed_at` e `merged_at` retornados pelo GitHub. Calcule o intervalo entre abertura e fechamento; não use a data de autoria do commit para isso. A revisão tem prioridade sobre cinco minutos, e a atividade não garante Quickdraw nem prazo de processamento.

## Fontes

Consultadas em 29/10/2026:

- [Políticas de execução do PowerShell](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.core/about/about_execution_policies?view=powershell-5.1)
- [Invoke-RestMethod e enumeração de respostas](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.utility/invoke-restmethod?view=powershell-5.1)
- [Codificação de caracteres no PowerShell](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.core/about/about_character_encoding?view=powershell-5.1)
- [Identidade de e-mail nos commits](https://docs.github.com/en/account-and-profile/how-tos/email-preferences/setting-your-commit-email-address)
- [Métodos de merge e merges indiretos](https://docs.github.com/en/pull-requests/reference/pull-request-merges)

[Voltar ao README](../README.md)
