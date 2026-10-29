# Seu primeiro pull request

Um pull request (PR) propõe integrar alterações de uma branch em outra. Este guia usa somente este laboratório e uma melhoria real na documentação.

## 1. Prepare uma cópia isolada

Você precisa de Git instalado e acesso de escrita a este laboratório para publicar a branch. Autentique-se pelo método habitual do GitHub; nunca coloque tokens nos comandos ou nos arquivos.

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

```sh
git add docs/primeiro-pull-request.md
git diff --cached --check
git diff --cached -- docs/primeiro-pull-request.md
git commit -m "docs: esclarece etapa do primeiro pull request"
git status
```

O `git add` prepara apenas o arquivo indicado; o commit registra essa versão. Use uma mensagem que descreva a melhoria concreta. Se Git solicitar identidade, configure-a apenas neste clone, com `git config --local`, usando seu nome de exibição e o endereço no-reply indicado nas suas configurações de e-mail do GitHub. Não altere configurações globais para este exercício.

## 5. Publique a branch e abra o PR

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

Volte à conversa do PR e confira conflitos, verificações e requisitos de revisão. Se encontrar um problema, corrija na mesma branch, faça outro commit e publique: o PR será atualizado. Revise novamente a versão final.

## 7. Faça o merge e confirme

Quando o conteúdo estiver correto e os requisitos forem atendidos, escolha **Merge pull request → Confirm merge**, se esse método estiver disponível. Não ignore verificações nem altere proteções para conseguir integrar.

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
- [ ] Melhoria útil, com mensagem de commit clara.
- [ ] Diff preparado revisado antes do commit.
- [ ] Base e branch de origem do PR conferidas.
- [ ] Diff final, Markdown e links conferidos no GitHub.
- [ ] Requisitos de merge respeitados.
- [ ] Estado **Merged** e conteúdo na branch principal confirmados.

## Aprendizado e Achievements

A qualidade da melhoria tem prioridade sobre qualquer intervalo de tempo. Não crie erros, issues fictícias ou PRs repetitivos para obter selos. Este tutorial continua útil independentemente de um Achievement aparecer.

## Referências oficiais

- [GitHub flow](https://docs.github.com/en/get-started/using-github/github-flow)
- [Criar um pull request](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/proposing-changes-to-your-work-with-pull-requests/creating-a-pull-request)
- [Fazer merge de um pull request](https://docs.github.com/en/pull-requests/how-tos/merge-and-close-pull-requests/merging-a-pull-request)

[Voltar ao README](../README.md)
