# Entender .gitignore sem confundir arquivo local e histórico

O `.gitignore` ajuda a evitar a inclusão acidental de arquivos locais e gerados. Ele não é um mecanismo de sigilo nem apaga versões já commitadas. Este exercício complementa o [guia de desfazer alterações](desfazer-com-seguranca.md): aqui o objetivo é decidir o que rastrear, preservando a cópia local.

## Três estados diferentes

| Estado | Como reconhecer | Efeito de .gitignore |
| --- | --- | --- |
| Não rastreado | Ainda não está no índice; aparece como `??` no status curto | Pode passar a ser ignorado por uma regra |
| Ignorado | Não rastreado e coberto por uma regra; normalmente não aparece no status | Pode ser mostrado com `git status --short --ignored` como `!!` |
| Já rastreado | Aparece em `git ls-files`; suas modificações são acompanhadas | Acrescentar uma regra não interrompe o rastreamento |

O `.gitignore` normalmente deve ser versionado para compartilhar regras úteis àquele projeto. Regras de outros projetos ou modelos genéricos não devem substituir regras existentes sem revisão. Este guia não acrescenta um `.gitignore` ao laboratório: não foi identificada uma necessidade concreta além do exercício.

## Padrões usados no exercício

| Padrão | Significado neste .gitignore da raiz |
| --- | --- |
| `# comentario` | Linha de comentário; linhas vazias também são ignoradas |
| `*.log` | Nomes terminados em `.log`, em qualquer nível abaixo desta pasta |
| `!manter.log` | Exceção à regra anterior para esse nome |
| `/cache-exemplo/` | Diretório na raiz; a barra final restringe a diretórios |
| `/preferencias-local.txt` | Arquivo com esse nome na raiz |

Uma regra com barra inicial é relativa à pasta do `.gitignore` que a contém. Na mesma origem e nível de precedência, a última regra aplicável decide. Regras também podem vir de arquivos em outras pastas e exclusões pessoais; `check-ignore -v` ajuda a descobrir sua origem. Uma exceção de arquivo não reabre sozinha um diretório pai ignorado: para incluir um filho, o Git precisa poder percorrer o pai. O exemplo `manter.log` fica fora do diretório ignorado para evitar essa armadilha.

## 1. Prepare somente o repositório temporário

Use Git 2.28 ou mais recente e Windows PowerShell 5.1 ou PowerShell 7, na mesma sessão. Não copie os prefixos `PS C:\...>` do terminal. Os comandos abaixo criam uma pasta com GUID em `$env:TEMP`, separada do laboratório, sem remoto. Todos os dados são fictícios; nenhuma credencial é necessária.

No laboratório, limite-se à leitura e à [verificação da documentação](verificacao-documentacao.md). **Não execute `git rm --cached` em seus arquivos para seguir este exercício.**

