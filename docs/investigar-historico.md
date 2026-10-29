# Investigar a origem e o contexto de uma alteração

Para entender uma linha, combine histórico, patch e mensagem. O commit mais recente da branch pode ter mudado outra parte do arquivo. Este guia complementa a [comparação de branches](sincronizacao-segura.md), o [diagnóstico de CI](diagnostico-ci.md) e a [reversão sem apagar histórico](desfazer-com-seguranca.md); investigar não exige desfazer nada.

## Da visão geral à linha

| Comando | Pergunta que ajuda a responder |
| --- | --- |
| `git log --oneline --graph --decorate` | Quais commits são alcançáveis a partir de HEAD e como estão ligados? |
| `git log --oneline -- plano.txt` | Quais commits do histórico selecionado afetam esse caminho? |
| `git show SHA -- plano.txt` | Qual mensagem e patch desse commit são exibidos para o arquivo? |
| `git diff ANTES DEPOIS -- plano.txt` | Como o conteúdo do primeiro estado difere do segundo? |
| `git blame -L 2,2 HEAD -- plano.txt` | A qual commit a linha 2 da versão selecionada é atribuída? |

`--oneline` resume cada commit em SHA abreviado e título; `--graph` mostra conexões; `--decorate` exibe referências como branch e HEAD. Sem `--all`, o log não reúne automaticamente todas as branches. Um desenho linear, como o exercício abaixo, continua sendo um histórico válido.

O separador `--` distingue revisões e opções dos caminhos. Tudo depois dele é tratado como seleção de caminhos, evitando confundir um nome de arquivo com uma revisão. Nos exemplos, SHA, ANTES e DEPOIS são lugares para valores reais, não textos para copiar literalmente.

Em `git diff ANTES DEPOIS`, linhas com `-` pertencem ao primeiro estado e linhas com `+` ao segundo; linhas sem esses sinais no corpo do patch dão contexto. As linhas de cabeçalho `---` e `+++` identificam os lados. Inverter os argumentos inverte a direção da comparação. O comando não altera os arquivos e não enumera commits: comparar dois snapshots é diferente de consultar um intervalo com `log`.

## Exercício temporário: três mudanças distintas

Use Git 2.28 ou posterior e Windows PowerShell 5.1 ou PowerShell 7. Execute os três blocos na ordem, na mesma sessão. A pasta nova em `$env:TEMP` terá um repositório sem remoto e um arquivo fictício. No laboratório, limite-se à leitura e aos [testes e verificador](verificacao-documentacao.md); os comandos com `-C` abaixo apontam exclusivamente para a pasta temporária.

### 1. Crie o arquivo e obtenha os SHAs durante a execução

