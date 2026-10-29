# Contribuir com o laboratório

Este é o ponto de entrada para propor uma melhoria útil e coesa. Os tutoriais ensinam cada operação; este roteiro reúne a preparação, a revisão e a confirmação da publicação. Recomendações deste documento não significam que existam proteções de branch configuradas: consulte as regras atuais no GitHub e respeite os requisitos exibidos no PR.

## Ambiente necessário

- Git com `switch` e `restore` (introduzidos no Git 2.23). Os exercícios temporários dos guias usam `init --initial-branch`, que requer Git 2.28 ou posterior.
- Python 3.11 ou posterior para os testes e o verificador, somente com a biblioteca padrão. O workflow usa Python 3.13; não há dependências para instalar com pip.
- Editor que preserve UTF-8 e terminal com Git e Python disponíveis. Os exemplos de identidade abaixo são para Windows PowerShell 5.1 ou PowerShell 7, colados na mesma sessão; não exigem executar um arquivo `.ps1`.
- Acesso de leitura para clonar. Publicar neste laboratório exige autenticação e permissão de escrita; tokens não devem aparecer em arquivos ou comandos compartilhados.

Confira os programas antes de começar:

```sh
git --version
python --version
```

Se `python` for apenas um atalho da Microsoft Store, pare e selecione um interpretador instalado. Se houver Python Launcher, pode usar `py -3` no lugar de `python`, conferindo a versão selecionada. Nenhum caminho particular de computador ou script de automação local é requisito para contribuir.

## Comece pela main atualizada

Para obter uma cópia nova, siga a preparação do [primeiro PR](docs/primeiro-pull-request.md). Na raiz do clone correto, confira:

```sh
git remote -v
git status --short
git branch --show-current
git switch main
git pull --ff-only origin main
git switch -c docs/melhoria-coesa
```

Execute um comando por vez e pare se houver erro. O remoto deste laboratório deve apontar para `murilomoncao7-crypto/github-workflow-lab`. Antes da troca de branch, o status deve estar limpo; preserve qualquer trabalho pendente antes de continuar. No PowerShell, confira `$LASTEXITCODE` imediatamente depois de cada programa nativo: retorno zero indica sucesso. Se o nome da branch já existir, escolha outro; não o sobrescreva.

Leia o README e os guias antes de editar. Reúna mudanças que resolvem o mesmo problema em um único PR, em vez de separar uma tarefa coesa para gerar atividade. Os exercícios de [conflitos](docs/conflitos-de-merge.md), [desfazer alterações](docs/desfazer-com-seguranca.md) e [.gitignore](docs/gitignore-pratico.md) pertencem a repositórios temporários sem remoto; não reproduza seus comandos de descarte ou remoção de rastreamento nos arquivos do laboratório.

Para entender fetch, upstream e uma recusa de avanço direto, pratique a [sincronização segura de branches](docs/sincronizacao-segura.md) com um remoto e dois clones exclusivamente locais.

Se precisar alternar de tarefa com alterações pendentes, consulte [como guardar e recuperar trabalho com stash](docs/stash-seguro.md); pratique somente no repositório temporário indicado.

## Prepare a identidade antes do commit

