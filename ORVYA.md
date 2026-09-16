# ORVYA — blueprint único de implementação

> **Objetivo:** construir o Orvya do zero, de forma autônoma, direta e reproduzível, preservando o comportamento funcional vigente e evitando carregar a complexidade histórica do projeto anterior.
>
> **Repositório de implementação:** `orvya/orvya`, branch `main`.
>
> **Baseline funcional verificada:** comportamento de `orvya/orvya-base@f11abd463f27cbdc3515fc14de272bbd86767d62`, cuja instalação em homologação foi registrada posteriormente em `b3c07fea8d306f3464a02262586ea9d38b7eb1f6`.
>
> **Regra de prevalência:** este arquivo descreve o produto novo. Onde uma escolha deste documento divergir do projeto histórico, **este arquivo prevalece**.

---

# 1. Resultado esperado

O Orvya é um SaaS jurídico multi-tenant para escritórios e profissionais da advocacia.

O produto possui somente duas superfícies:

| Superfície | Host | Finalidade |
|---|---|---|
| App | `app.orvya.net` | produto utilizado pelos escritórios |
| Admin | `admin.orvya.net` | administração global da Plataforma |

A API fica sob `/api/v1` e atende as duas superfícies.

O núcleo conecta:

- Escritórios e usuários;
- Pessoas;
- Processos judiciais e administrativos;
- Agenda e Atividades;
- Publicações;
- Documentos e Modelos DOCX;
- Financeiro;
- Relatórios;
- Notificações;
- Pesquisa Global;
- Configurações do escritório;
- Administração da Plataforma.

## 1.1 Decisões já consolidadas para esta reconstrução

Estas decisões são definitivas para o novo Orvya:

- não implementar website institucional ou landing page;
- não implementar Google Auth;
- não implementar Google Calendar;
- não implementar rotina ou painel de backup;
- usar **Adobe Spectrum 2 exclusivamente** como Design System;
- o cabeçalho do App não mostra o nome do escritório;
- a Pesquisa Global fica geometricamente centralizada no cabeçalho;
- botões do cabeçalho são somente ícones;
- Processos e Atividades usam **listas operacionais**, não tabelas administrativas;
- a mesma linguagem de lista deve ser preferida nas demais áreas operacionais quando a informação tiver hierarquia natural em vez de comparação por colunas.

## 1.2 Critério de conclusão

A implementação termina somente quando:

- um banco vazio recebe a migration inicial e sobe sem intervenção manual;
- cadastro, confirmação de e-mail, login, sessão e recuperação de senha funcionam;
- App e Admin compilam e funcionam;
- isolamento entre escritórios está garantido no backend;
- todas as fatias verticais abaixo estão implementadas;
- integrações ausentes aparecem como indisponíveis, sem simular sucesso;
- deploy HTTPS dos dois hosts funciona;
- smoke tests finais passam;
- não existe erro de migration, typecheck ou build.

---

# 2. Protocolo de execução para a IA

A IA deve tratar esta especificação como **uma tarefa contínua**, sem solicitar aprovação entre fases.

## 2.1 Regras de trabalho

1. Reproduzir produto, regras e experiência vigentes, não a arquitetura histórica.
2. Usar **monólito modular**.
3. Não criar microserviços por domínio.
4. Criar **uma migration inicial limpa** com o schema final conhecido.
5. Criar novas migrations somente se o schema mudar durante a própria implementação.
6. Não gerar EFs, ETs, matrizes, relatórios de evidência ou documentação paralela.
7. Não perseguir cobertura de testes enquanto o produto ainda está incompleto.
8. Validar apenas grandes marcos durante a construção.
9. Fazer a rodada ampla de correções e testes no final.
10. Não inventar preço, cobrança, checkout ou funcionalidade comercial.
11. Não armazenar segredo no Git.
12. Não criar dados fictícios persistentes para preencher interfaces.
13. Integração externa não configurada não bloqueia a construção do restante do produto.
14. Defeito não estrutural pode ser anotado temporariamente e resolvido na estabilização final.
15. Commits devem acompanhar marcos grandes e coerentes.

## 2.2 Método obrigatório: fatias verticais

Cada domínio deve ser construído nesta sequência:

```text
schema/modelo
→ regra de domínio
→ persistência/serviço
→ API
→ cliente frontend
→ listagem/ficha/formulário
→ smoke curto
```

Não implementar o banco inteiro primeiro, depois toda a API e somente depois o frontend.

A unidade de avanço é uma função real do produto funcionando ponta a ponta.

## 2.3 Grafo de dependência

```text
F0 Fundação
 ├─ F1 Conta, acesso, Plano e permissões
 │   ├─ F2 Pessoas
 │   ├─ F3 Processos
 │   │   └─ F4 Atividades, Agenda e Área de trabalho
 │   │       └─ F5 Publicações, Pesquisa e Notificações
 │   └─ F6 Arquivos, Documentos e Modelos
 │
 ├─ F7 Financeiro
 │   └─ F8 Relatórios
 │
 └─ F9 Administração da Plataforma

F0..F9 → F10 Deploy → F11 Estabilização final
```

---

# 3. Arquitetura alvo

Use um monorepo simples.

```text
orvya/
├─ ORVYA.md
├─ README.md
├─ .env.example
├─ docker-compose.yml
├─ backend/
│  ├─ pyproject.toml
│  ├─ alembic.ini
│  ├─ migrations/
│  └─ app/
│     ├─ main.py
│     ├─ config.py
│     ├─ db.py
│     ├─ core/
│     │  ├─ errors.py
│     │  ├─ security.py
│     │  ├─ permissions.py
│     │  ├─ pagination.py
│     │  └─ audit.py
│     ├─ auth/
│     ├─ accounts/
│     ├─ people/
│     ├─ cases/
│     ├─ activities/
│     ├─ publications/
│     ├─ files/
│     ├─ documents/
│     ├─ finance/
│     ├─ reports/
│     ├─ notifications/
│     ├─ search/
│     ├─ integrations/
│     ├─ admin/
│     ├─ operations/
│     └─ worker/
├─ frontend/
│  ├─ package.json
│  ├─ apps/
│  │  ├─ app/
│  │  └─ admin/
│  └─ shared/
│     ├─ api/
│     ├─ auth/
│     ├─ routing/
│     ├─ formatting/
│     └─ components/
└─ deploy/
   ├─ nginx.conf
   ├─ Dockerfile.backend
   └─ Dockerfile.frontend
```

A divisão física pode variar sem alterar a separação de responsabilidades.

## 3.1 Runtime

Use Docker Compose com:

1. `postgres` — PostgreSQL;
2. `api` — FastAPI;
3. `worker` — tarefas persistentes e recorrentes;
4. `ops` — executor mínimo e allowlisted para operações administrativas;
5. `nginx` — assets do frontend e proxy da API.

Não adicionar Redis ou outro broker sem necessidade concreta. A fila interna pode usar PostgreSQL.

---

# 4. Stack

## 4.1 Backend

- Python 3.13;
- FastAPI;
- Uvicorn;
- SQLAlchemy 2;
- PostgreSQL;
- psycopg 3;
- Alembic;
- Pydantic 2;
- Argon2id;
- HTTPX;
- boto3 para armazenamento compatível com S3;
- biblioteca DOCX pequena e mantida;
- biblioteca XLSX pequena e mantida;
- conversão PDF somente onde necessária.

## 4.2 Frontend

- TypeScript;
- React;
- React Router;
- Vite;
- npm workspaces;
- **Adobe Spectrum 2 exclusivamente**;
- `@react-spectrum/s2`;
- `@react-spectrum/s2/style`;
- ícones `@react-spectrum/s2/icons/*`.

Fixar uma versão estável no lockfile e não misturar Spectrum 2 com biblioteca visual concorrente.

## 4.3 Provider

App e Admin montam `Provider` Spectrum 2 na raiz com:

- locale `pt-BR`;
- integração com roteamento;
- esquema de cor adotado;
- comportamento responsivo oficial;
- tipografia fornecida pelo próprio Spectrum.

Não carregar família tipográfica externa para a interface.

---

# 5. Design System e identidade

Spectrum 2 é a única fonte de:

