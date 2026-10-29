# Resolver um conflito de merge, do início ao fim

Um conflito ocorre quando o Git não consegue combinar alterações automaticamente. Neste exercício duas branches mudam a mesma linha; você examina as duas propostas e registra uma solução que preserva a intenção das duas.

## Onde executar cada coisa

| Local | Finalidade |
| --- | --- |
| Clone do `github-workflow-lab` | Ler este guia e executar o [verificador de documentação](verificacao-documentacao.md). Não criar aqui as branches do exercício. |
| Pasta nova em `$env:TEMP`, identificada por um GUID | Executar os comandos abaixo. Será um repositório local independente, sem remoto e sem publicação. |

Use Git 2.28 ou mais recente e Windows PowerShell 5.1 ou PowerShell 7. Execute os blocos na ordem, na mesma sessão. Não copie os prefixos `PS C:\...>` ou `>>` do terminal. Nenhum bloco precisa ser salvo como `.ps1`; políticas de execução de arquivos não precisam ser alteradas.

O exercício usa apenas um arquivo de exemplo. Em um projeto real, comece com a árvore de trabalho limpa, leia o contexto do conflito e valide o comportamento resultante. Não escolha automaticamente um lado apenas para eliminar marcadores.

## 1. Crie a área temporária e a base

O código recusa variáveis de ambiente que poderiam redirecionar o Git ou substituir a identidade. Se isso acontecer, use uma sessão apropriada sem essas variáveis; não modifique credenciais ou configurações globais para continuar.

