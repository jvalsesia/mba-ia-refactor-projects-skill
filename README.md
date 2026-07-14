# Criação de Skills — Refatoração Arquitetural Automatizada

Ao longo do curso você aprendeu o que são Skills e como elas permitem que um agente de IA atue como um especialista em tarefas específicas. Agora imagine o seguinte cenário: você herdou 3 projetos legados com problemas de arquitetura, segurança e qualidade de código. Revisar e corrigir tudo manualmente levaria dias.

Neste desafio, você vai criar uma Skill que automatiza esse processo — analisando, auditando e refatorando qualquer projeto para o padrão MVC, independente da tecnologia.

---

# 📋 Documentação da Entrega

> As seções abaixo (**Análise Manual**, **Construção da Skill**, **Resultados** e **Como Executar**) documentam a solução entregue, conforme exigido em _"README.md deve conter"_. O restante do documento é o enunciado original do desafio.

## A) Análise Manual

Antes de construir a skill, cada projeto foi lido manualmente para entender os problemas que a skill precisaria detectar. Abaixo estão os achados por projeto, classificados por severidade, com a justificativa de relevância. A skill posteriormente confirmou (e ampliou) esses achados — os relatórios completos estão em `reports/audit-project-{1,2,3}.md`.

### Projeto 1 — `code-smells-project` (Python/Flask, API de E-commerce)

Monolito de 4 arquivos (`app.py`, `controllers.py`, `models.py`, `database.py`), sem separação de camadas.

| # | Problema | Severidade | Local | Por que é relevante |
|---|---|---|---|---|
| 1 | **SQL Injection por interpolação de string** | CRITICAL | `models.py` (dezenas de queries) + `app.py:59-78` (`/admin/query`) | Quase toda query concatena input direto no SQL; `/admin/query` executa SQL arbitrário do cliente — permite roubo/alteração de dados e bypass de login. |
| 2 | **Credenciais hardcoded** | CRITICAL | `app.py:7`, `controllers.py:289` | `SECRET_KEY` fixa no código e ainda ecoada pelo `/health` a qualquer chamador anônimo — vazamento imediato. |
| 3 | **Rotas sensíveis sem autenticação** | CRITICAL | `/admin/reset-db`, `/admin/query`, `GET /usuarios` | Qualquer anônimo apaga o banco, roda SQL e coleta senhas em texto plano. |
| 4 | **God File / sem separação de camadas** | HIGH | `controllers.py`, `models.py`, `app.py` | Parsing, validação, regra de negócio, SQL e resposta misturados — impossível testar em isolamento. |
| 5 | **Lógica de negócio e acesso a banco nos handlers** | HIGH | `app.py:47-78`, `controllers.py:264-292` | Handlers abrem cursores e rodam SQL — web acoplada ao banco, sem reuso/teste. |
| 6 | **Query N+1** | MEDIUM | `models.py:171-233` | Uma query por item por pedido — latência cresce linearmente com o volume. |
| 7 | **Lógica duplicada (copy-paste)** | MEDIUM | `controllers.py:28-50` vs `:72-90`; `models.py:177-200` vs `:209-232` | Validação de produto e montagem de pedido+itens copiadas — correções precisam ser feitas em vários lugares, gerando drift. |
| 8 | **Magic numbers** | LOW | `models.py:257-262` (tiers de desconto) | Literais de desconto/limites sem nome — intenção opaca e propensa a bug. |
| 9 | **Nomes ruins / shadowing** | LOW | `models.py:187-193`, `:219-225` | Cursores `cursor2`/`cursor3` e o builtin `id` usado como nome de parâmetro — dificultam leitura e mascaram builtin do Python. |

### Projeto 2 — `ecommerce-api-legacy` (Node.js/Express, LMS com checkout)

3 arquivos (`src/app.js`, `src/AppManager.js`, `src/utils.js`); a classe `AppManager` faz tudo.

| # | Problema | Severidade | Local | Por que é relevante |
|---|---|---|---|---|
| 1 | **Segredos hardcoded** | CRITICAL | `src/utils.js:1-7`, `src/AppManager.js:45` | Senha de banco e **chave de pagamento `pk_live_…`** embutidas e logadas em stdout — breach imediato. |
| 2 | **Rotas sensíveis sem auth** | CRITICAL | `/api/admin/financial-report`, `DELETE /api/users/:id` | Exfiltração anônima de dados financeiros e deleção não autenticada de usuários. |
| 3 | **God Class** | HIGH | `src/AppManager.js:4-141` | Banco, schema, rotas e regra de negócio numa só classe. |
| 4 | **Lógica de negócio no handler de rota** | HIGH | `src/AppManager.js:28-78` (`/api/checkout`) | Validação, hashing, decisão de pagamento e inserts todos no callback da rota. |
| 5 | **Acoplamento forte / sem DI** | HIGH | `src/AppManager.js:7` | `new sqlite3.Database()` no construtor — impossível mockar/trocar. |
| 6 | **Query N+1** | MEDIUM | `src/AppManager.js:83-127` | `financial-report` faz uma query por curso/matrícula/pagamento. |
| 7 | **Lógica duplicada (copy-paste)** | MEDIUM | `src/AppManager.js:38,41,51,55` | Blocos `res.status(5xx).send("Erro …")` quase idênticos repetidos ao longo do checkout — drift de comportamento de erro. |
| 8 | **Magic numbers** | LOW | `src/utils.js:18-22`, `src/AppManager.js:46` | `badCrypto` itera `10000`x, `substring(0,2)`/`(0,10)` e a decisão de pagamento usa o literal `"4"` (`cc.startsWith("4")`) — intenção opaca. |
| 9 | **Nomes ruins** | LOW | `src/AppManager.js:29-33` | `u`, `e`, `p`, `cid`, `cc` para valores não triviais do checkout. |