- componentes;
- tipografia;
- cores de interface;
- espaçamentos;
- raios;
- elevação;
- foco;
- ícones;
- estados;
- menus;
- listas;
- tabelas;
- formulários;
- diálogos;
- tooltips;
- skeletons/progresso;
- comportamento de toque e responsividade dos controles.

Usar componentes oficiais sempre que existirem, especialmente:

- `Provider`;
- `Button`;
- `ActionButton`;
- `ActionMenu`;
- `Menu`;
- `SearchField`;
- `TextField`;
- `TextArea`;
- `ComboBox`;
- `Picker`;
- `Checkbox`;
- `Switch`;
- componentes de data/hora;
- `Dialog`;
- `AlertDialog`;
- `Tabs`;
- `SegmentedControl`;
- `ListView`;
- `TableView`;
- `SideNav`;
- `Avatar`;
- `Badge` ou `StatusLight`;
- `Toast`;
- `Tooltip`;
- `Skeleton`;
- `ProgressCircle`.

## 5.1 Styling adicional

Quando necessário:

```ts
import {style, focusRing} from '@react-spectrum/s2/style' with {type: 'macro'};
```

Usar tokens Spectrum antes de valor arbitrário.

Não criar:

- Design System intermediário próprio;
- paleta paralela;
- reset global agressivo;
- cópias de componentes Spectrum;
- CSS que reestilize internamente o Spectrum para parecer outra biblioteca.

## 5.2 Marca

- nome sempre `Orvya`;
- logotipo oficial completa em SVG onde houver espaço;
- emblema oficial em contexto compacto;
- não reconstruir a marca com texto comum;
- cores da marca não redefinem a paleta de UI.

## 5.3 Cor de Atividade

O banco armazena **chave de cor do produto**, nunca hexadecimal.

Use conjunto fechado mapeado para tokens Spectrum.

A mesma chave gera o mesmo marcador na Área de trabalho, Agenda, Processo, Pesquisa, Notificações e Relatórios.

Cor nunca é o único indicador de significado.

---

# 6. Padrão de listas operacionais

Esta seção é normativa para o App.

A organização visual foi revista tomando como referência o modelo mental observado na documentação do Astrea para Processos/Casos e tarefas/Agenda: informação principal em destaque, contexto logo abaixo, filtros no topo, linha clicável e ações discretas. **Não copiar recursos do Astrea que não existam no Orvya.**

Não introduzir por essa referência:

- etiquetas;
- prioridade;
- estrela de importante;
- listas pessoais de tarefas;
- Kanban;
- privacidade por Processo;
- ações em lote inexistentes;
- qualquer outra regra funcional não definida neste documento.

A referência é de **composição e densidade**, não de feature parity.

## 6.1 Lista operacional x tabela

Use **`ListView` / lista de leitura** quando cada item for um objeto que a pessoa reconhece por título + contexto.

Use **`TableView`** quando o objetivo principal for comparar valores entre colunas.

### Lista operacional obrigatória

- Processos;
- Agenda na visão Lista;
- Minhas atividades da Área de trabalho.

### Lista operacional preferida

Também preferir lista para:

- Pessoas;
- Publicações;
- Documentos;
- Notificações;
- resultados de Pesquisa;
- relações curtas dentro de fichas.

Tabela continua adequada para:

- Financeiro quando houver comparação numérica;
- Relatórios;
- extratos;
- grades administrativas do Admin;
- catálogos técnicos;
- auditoria e migrations.

## 6.2 Anatomia de um item operacional

Um item deve possuir no máximo três níveis de leitura:

```text
[Título / identificação principal]                         [estado/ação]
[Contexto principal]
[metadado · metadado · metadado]
```

Regras:

- sem cabeçalho de colunas;
- sem linhas verticais de grade;
- sem transformar cada metadado em coluna fixa;
- altura natural;
- separador discreto entre itens ou tratamento visual nativo do `ListView`;
- item inteiro navegável;
- ação interativa interna não dispara a navegação;
- foco e seleção seguem Spectrum;
- estado de hover é discreto;
- nenhuma sombra pesada por item;
- não criar um Card visual independente para cada linha de uma lista longa.

`Card` fica para objetos isolados, resumo ou composição em que o próprio Spectrum recomende.

## 6.3 Ações e seleção

Ações recorrentes e inequívocas podem aparecer como ícone.

Ações secundárias ficam em `ActionMenu`.

Seleção múltipla só aparece se a tela possuir uma ação coletiva real.

Não adicionar checkbox apenas por semelhança com outro produto.

Quando seleção múltipla existir, usar suporte de seleção do `ListView`/Spectrum e uma barra de ações apropriada.

## 6.4 Responsividade

Em largura estreita:

```text
Título                         ação
Contexto
metadado
metadado
```

Os metadados podem quebrar linha. Não virar tabela rolável para preservar colunas inexistentes.

## 6.5 Ferramentas da lista

Acima da lista:

```text
[Pesquisa........................] [filtro principal] [Mais filtros] [paginação]
```

Filtros principais podem ficar visíveis. Filtros secundários ficam em `Mais filtros`.

Filtros ativos devem ser perceptíveis e removíveis sem abrir novamente o formulário quando o Spectrum oferecer padrão apropriado.

---

# 7. Configuração

`.env.example` contém apenas nomes de variáveis.

```text
DATABASE_URL=
APP_BASE_URL=https://app.orvya.net
ADMIN_BASE_URL=https://admin.orvya.net
SESSION_SECRET=
ENCRYPTION_KEY=
SMTP_HOST=
SMTP_PORT=
SMTP_USER=
SMTP_PASSWORD=
SMTP_FROM=
S3_ENDPOINT=
S3_REGION=
S3_BUCKET=
S3_ACCESS_KEY=
S3_SECRET_KEY=
CNJ_BASE_URL=
CNJ_TOKEN=
OPS_TOKEN=
```

A aplicação deve iniciar sem integrações externas configuradas, exceto quando a operação solicitada depender delas.

---

# 8. Segurança, sessão e autoridade

## 8.1 Sessão

Sessão opaca controlada pelo servidor:

- segredo aleatório criptográfico com pelo menos 256 bits;
- somente derivação é persistida;
- cookie `HttpOnly`;
- `Secure` em produção;
- host-only;
- App e Admin nunca compartilham cookie;
- `SameSite=Lax` ou mais restritivo quando compatível;
- 30 minutos de inatividade;
- 8 horas de duração absoluta.

Escopos:

- App;
- Admin;
- acesso assistido no App pertencente ao Administrador da Plataforma real.

## 8.2 CSRF

Mutações autenticadas exigem:

```text
X-Orvya-CSRF
```

Token somente na memória da aplicação.

Não usar `localStorage`, `sessionStorage` ou IndexedDB para sessão/credenciais.

## 8.3 Correlação

Toda resposta da API possui:

```text
X-Orvya-Operation-Id
```

## 8.4 Senhas

- Argon2id;
- nunca logar senha ou token;
- recuperação por token de uso único;
- pedido de recuperação não revela se e-mail existe.

## 8.5 Autoridade central

Uma única camada de autorização decide, a cada requisição:

- identidade;
- tenant;
- estado da conta;
- estado do usuário;
- Administrador do Sistema;
- permissões granulares;
- recurso do Plano;
- limite aplicável;
- alcance do objeto.

Frontend apenas projeta capacidades. Segurança real é do servidor.

## 8.6 Multi-tenant

- tenant vem da sessão;
- App não aceita `account_id` do cliente como autoridade;
- toda consulta aplica tenant;
- relação entre tenants é recusada;
- ID de outro escritório não vaza existência;
- Pesquisa, Relatórios, arquivos e histórico obedecem à mesma fronteira.

## 8.7 Acesso assistido

`Acessar escritório` no Admin cria contexto temporário próprio no host do App.

- não cria usuário local;
- não consome vaga;
- autoria é do Administrador da Plataforma;
- interface mostra faixa clara de acesso assistido;
- há ação para retornar ao Admin;
- ações entram no histórico com ator real.

---

# 9. Contrato HTTP canônico

REST JSON sob `/api/v1`.

Nomes funcionais das famílias de rotas permanecem em português quando já são canônicos no Orvya.

## 9.1 Coleções

Parâmetros comuns:

```text
q
sort
direction
page
page_size
+ filtros tipados do domínio
```

Regras:

- `page` começa em 1;
- `page_size`: 25, 50 ou 100;
- padrão 25;
- `q` até 200 caracteres;
- ordenação estável com desempate por ID;
- valor inválido é erro de campo.

Envelope:

```json
{
  "items": [],
  "total": 0,
  "page": 1,
  "page_size": 25,
  "as_of": "2026-09-15T12:00:00Z"
}
```

## 9.2 Erros

```json
{
  "erro": {
    "code": "codigo_estavel",
    "mensagem": "Mensagem compreensível.",
    "field": "campo_opcional",
    "operation_id": "identificador",
    "retryable": false
  }
}
```

Nunca serializar traceback, segredo, token ou conteúdo de outro tenant.

Status principais:

- `400` entrada inválida;
- `401` sem sessão;
- `403` sem autoridade;
- `404` ausente ou fora do alcance;
- `409` conflito de revisão;
- `422` regra de domínio;
- `429` limite técnico;
- `503` dependência necessária indisponível.

## 9.3 Revisão otimista

Registros editáveis importantes possuem `revision`.

Mutação envia `expected_revision`.

Conflito retorna `409`; frontend oferece recarregar/revisar e nunca sobrescreve silenciosamente.

## 9.4 Idempotência

Comandos capazes de duplicar efeito por repetição de rede usam chave de operação reaproveitada na mesma tentativa deliberada.

Aplicar especialmente ao Financeiro e efeitos externos.

## 9.5 Dinheiro

Dinheiro viaja como string decimal.

```json
{"principal":"1250.00","open":"500.00"}
```

Nunca `float`.

## 9.6 Famílias de rotas

```text
/api/v1/auth/*
/api/v1/admin/auth/*
/api/v1/escritorio/*
/api/v1/pessoas/*
/api/v1/processos/*
/api/v1/processos/buscas/*
/api/v1/atividades/*
/api/v1/publicacoes/*
/api/v1/arquivos/*
/api/v1/documentos/*
/api/v1/modelos/*
/api/v1/financeiro/*
/api/v1/painel/*
/api/v1/alertas/*
/api/v1/pesquisa/*
/api/v1/relatorios/*
/api/v1/admin/gestao/*
/api/v1/admin/integracoes/*
/api/v1/admin/operacao/*
/api/v1/saude
/api/v1/saude/pronto
/api/v1/saude/dependencias
```

Não criar endpoint para cada pequena composição visual.

---

# 10. Modelo de dados mínimo

UUID como identificador, timestamps timezone-aware para instantes e `DATE` para datas civis.

## 10.1 Globais

- Planos;
- recursos e limites de Plano;
- Administradores da Plataforma;
- catálogos iniciais;
- catálogos referenciais;
- variáveis de Documentos;
- configurações de integração;
- histórico da Plataforma;
- execuções operacionais.

## 10.2 Por escritório

- contas;
- usuários;
- permissões;
- convites;
- sessões;
- tokens de confirmação/recuperação;
- Pessoas, contatos, endereços, identificações e vínculos;
- Processos, partes, responsáveis e monitoramento;
- buscas processuais;
- Atividades e catálogos de Atividade;
- Publicações;
- arquivos;
- Documentos, vínculos documentais e Modelos;
- contas financeiras, categorias, centros, formas;
- Lançamentos, baixas, transferências, conciliações;
- Notificações e preferências;
- catálogos da conta;
- fatos de histórico;
- definições salvas de Relatórios quando utilizadas.

## 10.3 Regras transversais

- dado tenant-scoped possui `account_id` direto ou relação inequívoca;
- dinheiro usa `NUMERIC`;
- histórico append-only;
- data civil não vira meia-noite artificial UTC;
- `Não informado` não é persistido;
- relação não duplica entidade;
- excluir relação não exclui automaticamente registro relacionado.

---

# 11. Planos e Teste Grátis

Toda conta possui Plano.

## 11.1 Limites

- usuários;
- Processos monitorados;
- armazenamento.

Modos:

- limitado;
- ilimitado;
- pendente.

Zero é limite válido.

## 11.2 Recursos

No mínimo:

- núcleo;
- Publicações;
- Documentos;
- Modelos;
- Financeiro;
- Relatórios.

## 11.3 Teste Grátis

- Plano estrutural permanente;
- 7 dias exatos desde a criação;
- padrão do autocadastro;
- ao expirar, suspender se conta continuar nele;
- mudança para outro Plano encerra efeito da expiração;
- retorno posterior não reinicia sete dias.

Redução de Plano não apaga dados.

---

# 12. Gramática comum de UX

## 12.1 Ver é página; agir é Dialog

| Intenção | Superfície |
|---|---|
| visualizar registro principal | página/ficha |
| criar/editar/vincular | Dialog |
| reagendar/redesignar | Dialog |
| ação secundária | ActionMenu/Menu |
| ação crítica | confirmação auditável |
| objeto operacional em coleção | ListView/lista de leitura |
| comparação tabular | TableView |
| histórico | seção/aba/timeline |

Não usar drawer lateral para ficha ou formulário.

## 12.2 Página

- largura útil máxima aproximada de 1440 px;
- centralizada;
- gutters responsivos;
- `min-width: 0` nas regiões flexíveis;
- formulários controlam a própria largura;
- 320 px não produz overflow da página inteira.

## 12.3 Blocos de dados

Não criar Card por campo.

```text
Bloco
  seção
    rótulo | valor
    rótulo | valor
  divisor
  seção
    ...
```

## 12.4 Consultas e filtros

- pesquisa interna automática após 300 ms;
- Enter antecipa;
- resposta antiga não substitui nova;
- mudar filtro/termo volta à página 1;
- `Limpar filtros` restaura padrão e mantém tamanho;
- `0 a 0 de 0` somente com zero confirmado;
- durante atualização manter conteúdo anterior inerte quando seguro.

## 12.5 Seleção assistida

Relações extensas usam `ComboBox` remoto:

- 2 caracteres;
- 300 ms;
- até aproximadamente 10 sugestões;
- identificação + contexto;
- nunca carregar milhares de itens no browser.

## 12.6 Ações críticas

Dialog de confirmação:

```text
Título
Registro afetado
Consequência
Justificativa
[Cancelar] [Confirmar]
```

Justificativa de 5 a 500 caracteres quando exigida.

Aplicar ao menos a:

- concluir/cancelar/reabrir Atividade;
- excluir registros principais;
- alterar permissões;
- suspender/reativar usuário ou conta;
- ações administrativas destrutivas;
- desconexões externas relevantes.

Edição comum, reagendamento e redesignação não exigem justificativa só por serem edições.

---

# 13. Cabeçalho do App

O nome do escritório **não aparece no cabeçalho**.

Desktop:

```text
┌──────────────────────────────────────────────────────────────────────────────┐
│ [ORVYA]                  [       PESQUISA GLOBAL       ]      [+] [🔔] [◉] │
└──────────────────────────────────────────────────────────────────────────────┘
```

Estrutura:

```text
esquerda = 1fr
centro   = largura controlada da pesquisa
direita  = 1fr
```

Pesquisa Global fica geometricamente centralizada independentemente dos lados.

## 13.1 Botões do cabeçalho

Todos os botões são somente ícones:

- Menu no mobile;
- `+` global;
- Notificações;
- conta/perfil via Avatar ou ícone.

Não mostrar texto `Adicionar`, `Notificações`, `Conta`, `Menu` ou `Sessão` ao lado.

Cada ação precisa de:

- `aria-label`;
- `Tooltip` quando útil;
- foco Spectrum;
- alvo de toque adequado;
- estado aberto/selecionado perceptível.

## 13.2 Pesquisa Global

`SearchField` Spectrum:

- mínimo 2 caracteres;
- 300 ms;
- até 5 resultados por grupo na visão rápida;
- setas navegam;
- Enter abre;
- Esc fecha resultados;
- `Ver todos os resultados` abre `/pesquisa`.

Em tela estreita pode ocupar uma segunda linha do cabeçalho, mantendo-se na própria casca.

## 13.3 Conta

Menu do Avatar:

```text
Meu perfil
Configurações do escritório
Sair
```

