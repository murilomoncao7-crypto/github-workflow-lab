# Guardar alterações ao alternar de tarefa

Stash permite guardar temporariamente o estado do arquivo de trabalho e da preparação para uma interrupção curta. Antes de usá-lo, confira `git status`, `git diff` e `git diff --cached`; leia arquivos novos no editor, pois eles não aparecem nesses diffs. Para entender índice e arquivo de trabalho, consulte o [guia de desfazer alterações](desfazer-com-seguranca.md).

## Stash ou commit em uma branch?

Use stash para uma pausa breve, quando você pretende retomar logo e consegue identificar o conteúdo guardado. Prefira um commit em uma branch de trabalho para registrar uma etapa que precisa de histórico durável, revisão ou compartilhamento; confira o conteúdo e a identidade antes de publicar, seguindo o [fluxo de contribuição](../CONTRIBUTING.md). Nenhuma alternativa deve incluir credenciais ou dados pessoais por acidente.

Stash fica no repositório local. O push habitual de uma branch não envia suas entradas de stash, e elas não substituem backup. Perder o clone ou remover uma entrada pode tornar o trabalho inacessível. Não deixe a única cópia de trabalho importante indefinidamente numa lista de stashes.

## Operações e cuidados

| Operação | Efeito |
| --- | --- |
| `git stash push -m "pausa: revisar guia"` | Guarda alterações de arquivos rastreados, incluindo o estado do índice, e retira essas alterações do trabalho atual |
| `git stash push -u -m "pausa: revisar guia"` | Inclui também arquivos não rastreados que não estejam ignorados; eles saem da pasta de trabalho até a recuperação |
| `git stash list` | Lista entradas locais, com referência e mensagem |
| `git stash show --include-untracked -p 'stash@{0}'` | Mostra o patch, incluindo arquivos não rastreados guardados |
| `git stash apply 'stash@{0}'` | Tenta reaplicar, mantendo a entrada na lista |
| `git stash apply --index 'stash@{0}'` | Tenta restaurar também a preparação anterior |
| `git stash pop 'stash@{0}'` | Tenta reaplicar e remove a entrada somente se a aplicação for bem-sucedida |

Sem `--index`, não conte com a recuperação da separação original entre preparado e não preparado; a opção tenta restaurá-la, mas pode falhar, especialmente diante de conflitos. Se `pop` causar conflito, a entrada permanece para recuperação. Para uma conferência cuidadosa, o exercício usa `apply --index` e só depois remove a entrada específica.

Arquivos ignorados não entram no procedimento com `-u`. Eles podem permanecer na pasta mesmo quando o status comum fica limpo; veja [as diferenças entre ignorado e não rastreado](gitignore-pratico.md). Não amplie a coleta indiscriminadamente para incluir arquivos ignorados que possam conter dados sensíveis.

No PowerShell, use aspas em referências como `'stash@{0}'`. Os números podem mudar quando novas entradas são criadas ou removidas; confira a mensagem e o SHA, não apenas a posição. Stashes podem ser aplicados em outra branch, mas isso não garante compatibilidade com seu conteúdo.

## Exercício isolado, sem remoto

Use Git 2.35 ou posterior, com as opções de inspeção deste guia, e Windows PowerShell 5.1 ou PowerShell 7. Execute os quatro blocos em ordem, na mesma sessão. Eles criam um repositório novo em `$env:TEMP`, somente com arquivos fictícios. Não execute stash no laboratório para seguir o exercício; nele, limite-se à leitura e à [verificação documental](verificacao-documentacao.md).

### 1. Prepare a base e as alterações