### Projeto 3 — `task-manager-api` (Python/Flask, Task Manager parcialmente organizado)

Já possui `models/`, `routes/`, `services/`, `utils/` — mas a organização não garante arquitetura adequada.

| # | Problema | Severidade | Local | Por que é relevante |
|---|---|---|---|---|
| 1 | **Segredos hardcoded** | CRITICAL | `app.py:11-13`, `services/notification_service.py:7-10` | `SECRET_KEY` e credenciais SMTP fixas; `python-dotenv` declarado mas nunca usado. |
| 2 | **Rotas sensíveis sem auth** | CRITICAL | `user_routes.py:134`, `task_routes.py:225`, `report_routes.py:211` | `DELETE /users/<id>` cascateia; `/login` devolve `'fake-jwt-token-'+id` que nunca é verificado. |
| 3 | **Lógica de negócio nos handlers** | HIGH | `task_routes.py:85-154`, `report_routes.py:12-101` | `summary_report` tem ~90 linhas de agregação dentro da view. |
| 4 | **God File** | HIGH | `report_routes.py` (reports **+** CRUD de Category), `task_routes.py` (300 linhas) | Responsabilidades não relacionadas no mesmo arquivo. |
| 5 | **Uso de API deprecated** | MEDIUM | `datetime.utcnow()` (espalhado) + `Model.query.get()` | Deprecated no Python 3.12 / SQLAlchemy 2.0 — quebra no próximo upgrade. |
| 6 | **Query N+1** | MEDIUM | `task_routes.py:41-57`, `report_routes.py:53-68` | `User.query.get()` / `Category.query.get()` por iteração. |
| 7 | **Lógica duplicada (copy-paste)** | MEDIUM | `task_routes.py:30-39` (repetido em `:71-80`, `:283-287`, `user_routes.py:171-180`, `report_routes.py:33-37`) | Cálculo de "atrasada" copiado em 5 handlers, mesmo já existindo `Task.is_overdue()` — drift no relatório de atraso. |
| 8 | **Magic numbers** | LOW | status/prioridade inline (`task_routes.py:96-100,110,113`), porta SMTP `587`, janela `days=7` | Constantes já existiam em `utils/helpers.py` (`VALID_STATUSES`, `MAX_TITLE_LENGTH`) mas as rotas as reimplementam. |
| 9 | **Nomes ruins** | LOW | `report_routes.py:24-28` (`p1..p5`), `models/category.py:14` (`d`), `utils/helpers.py:25` (`s`) | Valores não triviais com nomes de uma letra — elevam o custo de leitura e mudança segura. |

## B) Construção da Skill

### Decisões de design: estrutura do `SKILL.md` e das referências

O `SKILL.md` é o **orquestrador** — ele não contém conhecimento de domínio, apenas o sequenciamento estrito das 3 fases, o carregamento das referências (Step 0) e a **porta de confirmação** obrigatória entre Fase 2 e Fase 3. Todo o conhecimento vive em **5 arquivos de referência** em `references/`, um por área exigida:

| Arquivo de referência | Área de conhecimento | Consumido por |
|---|---|---|
| `detection-heuristics.md` | Análise de projeto (6 categorias: linguagem, framework, deps, banco, domínio, arquitetura) | Fase 1 |
| `anti-patterns-catalog.md` | Catálogo de anti-patterns (AP-01…AP-12, com sinal de detecção e severidade) | Fase 2 |
| `report-template.md` | Template do relatório de auditoria | Fase 2 |
| `mvc-guidelines.md` | Guidelines de arquitetura (as 6 camadas MVC-alvo) | Fase 3 |
| `refactoring-playbook.md` | Playbook de refatoração (P-01…P-12, antes/depois) | Fase 3 |

Essa separação **orquestrador ↔ conhecimento** é o que torna a skill copiável: o `SKILL.md` não hardcoda nome, path ou stack de projeto algum.

### Anti-patterns incluídos no catálogo e por quê

12 anti-patterns (supera o mínimo de 8), com severidade distribuída e mapeamento 1:1 para o playbook:

| ID | Anti-pattern | Severidade | → Playbook |
|---|---|---|---|
| AP-01 | Hardcoded Credentials / Secrets | CRITICAL | P-01 Extract Config & Secrets |
| AP-02 | SQL Injection via String Interpolation | CRITICAL | P-02 Parameterize Queries |
| AP-03 | Missing Authentication / Authorization | CRITICAL | P-08 Centralize Auth Middleware |
| AP-04 | God Class / God File | HIGH | P-03 Split God Class into MVC Layers |
| AP-05 | Business Logic in Route Handlers / Views | HIGH | P-04 Move Business Logic to Controllers |
| AP-06 | Tight Coupling / No Dependency Injection | HIGH | P-05 Introduce Dependency Injection |
| AP-07 | N+1 Query | MEDIUM | P-06 Fix N+1 with Batched Query |
| AP-08 | Duplicated Logic (Copy-Paste) | MEDIUM | P-07 Extract Shared Helper |
| AP-09 | Missing / Inconsistent Error Handling | MEDIUM | P-09 Centralize Error Handling |
| AP-10 | Magic Numbers / Hardcoded Literals | LOW | P-10 Extract Magic Numbers to Constants |
| AP-11 | **Deprecated API Usage** | MEDIUM | P-11 Replace Deprecated API |
| AP-12 | Poor / Misleading Naming | LOW | P-12 Rename for Intent |

A escolha cobre as três dimensões do enunciado — **segurança** (AP-01/02/03), **arquitetura/SOLID** (AP-04/05/06) e **qualidade/performance** (AP-07…AP-12) — e inclui obrigatoriamente a **detecção de APIs deprecated** (AP-11: `datetime.utcnow()`, `Model.query.get()`, `new Buffer()`, `url.parse()`), recomendando o equivalente moderno.

### Como a skill é agnóstica de tecnologia

- **Zero hardcode de stack** no `SKILL.md`; toda detecção sai de `detection-heuristics.md`, que descreve sinais para Python/Flask **e** Node/Express (imports, manifestos, ORMs).
- As 6 camadas MVC são definidas por **responsabilidade**, não por nome de arquivo — a Fase 3 adapta os nomes ao stack (`app.py` vs `index.js`, `models/` vs `src/models/`).
- O mesmo playbook P-01…P-12 dirige Flask e Express de forma idêntica.
- **Contrato de copiabilidade:** copiar `.claude/skills/refactor-arch/` sem alterações para outro projeto reproduz o pipeline. Foi validado nos 3 projetos.

### Desafios encontrados e como resolvi

- **Impedir mutação antes da aprovação humana:** a porta de confirmação foi colocada no **orquestrador** (não nas fases), garantindo que nenhuma fase escreva arquivo antes de `y`. Em `abort`, o projeto fica byte-a-byte intacto.
- **Provar que a refatoração não quebrou nada:** a Fase 3 captura um **baseline de endpoints antes** de mutar e compara status/shape **depois**; só declara `SUCCESS` se boot **e** todos os endpoints baterem.
- **Projeto parcialmente organizado (P3):** ter pastas não significa arquitetura correta. A skill detecta problemas mesmo com camadas presentes (God File em `report_routes.py`, lógica nas views, deprecated APIs) e melhora sem reescrever do zero.
- **Contagem de arquivos honesta:** a Fase 1 exclui `venv`/`node_modules`/`.git` para que o total analisado reflita a realidade.

## C) Resultados

### Resumo dos relatórios de auditoria (findings por severidade)

| Projeto | Stack | CRITICAL | HIGH | MEDIUM | LOW | **Total** |
|---|---|:---:|:---:|:---:|:---:|:---:|
| 1 — code-smells-project | Python/Flask 3.1.1 | 3 | 3 | 3 | 2 | **11** |
| 2 — ecommerce-api-legacy | Node.js/Express 4 | 2 | 3 | 3 | 2 | **10** |
| 3 — task-manager-api | Python/Flask 3.0.0 | 2 | 3 | 4 | 2 | **11** |

Relatórios completos: `reports/audit-project-1.md`, `reports/audit-project-2.md`, `reports/audit-project-3.md`.

### Comparação antes/depois da estrutura

**Projeto 1 — code-smells-project**
```
ANTES (monolito, 4 arquivos)          DEPOIS (MVC)
app.py                                app.py                (composition root)
controllers.py                        config/               settings.py, constants.py
models.py                             models/               produto, usuario, pedido, system, db
database.py                           controllers/          produto, pedido, usuario, system, validation
                                      routes/               produto, pedido, usuario, relatorio, system
                                      middleware/           auth.py, errors.py
                                      .env.example
```

**Projeto 2 — ecommerce-api-legacy**
```
ANTES (God Class, 3 arquivos)         DEPOIS (MVC)
src/app.js                            src/app.js            (bootstrap)
src/AppManager.js                     src/config/           index.js
src/utils.js                          src/models/           user, course, enrollment, payment, report, auditLog, database
                                      src/controllers/      checkout, report, user
                                      src/routes/           index.js
                                      src/middleware/       auth.js, errorHandler.js
                                      src/services/         passwordService.js
                                      .env.example
```

**Projeto 3 — task-manager-api**
```
ANTES (parcial)                       DEPOIS (MVC completo)
app.py                                app.py                (composition root)
database.py, seed.py                  config/               settings.py, constants.py   ← novo
models/  (task, user, category)       controllers/          task, user, category, report ← novo
routes/  (task, user, report)         middleware/           auth.py, error_handler.py    ← novo
services/ (notification)              exceptions.py                                       ← novo
utils/   (helpers)                    utils/timeutils.py                                  ← novo
                                      models/ routes/ services/ utils/  (mantidos e limpos)
                                      routes/category_routes.py  (separado de reports)     ← novo
                                      .env.example
```

