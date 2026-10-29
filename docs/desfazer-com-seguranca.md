# Desfazer alterações com segurança

Antes de escolher um comando, descubra onde a alteração está: no arquivo de trabalho, na área de preparação ou em um commit. Este guia complementa o [primeiro PR](primeiro-pull-request.md) e o [exercício de conflitos](conflitos-de-merge.md); aqui não há merge em conflito para abandonar.

## Escolha pelo estado, não pelo nome do comando

| Intenção | Comando deste guia | Efeito no arquivo | Efeito no histórico |
| --- | --- | --- | --- |
| Retirar um arquivo do próximo commit | `git restore --staged -- anotacao.txt` | Preserva o conteúdo local | Não move a branch |
| Descartar uma edição local de arquivo rastreado | `git restore -- anotacao.txt` | Substitui pelo conteúdo do índice; pode perder trabalho não commitado | Não move a branch |
| Desfazer um commit já compartilhado | `git revert SHA` | Aplica a mudança inversa | Acrescenta um commit; mantém os anteriores |
| Refazer o último commit local, mantendo sua preparação | `git reset --soft HEAD~1` | Preserva o conteúdo e o índice | Move a branch local para o pai |
| Refazer o último commit local, sem manter sua preparação | `git reset --mixed HEAD~1` | Preserva o conteúdo, atualiza o índice para o pai | Move a branch local para o pai |

Neste guia, os resets são usados **somente em repositórios temporários sem remoto, com commits não publicados**. Não os aplique ao histórico compartilhado do laboratório. Nenhum exemplo usa reset com descarte forçado, force push ou limpeza automática.

## Ambiente e separação das pastas

Use Git 2.28 ou mais recente e Windows PowerShell 5.1 ou PowerShell 7. Os blocos abaixo são executados na mesma sessão, fora do clone do laboratório. Cada cenário cria uma pasta nova em `$env:TEMP`, sem remoto. A identidade fictícia é configurada apenas nela.

No laboratório, execute somente os testes e o [verificador de documentação](verificacao-documentacao.md) para revisar este guia. **Não execute os comandos restore ou reset deste exercício no laboratório.** Se hooks, assinatura ou outra configuração legítima impedirem um comando, pare e trate a causa sem desativar a proteção.

## 1. Prepare as funções do exercício

Este bloco define funções, mas ainda não altera arquivos versionados. A criação de cada cenário recusa variáveis de ambiente que poderiam redirecionar o Git ou substituir a identidade.

