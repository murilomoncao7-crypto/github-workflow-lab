# Sincronizar branches sem descartar trabalho

O [primeiro PR](primeiro-pull-request.md) usa `pull --ff-only` para atualizar a main. Aqui vamos entender o que é comparado, separar obtenção de integração e diagnosticar uma recusa. Para revisar alterações e publicar no laboratório, siga o [fluxo de contribuição](../CONTRIBUTING.md).

## Três referências, em dois repositórios

| Termo | Exemplo | Onde fica e o que representa |
| --- | --- | --- |
| Branch local | `main` | Referência `refs/heads/main` no clone; aponta para um commit local |
| Branch no remoto | `main` em `origin` | Referência `refs/heads/main` no outro repositório; pode mudar sem seu clone saber |
| Referência de acompanhamento remoto | `origin/main` | Referência `refs/remotes/origin/main` no clone; registra a informação obtida do remoto, atualizada por operações como fetch |

`origin` é o nome de um remoto configurado, não necessariamente o GitHub. A upstream é a referência associada à branch local para acompanhar sua relação com outra branch; no clone comum de main, costuma ser `origin/main`. Confira em vez de presumir. `origin/main` não é uma consulta ao servidor em tempo real nem a própria branch local `main`.

## Antes de atualizar, saiba onde está

Estes comandos são de inspeção, executados na raiz do clone que você pretende atualizar:

```sh
git branch --show-current
git status --short --branch
git branch -vv
git rev-parse --abbrev-ref --symbolic-full-name '@{upstream}'
git remote -v
git diff
git diff --cached
```

O status mostra alterações e a relação conhecida com a upstream; `branch -vv` mostra a associação de cada branch local. Se não houver upstream, a consulta `@{upstream}` falha: confira o remoto e a branch pretendidos antes de configurar uma associação. Se estiver em HEAD destacado, `branch --show-current` pode ficar vazio. Nenhuma dessas situações deve ser resolvida descartando arquivos por tentativa.

Antes da integração, preserve alterações pendentes e confira se a branch e o remoto são os corretos. Os exemplos abaixo começam com índice e árvore de trabalho limpos. Os contadores ahead/behind só refletem a informação disponível localmente.

## Fetch obtém; pull obtém e tenta integrar

`git fetch origin` busca objetos e atualiza as referências de acompanhamento conforme a configuração do remoto. No clone comum usado aqui, atualiza `origin/main`, sem trocar o commit da branch atual nem editar seus arquivos de trabalho. Depois do fetch, inspecione antes de integrar:

```sh
git fetch origin
git log --oneline --graph --decorate --all
git log --oneline HEAD..origin/main
git log --oneline origin/main..HEAD
git rev-list --left-right --count HEAD...origin/main
git diff HEAD origin/main
```

Use `origin/main` somente depois de conferir que é a referência que deseja comparar. Os dois logs mostram, respectivamente, commits presentes apenas no lado remoto conhecido e apenas no lado local. Na contagem com três pontos, a primeira coluna é exclusiva de HEAD; a segunda é exclusiva de `origin/main`. O diff com dois argumentos compara os conteúdos dos dois commits; ele não substitui a leitura da topologia do histórico.

`git pull` faz fetch e tenta integrar na branch atual o histórico selecionado, segundo opções e configuração. Para aceitar somente avanço direto, use `git pull --ff-only origin main` **estando na main correta**. Informar `main` nesse comando não troca sua branch atual. Há avanço direto quando o commit atual é ancestral do destino; a referência local avança sem criar commit de merge. Se já estiver atualizada, pode não haver nada para integrar. Havendo commits exclusivos dos dois lados, o modo `--ff-only` recusa a integração.

## Exercício: um bare e dois clones, todos locais

Requer Git 2.28 ou posterior e Windows PowerShell 5.1 ou PowerShell 7. Execute os blocos em ordem, na mesma sessão. Todos os caminhos do exercício ficam numa pasta nova em `$env:TEMP`; nenhum comando conecta ao GitHub. O bare armazena o histórico compartilhado local e não tem árvore de trabalho. Os clones A e B simulam duas cópias de trabalho.