### Checklist de validação (preenchido para os 3 projetos)

| Item | P1 | P2 | P3 |
|---|:--:|:--:|:--:|
| **Fase 1** — Linguagem detectada | ✅ Python | ✅ Node.js | ✅ Python |
| **Fase 1** — Framework detectado | ✅ Flask 3.1.1 | ✅ Express 4 | ✅ Flask 3.0.0 |
| **Fase 1** — Domínio descrito | ✅ E-commerce | ✅ LMS/checkout | ✅ Task Manager |
| **Fase 1** — Nº de arquivos condiz | ✅ 4 | ✅ 3 | ✅ 15 |
| **Fase 2** — Segue o template | ✅ | ✅ | ✅ |
| **Fase 2** — File:line em cada finding | ✅ | ✅ | ✅ |
| **Fase 2** — Ordenado CRITICAL→LOW | ✅ | ✅ | ✅ |
| **Fase 2** — ≥ 5 findings | ✅ 11 | ✅ 10 | ✅ 11 |
| **Fase 2** — Detecção de deprecated | ➖ n/a | ➖ n/a | ✅ AP-11 |
| **Fase 2** — Pausa/confirma antes da Fase 3 | ✅ | ✅ | ✅ |
| **Fase 3** — Estrutura MVC | ✅ | ✅ | ✅ |
| **Fase 3** — Config sem hardcoded | ✅ | ✅ | ✅ |
| **Fase 3** — Models de dados | ✅ | ✅ | ✅ |
| **Fase 3** — Views/Routes separadas | ✅ | ✅ | ✅ |
| **Fase 3** — Controllers concentram fluxo | ✅ | ✅ | ✅ |
| **Fase 3** — Error handling centralizado | ✅ | ✅ | ✅ |
| **Fase 3** — Entry point claro | ✅ | ✅ | ✅ |
| **Fase 3** — App inicia sem erros | ✅ | ✅ | ✅ |
| **Fase 3** — Endpoints respondem | ✅ | ✅ | ✅ |

### Logs das aplicações rodando após a refatoração

Smoke test executado nos 3 projetos refatorados (portas de teste):

```
# Projeto 1 — code-smells-project (:8101)
==================================================
SERVIDOR INICIADO
Rodando em http://localhost:8101
==================================================
GET /produtos  -> HTTP 200
GET /usuarios  -> HTTP 200
GET /health    -> HTTP 200

# Projeto 2 — ecommerce-api-legacy (:8102)
Frankenstein LMS rodando na porta 8102...
GET  /api/admin/financial-report -> HTTP 200
POST /api/checkout (body vazio)  -> HTTP 400   (validação ativa, endpoint vivo)

# Projeto 3 — task-manager-api (:8103)
 * Running on http://127.0.0.1:8103
GET /           -> HTTP 200
GET /tasks      -> HTTP 200
GET /users      -> HTTP 200
GET /categories -> HTTP 200
```

### Observações sobre stacks diferentes

- **Mesma skill, sem edição:** a pasta `refactor-arch/` foi copiada sem alterações para os 3 projetos; a adaptação (nomes de arquivo, entry point, ORM vs SQL cru) veio inteiramente das referências.
- **Python vs Node:** em Flask a Fase 3 produz `app.py` + Blueprints; em Express, `src/app.js` + routers — ambos derivados das mesmas 6 camadas.
- **Deprecated API só onde existe:** AP-11 disparou apenas no Projeto 3 (`datetime.utcnow()` / `query.get()`), demonstrando detecção condicional ao stack em vez de finding fixo.
- **Projeto já organizado:** no P3 a skill não "reorganizou por reorganizar" — separou Category de Reports, extraiu controllers/middleware/config e trocou APIs deprecated, preservando o que já estava bom.

## D) Como Executar

### Pré-requisitos

- **Claude Code** instalado e autenticado (a ferramenta usada no curso).
- **Python 3.12+** (Projetos 1 e 3) e **Node.js 18+** (Projeto 2).
- Dependências de cada projeto instaladas:
  ```bash
  # Projetos Python (1 e 3)
  python -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt
  # Projeto Node (2)
  npm install
  ```

### Executar a skill em cada projeto

A skill já está copiada em `.claude/skills/refactor-arch/` dentro dos 3 projetos. Basta invocá-la a partir da raiz de cada um:

```bash
cd code-smells-project     && claude "/refactor-arch"   # Projeto 1
cd ../ecommerce-api-legacy && claude "/refactor-arch"   # Projeto 2
cd ../task-manager-api     && claude "/refactor-arch"   # Projeto 3
```

Em cada execução: a **Fase 1** imprime o resumo do stack, a **Fase 2** gera o relatório e **pausa pedindo confirmação** (`[y/n]`) — responda `y` para autorizar a **Fase 3**, que refatora e valida.

### Validar que a refatoração funcionou