O nome do escritório permanece disponível apenas onde for conteúdo real, como Configurações ou acesso assistido.

---

# 14. Navegação do App

Use `SideNav` Spectrum.

```text
Área de trabalho
Agenda
Pessoas
Processos
Publicações
Documentos
Financeiro
Relatórios
```

Subnavegação:

```text
Processos
  Processos cadastrados
  Buscas processuais

Documentos
  Biblioteca

Financeiro
  Lançamentos
  Movimentações
  Fluxo de caixa
  Conciliação bancária
  Configurações

Relatórios
  Central
  Modelos e relatórios salvos
```

Navegação filtrada pelas capacidades do servidor.

Mobile:

- SideNav sobreposto;
- botão Menu somente ícone;
- Esc/cortina fecham;
- foco retorna ao acionador.

## 14.1 Rotas canônicas

```text
/dashboard
/agenda
/agenda/:id
/pessoas
/pessoas/:id
/processos
/processos/:id
/processos/buscas
/publicacoes
/publicacoes/:id
/documentos/biblioteca
/documentos/biblioteca/:id
/financeiro/lancamentos
/financeiro/lancamentos/:id
/financeiro/movimentacoes
/financeiro/fluxo
/financeiro/conciliacao
/financeiro/configuracoes
/relatorios
/relatorios/modelos
/pesquisa
/alertas
/conta/perfil
/conta/configuracoes
/conta/configuracoes/usuarios
/conta/configuracoes/agenda
/conta/configuracoes/catalogos
/conta/configuracoes/modelos
/conta/configuracoes/plano
/conta/configuracoes/acoes-criticas
```

Ao abrir ficha preservar termo, filtros, página, tamanho, ordenação, visão, data e posição aproximada de rolagem.

---

# 15. F0 — Fundação

Implementar:

- monorepo;
- Docker Compose;
- PostgreSQL;
- configuração;
- migration inicial;
- erros comuns;
- paginação;
- correlação;
- Spectrum Provider;
- cliente HTTP;
- roteamento App/Admin;
- health checks.

API mínima:

```text
GET /api/v1/saude
GET /api/v1/saude/pronto
GET /api/v1/saude/dependencias
```

`/saude` mede somente vivacidade.

`/saude/pronto` depende do banco e revisão esperada do schema.

Integração opcional indisponível não derruba readiness geral.

### Pronto quando

- migration sobe em banco vazio;
- API inicia;
- App e Admin vazios iniciam;
- Spectrum renderiza;
- typecheck passa.

---

# 16. F1 — Conta, acesso, Plano e permissões

## 16.1 Conta

Estados:

- Ativa;
- Suspensa.

Campos principais:

- nome;
- CPF/CNPJ opcional;
- telefone;
- e-mail institucional;
- fuso;
- logotipo;
- Plano;
- criação;
- expiração do Teste Grátis.

## 16.2 Usuário

Estados:

- Ativo;
- Suspenso.

Exclusão é ação, não terceiro estado.

Campos:

- nome;
- e-mail;
- hash de senha;
- Administrador do Sistema;
- permissões;
- foto opcional;
- preferências;
- revisão.

E-mail de usuário operacional é único enquanto cadastro existir.

## 16.3 Administrador do Sistema

Acesso integral ao escritório dentro do Plano.

Permissões individuais continuam guardadas e voltam a valer se a condição for removida.

Não criar cargos fixos como fonte de autoridade.

## 16.4 Cadastro

Rota visível `/cadastro`.

Campos:

- nome;
- e-mail;
- senha;
- nome do escritório.

Fluxo:

1. criar conta;
2. criar usuário inicial;
3. marcar Administrador do Sistema;
4. associar Teste Grátis;
5. enviar confirmação de e-mail;
6. confirmar antes do acesso operacional.

## 16.5 Login

```text
[Logo]
Entrar no Orvya
E-mail
Senha
[Entrar]
Esqueci minha senha
Criar escritório
```

Somente e-mail + senha.

## 16.6 Convites

Administrador cria usuário com nome, e-mail, permissões e condição administrativa opcional.

Destinatário define senha. Convite pendente pode ser reenviado.

## 16.7 Exclusão de usuário

Se houver responsabilidades:

- escolher usuário ativo da mesma conta;
- reatribuir Atividades Pendentes, inclusive atrasadas;
- reatribuir Processos em que seja responsável principal;
- fatos históricos preservam autor original.

## 16.8 Meu perfil `/conta/perfil`

```text
Identificação | Notificações | Segurança
```

Identificação:

- nome;
- e-mail;
- foto;
- dados pessoais existentes.

Foto:

- PNG/JPEG/WebP;
- até 2 MB;
- armazenamento central;
- sem storage configurado, mostrar indisponibilidade real.

Notificações: preferências individuais.

Segurança:

- alterar senha;
- encerrar sessão;
- informações de segurança existentes.

## 16.9 Configurações do escritório

```text
Escritório
Equipe e acesso
Agenda
Catálogos
Modelos de documentos
Plano e utilização
Ações críticas
```

### Escritório

Read-first; Editar abre Dialog.

### Equipe e acesso

Aqui **TableView é apropriada**, pois há comparação administrativa de usuários.

Campos principais:

```text
Usuário | Status | Administrador do Sistema | Convite/acesso
```

### Agenda

Somente fuso compartilhado e acesso ao catálogo de Atividades.

### Plano e utilização

- Plano atual;
- usuários usados/limite;
- monitorados usados/limite;
- armazenamento usado/limite;
- recursos habilitados.

### Pronto quando

- cadastro confirmado entra;
- usuário/conta suspensos não entram;
- sessão expira;
- permissões server-side funcionam;
- convite, Perfil e Configurações funcionam.

---

# 17. F2 — Pessoas

## 17.1 Entidade

Naturezas:

- Pessoa Física;
- Pessoa Jurídica;
- natureza ainda não identificada pode ser `null`.

Dados:

- nome/razão social;
- nome social/fantasia;
- CPF/CNPJ;
- nascimento/abertura;
- nacionalidade;
- estado civil;
- profissão;
- classificações;
- observações;
- contatos;
- endereços;
- identificações;
- vínculos entre Pessoas.

CPF/CNPJ duplicado no mesmo escritório orienta ao registro existente e não sobrescreve.

## 17.2 API

Família `/api/v1/pessoas`.

Tenant sempre da sessão.

## 17.3 Listagem `/pessoas`

Preferir lista operacional, não tabela, porque a Pessoa é reconhecida por identidade + contatos.

```text
[Pessoas]                                            [Adicionar pessoa]
[Pesquisar nome/documento/contato] [Natureza] [paginação]

Joana Silva                                         [Pessoa Física] [⋯]
CPF 000.000.000-00
joana@email.com · (45) 99999-9999 · atualizada em 15/09/2026
────────────────────────────────────────────────────────────────────
Empresa Exemplo Ltda                                [Pessoa Jurídica] [⋯]
CNPJ 00.000.000/0001-00
financeiro@exemplo.com · atualizada em 14/09/2026
```

A linha inteira abre a ficha.

## 17.4 Ficha `/pessoas/:id`

```text
[← Pessoas] Nome da Pessoa                     [Natureza] [Editar] [⋯]
            Pessoa Física/Jurídica · documento
[Resumo] [Processos] [Documentos] [Financeiro] [Histórico]
```

Resumo read-first com Identificação, Classificações, Observações, Contatos, Endereços, Identificações e Vínculos.

Criar/editar coleção abre Dialog.

Relações curtas dentro das abas podem usar listas compactas em vez de mini-tabelas quando houver contexto hierárquico.

Histórico usa timeline.

### Pronto quando

- CRUD;
- contatos/endereço/identificações/vínculos;
- principal;
- duplicidade;
- relações reais sem cópia.

---

# 18. F3 — Processos

## 18.1 Naturezas

- Judicial;
- Administrativo.

## 18.2 Judicial

Pode possuir:

- número CNJ;
- tribunal;
- grau;
- sistema;
- juízo;
- classe;
- assunto;
- valor da causa;
- distribuição;
- Situação;
- responsável principal;
- partes;
- monitoramento.

Cadastro manual não consulta fonte externa para autorizar salvamento.

## 18.3 Administrativo

Pode possuir:

- título;
- protocolo;
- tipo;
- órgão;
- início;
- valor de referência;
- Situação;
- responsável principal;
- envolvidos.

## 18.4 Partes

Polos:

- Ativo;
- Passivo;
- Terceiro interessado.

Parte aponta para Pessoa da mesma conta.

## 18.5 Monitoramento

- somente Judicial elegível;
- exige número CNJ válido;
- manual nasce sem monitoramento;
- falta de vaga não impede cadastro;
- desativação preserva Publicações;
- falha externa não altera sozinha o estado.

## 18.6 Buscas processuais

Família `/api/v1/processos/buscas`.

Modos:

- número CNJ;
- OAB + UF + período quando aplicável.

Busca externa é comando explícito.

Ao concluir:

- mostrar candidatos;
- marcar já cadastrados;
- permitir seleção do que adicionar;
- nunca cadastrar tudo automaticamente.

## 18.7 Listagem `/processos`

**Usar `ListView`/lista operacional. Não usar `TableView` para a listagem principal de Processos.**

A tela deve lembrar uma lista jurídica de trabalho, não uma grade de banco de dados.

Topo:

```text
[Processos]                                              [Novo processo]
[Pesquisar número, partes ou título.................................]
[Natureza] [Monitoramento] [Situação] [Mais filtros]       [paginação]
```

Item Judicial:

```text
Parte 1 x Parte 2                                      [Situação] [⋯]
0001234-56.2026.8.16.0001 · Judicial · TJPR
Responsável: Maria Souza · Monitorado · atualizado em 15/09/2026
────────────────────────────────────────────────────────────────────
```

Item Administrativo:

```text
Título do procedimento                                  [Situação] [⋯]
Protocolo 12345 · Administrativo · Órgão X
Responsável: João Silva · atualizado em 14/09/2026
────────────────────────────────────────────────────────────────────
```

Hierarquia obrigatória:

1. **título reconhecível:** `Parte 1 x Parte 2` ou título administrativo;
2. **identificação jurídica:** CNJ/protocolo + natureza + tribunal/órgão;
3. **contexto operacional:** responsável + monitoramento + atualização.

Regras:

- linha inteira abre ficha;
- `ActionMenu` não abre ficha;
- Situação pode aparecer como `StatusLight`/Badge discreto;
- monitoramento é texto ou status discreto, não coluna;
- não usar cabeçalho `Processo | Situação | Responsável | Atualização`;
- não alinhar cada metadado como se fosse célula;
- sem nomes de partes se usuário não tiver leitura correspondente;
- seleção múltipla somente se uma ação coletiva real vier a existir no Orvya.

## 18.8 Ficha `/processos/:id`

```text
[← Processos] Parte 1 x Parte 2                 [Monitoramento] [+] [Editar] [⋯]
              identificação · natureza · Situação · Tribunal
[Resumo] [Atividades] [Publicações] [Documentos] [Financeiro] [Histórico]
```

`+` contextual reutiliza os mesmos Dialogs:

- Nova atividade;
- Vincular Pessoa;
- Adicionar Documento;
- Novo lançamento.

Menu:

- Gerar documento;
- ativar/desativar monitoramento;
- excluir.

### Resumo

```text
┌ Próximas atividades, até 5 ┐  ┌ Dados do processo ┐
└────────────────────────────┘  └────────────────────┘

PARTES E RESPONSÁVEIS
  listas de leitura

ÚLTIMOS EVENTOS
  timeline curta
```

Em largura estreita empilhar.

A aba Atividades usa o mesmo padrão visual de lista de Atividades da Agenda, já filtrado pelo Processo.

Financeiro do Processo é somente resumo do Processo, sem segundo motor financeiro.

### Pronto quando

- Judicial/Administrativo;
- partes/responsáveis;
- título por partes;
- monitoramento;
- buscas externas separadas do cadastro manual;
- lista principal sem grade tabular;
- ficha agrega relações sem duplicar dados.

---

# 19. F4 — Atividades, Agenda e Área de trabalho

## 19.1 Atividade

Modalidades:

- Audiência;
- Prazo;
- Tarefa;
- Evento.

Estados persistidos:

- Pendente;
- Concluída;
- Cancelada.

`Atrasada` é condição derivada.

Pendentes inclui atrasadas.

Campos principais:

- item catalogado/título;
- modalidade;
- responsável;
- data;
- horário opcional;
- descrição;
- Processo opcional conforme origem;
- origem;
- cor do tipo;
- revisão;
- histórico.

Origem:

- Agenda;
- Processo;
- tratamento de Publicação.

Criada no Processo herda Processo.

Criada de Publicação herda obrigatoriamente o Processo da Publicação.

## 19.2 API

Família `/api/v1/atividades`.

Servidor calcula:

- atraso;
- marco de atraso;
- contagens;
- janela de calendário;
- cor do tipo;
- transições válidas.

## 19.3 Agenda `/agenda`

Topo:

```text
[Agenda e Atividades]                                   [Nova atividade]
[Lista] [Dia] [Semana] [Mês]
[‹] período [Hoje] [›]
[Pesquisar atividade/processo] [Modalidade] [Recorte] [Responsável] [Mais filtros]
Pendentes N · Atrasadas N · Sem data N · Concluídas N
```

Visão inicial: Lista.

Recortes:

- Pendentes;
- Atrasadas;
- Próximos 7 dias;
- Sem data;
- Concluídas;
- Canceladas;
- Todas.

### 19.3.1 Lista

**Usar `ListView`. Não usar tabela de colunas para a Agenda em modo Lista.**

Agrupar por data quando houver data:

```text
VENCIDAS

● Protocolar contestação                                   [Concluir] [⋯]
  Silva x Empresa Exemplo
  Prazo · 14/09/2026 18:00 · Maria Souza
────────────────────────────────────────────────────────────────────

HOJE · 15 DE SETEMBRO

● Reunião de alinhamento                                   [Concluir] [⋯]
  Processo 0001234-56.2026.8.16.0001
  Evento · 14:30–15:30 · João Pereira
────────────────────────────────────────────────────────────────────

● Revisar documentos                                       [Concluir] [⋯]
  Sem Processo
  Tarefa · sem horário · Ana Costa
```

Anatomia:

1. marcador visual do tipo;
2. título da Atividade;
3. Processo/contexto;
4. modalidade + data/horário + responsável;
5. ação rápida aplicável;
6. menu secundário.

Não exibir cabeçalho:

```text
Atividade | Modalidade | Quando | Responsável | Estado | Ações
```

A linha inteira abre a ficha.

Ações conforme estado/capacidade:

- concluir/reabrir;
- reagendar;
- redesignar;
- editar;
- cancelar;
- excluir.

A ação mais frequente pode aparecer diretamente; as demais ficam no menu.

### 19.3.2 Dia

- largura inteira;
- faixa Sem horário;
- grade temporal;
- criação em horário escolhido;
- arraste para reagendar;
- comando Reagendar sempre disponível.

### 19.3.3 Semana

- sete dias;
- faixa Sem horário;
- linha de horário atual;
- colisões em raias;
- cabeçalho do dia abre Dia.

### 19.3.4 Mês

- sete colunas;
- poucos itens por dia;
- `+ N` abre Dia;
- clicar dia abre Dia;
- sem painel lateral.

## 19.4 Ficha `/agenda/:id`

```text
[← Agenda] ● Título                     [Estado] [ações] [⋯]
           Modalidade · Processo · Quando · Responsável

INFORMAÇÕES DA ATIVIDADE
  Descrição
  divisor
  Dados
  divisor
  Processo
  divisor
  Histórico
```

Editar, Reagendar e Redesignar usam Dialog.

## 19.5 Área de trabalho `/dashboard`

A Área de trabalho é mesa diária, não painel de KPI.

Desktop:

```text
[Área de trabalho]
[Aviso do Teste Grátis, quando aplicável]

┌──────────────────────────────────────────────┬─────────────────────────┐
│ MINHAS ATIVIDADES                            │ CALENDÁRIO              │
│ [Hoje] [Esta semana] [Este mês] [Filtros]   │       ‹ mês ano ›       │
│                                              │                         │
│ VENCIDAS                                     │                         │
│ ● Atividade                                  │ RESUMO DO ESCRITÓRIO    │
│   contexto                       [Concluir]  │ Processos cadastrados N │
│   data/hora · modalidade                     │ Processos monitorados N │
│                                              │ Pessoas cadastradas N   │
│ HOJE / AMANHÃ / DATA                         │ Atividades pendentes N  │
│ ...                                          │                         │
│ + N atividades                              │                         │
│ Ver todas na Agenda                         │                         │
└──────────────────────────────────────────────┴─────────────────────────┘
```