```powershell
# desfazer: preparar
$pastaAnterior = (Get-Location).Path
function Git-Desfazer {
    param([string[]]$Argumentos)
    & git @Argumentos
    if ($LASTEXITCODE -ne 0) { throw 'Comando Git falhou. Pare e confira a mensagem.' }
}
function Novo-ExercicioDesfazer {
    param([string]$Cenario)
    foreach ($nome in @('GIT_DIR','GIT_WORK_TREE','GIT_INDEX_FILE','GIT_COMMON_DIR','GIT_AUTHOR_NAME','GIT_AUTHOR_EMAIL','GIT_COMMITTER_NAME','GIT_COMMITTER_EMAIL')) {
        if ([Environment]::GetEnvironmentVariable($nome, 'Process')) {
            throw "Variavel Git ativa: $nome. Confira o ambiente antes de continuar."
        }
    }
    if (-not $env:TEMP -or -not (Test-Path -LiteralPath $env:TEMP -PathType Container)) {
        throw 'Pasta TEMP indisponivel.'
    }
    $pasta = Join-Path $env:TEMP ('github-desfazer-' + $Cenario + '-' + [guid]::NewGuid().ToString('N'))
    if (Test-Path -LiteralPath $pasta) { throw 'Pasta ja existe; nao a reutilize.' }
    New-Item -ItemType Directory -Path $pasta -ErrorAction Stop | Out-Null
    Git-Desfazer @('-C',$pasta,'init','--initial-branch=main') | Out-Host
    Git-Desfazer @('-C',$pasta,'config','--local','user.name','Aprendiz Git') | Out-Host
    Git-Desfazer @('-C',$pasta,'config','--local','user.email','aprendiz@example.invalid') | Out-Host
    Git-Desfazer @('-C',$pasta,'config','--local','core.autocrlf','false') | Out-Host
    $utf8Local = New-Object System.Text.UTF8Encoding($false)
    [IO.File]::WriteAllText((Join-Path $pasta 'anotacao.txt'), "Versao: base`n", $utf8Local)
    Git-Desfazer @('-C',$pasta,'add','anotacao.txt') | Out-Host
    Git-Desfazer @('-C',$pasta,'commit','-m','docs: cria base do exercicio') | Out-Host
    return $pasta
}
$utf8 = New-Object System.Text.UTF8Encoding($false)
```

O endereço reservado `aprendiz@example.invalid` não é sua identidade GitHub. Não publique os repositórios do exercício. As funções usam o Git normal, conferem seu código de saída e não alteram configurações globais.

## 2. Inspecione, retire da preparação e preserve o conteúdo

Estado inicial: um commit com `Versao: base` e árvore limpa. A edição será preparada com `git add`. No status curto, a primeira coluna representa o índice e a segunda o arquivo de trabalho: `M ` significa preparado; ` M` significa modificado sem preparação.

```powershell
# desfazer: staged
$pastaRestore = Novo-ExercicioDesfazer 'restore'
Set-Location -LiteralPath $pastaRestore -ErrorAction Stop
$arquivo = Join-Path $pastaRestore 'anotacao.txt'
$headInicial = Git-Desfazer @('rev-parse','HEAD')
[IO.File]::WriteAllText($arquivo, "Versao: rascunho`n", $utf8)
Git-Desfazer @('status','--short')
Git-Desfazer @('diff','--','anotacao.txt')
Git-Desfazer @('add','anotacao.txt')
Git-Desfazer @('status','--short')
Git-Desfazer @('diff','--cached','--','anotacao.txt')
Git-Desfazer @('restore','--staged','--','anotacao.txt')
Git-Desfazer @('status','--short')
Git-Desfazer @('diff','--cached','--','anotacao.txt')
Get-Content -LiteralPath $arquivo -Encoding UTF8
```

Resultado esperado: o status volta a ` M anotacao.txt`, o diff preparado fica vazio e o arquivo ainda contém `Versao: rascunho`. `HEAD` não muda. `restore --staged` retirou a alteração do índice, sem apagar o rascunho. `git diff` mostra o que falta preparar; `git diff --cached` mostra o que entraria no commit.

## 3. Descarte somente o rascunho de exemplo

**Há perda de conteúdo neste passo.** `git restore -- anotacao.txt` substitui o arquivo de trabalho pelo índice. Neste cenário o índice contém a base, pois a seção anterior retirou a edição da preparação. O rascunho nunca foi commitado e o Git não oferece garantia de recuperação. Em trabalho real, preserve uma cópia se houver dúvida; não execute o descarte por tentativa.

```powershell
# desfazer: descartar
Git-Desfazer @('status','--short')
Git-Desfazer @('diff','--','anotacao.txt')
Git-Desfazer @('diff','--cached','--','anotacao.txt')
# Descarte deliberado apenas do arquivo ficticio neste repositorio temporario.
Git-Desfazer @('restore','--','anotacao.txt')
Get-Content -LiteralPath $arquivo -Encoding UTF8
Git-Desfazer @('status','--short')
if ([IO.File]::ReadAllText($arquivo) -cne "Versao: base`n") { throw 'Conteudo inesperado.' }
if ((Git-Desfazer @('rev-parse','HEAD')) -cne $headInicial) { throw 'HEAD mudou inesperadamente.' }
Set-Location -LiteralPath $pastaAnterior -ErrorAction Stop
```

Resultado: arquivo e índice iguais à base, status limpo e o mesmo commit. O comando trata o arquivo rastreado especificado; não remove arquivos não rastreados e não é uma limpeza geral do projeto. Se a edição ainda estivesse preparada, restore sem `--staged` recuperaria a versão preparada, não necessariamente a de `HEAD`.

## 4. Reverta um commit preservando o histórico

Este cenário é outro repositório temporário. Ele demonstra localmente a estratégia apropriada para um commit já compartilhado; nenhum push é feito para simular compartilhamento. `revert` registra a mudança inversa em um novo commit, sem remover o commit original do histórico da branch.

```powershell
# desfazer: reverter
$pastaRevert = Novo-ExercicioDesfazer 'revert'
Set-Location -LiteralPath $pastaRevert -ErrorAction Stop
$arquivo = Join-Path $pastaRevert 'anotacao.txt'
$baseRevert = Git-Desfazer @('rev-parse','HEAD')
[IO.File]::WriteAllText($arquivo, "Versao: publicada no exemplo`n", $utf8)
Git-Desfazer @('add','anotacao.txt')
Git-Desfazer @('commit','-m','docs: registra alteracao que sera revertida')
$commitOriginal = Git-Desfazer @('rev-parse','HEAD')
Git-Desfazer @('status','--short')
Git-Desfazer @('show','--stat','--oneline',$commitOriginal)
Git-Desfazer @('diff',$baseRevert,$commitOriginal,'--','anotacao.txt')
Git-Desfazer @('revert','--no-edit',$commitOriginal)
Get-Content -LiteralPath $arquivo -Encoding UTF8
Git-Desfazer @('status','--short')
Git-Desfazer @('log','--oneline','-3')
if ((Git-Desfazer @('rev-parse','HEAD^')) -cne $commitOriginal) { throw 'O commit original deveria permanecer como pai.' }
if ([IO.File]::ReadAllText($arquivo) -cne "Versao: base`n") { throw 'A reversao nao restaurou o conteudo esperado.' }
Set-Location -LiteralPath $pastaAnterior -ErrorAction Stop
```

Resultado: três commits na branch, na ordem base → alteração original → reversão; conteúdo de volta à base, índice correspondente e estado limpo. Em um projeto compartilhado, revise e publique a reversão pelo fluxo normal de PR. Mudanças posteriores podem causar conflitos ao reverter; este exemplo simples não cobre reversão de merges nem usa opções de escolha de pai.

## 5. Compare soft e mixed em commits locais não publicados

Cada modo recebe um repositório temporário novo. Os dois começam com a base e um segundo commit, sem alterações pendentes. Somente nesses repositórios sem remoto a branch será movida para o primeiro commit. Os commits anteriores continuam sendo objetos Git, mas o último deixa de fazer parte do histórico atual da branch; isso não equivale a acrescentar uma reversão.

```powershell
# desfazer: resets
foreach ($modo in @('soft','mixed')) {
    $pastaReset = Novo-ExercicioDesfazer $modo
    Set-Location -LiteralPath $pastaReset -ErrorAction Stop
    $arquivo = Join-Path $pastaReset 'anotacao.txt'
    $baseReset = Git-Desfazer @('rev-parse','HEAD')
    [IO.File]::WriteAllText($arquivo, "Versao: segundo commit local`n", $utf8)
    Git-Desfazer @('add','anotacao.txt')
    Git-Desfazer @('commit','-m','docs: cria segundo commit apenas local')
    Git-Desfazer @('status','--short')
    Git-Desfazer @('diff')
    Git-Desfazer @('diff','--cached')
    Git-Desfazer @('log','--oneline','-2')
    Git-Desfazer @('reset',('--' + $modo),'HEAD~1')
    Git-Desfazer @('status','--short')
    Git-Desfazer @('diff','--','anotacao.txt')
    Git-Desfazer @('diff','--cached','--','anotacao.txt')
    Get-Content -LiteralPath $arquivo -Encoding UTF8
    Git-Desfazer @('log','--oneline')
    if ((Git-Desfazer @('rev-parse','HEAD')) -cne $baseReset) { throw 'HEAD deveria voltar a base.' }
    if ([IO.File]::ReadAllText($arquivo) -cne "Versao: segundo commit local`n") { throw 'O arquivo deveria ser preservado.' }
    Write-Output "Cenario $modo preservado em: $pastaReset"
    Set-Location -LiteralPath $pastaAnterior -ErrorAction Stop
}
```

| Após o comando | HEAD / histórico atual | Índice | Arquivo de trabalho | Status esperado |
| --- | --- | --- | --- | --- |
| `--soft` | Primeiro commit | Segundo conteúdo, ainda preparado | Segundo conteúdo preservado | `M  anotacao.txt` |
| `--mixed` | Primeiro commit | Conteúdo da base | Segundo conteúdo preservado, sem preparação | ` M anotacao.txt` |

No soft, o diff comum fica vazio e o diff preparado mostra a alteração. No mixed ocorre o inverso. Para refazer o commit, revise e faça commit diretamente no soft; no mixed, prepare primeiro os arquivos escolhidos. Não execute esses resets em uma branch publicada para depois tentar forçar o remoto a aceitá-la.

## Encerramento e conferência

As pastas ficam preservadas para inspeção. Você pode consultar cada uma com `git -C CAMINHO status`, `git -C CAMINHO diff`, `git -C CAMINHO diff --cached` e `git -C CAMINHO log --oneline`, substituindo CAMINHO pelo caminho exato entre aspas. `git -C CAMINHO remote -v` deve ficar vazio.

Para limpeza, confira manualmente o conteúdo no Explorador e remova somente a pasta temporária `github-desfazer-...` identificada, se não precisar mais dela. Não remova TEMP inteira ou qualquer clone. Este guia não executa limpeza automática.

Ao terminar, volte ao clone do laboratório apenas para os [testes e a análise documental](verificacao-documentacao.md). Os resets e o descarte de rascunho acima pertencem exclusivamente aos exercícios temporários; a publicação deste guia preserva o histórico do laboratório.

## Referências

Manuais oficiais consultados em 29/10/2026:

- [git restore](https://git-scm.com/docs/git-restore)
- [git revert](https://git-scm.com/docs/git-revert)
- [git reset](https://git-scm.com/docs/git-reset)

[Voltar ao README](../README.md)