```bash
# Projeto 1 (Flask)
cd code-smells-project && python app.py &
curl -s -o /dev/null -w "%{http_code}\n" http://localhost:5000/produtos   # espera 200

# Projeto 2 (Express)
cd ecommerce-api-legacy && npm start &
curl -s -o /dev/null -w "%{http_code}\n" http://localhost:3000/api/admin/financial-report  # espera 200

# Projeto 3 (Flask)
cd task-manager-api && python app.py &
curl -s -o /dev/null -w "%{http_code}\n" http://localhost:5000/tasks      # espera 200
```

Critério de sucesso: **a aplicação inicia sem erros e todos os endpoints originais continuam respondendo** — exatamente o que a Fase 3 verifica automaticamente contra o baseline pré-refatoração.

---

## Objetivo

Você deve entregar uma Skill capaz de:

- Analisar uma codebase detectando linguagem, framework e arquitetura atual
- Identificar anti-patterns e code smells, classificando por severidade com arquivo e linha exatos
- Gerar um relatório de auditoria estruturado com todos os achados
- Refatorar o projeto para o padrão MVC (Model-View-Controller), eliminando os problemas encontrados
- Validar o resultado garantindo que a aplicação continua funcionando após as mudanças

A skill deve ser agnóstica de tecnologia, funcionando com diferentes linguagens e frameworks.

## Contexto

### Definição de Severidades

Para padronizar a sua auditoria e os relatórios gerados pela IA, utilize a seguinte escala de classificação baseada em problemas de MVC e SOLID:

- **CRITICAL:** Falhas graves de arquitetura ou segurança que impedem o funcionamento correto, expõem dados sensíveis (ex: credenciais hardcoded, SQL Injection) ou violam completamente a separação de responsabilidades (ex: "God Class" contendo banco de dados, lógicas complexas e roteamento no mesmo arquivo).
- **HIGH:** Fortes violações do padrão MVC ou princípios SOLID que dificultam muito a manutenção e testes (ex: lógicas de negócio pesadas presas dentro de Controllers, forte acoplamento sem Injeção de Dependência, ou uso de estado global mutável em toda a aplicação).
- **MEDIUM:** Problemas de padronização, duplicação de código ou gargalos de performance moderada (ex: Queries N+1 no banco de dados, uso inadequado de middlewares, validações ausentes nas rotas).
- **LOW:** Melhorias de legibilidade, nomenclatura de variáveis ruins, ou "magic numbers" soltos pelo código.

### Exemplo de Uso no CLI

```bash
# Executar a skill no projeto com problemas
cd code-smells-project
claude "/refactor-arch"
```

```
================================
PHASE 1: PROJECT ANALYSIS
================================
Language:      Python
Framework:      Flask 3.1.1
Dependencies:  flask-cors
Domain:        E-commerce API (produtos, pedidos, usuários)
Architecture:  Monolítica — tudo em 4 arquivos, sem separação de camadas
Source files:  4 files analyzed
DB tables:     produtos, usuarios, pedidos, itens_pedido
================================
```

```
================================
ARCHITECTURE AUDIT REPORT
================================
Project: code-smells-project
Stack:   Python + Flask
Files:   4 analyzed | ~800 lines of code

## Summary
CRITICAL: 4 | HIGH: 5 | MEDIUM: 2 | LOW: 3

## Findings

### [CRITICAL] God Class / God Method
File: models.py:1-350
Description: Arquivo único contém toda lógica de negócio, queries SQL, validação e formatação para 4 domínios diferentes.
Impact: Impossível testar em isolamento, qualquer mudança afeta tudo.
Recommendation: Separar em models e controllers por domínio.

### [CRITICAL] Hardcoded Credentials
File: app.py:8
Description: SECRET_KEY hardcoded como 'minha-chave-super-secreta-123'
...

================================
Total: 14 findings
================================

Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]
> y
```

```
[... refatoração executada ...]

================================
PHASE 3: REFACTORING COMPLETE
================================
## New Project Structure
src/
├── config/settings.py
├── models/
│   ├── produto_model.py
│   └── usuario_model.py
├── views/
│   └── routes.py
├── controllers/
│   ├── produto_controller.py
│   └── pedido_controller.py
├── middlewares/error_handler.py
└── app.py (composition root)

## Validation
  ✓ Application boots without errors
  ✓ All endpoints respond correctly
  ✓ Zero anti-patterns remaining
================================
```

## Tecnologias obrigatórias

- **Ferramenta:** uma das três opções abaixo (não são aceitas outras ferramentas):
  - Claude Code
  - Gemini CLI
  - OpenAI Codex
- **Recurso:** Custom Skills (ou o equivalente na ferramenta escolhida)
- **Formato dos arquivos de referência:** Markdown
- **Projetos-alvo:** Python/Flask (2 projetos) e Node.js/Express (1 projeto) (fornecidos no repositório base)

> **Nota sobre a ferramenta:** Os exemplos deste documento usam o Claude Code (`.claude/skills/`) como referência, pois é a ferramenta utilizada no curso. Se você optar por Gemini CLI ou Codex, adapte o nome da pasta e o comando de invocação conforme a convenção dela — o conceito de skill e a estrutura interna (SKILL.md + arquivos de referência) permanecem os mesmos.

## Requisitos

### 1. Análise Manual dos Projetos

Antes de criar a skill, você deve entender os problemas que ela vai resolver.

**Tarefas:**