Largura aproximada 67/33; abaixo de 960 px empilhar com Minhas atividades primeiro.

### Minhas atividades

Usar o **mesmo componente base de item de Atividade da Agenda**, com variante compacta.

- somente Atividades do usuário atual;
- somente Pendentes;
- Hoje padrão;
- Hoje/Esta semana/Este mês mutuamente exclusivos;
- Mais filtros: Modalidade e Sem data;
- dia do calendário substitui período;
- `Voltar para hoje` restaura Hoje;
- vencidas primeiro;
- até 12 itens;
- excedente `+ N atividades`;
- sem paginação;
- linha abre Atividade;
- única ação rápida: Concluir.

Vencida difere **somente** pela data/hora em cor negativa Spectrum.

Não usar selo, fundo ou borda especial para atraso.

### Calendário compacto

- mês;
- segunda → domingo;
- cabeçalho apenas `‹ MÊS ANO ›`;
- sem texto de Atividades dentro dos dias;
- sem horários/arraste;
- um dia com Atividade Pendente recebe uma marca discreta;
- quantidade não muda a marca;
- trocar mês não muda lista;
- clicar dia filtra lista.

### Resumo do escritório

Exatamente:

1. Processos cadastrados;
2. Processos monitorados;
3. Pessoas cadastradas;
4. Atividades pendentes neste mês.

Quatro linhas de texto, sem cards individuais, gráficos, ícones decorativos ou números gigantes.

### Pronto quando

- CRUD/transições;
- atraso calculado;
- Lista/Dia/Semana/Mês;
- Lista é realmente uma lista, não tabela;
- retorno de calendário preserva contexto;
- Área de trabalho segue mesa diária.

---

# 20. F5 — Publicações, Pesquisa e Notificações

## 20.1 Publicações

Publicação nasce somente da integração judicial autorizada.

Condições:

- Nova;
- Tratada.

`Tratada` é operacional e não declara efeito jurídico.

Conteúdo ausente e falha são estados diferentes.

Conteúdo é apresentado como texto seguro.

Ações:

- Criar providência;
- Concluir;
- Concluir e abrir a próxima;
- Descartar.

Criar providência cria Atividade real.

Concluir preserva a Publicação.

Descartar remove a Publicação sem apagar Atividades independentes.

### Listagem `/publicacoes`

Preferir lista operacional:

```text
[Publicações]
[Novas N] [Tratadas N] [Total N]
[Pesquisar] [Condição] [paginação]

Tipo da publicação                                      [Nova] [⋯]
Processo 0001234-56.2026.8.16.0001 · TJPR
Fonte 14/09/2026 · recebida 15/09/2026
Trecho curto do conteúdo recebido…
────────────────────────────────────────────────────────────────────
```

Linha abre Publicação, não Processo.

### Ficha `/publicacoes/:id`

```text
[Anterior]                         12 de 48                         [Próxima]

[← Publicações] Publicação    [Condição] [Criar providência] [Concluir] [⋯]
                Processo · Tipo · Tribunal · recebida em...

CONTEÚDO RECEBIDO
PROCESSO
PROVIDÊNCIAS
```

`Concluir e abrir a próxima` só navega após sucesso e preserva recorte original.

## 20.2 Pesquisa Global

Família `/api/v1/pesquisa`.

Grupos conforme capacidade:

- Pessoas;
- Processos;
- Atividades;
- Publicações;
- Documentos;
- Financeiro;
- Relatórios salvos.

- mínimo 2 caracteres;
- máximo 200;
- grupo vedado não existe na resposta;
- somente consultiva;
- resultado abre destino canônico.

Página `/pesquisa` apresenta resultados como listas agrupadas, não como tabela universal.

## 20.3 Notificações

Pertence ao destinatário.

Tipos iniciais:

- nova Publicação;
- Atividade atribuída;
- Prazo próximo/vencido;
- Audiência próxima;
- aviso interno.

`Lido` não significa resolvido.

Tela `/alertas` usa lista de cards/itens Spectrum com mensagem, contexto, instante e destino.

### Pronto quando

- Publicações deduplicam;
- sequência funciona;
- Pesquisa não vaza grupo proibido;
- Notificações são por destinatário.

---

# 21. F6 — Arquivos, Documentos e Modelos

## 21.1 Arquivos

Fluxo central:

1. cliente valida por conveniência;
2. servidor valida cota e reserva;
3. bytes são enviados;
4. servidor calcula tamanho/SHA-256;
5. confirma;
6. somente confirmado pode virar vínculo de negócio.

Persistir tenant, finalidade, chave física, nome original, tamanho, MIME, SHA-256 e estado.

Chave física usa tenant + UUID.

Download autenticado.

## 21.2 Documento

- nome;
- Tipo de Documento;
- descrição;
- arquivo vigente;
- revisão;
- vínculos.

Pode vincular Pessoa, Processo, Atividade, Publicação e Lançamento.

Vincular não copia bytes. Desvincular não exclui Documento.

## 21.3 Exclusão

Se remoção física falhar:

- estado de exclusão pendente;
- bloquear edição/download/vínculo/substituição;
- continuar contando espaço;
- ação `Retomar exclusão`.

## 21.4 Biblioteca `/documentos/biblioteca`

Preferir lista operacional:

```text
[Documentos]                       [Gerenciar modelos] [Incluir Documento]
[Pesquisar] [Tipo de Documento] [paginação]

Nome do documento                                       [Tipo] [⋯]
arquivo-original.pdf · 1,8 MB
Cadastrado em 15/09/2026 · Processo/Pessoa quando houver
────────────────────────────────────────────────────────────────────
```

## 21.5 Inclusão

Dialog único:

1. selecionar arquivo;
2. transferir/confirmar;
3. nome;
4. tipo;
5. descrição;
6. vínculo opcional;
7. cadastrar.

## 21.6 Ficha

```text
[← Documentos] Nome                     [Visualizar] [Baixar] [Substituir] [⋯]
               Tipo · arquivo

DOCUMENTO
  Pré-visualização
  Dados
  Vínculos
  Arquivo

HISTÓRICO
```

PDF/imagem com preview; outros formatos oferecem download.

## 21.7 Modelos DOCX

Rota `/conta/configuracoes/modelos`.

Contextos:

- Pessoa;
- Processo.

Operações:

- listar;
- cadastrar;
- editar;
- substituir base;
- validar;
- excluir;
- consultar variáveis.

Geração começa em Pessoa ou Processo.

Sintaxe:

```text
{{contexto.campo}}
{{aberto.nome}}
```

Fluxo resolve variáveis, solicita abertas, gera DOCX, converte PDF se solicitado e salva na Biblioteca somente por ação explícita.

### Pronto quando

- upload/cota;
- Biblioteca;
- vínculos;
- substituição;
- exclusão retomável;
- geração válida;
- Modelo inválido não gera.

---

# 22. F7 — Financeiro

## 22.1 Lançamento

Naturezas:

- Receita;
- Despesa.

Relações opcionais:

- Pessoa;
- Processo;
- Documento.

Situações calculadas:

- Em aberto;
- Parcialmente liquidado;
- Liquidado;
- Cancelado.

`Vencido` é condição derivada.

## 22.2 Regras

- baixa reduz aberto;
- estorno recompõe;
- cancelamento preserva histórico;
- transferência gera movimentos relacionados, não Receita/Despesa comum;
- saldos dependem de abertura + movimentos;
- saldo insuficientemente determinado é `Indeterminado`;
- servidor calcula totais.

Orvya registra fatos financeiros declarados, não executa operação bancária externa.

## 22.3 Navegação

```text
Lançamentos | Movimentações | Fluxo de caixa | Conciliação bancária | Configurações
```

## 22.4 Lançamentos

Aqui `TableView` é adequado, pois valores precisam ser comparados por coluna.