**No laboratório:** leia este guia e execute somente os [testes e o verificador](verificacao-documentacao.md). **No exercício:** os comandos com `-C`, clone e init abaixo apontam para pastas temporárias. Não substitua esses caminhos pelo clone do laboratório.

### 1. Prepare o remoto local, A e a base

```powershell
# sincronizacao: preparar
foreach ($nome in @('GIT_DIR','GIT_WORK_TREE','GIT_INDEX_FILE','GIT_COMMON_DIR','GIT_AUTHOR_NAME','GIT_AUTHOR_EMAIL','GIT_COMMITTER_NAME','GIT_COMMITTER_EMAIL')) {
    if ([Environment]::GetEnvironmentVariable($nome, 'Process')) { throw "Variavel Git ativa: $nome. Confira o ambiente." }
}
if (-not $env:TEMP -or -not (Test-Path -LiteralPath $env:TEMP -PathType Container)) { throw 'TEMP indisponivel.' }
$exercicio = Join-Path $env:TEMP ('github-sincronizacao-' + [guid]::NewGuid().ToString('N'))
if (Test-Path -LiteralPath $exercicio) { throw 'Pasta existente; nao a reutilize.' }
New-Item -ItemType Directory -Path $exercicio -ErrorAction Stop | Out-Null
$remoto = Join-Path $exercicio 'remoto.git'
$cloneA = Join-Path $exercicio 'clone-a'
$cloneB = Join-Path $exercicio 'clone-b'
function Git-Sync {
    param([string[]]$Argumentos)
    $resultado = & git @Argumentos
    if ($LASTEXITCODE -ne 0) { throw 'Git falhou. Pare e confira a mensagem.' }
    return $resultado
}
function Identidade-Sync {
    param([string]$Clone)
    Git-Sync @('-C',$Clone,'config','--local','user.name','Aprendiz Git')
    Git-Sync @('-C',$Clone,'config','--local','user.email','aprendiz@example.invalid')
    Git-Sync @('-C',$Clone,'config','--local','core.autocrlf','false')
}
$utf8 = New-Object System.Text.UTF8Encoding($false)
Git-Sync @('init','--bare','--initial-branch=main',$remoto)
Git-Sync @('clone','--config','core.autocrlf=false',$remoto,$cloneA)
Identidade-Sync $cloneA
[IO.File]::WriteAllText((Join-Path $cloneA 'estado.txt'), "Estado: base`n", $utf8)
Git-Sync @('-C',$cloneA,'add','estado.txt')
Git-Sync @('-C',$cloneA,'commit','-m','docs: cria base do exercicio')
Git-Sync @('-C',$cloneA,'push','-u','origin','main')
Git-Sync @('clone','--config','core.autocrlf=false',$remoto,$cloneB)
Identidade-Sync $cloneB
Git-Sync @('-C',$cloneB,'branch','-vv')
Git-Sync @('-C',$cloneB,'remote','-v')
```

O aviso ao clonar um repositório inicialmente vazio em A é esperado. B é clonado depois do primeiro push e começa na main com a base e upstream `origin/main`. Seu remoto aponta para `remoto.git` dentro da pasta temporária. A identidade reservada `aprendiz@example.invalid` vale somente nesses clones; não os publique. Se hooks, assinatura, política de transporte local ou outra configuração bloquear um comando, pare sem desativar controles.

`clone --config core.autocrlf=false` grava a opção somente no clone novo, antes do primeiro checkout. Os arquivos fictícios deste exercício usam LF. Configurar a opção apenas depois de clonar poderia deixar o arquivo já convertido para CRLF no Windows, causando uma diferença local antes mesmo do fetch; por isso a preparação precisa ocorrer antes do checkout, sem alterar a configuração global.

### 2. A publica; B obtém sem alterar o arquivo

```powershell
# sincronizacao: obter
[IO.File]::WriteAllText((Join-Path $cloneA 'estado.txt'), "Estado: remoto 1`n", $utf8)
Git-Sync @('-C',$cloneA,'add','estado.txt')
Git-Sync @('-C',$cloneA,'commit','-m','docs: atualiza estado no clone A')
Git-Sync @('-C',$cloneA,'push','origin','main')
$headAntes = Git-Sync @('-C',$cloneB,'rev-parse','HEAD')
$conteudoAntes = [IO.File]::ReadAllText((Join-Path $cloneB 'estado.txt'))
if ($conteudoAntes -cne "Estado: base`n") { throw 'Checkout inicial diferente do esperado; pare antes do fetch.' }
if (@(Git-Sync @('-C',$cloneB,'status','--porcelain')).Count -ne 0) { throw 'B deveria estar limpo antes do fetch.' }
Git-Sync @('-C',$cloneB,'fetch','origin')
Git-Sync @('-C',$cloneB,'status','--short','--branch')
Git-Sync @('-C',$cloneB,'log','--oneline','--graph','--decorate','--all')
Git-Sync @('-C',$cloneB,'log','--oneline','HEAD..origin/main')
Git-Sync @('-C',$cloneB,'diff','HEAD','origin/main','--','estado.txt')
$contagem = (Git-Sync @('-C',$cloneB,'rev-list','--left-right','--count','HEAD...origin/main')).Trim() -split '\s+'
if (($contagem -join ',') -cne '0,1') { throw 'Era esperado zero commit local exclusivo e um remoto.' }
if ((Git-Sync @('-C',$cloneB,'rev-parse','HEAD')) -cne $headAntes) { throw 'Fetch nao deveria mover HEAD.' }
if ([IO.File]::ReadAllText((Join-Path $cloneB 'estado.txt')) -cne $conteudoAntes) { throw 'Fetch nao deveria mudar o arquivo.' }
Git-Sync @('-C',$cloneB,'diff','--exit-code')
Git-Sync @('-C',$cloneB,'diff','--cached','--exit-code')
```

Resultado: B está um commit atrás, `origin/main` conhece a alteração de A, mas HEAD, índice e arquivo de B continuam na base. Os diffs locais sem destino ficam vazios; o diff entre HEAD e `origin/main` mostra o conteúdo recebido.

### 3. Atualize B por avanço direto

```powershell
# sincronizacao: avancar
Git-Sync @('-C',$cloneB,'pull','--ff-only','origin','main')
if ((Git-Sync @('-C',$cloneB,'rev-parse','HEAD')) -cne (Git-Sync @('-C',$cloneB,'rev-parse','origin/main'))) {
    throw 'HEAD deveria coincidir com origin/main.'
}
if ([IO.File]::ReadAllText((Join-Path $cloneB 'estado.txt')) -cne "Estado: remoto 1`n") { throw 'Conteudo nao atualizado.' }
if ((Git-Sync @('-C',$cloneB,'rev-list','--count','HEAD')) -ne '2') { throw 'Deveriam existir apenas os dois commits de A.' }
Git-Sync @('-C',$cloneB,'status','--short','--branch')
Git-Sync @('-C',$cloneB,'log','--oneline','-2')
```

Resultado: retorno zero, arquivo atualizado e dois commits no histórico, sem terceiro commit de merge. O wrapper interrompe qualquer comando que retorne falha.

### 4. Crie divergência e confirme a recusa preservando o trabalho

Os clones agora criam commits diferentes a partir da mesma base. Usamos arquivos distintos para mostrar que divergência de histórico não depende de um conflito textual.

```powershell
# sincronizacao: divergir
[IO.File]::WriteAllText((Join-Path $cloneB 'local.txt'), "Trabalho local preservado`n", $utf8)
Git-Sync @('-C',$cloneB,'add','local.txt')
Git-Sync @('-C',$cloneB,'commit','-m','docs: registra trabalho exclusivo de B')
$headLocal = Git-Sync @('-C',$cloneB,'rev-parse','HEAD')
[IO.File]::WriteAllText((Join-Path $cloneA 'remoto.txt'), "Trabalho publicado por A`n", $utf8)
Git-Sync @('-C',$cloneA,'add','remoto.txt')
Git-Sync @('-C',$cloneA,'commit','-m','docs: registra trabalho exclusivo de A')
Git-Sync @('-C',$cloneA,'push','origin','main')
# Aqui a falha e esperada; capture o retorno imediatamente, fora do wrapper.
git -C "$cloneB" pull --ff-only origin main
$codigoRecusa = $LASTEXITCODE
if ($codigoRecusa -eq 0) { throw 'Era esperada uma recusa por divergencia.' }
$contagem = (Git-Sync @('-C',$cloneB,'rev-list','--left-right','--count','HEAD...origin/main')).Trim() -split '\s+'
if (($contagem -join ',') -cne '1,1') { throw 'A recusa precisa ser acompanhada de divergencia confirmada.' }
if ((Git-Sync @('-C',$cloneB,'rev-parse','HEAD')) -cne $headLocal) { throw 'Commit local nao foi preservado.' }
if ([IO.File]::ReadAllText((Join-Path $cloneB 'local.txt')) -cne "Trabalho local preservado`n") { throw 'Trabalho local nao preservado.' }
if ([IO.File]::ReadAllText((Join-Path $cloneB 'estado.txt')) -cne "Estado: remoto 1`n") { throw 'Arquivo anterior mudou.' }
if (Test-Path -LiteralPath (Join-Path $cloneB 'remoto.txt')) { throw 'A integracao deveria ter sido recusada.' }
if (@(Git-Sync @('-C',$cloneB,'status','--porcelain')).Count -ne 0) { throw 'Indice e arquivos deveriam continuar limpos.' }
Git-Sync @('-C',$cloneB,'log','--oneline','--graph','--decorate','--all')
Write-Output "Recusa confirmada com codigo $codigoRecusa. Exercicio preservado em: $exercicio"
```

O Git informa que não é possível fazer avanço direto e retorna valor diferente de zero (a redação varia por versão e idioma). B continua com seu commit e arquivo local, sem integrar o arquivo exclusivo de A. O fetch interno pode atualizar `origin/main` mesmo quando o pull recusa integrar: por isso não interprete a recusa como ausência de qualquer alteração nos metadados locais. Esta recusa ocorre antes de uma tentativa de merge com conflito; não há conflito pendente para abandonar neste cenário.

## Próximo diagnóstico diante da divergência

Confira primeiro a branch atual, a upstream, os remotos e alterações não commitadas. Após um fetch bem-sucedido, leia os commits exclusivos dos dois lados e os diffs; confirme que ambos pertencem à linha de trabalho desejada. Falha de rede ou permissão não prova divergência: verifique a mensagem e não use contagens antigas como diagnóstico atual.

No exemplo, há um commit exclusivo de cada lado. Um projeto pode optar por integrar com merge, após revisar a intenção das mudanças e respeitar suas regras; esse passo fica fora deste exercício. Se a integração escolhida gerar conflito, consulte o [guia de conflitos](conflitos-de-merge.md), incluindo os limites de `merge --abort`. Preserve commits compartilhados; não resolva a recusa com force push, reescrita ou descarte indiscriminado.

Nenhum comando deste guia faz limpeza automática. Confira o caminho e o conteúdo da pasta `github-sincronizacao-...`; se não precisar mais dela, remova manualmente somente essa pasta do exercício, incluindo seus três repositórios. Não remova TEMP inteira nem o laboratório.

## Referências

Fontes oficiais consultadas em 29/10/2026:

- [git fetch](https://git-scm.com/docs/git-fetch)
- [git pull](https://git-scm.com/docs/git-pull)
- [git clone e configuração antes do checkout](https://git-scm.com/docs/git-clone)
- [Pro Git: branches remotas](https://git-scm.com/book/en/v2/Git-Branching-Remote-Branches)

[Voltar ao fluxo de contribuição](../CONTRIBUTING.md)