```powershell
# stash: preparar
foreach ($nome in @('GIT_DIR','GIT_WORK_TREE','GIT_INDEX_FILE','GIT_COMMON_DIR','GIT_AUTHOR_NAME','GIT_AUTHOR_EMAIL','GIT_COMMITTER_NAME','GIT_COMMITTER_EMAIL')) {
    if ([Environment]::GetEnvironmentVariable($nome, 'Process')) { throw "Variavel Git ativa: $nome. Confira o ambiente." }
}
if (-not $env:TEMP -or -not (Test-Path -LiteralPath $env:TEMP -PathType Container)) { throw 'TEMP indisponivel.' }
$exercicio = Join-Path $env:TEMP ('github-stash-' + [guid]::NewGuid().ToString('N'))
if (Test-Path -LiteralPath $exercicio) { throw 'Pasta existente; nao a reutilize.' }
New-Item -ItemType Directory -Path $exercicio -ErrorAction Stop | Out-Null
function Git-Guardar {
    param([string[]]$Argumentos)
    $resultado = & git @Argumentos
    if ($LASTEXITCODE -ne 0) { throw 'Git falhou. Pare e confira a mensagem.' }
    return $resultado
}
Git-Guardar @('-C',$exercicio,'init','--initial-branch=main')
Git-Guardar @('-C',$exercicio,'config','--local','user.name','Aprendiz Git')
Git-Guardar @('-C',$exercicio,'config','--local','user.email','aprendiz@example.invalid')
Git-Guardar @('-C',$exercicio,'config','--local','core.autocrlf','false')
$utf8 = New-Object System.Text.UTF8Encoding($false)
$anotacao = Join-Path $exercicio 'anotacao.txt'
$novo = Join-Path $exercicio 'novo.txt'
$ignorado = Join-Path $exercicio 'cache-ficticio.txt'
[IO.File]::WriteAllText($anotacao, "Linha: base`n", $utf8)
[IO.File]::WriteAllText((Join-Path $exercicio '.gitignore'), "/cache-ficticio.txt`n", $utf8)
Git-Guardar @('-C',$exercicio,'add','anotacao.txt','.gitignore')
Git-Guardar @('-C',$exercicio,'commit','-m','docs: cria base ficticia do exercicio')
Git-Guardar @('-C',$exercicio,'switch','-c','tarefa')
$headInicial = Git-Guardar @('-C',$exercicio,'rev-parse','HEAD')
[IO.File]::WriteAllText($anotacao, "Linha: preparada`n", $utf8)
Git-Guardar @('-C',$exercicio,'add','anotacao.txt')
[IO.File]::WriteAllText($anotacao, "Linha: preparada`nComplemento: local`n", $utf8)
[IO.File]::WriteAllText($novo, "Arquivo novo ficticio`n", $utf8)
[IO.File]::WriteAllText($ignorado, "Cache ficticio permanece local`n", $utf8)
Git-Guardar @('-C',$exercicio,'status','--short','--ignored')
Git-Guardar @('-C',$exercicio,'diff','--','anotacao.txt')
Git-Guardar @('-C',$exercicio,'diff','--cached','--','anotacao.txt')
```

Resultado inicial: `MM anotacao.txt` (edição preparada e outra posterior), `?? novo.txt` e `!! cache-ficticio.txt`. A identidade reservada vale somente neste repositório temporário. Se hooks, assinatura ou outra configuração legítima impedir uma operação, pare sem desativá-la.

### 2. Guarde, confira e alterne de branch

```powershell
# stash: guardar
Git-Guardar @('-C',$exercicio,'stash','push','-u','-m','pausa: rascunho ficticio da tarefa')
$stashSha = Git-Guardar @('-C',$exercicio,'rev-parse','stash@{0}')
if (@(Git-Guardar @('-C',$exercicio,'stash','list')).Count -ne 1) { throw 'Era esperado somente o stash deste exercicio.' }
if (@(Git-Guardar @('-C',$exercicio,'status','--porcelain')).Count -ne 0) { throw 'O estado comum deveria estar limpo.' }
if ([IO.File]::ReadAllText($anotacao) -cne "Linha: base`n") { throw 'Arquivo rastreado nao voltou a base.' }
if (Test-Path -LiteralPath $novo) { throw 'O arquivo novo deveria estar guardado.' }
if ([IO.File]::ReadAllText($ignorado) -cne "Cache ficticio permanece local`n") { throw 'O ignorado deveria permanecer.' }
Git-Guardar @('-C',$exercicio,'diff','--cached','--exit-code')
Git-Guardar @('-C',$exercicio,'switch','main')
Git-Guardar @('-C',$exercicio,'status','--short','--branch')
Git-Guardar @('-C',$exercicio,'switch','tarefa')
```

O índice e os arquivos rastreados voltaram à base; o arquivo novo foi guardado. O cache ignorado permanece, por isso estado limpo no status comum não significa pasta vazia. A troca de branch e o retorno não criam commits. Nenhum desses comandos configura remoto.

### 3. Inspecione e reaplique, preservando a entrada

```powershell
# stash: reaplicar
Git-Guardar @('-C',$exercicio,'stash','list')
Git-Guardar @('-C',$exercicio,'stash','show','--include-untracked','-p','stash@{0}')
if ((Git-Guardar @('-C',$exercicio,'rev-parse','stash@{0}')) -cne $stashSha) { throw 'Entrada diferente da guardada.' }
Git-Guardar @('-C',$exercicio,'stash','apply','--index','stash@{0}')
if ([IO.File]::ReadAllText($anotacao) -cne "Linha: preparada`nComplemento: local`n") { throw 'Conteudo rastreado nao restaurado.' }
if ([IO.File]::ReadAllText($novo) -cne "Arquivo novo ficticio`n") { throw 'Arquivo novo nao restaurado.' }
if ((Git-Guardar @('-C',$exercicio,'show',':anotacao.txt')) -cne 'Linha: preparada') { throw 'Preparacao anterior nao restaurada.' }
if (@(Git-Guardar @('-C',$exercicio,'ls-files','--','novo.txt')).Count -ne 0) { throw 'O arquivo novo deveria continuar nao rastreado.' }
if ((Git-Guardar @('-C',$exercicio,'rev-parse','HEAD')) -cne $headInicial) { throw 'O historico da branch nao deveria mudar.' }
if (@(Git-Guardar @('-C',$exercicio,'stash','list')).Count -ne 1) { throw 'Apply deveria preservar a entrada.' }
if ((Git-Guardar @('-C',$exercicio,'rev-parse','stash@{0}')) -cne $stashSha) { throw 'Stash preservado deveria ter o mesmo SHA.' }
Git-Guardar @('-C',$exercicio,'status','--short','--ignored')
Git-Guardar @('-C',$exercicio,'diff','--cached','--','anotacao.txt')
Git-Guardar @('-C',$exercicio,'diff','--','anotacao.txt')
```

Resultado: o arquivo tem as duas linhas, mas o índice contém somente `Linha: preparada`; `novo.txt` voltou como não rastreado. O status retorna a `MM`, `??` e `!!` nos respectivos arquivos. `apply --index` recuperou a preparação e manteve o stash para conferência. O histórico da branch continua no commit inicial.

### 4. Remova somente a entrada recuperada

Faça este bloco apenas depois de todas as conferências anteriores passarem. Ele remove a referência de recuperação, não os arquivos restaurados. Em trabalho real, preserve uma cópia adequada antes de eliminar a única referência a uma versão necessária.

```powershell
# stash: concluir
if ((Git-Guardar @('-C',$exercicio,'rev-parse','stash@{0}')) -cne $stashSha) { throw 'Nao remova uma entrada diferente.' }
Git-Guardar @('-C',$exercicio,'stash','drop','stash@{0}')
if (@(Git-Guardar @('-C',$exercicio,'stash','list')).Count -ne 0) { throw 'A unica entrada do exercicio deveria ter sido removida.' }
if ([IO.File]::ReadAllText($anotacao) -cne "Linha: preparada`nComplemento: local`n") { throw 'Conteudo restaurado mudou.' }
if ([IO.File]::ReadAllText($novo) -cne "Arquivo novo ficticio`n") { throw 'Arquivo novo mudou.' }
if ((Git-Guardar @('-C',$exercicio,'show',':anotacao.txt')) -cne 'Linha: preparada') { throw 'Indice mudou.' }
if ([IO.File]::ReadAllText($ignorado) -cne "Cache ficticio permanece local`n") { throw 'Ignorado mudou.' }
if (@(Git-Guardar @('-C',$exercicio,'remote','-v')).Count -ne 0) { throw 'O exercicio nao deveria ter remoto.' }
Git-Guardar @('-C',$exercicio,'status','--short','--ignored')
Write-Output "Exercicio concluido e preservado em: $exercicio"
```

Não há remoção automática de pastas. Se não precisar mais do exercício, confira manualmente o caminho e o conteúdo e remova somente a pasta `github-stash-...` identificada; não remova TEMP inteira nem o laboratório.

## Se a reaplicação não for limpa

Uma base alterada pode causar conflitos, inclusive ao tentar restaurar o índice. Pare, confira `git status` e os arquivos envolvidos; mantenha a entrada e não repita apply ou pop sobre o estado parcialmente aplicado. O [guia de conflitos](conflitos-de-merge.md) explica como ler marcadores e revisar uma solução, mas a reaplicação de stash não é um merge de branches pendente: não transplante automaticamente a etapa de concluir merge ou `merge --abort` para esse caso.

O exercício acima reaplica na mesma base e não provoca conflitos. Não remova o stash até confirmar a recuperação e, se necessário, resolver e validar os arquivos. Um conflito não justifica descarte indiscriminado nem tentativa de publicação forçada.

## Referência

- [Manual oficial de git stash](https://git-scm.com/docs/git-stash), consultado em 29/10/2026.

[Voltar ao fluxo de contribuição](../CONTRIBUTING.md)