```powershell
# exercicio: preparar
$pastaAnterior = (Get-Location).Path
foreach ($nomeVariavel in @('GIT_DIR','GIT_WORK_TREE','GIT_INDEX_FILE','GIT_COMMON_DIR','GIT_AUTHOR_NAME','GIT_AUTHOR_EMAIL','GIT_COMMITTER_NAME','GIT_COMMITTER_EMAIL')) {
    if ([Environment]::GetEnvironmentVariable($nomeVariavel, 'Process')) {
        throw "Variavel Git ativa: $nomeVariavel. Pare e confira o ambiente."
    }
}
if (-not $env:TEMP -or -not (Test-Path -LiteralPath $env:TEMP -PathType Container)) {
    throw 'Pasta TEMP indisponivel.'
}
$pastaExercicio = Join-Path $env:TEMP ('github-merge-exercicio-' + [guid]::NewGuid().ToString('N'))
if (Test-Path -LiteralPath $pastaExercicio) { throw 'A pasta ja existe. Nao a reutilize.' }
New-Item -ItemType Directory -Path $pastaExercicio -ErrorAction Stop | Out-Null
Set-Location -LiteralPath $pastaExercicio -ErrorAction Stop
function Git-Exercicio {
    param([string[]]$Argumentos)
    & git @Argumentos
    if ($LASTEXITCODE -ne 0) { throw 'Comando Git falhou. Pare e confira a mensagem.' }
}
Git-Exercicio @('init','--initial-branch=main')
Git-Exercicio @('config','--local','user.name','Aprendiz Git')
Git-Exercicio @('config','--local','user.email','aprendiz@example.invalid')
Git-Exercicio @('config','--local','core.autocrlf','false')
Git-Exercicio @('config','--local','merge.conflictStyle','merge')
$utf8 = New-Object System.Text.UTF8Encoding($false)
$arquivoExercicio = Join-Path $pastaExercicio 'mensagem.txt'
[IO.File]::WriteAllText($arquivoExercicio, "Cor: original`n", $utf8)
Git-Exercicio @('add','mensagem.txt')
Git-Exercicio @('commit','-m','docs: registra mensagem inicial do exercicio')
Write-Output "Pasta exclusiva do exercicio: $pastaExercicio"
```

O domínio `example.invalid` é um exemplo, não seu endereço GitHub. Essa identidade vale somente neste repositório temporário. O estilo de conflito foi definido localmente para reproduzir os três marcadores apresentados abaixo. Se hooks, assinatura de commits ou outra configuração legítima impedirem um comando, pare e trate a causa sem desativar a proteção.

## 2. Crie duas branches que divergem na mesma linha

As duas branches partem da mesma base `main`: uma propõe azul e a outra verde.

```powershell
# exercicio: divergir
Git-Exercicio @('switch','-c','cor-azul','main')
[IO.File]::WriteAllText($arquivoExercicio, "Cor: azul`n", $utf8)
Git-Exercicio @('add','mensagem.txt')
Git-Exercicio @('commit','-m','docs: propoe a cor azul')
Git-Exercicio @('switch','-c','cor-verde','main')
[IO.File]::WriteAllText($arquivoExercicio, "Cor: verde`n", $utf8)
Git-Exercicio @('add','mensagem.txt')
Git-Exercicio @('commit','-m','docs: propoe a cor verde')
Git-Exercicio @('switch','cor-azul')
$antesDoMerge = Git-Exercicio @('rev-parse','HEAD')
Git-Exercicio @('status','--short')
```

A saída de `status --short` deve estar vazia. Você está em `cor-azul` e tentará integrar `cor-verde` nela. Isso não altera a branch `main`.

## 3. Reproduza e examine o conflito

Neste ponto o retorno `1` do merge é esperado e será conferido explicitamente. Os demais comandos Git continuam exigindo retorno zero.

```powershell
# exercicio: conflitar
git merge --no-ff --no-commit cor-verde
$codigoMerge = $LASTEXITCODE
if ($codigoMerge -ne 1) { throw 'O conflito esperado nao foi reproduzido. Pare para conferir.' }
$pendencias = @(Git-Exercicio @('ls-files','--unmerged'))
if ($pendencias.Count -eq 0) { throw 'Nao ha arquivo em conflito. Pare para conferir.' }
Git-Exercicio @('status','--short')
Get-Content -LiteralPath $arquivoExercicio -Encoding UTF8
```

O Git deve informar um conflito de conteúdo. O status resumido mostra `UU mensagem.txt`. O arquivo apresenta:

| Linha | Conteúdo do arquivo |
| --- | --- |
| 1 | `<<<<<<< HEAD` |
| 2 | `Cor: azul` |
| 3 | `=======` |
| 4 | `Cor: verde` |
| 5 | `>>>>>>> cor-verde` |

`<<<<<<< HEAD` inicia a proposta da branch atual, `cor-azul`; `=======` separa as propostas; `>>>>>>> cor-verde` encerra a proposta que está entrando. Os marcadores são instruções para a revisão, não devem ficar na versão final. Em outros estilos de conflito, a versão ancestral também pode aparecer.

Agora escolha: siga a seção 4 para resolver ou use a alternativa da seção 6 para abandonar. Não execute os dois caminhos em sequência no mesmo conflito.

## 4. Resolva, prepare o arquivo e conclua o merge

Neste exemplo a decisão é manter as duas cores em uma frase. Em um arquivo real, edite somente as regiões necessárias e valide o resultado; substituir o arquivo inteiro aqui é apropriado porque ele contém uma única linha de exemplo.

```powershell
# exercicio: resolver
[IO.File]::WriteAllText($arquivoExercicio, "Cores: azul e verde`n", $utf8)
Get-Content -LiteralPath $arquivoExercicio -Encoding UTF8
Git-Exercicio @('diff','--check')
Git-Exercicio @('add','mensagem.txt')
Git-Exercicio @('diff','--cached','--','mensagem.txt')
$pendencias = @(Git-Exercicio @('ls-files','--unmerged'))
if ($pendencias.Count -ne 0) { throw 'Ainda ha conflitos para resolver.' }
Git-Exercicio @('commit','-m','docs: combina as cores e conclui o merge')
Git-Exercicio @('status','--short')
Git-Exercicio @('log','-1','--format=%h %p %s')
Git-Exercicio @('remote','-v')
```

O `git add` marca o arquivo como resolvido; o `git commit` conclui o merge pendente. O último commit terá dois pais e o status deve ficar limpo. `git remote -v` não deve mostrar nada: não houve configuração de remoto, PR ou push neste exercício. Não use um conector para publicar essa identidade fictícia.

## 5. Confira o resultado e volte à pasta anterior

```powershell
# exercicio: finalizar
$pais = (Git-Exercicio @('show','-s','--format=%P','HEAD')) -split ' '
if ($pais.Count -ne 2) { throw 'Era esperado um commit de merge com dois pais.' }
if ([IO.File]::ReadAllText($arquivoExercicio) -cne "Cores: azul e verde`n") {
    throw 'Conteudo final diferente do esperado.'
}
Write-Output "Exercicio concluido em: $pastaExercicio"
Set-Location -LiteralPath $pastaAnterior -ErrorAction Stop
```

## 6. Alternativa: abandone uma integração ainda em conflito

Use este bloco **no lugar da seção 4**, logo após reproduzir o conflito da seção 3. Não é um comando para desfazer um merge já commitado. Como o exercício começou sem alterações locais pendentes, o abandono deve restaurar `cor-azul` e seu conteúdo anterior.

```powershell
# exercicio: abortar
Git-Exercicio @('merge','--abort')
if ((Git-Exercicio @('rev-parse','HEAD')) -cne $antesDoMerge) {
    throw 'HEAD diferente do ponto anterior ao merge.'
}
if ([IO.File]::ReadAllText($arquivoExercicio) -cne "Cor: azul`n") {
    throw 'Conteudo anterior nao foi restaurado.'
}
Git-Exercicio @('status','--short')
Write-Output "Merge abandonado; branches preservadas em: $pastaExercicio"
Set-Location -LiteralPath $pastaAnterior -ErrorAction Stop
```

O status deve estar limpo. As duas branches e seus commits permanecem disponíveis. Em projetos com mudanças não commitadas antes do merge, `--abort` pode não reconstruir tudo; por isso o exercício começa com a árvore limpa.

## Limpeza manual e verificação do laboratório

Não há comando de remoção automática. Anote o caminho exato exibido, confira seu conteúdo no Explorador de Arquivos e, se não precisar mais dele, remova manualmente **somente aquela pasta `github-merge-exercicio-...`**. Não remova a pasta TEMP inteira, o clone do laboratório ou outras pastas. O caminho de resolução e o caminho de abandono, quando testados em sessões separadas, criam pastas diferentes.

No clone do laboratório, os únicos comandos desta atividade de leitura e revisão são os descritos no [guia de verificação](verificacao-documentacao.md), como os testes e `python -B scripts/check_docs.py`. Não copie as branches `cor-azul` e `cor-verde` para o laboratório.

## Referência

- [Manual oficial de git merge](https://git-scm.com/docs/git-merge), consultado em 29/10/2026: apresentação de conflitos, resolução e limites de `--abort`.

[Voltar ao README](../README.md)