Consulte seu próprio noreply em [Settings / Emails](https://github.com/settings/emails). Configure somente este clone, sem copiar a identidade de outro participante:

```powershell
$nomeGit = Read-Host 'Nome de exibicao para este clone'
$noreply = Read-Host 'Noreply confirmado no GitHub'
if ([string]::IsNullOrWhiteSpace($nomeGit) -or $noreply -notmatch '^[^\s<>]+@users\.noreply\.github\.com$') {
    throw 'Confira nome e noreply antes de continuar.'
}
git config --local user.name "$nomeGit"
if ($LASTEXITCODE -ne 0) { throw 'Falha na identidade local.' }
git config --local user.email "$noreply"
if ($LASTEXITCODE -ne 0) { throw 'Falha no email local.' }
foreach ($campo in @('GIT_AUTHOR_IDENT','GIT_COMMITTER_IDENT')) {
    $identidade = git var $campo
    if ($LASTEXITCODE -ne 0 -or $identidade -notmatch ('<' + [regex]::Escape($noreply) + '> ')) {
        throw 'Identidade efetiva divergente; valor omitido. Nao crie o commit.'
    }
}
```

A conferência de formato não prova a titularidade do endereço. `git var` verifica a identidade efetiva, inclusive substituições por variáveis de ambiente; o valor é capturado, sem imprimir um endereço inesperado. Veja os detalhes em [PowerShell e privacidade](docs/powershell-e-privacidade.md). Não desative hooks, assinatura exigida ou políticas de execução para continuar.

## Valide e revise o que entrará no commit

Na raiz do clone, execute exatamente os comandos do [workflow Documentacao](.github/workflows/documentacao.yml):

```sh
python -B -m unittest discover -s tests -v
python -B scripts/check_docs.py
git diff --check
git status --short
git diff
```

Todos devem terminar com retorno zero. Leia também arquivos novos no editor: eles ainda não aparecem no diff comum. O verificador confere links locais e blocos de código, mas não executa exemplos nem acessa URLs externas. Consulte seu [escopo e limitações](docs/verificacao-documentacao.md); execute exemplos novos em uma área apropriada e inspecione o resultado. Testes que só procuram frases na documentação não substituem essa revisão.

Prepare apenas os arquivos da sua alteração. Por exemplo, se a melhoria afetar este roteiro e o README:

```sh
git add -- CONTRIBUTING.md README.md
git diff --cached --name-status
git diff --cached --check
git diff --cached
git commit -m "docs: orienta o fluxo de contribuição do laboratório"
git status --short
```

Adapte os caminhos e a mensagem à melhoria real. Antes do commit, leia o diff preparado inteiro, incluindo arquivos novos, e confirme a ausência de dados pessoais, credenciais e arquivos alheios ao escopo. O commit registra o conteúdo preparado, não edições posteriores. Use mensagens que expliquem a mudança concreta.

## Confira todos os commits novos antes do push

Ainda na mesma sessão PowerShell, com `$noreply` confirmado acima:

```powershell
$commitsNovos = @(git rev-list origin/main..HEAD)
if ($LASTEXITCODE -ne 0 -or $commitsNovos.Count -eq 0) {
    throw 'Nao foi possivel identificar commits novos para revisar.'
}
foreach ($sha in $commitsNovos) {
    $enderecos = @(git show -s --format='%ae%n%ce' $sha)
    if ($LASTEXITCODE -ne 0 -or $enderecos.Count -ne 2) { throw 'Falha ao ler metadados.' }
    if (@($enderecos | Where-Object { $_ -cne $noreply }).Count -gt 0) {
        throw 'Autor ou committer divergente; valores omitidos. Nao publique.'
    }
}
'Autor e committer dos commits novos conferidos.'
```

`origin/main` representa a última referência obtida do remoto; não é uma consulta em tempo real. Se houver demora ou mudança na base, atualize a leitura e revise novamente antes de publicar. Se a identidade divergir, pare antes do envio e trate o caso; este roteiro não autoriza reescrever histórico publicado.

## Publique e descreva um único PR

Depois das verificações, para a branch criada neste roteiro:

```sh
git push -u origin docs/melhoria-coesa
git ls-remote origin refs/heads/docs/melhoria-coesa
git rev-parse HEAD
```

Compare o SHA remoto com o local. Abra o PR para `main` pelo GitHub, conforme o [tutorial inicial](docs/primeiro-pull-request.md), com título objetivo e descrição contendo:

- **Problema:** qual lacuna ou falha real foi encontrada.
- **Solução:** o que mudou e por que esse escopo resolve o problema.
- **Validação:** comandos executados, resultados e limitações de conferência.

Em **Files changed**, revise o diff completo da versão publicada e os links na renderização Markdown. Na conversa do PR e em **Checks**, abra a execução de **Documentacao / verificar** e confirme sucesso na versão atual. O workflow também roda em pushes para `main` e `ci/verificacao-documentacao`; não espere uma execução de push em toda branch de documentação. Checks ausentes, pendentes ou com falha não equivalem a aprovação. Corrija na mesma branch e aguarde a nova execução.

Se uma execução falhar, siga o [guia de diagnóstico de CI](docs/diagnostico-ci.md) para localizar a causa nos logs e reproduzi-la em uma fixture isolada.

## Integre e confirme o resultado

Confira conflitos, regras atuais e eventuais revisões exigidas. Não desative proteções nem trate recomendações deste guia como regras já instaladas. Antes de integrar, confirme que o método escolhido preserva o noreply em **autor e committer**, inclusive no commit de merge. Configuração local não controla site ou conector. Se essa garantia não estiver disponível, pare antes de integrar e prepare um método verificável, conforme o [guia de privacidade](docs/powershell-e-privacidade.md).

Um merge local permite inspecionar os objetos antes do envio, mas só pode ser publicado quando o fluxo permitido e os checks forem atendidos. Não use essa alternativa para contornar exigências do GitHub.

Após a integração, consulte novamente o PR: deve aparecer **Merged**, com SHA e horário do merge. Fechado sem merge é outro estado. Confira o SHA na `main` remota e os dois campos de identidade do commit correspondente. Para atualizar a cópia local limpa, use a sequência final do [primeiro PR](docs/primeiro-pull-request.md). A data de autoria do commit não é o horário em que o PR foi integrado.

## Conexão indisponível ou limite de API

Se uma gravação retornar erro ou a consulta posterior falhar, o resultado pode ser incerto. Guarde o SHA local e a URL do PR; **não repita imediatamente push, criação de PR ou merge**. Consulte primeiro o estado remoto por leitura: `git ls-remote origin refs/heads/main` e a branch da proposta, além da página do PR. Se não conseguir confirmar, pare e informe a limitação.

Para limite da API, respeite `Retry-After`, quando presente, e `X-RateLimit-Reset` quando a cota estiver esgotada; não faça consultas em loop. Uma resposta de limite não informa se o push anterior falhou. Após a espera indicada, consulte o PR existente e compare os SHAs antes de decidir qualquer ação. `Merged: False` em uma leitura logo após o envio também exige nova consulta posterior, não uma nova gravação automática. Não contorne limites alterando credenciais, TLS, conta ou proteções.

## Referências e próximos estudos

- [Identidades efetivas no Git](https://git-scm.com/docs/git-var).
- [Limites da API REST do GitHub](https://docs.github.com/en/rest/using-the-rest-api/rate-limits-for-the-rest-api).
- [README e índice dos tutoriais](README.md).

Este fluxo serve para aprender e melhorar o laboratório. Contribuições não garantem Achievements nem prazo de processamento.