```powershell
# ignorar: preparar
$pastaAnterior = (Get-Location).Path
foreach ($nome in @('GIT_DIR','GIT_WORK_TREE','GIT_INDEX_FILE','GIT_COMMON_DIR','GIT_AUTHOR_NAME','GIT_AUTHOR_EMAIL','GIT_COMMITTER_NAME','GIT_COMMITTER_EMAIL')) {
    if ([Environment]::GetEnvironmentVariable($nome, 'Process')) { throw "Variavel Git ativa: $nome. Confira o ambiente." }
}
if (-not $env:TEMP -or -not (Test-Path -LiteralPath $env:TEMP -PathType Container)) { throw 'Pasta TEMP indisponivel.' }
$pastaExercicio = Join-Path $env:TEMP ('github-gitignore-' + [guid]::NewGuid().ToString('N'))
if (Test-Path -LiteralPath $pastaExercicio) { throw 'Pasta ja existe; nao a reutilize.' }
New-Item -ItemType Directory -Path $pastaExercicio -ErrorAction Stop | Out-Null
Set-Location -LiteralPath $pastaExercicio -ErrorAction Stop
function Git-Ignorar {
    param([string[]]$Argumentos)
    & git @Argumentos
    if ($LASTEXITCODE -ne 0) { throw 'Comando Git falhou. Pare e confira a mensagem.' }
}
Git-Ignorar @('init','--initial-branch=main')
Git-Ignorar @('config','--local','user.name','Aprendiz Git')
Git-Ignorar @('config','--local','user.email','aprendiz@example.invalid')
Git-Ignorar @('config','--local','core.autocrlf','false')
$utf8 = New-Object System.Text.UTF8Encoding($false)
$preferencias = Join-Path $pastaExercicio 'preferencias-local.txt'
[IO.File]::WriteAllText($preferencias, "Tema ficticio: claro`n", $utf8)
Git-Ignorar @('add','preferencias-local.txt')
Git-Ignorar @('commit','-m','docs: registra preferencias ficticias antes da regra')
$commitInicial = Git-Ignorar @('rev-parse','HEAD')
Git-Ignorar @('status','--short')
Git-Ignorar @('ls-files','--','preferencias-local.txt')
```

Estado inicial: um commit, status limpo e `preferencias-local.txt` rastreado. A identidade reservada `aprendiz@example.invalid` foi configurada apenas nesta pasta. Se uma configuração legítima de hooks ou assinatura bloquear um comando, pare sem desativá-la.

## 2. Crie arquivos locais e regras explícitas

```powershell
# ignorar: regras
[IO.File]::WriteAllText((Join-Path $pastaExercicio 'rascunho.txt'), "Anotacao ficticia para versionar`n", $utf8)
[IO.File]::WriteAllText((Join-Path $pastaExercicio 'aplicacao.log'), "Registro ficticio descartavel`n", $utf8)
[IO.File]::WriteAllText((Join-Path $pastaExercicio 'manter.log'), "Exemplo de log que sera versionado`n", $utf8)
New-Item -ItemType Directory -Path (Join-Path $pastaExercicio 'cache-exemplo') -ErrorAction Stop | Out-Null
[IO.File]::WriteAllText((Join-Path $pastaExercicio 'cache-exemplo/item.txt'), "Cache ficticio`n", $utf8)
$regras = "# Regras somente deste exercicio`n*.log`n!manter.log`n/cache-exemplo/`n/preferencias-local.txt`n"
[IO.File]::WriteAllText((Join-Path $pastaExercicio '.gitignore'), $regras, $utf8)
Git-Ignorar @('status','--short','--ignored')
Git-Ignorar @('check-ignore','-v','--','aplicacao.log','cache-exemplo/item.txt')
git check-ignore -v -- manter.log
if ($LASTEXITCODE -notin @(0,1)) { throw 'Falha ao consultar a excecao.' }
```

Resultado: `aplicacao.log` e `cache-exemplo/` aparecem como ignorados; `rascunho.txt`, `manter.log` e `.gitignore` aparecem como não rastreados. Os arquivos continuam existindo no disco.

Na saída de `check-ignore -v`, leia **arquivo de origem, número da linha, padrão e caminho consultado**. Para `manter.log`, a regra exibida começa com `!`: isso é uma exceção, não uma indicação de que o arquivo será ignorado. No modo verbose, uma correspondência negativa também pode aparecer; não conclua o estado apenas pela presença de uma linha na saída. O retorno `1` pode simplesmente significar ausência de correspondência; erros de consulta não devem ser tratados como sucesso.

## 3. Confira o arquivo previamente rastreado

```powershell
# ignorar: rastreado
Git-Ignorar @('add','.gitignore','rascunho.txt','manter.log')
Git-Ignorar @('diff','--cached','--stat')
Git-Ignorar @('commit','-m','docs: registra regras e exemplos permitidos')
[IO.File]::WriteAllText($preferencias, "Tema ficticio: escuro`n", $utf8)
Git-Ignorar @('status','--short')
Git-Ignorar @('diff','--','preferencias-local.txt')
Git-Ignorar @('ls-files','--','preferencias-local.txt')
git check-ignore -v -- preferencias-local.txt
if ($LASTEXITCODE -ne 1) { throw 'Era esperado que check-ignore omitisse o arquivo ja rastreado.' }
Git-Ignorar @('check-ignore','--no-index','-v','--','preferencias-local.txt')
```

Resultado: ` M preferencias-local.txt` aparece no status e a diferença continua sendo acompanhada. Adicionar a regra não retirou o arquivo do índice. Por padrão, `check-ignore` omite arquivos rastreados; `--no-index` consulta a regra desconsiderando esse estado para diagnóstico, sem mudar o rastreamento. O arquivo excluído por regra continua acessível normalmente pelo sistema de arquivos.

## 4. Deixe de rastrear, preservando a cópia local

O único alvo deste comando é o arquivo fictício no repositório temporário. O índice ainda contém sua versão commitada; por isso a operação abaixo não precisa de força.

```powershell
# ignorar: retirar
Git-Ignorar @('rm','--cached','--','preferencias-local.txt')
if (-not (Test-Path -LiteralPath $preferencias -PathType Leaf)) { throw 'A copia local deveria continuar existindo.' }
Get-Content -LiteralPath $preferencias -Encoding UTF8
Git-Ignorar @('status','--short','--ignored')
Git-Ignorar @('diff','--cached','--','preferencias-local.txt')
$noIndice = @(Git-Ignorar @('ls-files','--','preferencias-local.txt'))
if ($noIndice.Count -ne 0) { throw 'O arquivo ainda esta no indice.' }
Git-Ignorar @('check-ignore','-v','--','preferencias-local.txt')
Git-Ignorar @('commit','-m','docs: deixa preferencias apenas na copia local')
Git-Ignorar @('status','--short')
```

Antes do commit, o status com `--ignored` pode mostrar tanto `D  preferencias-local.txt` (remoção preparada) quanto `!! preferencias-local.txt` (cópia local agora ignorada). Depois do commit, o status comum fica limpo. O conteúdo local `Tema ficticio: escuro` permanece, mas não faz parte do novo snapshot.

`--cached` limita a remoção ao índice. Não confunda com `git rm` sem essa opção, que também removeria a cópia de trabalho. Em um projeto compartilhado, o commit registra uma remoção para outros clones; revise esse efeito com os envolvidos antes de publicar. Não use remoções amplas nem força para resolver uma divergência entre índice e arquivo.

## 5. Prove que o conteúdo antigo continua no histórico

```powershell
# ignorar: historico
Git-Ignorar @('show',('{0}:preferencias-local.txt' -f $commitInicial))
Git-Ignorar @('log','--oneline','--','preferencias-local.txt')
Git-Ignorar @('remote','-v')
if ([IO.File]::ReadAllText($preferencias) -cne "Tema ficticio: escuro`n") { throw 'Conteudo local inesperado.' }
Write-Output "Exercicio preservado em: $pastaExercicio"
Set-Location -LiteralPath $pastaAnterior -ErrorAction Stop
```

O `show` ainda exibe `Tema ficticio: claro`, gravado no primeiro commit. Ignorar e deixar de rastrear não apagam o passado. O repositório do exercício não tem remoto e não deve ser publicado. Confira manualmente sua pasta antes de decidir removê-la no Explorador; não há limpeza automática, e TEMP inteira ou clones do laboratório nunca são alvos dessa limpeza.

## Se dados sensíveis já foram publicados

Uma regra de ignore, uma remoção do índice ou um novo commit de remoção não desfazem uma exposição anterior. Se houver segredo real, revogar ou rotacionar a credencial costuma ser a primeira medida; o tratamento do histórico e de cópias exige avaliação e coordenação específicas. Não faça reescrita ou force push como continuação automática deste exercício. Consulte o [procedimento oficial do GitHub](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/removing-sensitive-data-from-a-repository) e não reproduza o segredo em issues, PRs ou logs compartilhados.

## Referências

Manuais oficiais consultados em 29/10/2026:

- [.gitignore](https://git-scm.com/docs/gitignore)
- [git check-ignore](https://git-scm.com/docs/git-check-ignore)
- [git rm](https://git-scm.com/docs/git-rm)

[Voltar ao README](../README.md)