```text
Lançamento | Natureza | Principal | Em aberto | Vencimento | Situação
```

Valores monetários alinhados à direita.

Filtros e totais representam o conjunto inteiro filtrado.

## 22.5 Ficha

Read-first com dados, relações, parcelas, baixas, Documentos e histórico.

## 22.6 Movimentações

Extrato tabular com período, origem, forma e saldo corrido somente quando calculável.

## 22.7 Fluxo

Entradas/saídas temporais e totais do servidor.

## 22.8 Conciliação

Tela própria sobre os mesmos fatos.

## 22.9 Configurações

- contas bancárias/caixas;
- categorias;
- centros de custo;
- formas de pagamento.

### Pronto quando

- decimal exato;
- baixa/estorno/cancelamento;
- idempotência;
- transferência;
- saldos/totais reproduzíveis.

---

# 23. F8 — Relatórios

Relatório é projeção dos dados reais.

Fontes:

- Atividades;
- Publicações;
- Processos;
- Pessoas;
- Documentos;
- Financeiro;
- combinações autorizadas.

Definição pode declarar período, filtros, colunas, ordenação, agrupamento e totais.

## 23.1 Tela `/relatorios`

```text
[Relatórios]
[Relatório ▾] [Executar] [Exportar ▾]

[formulário da definição]
[parâmetros executados]
[tabela paginada]
[totais]
```

Aqui `TableView` é apropriado.

Resultado permanece ligado aos parâmetros executados; alterações ainda não aplicadas geram aviso.

Exportações PDF/XLSX usam o mesmo recorte.

### Pronto quando

- definição gera formulário;
- servidor aplica filtros/colunas/ordem;
- tabela, total, paginação e exportação usam mesma referência.

---

# 24. F9 — Administração da Plataforma

Admin é aplicação própria em `admin.orvya.net`.

Administrador da Plataforma é global, não pertence a escritório.

Sempre deve existir ao menos um ativo.

## 24.1 Cabeçalho

```text
[ORVYA · Administração da Plataforma › Página] [ PESQUISA ADMINISTRATIVA ] [◉]
```

Pesquisa centralizada geometricamente.

Botões do cabeçalho somente ícones.

## 24.2 Sidebar

```text
VISÃO GERAL
  Dashboard
PLATAFORMA
  Escritórios
  Usuários
  Planos
ACESSO
  Administradores
  Permissões
CADASTROS
  Catálogos Iniciais
  Catálogos Referenciais
  Variáveis de Documentos
INTEGRAÇÕES
  Integrações e conexões
  Domínios e endpoints
  APIs utilizadas
OPERAÇÃO
  Visão operacional
  Serviços
  Execuções
  Banco de dados
  Migrations
  Capacidade
  Operações e Limitações
AUDITORIA
  Histórico da Plataforma
  Conciliação Técnica
CONFIGURAÇÕES
  Configurações globais
```

Uma única casca.

## 24.3 Dashboard

Ordem:

1. Pendências administrativas;
2. Estado da plataforma;
3. Distribuição por Plano;
4. Atividade recente.

CPU/memória/disco ficam em Operação.

## 24.4 Escritórios

Admin continua podendo usar `TableView`, pois é gestão comparativa.

Ficha:

```text
[← Escritórios] Nome                   [Status] [Plano] [Acessar] [Editar] [⋯]
[Resumo] [Usuários] [Plano e utilização] [Histórico]
```

`Acessar` inicia acesso assistido.

## 24.5 Usuários globais

Somente metadados administrativos, sem conteúdo jurídico.

## 24.6 Planos

CRUD com nome, descrição, estrutural, recursos e limites.

Excluir Plano em uso exige destino.

## 24.7 Administradores

Adicionar, editar, suspender, reativar, excluir.

Não suspender/excluir último ativo.

## 24.8 Permissões

Registro técnico de capacidades em tabela administrativa.

## 24.9 Catálogos

- Iniciais;
- Referenciais;
- Variáveis de Documentos.

## 24.10 Integrações

Somente:

1. E-mail;
2. Armazenamento;
3. Comunica CNJ.

Ficha:

```text
Estado
Configuração
[Salvar]
[Testar]
[Ativar/Desativar]
Último diagnóstico
Último sucesso
Último erro
```

Salvar, Testar e Ativar são efeitos distintos.

Segredos nunca retornam completos.

### E-mail

Confirmação de cadastro, convite, recuperação e mensagens transacionais implementadas.

### Armazenamento

S3/compatível para Documentos, Modelos, logos, fotos e derivados explicitamente persistidos.

### Comunica CNJ

Busca por Processo/OAB, monitoramento e Publicações.

Uma rotina central processa monitoramentos elegíveis.

## 24.11 Operação

Visão operacional:

- API;
- worker;
- banco;
- storage;
- e-mail;
- Comunica CNJ;
- versão da aplicação;
- revisão do schema;
- execuções.

Comandos allowlisted, nunca shell arbitrário.

Migrations somente leitura no Admin; aplicação ocorre no deploy.

Capacidade mostra CPU, memória e disco.

## 24.12 Auditoria

TableView com Data/hora, Área, Ação, Autor, Alvo e Resultado.

Conciliação Técnica não vira editor genérico do banco.

### Pronto quando

- login separado;
- casca única;
- pesquisa;
- contas/usuários/Planos/admins;
- integrações reais;
- operação segura;
- acesso assistido;
- auditoria.

---

# 25. Worker

Um worker para toda instalação.

Responsabilidades:

- monitoramento judicial;
- recebimento/deduplicação de Publicações;
- expiração do Teste Grátis;
- envio de e-mail;
- limpeza de reservas abandonadas;
- conversões documentais demoradas;
- reconciliação temporal de Notificações;
- tarefas persistentes necessárias.

Tarefa possui ID, tipo, payload mínimo, estado, tentativas, próxima tentativa, erro sanitizado, timestamps e idempotência quando necessária.

Retries limitados.

---

# 26. Histórico funcional

Histórico do escritório e da Plataforma são separados.

Fato mínimo:

```text
id
account_id opcional
occurred_at
author_type
author_id
action
entity_type
entity_id
detail seguro
justification opcional
```

Não criar botão genérico `Adicionar histórico`.

Evento manual do caso é Atividade modalidade Evento.

---

# 27. Estados da interface

Toda consulta trata:

- carregando;
- vazio;
- erro;
- indisponível;
- pronto;
- atualizando com conteúdo anterior, quando seguro.

Regras:

- indisponível não é zero;
- horário ausente não vira `00:00`;
- saldo indeterminado não vira zero;
- sem permissão não vira lista vazia enganosa;
- recurso fora do Plano não vira erro técnico;
- acervo vazio e filtro sem resultado são mensagens distintas.

---

# 28. Acessibilidade

Preservar Spectrum 2:

- teclado completo;
- foco visível;
- labels reais;
- nomes acessíveis de botões de ícone;
- `aria-current`;
- foco contido em Dialog;
- retorno de foco ao fechar;
- contraste;
- toque;
- movimento reduzido;
- alto contraste;
- texto ampliado;
- listas e tabelas navegáveis;
- cor nunca como único sinal.

Não remover focus ring.

---

# 29. Deploy

Objetivo: instalação/atualização controlada em VPS Linux com Docker.

```text
1. validar .env
2. construir imagens
3. iniciar PostgreSQL
4. aguardar banco
5. alembic upgrade head
6. iniciar API
7. iniciar worker
8. iniciar ops
9. construir App/Admin
10. publicar assets
11. iniciar/recarregar Nginx
12. verificar /api/v1/saude
13. verificar /api/v1/saude/pronto
14. smoke dos dois hosts
```

Hosts:

```text
app.orvya.net
admin.orvya.net
```

Arquivos de usuário não ficam em diretório público do Nginx.

TLS válido com renovação automatizada pela infraestrutura.

---

# 30. Dados iniciais

Criar somente:

- identidade da instalação;
- primeiro Administrador da Plataforma por comando seguro;
- Plano estrutural de Teste Grátis;
- recursos padrão;
- catálogos mínimos necessários.

Não criar Pessoas, Processos, Atividades, Publicações ou Lançamentos fictícios.

Catálogos mínimos:

- Situações de Processo;
- Tipos de Audiência/Prazo/Tarefa/Evento;
- Formas de realização;
- Tipos de Documento;
- Tipos de contato;
- Finalidades de endereço;
- Tipos de identificação;
- Tipos de vínculo entre Pessoas;
- polos se não forem enum estrutural.

Financeiro não recebe categorias comerciais inventadas.

---

# 31. Estratégia de testes

Qualidade é obrigatória, mas a ordem deve ser econômica.

## Gate A — Fundação

- migration banco vazio;
- API inicia;
- typecheck;
- builds App/Admin;
- login mínimo.

## Gate B — Núcleo jurídico

Depois de Pessoas + Processos + Atividades:

- conta;
- Pessoa;
- Processo;
- Atividade;
- Agenda;
- isolamento simples entre duas contas.

## Gate C — Conteúdo

Depois de Publicações + Documentos:

- storage simulado/local;
- upload/download;
- geração DOCX;
- ingestão deduplicada.

## Gate D — Financeiro

- Receita/Despesa;
- baixa;
- estorno;
- transferência;
- idempotência;
- totais.

## Gate E — Admin

- login separado;
- escritório;
- Plano;
- integração;
- acesso assistido;
- último Administrador protegido.

## Gate F — Estabilização final

1. banco vazio;
2. migration;
3. typecheck;
4. builds;
5. testes de integração de alto valor;
6. stack completa;
7. dois tenants reais de teste;
8. isolamento;
9. jornada App;
10. jornada Admin;
11. responsividade 320/375/768/1440;
12. teclado/foco;
13. corrigir todos os defeitos;
14. repetir smoke integral.

Não perseguir cobertura percentual arbitrária.

---

# 32. Testes automatizados mínimos

Backend:

- login/expiração;
- CSRF;
- isolamento;
- permissão negada;
- conflito de revisão;
- duplicidade de Pessoa;
- Processo de outro tenant invisível;
- transições/atraso de Atividade;
- Publicação deduplicada;
- upload/cota;
- exclusão documental pendente;
- dinheiro decimal;
- idempotência financeira;
- Teste Grátis;
- último Administrador da Plataforma.

Frontend E2E inicial:

```text
App:
cadastro → confirmação → login
→ Área de trabalho
→ Pessoas
→ Processos em lista
→ Processo
→ Agenda em lista
→ Atividade
→ Documento
→ Financeiro
→ Relatório
→ Configurações

Admin:
login → Dashboard → Escritório → Plano → Integração
→ acesso assistido → retorno ao Admin
```

---

# 33. O que não construir

Sem nova decisão explícita, não adicionar:

- microserviços por módulo;
- event sourcing;
- CQRS;
- GraphQL;
- busca vetorial;
- editor DOCX interno;
- white-label;
- temas por escritório;
- preços/cobrança/gateway/checkout;
- aplicativo mobile nativo;
- chat interno;
- CRM paralelo;
- Kanban;
- etiquetas;
- prioridade de tarefa;
- estrela de Processo importante;
- listas pessoais de tarefas;
- privacidade de Processo inspirada em outro produto;
- segundo cadastro de Agenda;
- segundo cadastro de Documento;
- segundo motor Financeiro;
- segundo motor de Relatórios;
- fila por tenant;
- shell remoto arbitrário;
- Design System próprio;
- biblioteca concorrente ao Spectrum 2;
- paleta CSS paralela;
- suíte enorme de testes antes do produto funcionar.

---

# 34. Definition of Done por fatia

```text
[ ] schema/migration
[ ] regra de domínio server-side
[ ] tenant/permissão
[ ] consultas
[ ] comandos
[ ] erro estruturado
[ ] cliente frontend
[ ] listagem/ficha/formulário
[ ] padrão ListView ou TableView escolhido pela semântica
[ ] carregando/vazio/erro/indisponível
[ ] smoke ponta a ponta
```

---

# 35. Checklist visual e funcional final

## Cabeçalho

- [ ] Nome do escritório ausente.
- [ ] Pesquisa Global centralizada geometricamente.
- [ ] Pesquisa Administrativa centralizada geometricamente.
- [ ] Botões de header somente ícones.
- [ ] `aria-label` em cada botão.
- [ ] Tooltip quando adequado.

## Spectrum 2

- [ ] App/Admin somente Spectrum 2.
- [ ] Provider.
- [ ] SideNav.
- [ ] ListView para coleções operacionais.
- [ ] TableView somente quando comparação por colunas for útil.
- [ ] Dialog/Menu/Form oficiais.
- [ ] styling por tokens/macros.
- [ ] ícones Spectrum.

## Processos

- [ ] Listagem principal usa lista, não tabela.
- [ ] Título por partes/título administrativo é primeira informação.
- [ ] CNJ/protocolo + natureza + tribunal/órgão em segunda linha.
- [ ] responsável/monitoramento/atualização em terceira linha.
- [ ] linha inteira abre ficha.
- [ ] ações não transformam a linha em grade.
- [ ] Judicial/Administrativo.
- [ ] partes/responsáveis.
- [ ] monitoramento.
- [ ] buscas processuais.
- [ ] ficha-hub.

## Atividades

- [ ] Agenda Lista usa ListView, não tabela.
- [ ] marcador + título + contexto + metadados.
- [ ] agrupamento por data.
- [ ] ação rápida e menu secundário.
- [ ] Lista/Dia/Semana/Mês.
- [ ] Audiência/Prazo/Tarefa/Evento.
- [ ] atraso derivado.
- [ ] página própria.
- [ ] reagendar/redesignar.

## Área de trabalho

- [ ] Usa variante compacta do mesmo item de Atividade.
- [ ] Minhas atividades primeiro.
- [ ] Hoje/Esta semana/Este mês.
- [ ] Sem data.
- [ ] filtro por calendário.
- [ ] vencidas só com data/hora negativa.
- [ ] única ação rápida Concluir.
- [ ] resumo de quatro linhas.

## Demais módulos

- [ ] Pessoas e Documentos preferem listas quando houver hierarquia natural.
- [ ] Publicações usam lista operacional.
- [ ] Pesquisa e Notificações usam listas agrupadas.
- [ ] Financeiro/Relatórios/Admin mantêm tabelas quando comparação tabular é a tarefa real.

## Domínio e segurança

- [ ] Pessoas, Processos, Atividades, Publicações, Documentos, Financeiro, Relatórios e Admin funcionam.
- [ ] isolamento multi-tenant.
- [ ] permissões server-side.
- [ ] revisão otimista.
- [ ] histórico.
- [ ] dinheiro decimal.
- [ ] integrações ausentes não quebram núcleo.

## Deploy

- [ ] Docker Compose.
- [ ] migration controlada.
- [ ] HTTPS.
- [ ] dois hosts.
- [ ] health/readiness.
- [ ] logs sem segredos.

---

# 36. Commits sugeridos

```text
1. foundation: runtime, database, auth and Spectrum shell
2. core: accounts, people and cases
3. work: activities, agenda, workspace, search and notifications
4. content: publications, files, documents and templates
5. finance: finance and reports
6. admin: platform administration and integrations
7. deploy: production stack
8. stabilize: final fixes and smoke
```

---

# 37. Instrução final para o agente implementador

> Construa o Orvya completo neste repositório seguindo este `ORVYA.md` como especificação única. Implemente por fatias verticais, sempre conectando banco, regra, API e interface antes de avançar. Use Adobe Spectrum 2 exclusivamente. No App, trate Processos e Atividades como coleções operacionais em `ListView`, com título, contexto e metadados em linhas de leitura, não como tabelas de várias colunas. Prefira o mesmo princípio nas demais entidades operacionais quando houver hierarquia natural e reserve `TableView` para Financeiro, Relatórios e Administração quando a comparação entre colunas for a tarefa real. O cabeçalho não mostra o nome do escritório, mantém a pesquisa geometricamente centralizada e usa somente botões de ícone com nomes acessíveis. Preserve isolamento multi-tenant, permissões server-side, contratos canônicos em português, revisão concorrente, histórico e precisão financeira. Faça verificações curtas nos grandes marcos e deixe a bateria completa para a estabilização final. Termine somente quando a instalação limpa estiver funcional, segura, responsiva e reproduzível.