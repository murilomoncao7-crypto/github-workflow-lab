# Seu primeiro pull request

Um pull request (PR) propõe integrar alterações de uma branch em outra. Este guia usa somente este laboratório e uma melhoria real na documentação.

## 1. Prepare uma cópia isolada

Confira primeiro os requisitos de Git, Python e terminal no [fluxo de contribuição](../CONTRIBUTING.md). Publicar a branch exige acesso de escrita a este laboratório. Autentique-se pelo método habitual do GitHub; nunca coloque tokens nos comandos ou nos arquivos.

No terminal, entre em uma pasta destinada aos seus exercícios. Clone o endereço exibido no botão **Code** deste repositório para uma pasta nova. Por exemplo, no repositório original deste laboratório:

```sh
git clone https://github.com/murilomoncao7-crypto/github-workflow-lab.git meu-workflow-lab
cd meu-workflow-lab
git status
git remote -v
git branch --show-current
```

Se a pasta já existir, escolha outro nome. Confira se o remoto é o laboratório correto. O clone público permite leitura; o push exige permissão. Se você não tem escrita neste laboratório, pratique em um repositório próprio novo, usando o endereço dele.

Antes de continuar, confirme que a branch é `main` e que não há alterações pendentes.

## 2. Crie uma branch

```sh
git switch main
git pull --ff-only origin main
git switch -c docs/melhora-guia
```

A branch separa sua proposta da versão principal. Se esse nome já existir, escolha outro; não sobrescreva uma branch existente.

## 3. Faça uma melhoria útil e confira o diff

No editor, acrescente a este guia uma explicação que tenha ajudado você durante o exercício. Evite alterações sem propósito.

```sh
git status
git diff -- docs/primeiro-pull-request.md
git diff --check
```

Leia todas as linhas adicionadas e removidas. Confira ortografia, comandos e links. Não inclua credenciais, dados pessoais ou conteúdo de outros projetos. O diff vazio pode indicar que o arquivo ainda não foi salvo. Arquivos novos não aparecem no diff comum: confira seu conteúdo no editor e depois no diff preparado.

## 4. Prepare e registre o commit

Antes de criar o commit, siga a seção **Prepare a identidade antes do commit** do [fluxo de contribuição](../CONTRIBUTING.md), configurando e conferindo a identidade efetiva de autor e committer com seu noreply confirmado. Faça isso mesmo quando o Git já estiver configurado e não solicitar identidade: um commit bem-sucedido não prova que o endereço está correto.

Execute os [testes e o verificador de documentação](verificacao-documentacao.md) e corrija qualquer falha antes de preparar os arquivos. Esses comandos complementam a revisão manual do conteúdo e do diff.

```sh
git add docs/primeiro-pull-request.md
git diff --cached --check
git diff --cached -- docs/primeiro-pull-request.md
git commit -m "docs: esclarece etapa do primeiro pull request"
git status
```

O `git add` prepara apenas o arquivo indicado; o commit registra essa versão. Use uma mensagem que descreva a melhoria concreta. A configuração de identidade deve ter sido feita somente neste clone, sem alterar configurações globais.

## 5. Publique a branch e abra o PR

Antes do push, execute a conferência de **todos os commits novos** descrita em **Confira todos os commits novos antes do push**, no [fluxo de contribuição](../CONTRIBUTING.md). Ela verifica autor e committer sem imprimir um endereço inesperado. Se houver divergência, pare antes de publicar; não use reescrita de histórico remoto como correção automática.

```sh
git push -u origin docs/melhora-guia
```

No GitHub, entre em **Pull requests → New pull request**. Confira **base: main** e **compare: docs/melhora-guia**.

Dê um título objetivo e explique:

- qual dúvida a alteração resolve;
- o que foi modificado;
- como você verificou o resultado.

Abra um único PR para a melhoria. Não é necessário criar uma issue para este exercício.

## 6. Confira o diff no GitHub

Em **Files changed**, leia o diff completo e confira se somente os arquivos esperados foram alterados. Use a visualização renderizada ou abra o Markdown da branch para conferir títulos, listas, blocos de código e links relativos.

Volte à conversa do PR e confira conflitos, verificações e requisitos de revisão. Confirme que **Documentacao / verificar** terminou com sucesso na versão atual, seguindo o [guia de verificação](verificacao-documentacao.md); um check ausente ou pendente não equivale a sucesso. Se encontrar um problema, corrija na mesma branch, repita a validação, faça outro commit quando necessário e confira os metadados de todos os commits novos antes de publicar: o PR será atualizado. Revise novamente a versão final.

## 7. Faça o merge e confirme

Antes de integrar, confirme que o método de merge preserva seu noreply em autor e committer, conforme o [guia de privacidade](powershell-e-privacidade.md). A configuração local não controla o site ou um conector. Se não puder confirmar os metadados, pare antes do merge e prepare um método verificável que respeite as regras existentes.

Quando o conteúdo estiver correto, os requisitos forem atendidos e a identidade do merge estiver confirmada, escolha **Merge pull request → Confirm merge**, se esse método estiver disponível e atender a essas condições. Não ignore verificações nem altere proteções para conseguir integrar.

Confirme que o PR exibe **Merged**. Apenas fechar um PR sem merge não integra suas alterações.

Para atualizar sua cópia local:

```sh
git switch main
git pull --ff-only origin main
git log -3 --oneline
git status
```

Confira se a melhoria aparece na `main`. Se o Git bloquear uma troca de branch ou atualização por alterações locais, pare e revise o estado; não descarte trabalho para continuar.

## Checklist de conclusão

- [ ] Branch criada a partir da principal atualizada.
- [ ] Identidade efetiva configurada antes do commit e autor e committer de todos os commits novos conferidos antes do push.
- [ ] Melhoria útil, com mensagem de commit clara.
- [ ] Diff preparado revisado antes do commit.
- [ ] Testes e verificador passaram localmente; workflow da versão atual do PR aprovado.
- [ ] Base e branch de origem do PR conferidas.
- [ ] Diff final, Markdown e links conferidos no GitHub.
- [ ] Requisitos de merge respeitados.
- [ ] Método de merge conferido para preservar o noreply nos dois campos.
- [ ] Estado **Merged** e conteúdo na branch principal confirmados.

## Aprendizado e Achievements

A qualidade da melhoria tem prioridade sobre qualquer intervalo de tempo. Não crie erros, issues fictícias ou PRs repetitivos para obter selos. Este tutorial continua útil independentemente de um Achievement aparecer.

## Referências oficiais

- [GitHub flow](https://docs.github.com/en/get-started/using-github/github-flow)
- [Criar um pull request](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/proposing-changes-to-your-work-with-pull-requests/creating-a-pull-request)
- [Fazer merge de um pull request](https://docs.github.com/en/pull-requests/how-tos/merge-and-close-pull-requests/merging-a-pull-request)

[Voltar ao README](../README.md)