- Analisar o projeto `code-smells-project/` (Python/Flask — API de E-commerce)
- Analisar o projeto `ecommerce-api-legacy/` (Node.js/Express — LMS API com fluxo de checkout)
- Analisar o projeto `task-manager-api/` (Python/Flask — API de Task Manager)

Para cada projeto, identificar e documentar no mínimo 5 problemas, incluindo pelo menos:

- 1 de severidade CRITICAL ou HIGH
- 2 de severidade MEDIUM
- 2 de severidade LOW

Documentar os achados na seção "Análise Manual" do seu `README.md`

> **Dica:** Não precisa encontrar todos os problemas — foque nos que têm maior impacto arquitetural. Use os projetos como insumo para entender quais padrões sua skill precisa detectar.

> **Por que 3 projetos?** Dois são Python/Flask (com níveis de organização diferentes) e um é Node.js/Express. Sua skill precisa funcionar nos 3 para provar que é verdadeiramente agnóstica de tecnologia — lidando tanto com código completamente desestruturado quanto com projetos que já possuem alguma separação de camadas.

### 2. Criação da Skill

Agora que você conhece os problemas, crie uma skill que os detecte, gere um relatório de auditoria e corrija automaticamente.

**Tarefas:**

Criar a skill dentro do projeto `code-smells-project/` e implementar o SKILL.md com 3 fases sequenciais:

- **Fase 1 — Análise:** Detectar stack, mapear arquitetura atual, imprimir resumo
- **Fase 2 — Auditoria:** Cruzar código contra catálogo de anti-patterns, gerar relatório, pedir confirmação
- **Fase 3 — Refatoração:** Reestruturar para o padrão MVC, validar que funciona

Criar arquivos de referência em Markdown que forneçam à skill o conhecimento necessário para executar as 3 fases. Os arquivos devem cobrir **obrigatoriamente** as seguintes áreas de conhecimento:

| Área de conhecimento | O que deve conter |
|---|---|
| Análise de projeto | Heurísticas para detecção de linguagem, framework, banco de dados e mapeamento de arquitetura |
| Catálogo de anti-patterns | Anti-patterns com sinais de detecção e classificação de severidade |
| Template de relatório | Formato padronizado do relatório de auditoria (Fase 2) |
| Guidelines de arquitetura | Regras do padrão MVC alvo (camadas Models, Views/Routes e Controllers, responsabilidades de cada uma) |
| Playbook de refatoração | Padrões concretos de transformação para cada anti-pattern (com exemplos de código) |

> **Nota:** Você tem liberdade para organizar os arquivos de referência como preferir — pode usar os nomes e a quantidade de arquivos que fizer sentido para sua skill. O importante é que todas as 5 áreas de conhecimento estejam cobertas. O nome da skill (`refactor-arch`) e o arquivo `SKILL.md` são obrigatórios e não devem ser alterados. O path da skill segue a convenção da ferramenta escolhida (no Claude Code, por exemplo, é `.claude/skills/refactor-arch/`).

**Requisitos da skill:**

- Deve ser agnóstica de tecnologia — deve funcionar corretamente nos 3 projetos fornecidos, independente da stack ou nível de organização
- O catálogo de anti-patterns deve conter no mínimo 8 anti-patterns com severidade distribuída (CRITICAL, HIGH, MEDIUM, LOW)
- O catálogo deve incluir detecção de APIs deprecated — identificar uso de APIs obsoletas e recomendar o equivalente moderno
- O playbook deve ter no mínimo 8 padrões de transformação com exemplos de código antes/depois
- A Fase 2 deve pausar e pedir confirmação antes de modificar qualquer arquivo
- A Fase 3 deve validar o resultado (boot da aplicação + endpoints funcionando)

### 3. Execução da Skill

Execute sua skill nos 3 projetos e valide que ela funciona em todas as stacks.

#### Projeto 1 — code-smells-project (Python/Flask)

Invocar a skill no Claude Code:

```bash
claude "/refactor-arch"
```

> **Nota:** O comando acima é o exemplo com Claude Code. Se você estiver usando Gemini CLI ou Codex, utilize o comando equivalente para invocar uma skill na sua ferramenta.

- Verificar que a Fase 1 detecta corretamente a stack e imprime o resumo
- Verificar que a Fase 2 encontra no mínimo 5 dos problemas documentados na sua análise manual
- Confirmar a execução da Fase 3
- Verificar que a Fase 3:
  - Cria a estrutura de diretórios baseada em MVC
  - A aplicação inicia sem erros
  - Os endpoints originais continuam respondendo
- Salvar o relatório de auditoria (output da Fase 2) em `reports/audit-project-1.md`
- Commitar o código refatorado do projeto no repositório

#### Projeto 2 — ecommerce-api-legacy (Node.js/Express)

Prove que sua skill é reutilizável em outro projeto de backend, mas com stack diferente.

- Copiar a pasta `.claude/skills/refactor-arch/` para dentro de `ecommerce-api-legacy/`
- Invocar a skill:

```bash
cd ../ecommerce-api-legacy
claude "/refactor-arch"
```

- Verificar que as 3 fases executam corretamente neste projeto
- Salvar o relatório em `reports/audit-project-2.md`
- Commitar o código refatorado do projeto no repositório

