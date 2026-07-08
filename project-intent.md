# Project Intent — Skill de Auditoria e Refatoração Arquitetural

## Propósito

Construir uma **Custom Skill** (`refactor-arch`) para Claude Code que atue como um especialista em arquitetura de software, capaz de **analisar, auditar e refatorar** projetos legados para o padrão **MVC (Model-View-Controller)** — de forma **agnóstica de tecnologia**, funcionando em diferentes linguagens e frameworks.

## Problema a resolver

Herdamos 3 projetos legados com problemas de arquitetura, segurança e qualidade de código. Revisar e corrigir tudo manualmente levaria dias. A skill automatiza esse trabalho de forma repetível e padronizada.

## Resultado esperado

Uma skill que, ao ser invocada (`claude "/refactor-arch"`), executa 3 fases sequenciais:

1. **Análise** — detecta linguagem, framework, banco de dados e mapeia a arquitetura atual.
2. **Auditoria** — cruza o código contra um catálogo de anti-patterns, gera um relatório estruturado por severidade (com arquivo e linha exatos) e **pausa pedindo confirmação humana**.
3. **Refatoração** — reestrutura o projeto para MVC, elimina os problemas e valida que a aplicação continua funcionando (boot + endpoints).

## Escopo

### Projetos-alvo

| Projeto | Stack | Domínio |
| --- | --- | --- |
| `code-smells-project` | Python / Flask | API de E-commerce |
| `ecommerce-api-legacy` | Node.js / Express | LMS API com checkout |
| `task-manager-api` | Python / Flask | API de Task Manager (parcialmente organizado) |

A skill deve funcionar nos **3 projetos** para provar que é verdadeiramente agnóstica de tecnologia.

### Componentes da skill (`.claude/skills/refactor-arch/`)

- `SKILL.md` — o prompt orquestrador das 3 fases.
- **Análise de projeto** — heurísticas de detecção de stack e mapeamento de arquitetura.
- **Catálogo de anti-patterns** — mínimo **8 anti-patterns** com sinais de detecção e severidade distribuída (CRITICAL/HIGH/MEDIUM/LOW), incluindo detecção de **APIs deprecated**.
- **Template de relatório** — formato padronizado da auditoria (Fase 2).
- **Guidelines de arquitetura** — regras do padrão MVC alvo.
- **Playbook de refatoração** — mínimo **8 padrões de transformação** com exemplos de código antes/depois.

## Escala de severidade

| Severidade | Definição |
| --- | --- |
| **CRITICAL** | Falhas graves de arquitetura/segurança: credenciais hardcoded, SQL Injection, God Class misturando DB + lógica + roteamento. |
| **HIGH** | Fortes violações de MVC/SOLID: lógica de negócio dentro de Controllers, acoplamento sem DI, estado global mutável. |
| **MEDIUM** | Padronização/duplicação/performance: queries N+1, middlewares mal usados, validações ausentes. |
| **LOW** | Legibilidade: nomes ruins, magic numbers. |

## Critérios de aceite (mínimos em 3/3 projetos)

- [ ] Fase 1 detecta a stack corretamente
- [ ] Fase 2 encontra ≥ 5 findings
- [ ] Fase 2 inclui ao menos 1 CRITICAL ou HIGH
- [ ] Fase 2 pausa e pede confirmação antes de modificar arquivos
- [ ] Fase 3 aplica estrutura MVC e a aplicação funciona após a refatoração

## Entregáveis

- Skill completa em `.claude/skills/refactor-arch/` dentro dos 3 projetos.
- Código refatorado dos 3 projetos, commitado.
- 3 relatórios de auditoria em `reports/` (`audit-project-1/2/3.md`).
- `README.md` com as seções: Análise Manual, Construção da Skill, Resultados e Como Executar.

## Restrições

- Ferramenta: **Claude Code** (Custom Skills). Arquivos de referência em **Markdown**.
- A skill deve ser **copiável e desacoplada** — não pode depender de um projeto específico.
- A confirmação humana na Fase 2 é **obrigatória** antes de qualquer modificação.

## Princípios de design

- **Sinais de detecção acionáveis** — ex.: "query SQL dentro de loop `for`", não "código ruim".
- **Conhecimento no arquivo de referência, instrução no `SKILL.md`** — o `SKILL.md` diz *o que fazer*; os arquivos de referência fornecem o *domínio*.
- **Iteração esperada** — normal precisar de 2-4 ciclos de ajuste até atingir os critérios nos 3 projetos.