```powershell
# historico: preparar
foreach ($nome in @('GIT_DIR','GIT_WORK_TREE','GIT_INDEX_FILE','GIT_COMMON_DIR','GIT_AUTHOR_NAME','GIT_AUTHOR_EMAIL','GIT_COMMITTER_NAME','GIT_COMMITTER_EMAIL')) {
    if ([Environment]::GetEnvironmentVariable($nome, 'Process')) { throw "Variavel Git ativa: $nome. Confira o ambiente." }
}
if (-not $env:TEMP -or -not (Test-Path -LiteralPath $env:TEMP -PathType Container)) { throw 'TEMP indisponivel.' }
$exercicio = Join-Path $env:TEMP ('github-historico-' + [guid]::NewGuid().ToString('N'))
if (Test-Path -LiteralPath $exercicio) { throw 'Pasta existente; nao a reutilize.' }
New-Item -ItemType Directory -Path $exercicio -ErrorAction Stop | Out-Null
function Git-Historico {
    param([string[]]$Argumentos)
    $resultado = & git --no-pager @Argumentos
    if ($LASTEXITCODE -ne 0) { throw 'Git falhou. Pare e confira a mensagem.' }
    return $resultado
}
Git-Historico @('-C',$exercicio,'init','--initial-branch=main')
Git-Historico @('-C',$exercicio,'config','--local','user.name','Aprendiz Git')
Git-Historico @('-C',$exercicio,'config','--local','user.email','aprendiz@example.invalid')
Git-Historico @('-C',$exercicio,'config','--local','core.autocrlf','false')
$utf8 = New-Object System.Text.UTF8Encoding($false)
$arquivo = Join-Path $exercicio 'plano.txt'
[IO.File]::WriteAllText($arquivo, "Plano: oficina ficticia`nPrazo: 7 dias`nFormato: texto`n", $utf8)
Git-Historico @('-C',$exercicio,'add','plano.txt')
Git-Historico @('-C',$exercicio,'commit','-m','docs: registra plano ficticio inicial')
$shaBase = Git-Historico @('-C',$exercicio,'rev-parse','HEAD')
[IO.File]::WriteAllText($arquivo, "Plano: oficina ficticia`nPrazo: 14 dias`nFormato: texto`n", $utf8)
Git-Historico @('-C',$exercicio,'add','plano.txt')
Git-Historico @('-C',$exercicio,'commit','-m','docs: amplia prazo da oficina','-m','Contexto ficticio: reservar uma semana adicional para revisar os exemplos.')
$shaPrazo = Git-Historico @('-C',$exercicio,'rev-parse','HEAD')
[IO.File]::WriteAllText($arquivo, "Plano: oficina ficticia`nPrazo: 14 dias`nFormato: lista`n", $utf8)
Git-Historico @('-C',$exercicio,'add','plano.txt')
Git-Historico @('-C',$exercicio,'commit','-m','docs: apresenta o plano em lista')
$shaFormato = Git-Historico @('-C',$exercicio,'rev-parse','HEAD')
Git-Historico @('-C',$exercicio,'status','--short')
```

Há três commits: criação, alteração do prazo na linha 2 e alteração do formato na linha 3. Dois `-m` no segundo commit registram título e parágrafo de contexto. Os SHAs serão diferentes a cada execução e são obtidos com `rev-parse`, não copiados deste documento. A identidade reservada vale apenas neste repositório temporário; se hooks, assinatura ou outra configuração bloquear um comando, pare sem desativá-la.

### 2. Localize a linha e leia o commit correspondente

```powershell
# historico: investigar
Git-Historico @('-C',$exercicio,'log','--oneline','--graph','--decorate')
Git-Historico @('-C',$exercicio,'log','--oneline','--','plano.txt')
Git-Historico @('-C',$exercicio,'blame','-L','2,2','HEAD','--','plano.txt')
# O formato porcelain permite conferir o SHA completo sem analisar nomes e datas.
$origem = @(Git-Historico @('-C',$exercicio,'blame','--porcelain','-L','2,2','HEAD','--','plano.txt'))
$shaLinha = ($origem[0] -split ' ')[0]
if ($shaLinha -cne $shaPrazo) { throw 'A linha 2 deveria apontar para o commit do prazo.' }
if ($shaLinha -ceq $shaFormato) { throw 'O commit mais recente mudou somente o formato.' }
Git-Historico @('-C',$exercicio,'show',$shaLinha,'--','plano.txt')
$mensagem = @(Git-Historico @('-C',$exercicio,'show','-s','--format=%B',$shaLinha))
if ($mensagem -notcontains 'Contexto ficticio: reservar uma semana adicional para revisar os exemplos.') {
    throw 'O contexto esperado nao foi encontrado na mensagem.'
}
$patch = @(Git-Historico @('-C',$exercicio,'diff',$shaBase,$shaPrazo,'--','plano.txt'))
$patch | Write-Output
if ($patch -notcontains '-Prazo: 7 dias' -or $patch -notcontains '+Prazo: 14 dias') { throw 'Mudanca exata diferente da esperada.' }
```

Respostas verificadas: a linha 2 aponta para `$shaPrazo`, não para o último commit `$shaFormato`; o patch troca 7 por 14 dias; a mensagem registra uma semana adicional para revisão. Em `show`, o caminho limita o patch, enquanto a mensagem pertence ao commit inteiro. O exercício tem commits simples, cada um com um pai após a base; merges podem exigir escolher uma comparação apropriada com seus pais.

### 3. Compare os estados e confirme que a inspeção não os alterou

```powershell
# historico: comparar
Git-Historico @('-C',$exercicio,'diff',$shaBase,$shaFormato,'--','plano.txt')
$reverso = @(Git-Historico @('-C',$exercicio,'diff',$shaPrazo,$shaBase,'--','plano.txt'))
$reverso | Write-Output
if ($reverso -notcontains '-Prazo: 14 dias' -or $reverso -notcontains '+Prazo: 7 dias') { throw 'Direcao da comparacao inesperada.' }
$historico = @(Git-Historico @('-C',$exercicio,'log','--format=%H','--','plano.txt'))
if ($historico.Count -ne 3 -or ($historico -join ',') -cne (@($shaFormato,$shaPrazo,$shaBase) -join ',')) { throw 'Historico do arquivo inesperado.' }
if ([IO.File]::ReadAllText($arquivo) -cne "Plano: oficina ficticia`nPrazo: 14 dias`nFormato: lista`n") { throw 'Conteudo final inesperado.' }
if ((Git-Historico @('-C',$exercicio,'rev-parse','HEAD')) -cne $shaFormato) { throw 'HEAD mudou durante a inspecao.' }
if (@(Git-Historico @('-C',$exercicio,'status','--porcelain')).Count -ne 0) { throw 'A inspecao deveria preservar o estado limpo.' }
if (@(Git-Historico @('-C',$exercicio,'remote','-v')).Count -ne 0) { throw 'O exercicio nao deveria ter remoto.' }
Write-Output "Respostas confirmadas. Exercicio preservado em: $exercicio"
```

Entre a base e o terceiro commit aparecem as mudanças de prazo e formato. Entre o segundo commit e a base, a mesma mudança de prazo aparece ao contrário. Nenhum desses comandos aplica o patch. Todos os comandos Git devem retornar zero; um diff sem `--exit-code` retorna zero também quando há diferenças.

As pastas ficam preservadas. Para remover o exercício depois, confira manualmente o caminho e seu conteúdo e remova somente a pasta `github-historico-...` identificada. Não há limpeza automática; TEMP inteira e o laboratório não são alvos.

## Blame é uma pista para investigação

Blame associa linhas da versão selecionada a commits segundo o histórico e as opções usadas. Uma reformatação, cópia ou reaplicação pode mudar a atribuição sem representar a criação original da ideia. Linhas removidas não aparecem na versão atual, e renomeações e merges podem exigir inspeção adicional. Por isso, a linha atribuída não prova autoria original nem responsabilidade por um defeito.

Leia o patch e a mensagem, compare versões e considere testes e contexto de revisão. Se estiver investigando um check, consulte o [diagnóstico de CI](diagnostico-ci.md); se comparar seu clone ao remoto, confira antes a [sincronização](sincronizacao-segura.md). Caso a conclusão justifique desfazer uma alteração compartilhada, use o fluxo de revisão e a orientação sobre [revert](desfazer-com-seguranca.md), sem transformar investigação em reescrita automática do histórico.

## Referências

Manuais oficiais consultados em 29/10/2026:

- [git log](https://git-scm.com/docs/git-log)
- [git show](https://git-scm.com/docs/git-show)
- [git diff](https://git-scm.com/docs/git-diff)
- [git blame](https://git-scm.com/docs/git-blame)

[Voltar ao fluxo de contribuição](../CONTRIBUTING.md)