#### Projeto 3 — task-manager-api (Python/Flask)

Agora o teste com um projeto Python/Flask que já possui alguma organização de camadas (models, routes, services, utils).

- Copiar a pasta `.claude/skills/refactor-arch/` para dentro de `task-manager-api/`
- Invocar a skill:

```bash
cd ../task-manager-api
claude "/refactor-arch"
```

- Verificar que:
  - A Fase 1 detecta corretamente Python/Flask como stack e identifica o domínio de Task Manager
  - A Fase 2 identifica problemas mesmo em um projeto parcialmente organizado
  - A Fase 3 melhora a estrutura sem quebrar a aplicação (todos os endpoints devem continuar respondendo)
- Salvar o relatório em `reports/audit-project-3.md`
- Commitar o código refatorado do projeto no repositório

> **Nota:** Este projeto já possui alguma separação de camadas, mas isso não significa que a arquitetura está adequada. A skill deve identificar tanto problemas de código (segurança, performance, qualidade) quanto oportunidades de melhoria arquitetural. Se houver mudanças estruturais necessárias, a skill deve propô-las e executá-las.

#### Validação

Para cada projeto refatorado, valide o seguinte checklist:

```markdown
## Checklist de Validação

### Fase 1 — Análise
- [ ] Linguagem detectada corretamente
- [ ] Framework detectado corretamente
- [ ] Domínio da aplicação descrito corretamente
- [ ] Número de arquivos analisados condiz com a realidade

### Fase 2 — Auditoria
- [ ] Relatório segue o template definido nos arquivos de referência
- [ ] Cada finding tem arquivo e linhas exatos
- [ ] Findings ordenados por severidade (CRITICAL → LOW)
- [ ] Mínimo de 5 findings identificados
- [ ] Detecção de APIs deprecated incluída (se aplicável)
- [ ] Skill pausa e pede confirmação antes da Fase 3

### Fase 3 — Refatoração
- [ ] Estrutura de diretórios segue padrão MVC
- [ ] Configuração extraída para módulo de config (sem hardcoded)
- [ ] Models criados para abstrair dados
- [ ] Views/Routes separadas para visualização ou roteamento
- [ ] Controllers concentram o fluxo da aplicação
- [ ] Error handling centralizado
- [ ] Entry point claro
- [ ] Aplicação inicia sem erros
- [ ] Endpoints originais respondem corretamente
```

> **Dica:** Se a skill não detectou problemas suficientes ou a refatoração falhou, ajuste os arquivos de referência e execute novamente. É normal precisar de 2-4 iterações.

## Entregável

Repositório público no GitHub (fork do repositório base) contendo:

- Skill completa em `.claude/skills/refactor-arch/` (dentro dos 3 projetos)
- Código refatorado dos 3 projetos (resultado da execução da Fase 3, commitado no repositório)
- Relatórios de auditoria em `reports/` (3 arquivos)
- `README.md` atualizado

### Estrutura do repositório

Faça um fork do repositório base contendo os três projetos com code smells.

> **Nota:** A estrutura abaixo usa Claude Code como exemplo (`.claude/skills/`). Se estiver usando outra ferramenta, adapte os caminhos conforme a convenção dela.

```
desafio-skills/
├── README.md                              # Sua documentação
│
├── code-smells-project/                   # Projeto 1 — Python/Flask (API de E-commerce)
│   ├── .claude/
│   │   └── skills/
│   │       └── refactor-arch/             # ← SUA SKILL AQUI
│   │           ├── SKILL.md
│   │           └── (arquivos de referência)
│   ├── app.py
│   ├── controllers.py
│   ├── models.py
│   ├── database.py
│   └── requirements.txt
│
├── ecommerce-api-legacy/                  # Projeto 2 — Node.js/Express (LMS API com checkout)
│   ├── .claude/
│   │   └── skills/
│   │       └── refactor-arch/             # ← CÓPIA DA SKILL
│   │           └── ...
│   ├── src/
│   │   ├── app.js
│   │   ├── AppManager.js
│   │   └── utils.js
│   ├── api.http
│   └── package.json
│
├── task-manager-api/                      # Projeto 3 — Python/Flask (API de Task Manager)
│   ├── .claude/
│   │   └── skills/
│   │       └── refactor-arch/             # ← CÓPIA DA SKILL
│   │           └── ...
│   ├── app.py
│   ├── database.py
│   ├── seed.py
│   ├── requirements.txt
│   ├── models/
│   ├── routes/
│   ├── services/
│   └── utils/
│
└── reports/                               # Relatórios gerados
    ├── audit-project-1.md                 # Saída da Fase 2 no projeto 1
    ├── audit-project-2.md                 # Saída da Fase 2 no projeto 2
    └── audit-project-3.md                 # Saída da Fase 2 no projeto 3
```

**O que você vai criar:**

- `.claude/skills/refactor-arch/` — A skill completa (SKILL.md + arquivos de referência)
- Código refatorado dos 3 projetos — resultado da execução da Fase 3, commitado no repositório
- `reports/audit-project-{1,2,3}.md` — Relatório de auditoria de cada projeto
- `README.md` — Documentação do seu processo

**O que já vem pronto:**

- `code-smells-project/` — API de E-commerce Python/Flask com code smells intencionais
- `ecommerce-api-legacy/` — LMS API Node.js/Express (com fluxo de checkout) e problemas de implementação
- `task-manager-api/` — API de Task Manager Python/Flask com organização parcial e problemas de segurança/qualidade

> **Dica:** Cada projeto contém problemas intencionais de diferentes severidades (CRITICAL, HIGH, MEDIUM, LOW), incluindo falhas de segurança, violações arquiteturais e problemas de qualidade de código. Parte do desafio é identificá-los por conta própria através da análise manual do código.

### README.md deve conter

**A) Seção "Análise Manual":**

- Lista dos problemas identificados manualmente em cada projeto
- Classificação por severidade
- Justificativa de por que cada problema é relevante

**B) Seção "Construção da Skill":**

- Decisões de design: como estruturou o SKILL.md e os arquivos de referência
- Quais anti-patterns incluiu no catálogo e por quê
- Como garantiu que a skill é agnóstica de tecnologia
- Desafios encontrados e como resolveu

**C) Seção "Resultados":**

- Resumo dos relatórios de auditoria dos 3 projetos (quantos findings por severidade em cada)
- Comparação antes/depois da estrutura de cada projeto
- Checklist de validação preenchido para cada projeto
- Screenshots ou logs mostrando as aplicações rodando após refatoração
- Observações sobre como a skill se comportou em stacks diferentes

**D) Seção "Como Executar":**

- Pré-requisitos (a ferramenta escolhida — Claude Code, Gemini CLI ou Codex — instalada e configurada)
- Comandos para executar a skill em cada projeto
- Como validar que a refatoração funcionou

### Ordem de execução sugerida

**1. Analisar os projetos manualmente**

Leia o código dos três projetos e documente os problemas encontrados.

**2. Criar a skill**

Escreva o SKILL.md e os arquivos de referência.

**3. Executar nos 3 projetos**

```bash
# Projeto 1
cd code-smells-project
claude "/refactor-arch"

# Projeto 2
cd ../ecommerce-api-legacy
claude "/refactor-arch"

# Projeto 3
cd ../task-manager-api
claude "/refactor-arch"
```

Salve a saída da Fase 2 de cada projeto em `reports/audit-project-{1,2,3}.md`.

**4. Iterar**

Se a skill não detectou problemas suficientes ou a refatoração falhou, ajuste os arquivos de referência e execute novamente. É normal precisar de 2-4 iterações.

## Critérios de Aceite

A skill deve atingir os seguintes mínimos em **todos os 3 projetos**:

| Critério | Requisito |
|---|---|
| Fase 1 detecta stack corretamente | OBRIGATÓRIO (3/3 projetos) |
| Fase 2 encontra >= 5 findings | OBRIGATÓRIO (3/3 projetos) |
| Fase 2 inclui pelo menos 1 CRITICAL ou HIGH | OBRIGATÓRIO (3/3 projetos) |
| Fase 3 aplicação funciona após refatoração | OBRIGATÓRIO (3/3 projetos) |

**IMPORTANTE:** Todos os critérios devem ser atingidos nos 3 projetos, não apenas em um!

> **Sobre o projeto 3 (task-manager-api):** Este projeto já possui alguma organização. "aplicação funciona" significa que a API inicia sem erros e todos os endpoints continuam respondendo corretamente.

## Referências

- [Claude Code: Skills](https://docs.anthropic.com/en/docs/claude-code/skills) — Documentação oficial sobre como criar e estruturar Skills
- [Claude Code: Overview](https://docs.anthropic.com/en/docs/claude-code/overview) — Visão geral do Claude Code e suas capacidades
- [The Complete Guide to Building Skills for Claude (PDF)](https://resources.anthropic.com/hubfs/The-Complete-Guide-to-Building-Skill-for-Claude.pdf) — Guia completo da Anthropic sobre construção de Skills
- [Equipping Agents for the Real World with Agent Skills](https://claude.com/blog/equipping-agents-for-the-real-world-with-agent-skills) — Blog oficial da Anthropic sobre Agent Skills

---

## Dicas Finais

- **Comece pela análise manual** — entender os problemas profundamente é essencial para criar uma skill que os detecte.
- **O SKILL.md é um prompt** — ele instrui o agente sobre o que fazer, enquanto os arquivos de referência fornecem o conhecimento de domínio.
- **Seja específico nos sinais de detecção** — "código ruim" não ajuda; "query SQL dentro de loop for" é acionável.
- **Teste incrementalmente** — não tente criar a skill perfeita de primeira.
- **A skill deve ser copiável** — se ela só funciona em um projeto específico, está acoplada demais. Teste nos 3 projetos para validar.
- **Projetos diferentes exigem adaptação** — a Fase 3 de um projeto já parcialmente organizado não vai ter as mesmas transformações de um monolito. Sua skill deve se adaptar ao contexto.
- **Pedir confirmação na Fase 2 é obrigatório** — o humano deve revisar o relatório antes de qualquer modificação.
- **Consulte as referências do curso** — revise a documentação oficial da ferramenta escolhida e os materiais das aulas para relembrar a estrutura e anatomia de uma skill.