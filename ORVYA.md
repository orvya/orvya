# ORVYA — blueprint único de implementação

> **Objetivo:** construir o Orvya do zero, de forma autônoma, direta e reproduzível, preservando o comportamento funcional atual e removendo a complexidade histórica que não é necessária para o produto final.
>
> **Repositório de implementação:** `orvya/orvya`, branch `main`.
>
> **Baseline funcional verificada:** comportamento de `orvya/orvya-base@f11abd463f27cbdc3515fc14de272bbd86767d62`, cuja instalação na homologação foi registrada em `b3c07fea8d306f3464a02262586ea9d38b7eb1f6`.
>
> **Regra de prevalência:** este arquivo descreve o produto novo. Quando uma escolha aqui divergir de artefato histórico, **este arquivo prevalece**.

---

# 1. Resultado esperado

O Orvya é um SaaS jurídico multi-tenant para escritórios e profissionais da advocacia.

O produto final possui somente duas superfícies:

| Superfície | Host | Finalidade |
|---|---|---|
| App | `app.orvya.net` | produto utilizado pelos escritórios |
| Admin | `admin.orvya.net` | administração global da Plataforma |

A API fica sob `/api/v1` e é consumida pelas duas superfícies.

O núcleo do produto conecta:

- escritórios e usuários;
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

## 1.1 Critério real de conclusão

A implementação só termina quando:

- um banco vazio recebe uma migration inicial e sobe sem intervenção manual;
- cadastro, confirmação de e-mail, login, sessão e recuperação de senha funcionam;
- App e Admin compilam e funcionam;
- isolamento entre escritórios está garantido no backend;
- todas as fatias verticais deste documento estão implementadas;
- integrações ausentes aparecem como indisponíveis, sem simular sucesso;
- o deploy HTTPS dos dois hosts funciona;
- os smoke tests finais passam;
- não há erro de migration, typecheck ou build.

---

# 2. Protocolo de execução para a IA

A IA deve executar esta especificação como **uma tarefa contínua**, sem solicitar aprovação entre fases.

## 2.1 Regras de trabalho

1. Não reproduzir a arquitetura histórica por fidelidade ao passado.
2. Reproduzir regras de produto, fluxos, dados, navegação e experiência vigentes.
3. Usar um **monólito modular**, não microserviços por domínio.
4. Criar **uma migration inicial limpa** com o schema final.
5. Criar migrations adicionais apenas se o schema mudar durante a própria implementação.
6. Não gerar EFs, ETs, matrizes, relatórios de evidência ou documentos paralelos.
7. Não criar uma suíte massiva de testes enquanto o produto ainda está incompleto.
8. Validar apenas marcos grandes durante a construção.
9. Fazer a rodada completa de correções e testes no final.
10. Não inventar preço, cobrança, checkout ou recurso comercial ausente desta especificação.
11. Não armazenar segredo no Git.
12. Não criar dado fictício persistente para fazer a interface parecer pronta.
13. Se uma integração externa não estiver configurada, concluir o restante do produto e mostrar o estado real dessa integração.
14. Se um defeito não bloquear o avanço estrutural, registrá-lo temporariamente e continuar até a estabilização final.
15. Criar commits apenas em grandes marcos coerentes.

## 2.2 Método obrigatório: fatias verticais

Cada domínio deve ser implementado nesta ordem interna:

```text
schema/modelo
→ regras de domínio
→ serviço/persistência
→ API
→ cliente frontend
→ tela/listagem/ficha
→ smoke curto
```

Não implementar toda a camada de banco do produto, depois toda a API e só no fim todas as telas. Isso aumenta deriva entre camadas.

Cada fatia só precisa de um smoke curto para provar que está conectada. A bateria ampla fica para o final.

## 2.3 Grafo de dependência

```text
F0 Fundação
 ├─ F1 Conta, acesso, Plano e permissões
 │   ├─ F2 Pessoas
 │   ├─ F3 Processos
 │   │   └─ F4 Atividades, Agenda e Área de trabalho
 │   │       └─ F5 Publicações e Pesquisa
 │   └─ F6 Arquivos, Documentos e Modelos
 │
 ├─ F7 Financeiro
 │   └─ F8 Relatórios
 │
 └─ F9 Administração da Plataforma

F0..F9 → F10 Deploy → F11 Estabilização final
```

Implementar na ordem acima, podendo adiantar apenas componentes compartilhados realmente necessários ao próximo bloco.

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

A divisão de pastas pode variar se mantiver a mesma separação de responsabilidades.

## 3.1 Processos de runtime

Use Docker Compose com:

1. `postgres` — PostgreSQL;
2. `api` — FastAPI;
3. `worker` — tarefas persistentes e rotinas recorrentes;
4. `ops` — executor mínimo e allowlisted para ações operacionais que não devem ser executadas pelo processo HTTP;
5. `nginx` — arquivos do frontend e proxy para a API.

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
- conversor de PDF somente onde necessário.

## 4.2 Frontend

- TypeScript;
- React;
- React Router;
- Vite;
- npm workspaces;
- **Adobe Spectrum 2 exclusivamente**;
- pacote principal `@react-spectrum/s2`;
- styling com `@react-spectrum/s2/style`;
- ícones com `@react-spectrum/s2/icons/*`.

Usar uma versão estável atual de Spectrum 2 e travá-la no lockfile. Não misturar versões anteriores do Spectrum nem outra biblioteca de componentes.

## 4.3 Provider Spectrum

App e Admin devem montar `Provider` do Spectrum 2 na raiz, configurando:

- locale `pt-BR`;
- integração com o roteador;
- esquema de cor adotado pela aplicação;
- comportamento responsivo oficial;
- tipografia fornecida pelo próprio Spectrum.

Não carregar família tipográfica externa para a interface.

---

# 5. Design System e identidade

Spectrum 2 é a única fonte de:

- componentes;
- tipografia de interface;
- cores de interface;
- espaçamentos;
- raios;
- elevação;
- foco;
- ícones;
- estados;
- menus;
- tabelas;
- formulários;
- diálogos;
- tooltips;
- skeletons e progressos;
- responsividade de controles;
- comportamento de toque.

Use componentes oficiais sempre que existirem, especialmente:

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
- `DatePicker` e componentes temporais;
- `Dialog`;
- `AlertDialog`;
- `Tabs`;
- `SegmentedControl`;
- `TableView`;
- `SideNav`;
- `Avatar`;
- `Badge` ou `StatusLight` conforme semântica;
- `Toast`;
- `Tooltip`;
- `Skeleton`;
- `ProgressCircle`;
- `Breadcrumbs` quando realmente necessário.

## 5.1 Styling adicional

Quando layout adicional for necessário:

```ts
import {style, focusRing} from '@react-spectrum/s2/style' with {type: 'macro'};
```

Usar tokens Spectrum antes de qualquer valor arbitrário.

Não criar:

- Design System intermediário próprio;
- paleta paralela;
- reset global agressivo;
- cópias visuais de componentes Spectrum;
- CSS que sobrescreva internamente componentes para fazê-los parecer outra biblioteca.

## 5.2 Marca

- nome sempre `Orvya`;
- usar logotipo oficial completa em SVG onde houver espaço;
- usar emblema oficial em contexto compacto;
- não reconstruir a marca com texto comum;
- cores próprias da marca não redefinem a paleta de UI do Spectrum.

## 5.3 Cores de tipos de Atividade

O banco armazena uma **chave de cor do produto**, nunca hexadecimal.

Use conjunto fechado de opções visuais mapeadas para tokens Spectrum. A mesma chave deve gerar o mesmo marcador na Área de trabalho, Agenda, Processo, Pesquisa, Notificações e Relatórios.

Cor nunca é o único indicador de significado.

---

# 6. Configuração

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

A aplicação deve iniciar sem integrações externas configuradas, exceto quando a própria operação solicitada depender delas.

---

# 7. Segurança, sessão e autoridade

## 7.1 Sessão

Use sessão opaca controlada pelo servidor.

Regras vigentes:

- segredo aleatório criptográfico com pelo menos 256 bits;
- somente derivação do segredo é persistida;
- cookie `HttpOnly`;
- `Secure` em produção;
- host-only;
- App e Admin nunca compartilham cookie;
- `SameSite=Lax` ou mais restritivo quando compatível;
- 30 minutos de inatividade;
- 8 horas de duração absoluta.

Escopos distintos:

- App;
- Admin;
- acesso assistido no App, pertencente ao Administrador da Plataforma real.

## 7.2 CSRF

Mutações autenticadas exigem token da sessão no cabeçalho:

```text
X-Orvya-CSRF
```

O token fica apenas no estado em memória da aplicação.

Não usar `localStorage`, `sessionStorage` ou IndexedDB para sessão ou credenciais.

## 7.3 Operação/correlação

Toda resposta da API possui:

```text
X-Orvya-Operation-Id
```

Esse identificador serve para correlação segura de logs e erros.

## 7.4 Senhas

- Argon2id;
- nunca logar senha ou token;
- recuperação por token de uso único;
- resposta de pedido de recuperação não revela se o e-mail existe.

## 7.5 Autoridade central

Existe uma única função/serviço de decisão de autorização.

Toda requisição protegida reavalia:

- identidade;
- tenant;
- estado da conta;
- estado do usuário;
- condição de Administrador do Sistema;
- permissões granulares;
- recurso do Plano;
- limite aplicável;
- alcance do objeto quando necessário.

O frontend apenas esconde ou desabilita controles conforme o contexto recebido. A segurança real é do servidor.

## 7.6 Multi-tenant

- tenant vem da sessão;
- rotas operacionais do App não aceitam `account_id` como fonte de autoridade;
- toda consulta aplica tenant no servidor;
- relação entre dados de tenants diferentes é recusada;
- ID pertencente a outra conta responde como não localizado ou sem autoridade sem revelar existência;
- Pesquisa, Relatórios, arquivos e histórico obedecem à mesma fronteira.

## 7.7 Acesso assistido

`Acessar escritório` no Admin cria contexto temporário próprio no host do App.

Regras:

- não cria usuário local;
- não consome vaga;
- autoria continua sendo do Administrador da Plataforma;
- interface mostra faixa clara de acesso assistido;
- existe ação visível para retornar ao Admin;
- ações entram no histórico com o ator real.

---

# 8. Contrato HTTP canônico

Use REST JSON sob `/api/v1`.

Os nomes funcionais das famílias de rotas permanecem em português quando já são canônicos no Orvya.

## 8.1 Coleções

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
- `page_size` aceita somente 25, 50 ou 100;
- padrão 25;
- `q` tem no máximo 200 caracteres;
- ordenação é estável e desempata por ID;
- filtro inválido é erro de campo, não fallback silencioso.

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

## 8.2 Erros

Envelope obrigatório:

```json
{
  "erro": {
    "code": "codigo_estavel",
    "mensagem": "Mensagem compreensível em pt-BR.",
    "field": "campo_opcional",
    "operation_id": "identificador",
    "retryable": false
  }
}
```

Nunca serializar traceback, segredo, token ou conteúdo de outro tenant.

Status principais:

- `400` entrada inválida;
- `401` sem sessão válida;
- `403` sem autoridade;
- `404` ausente ou fora do alcance;
- `409` conflito de revisão/concorrência;
- `422` regra de domínio;
- `429` limite técnico quando aplicável;
- `503` dependência necessária indisponível.

## 8.3 Revisão otimista

Registros editáveis importantes possuem `revision`.

Mutação recebe:

```json
{"expected_revision": 3}
```

Se a revisão mudou:

- responder `409`;
- indicar campo `expected_revision` quando aplicável;
- frontend oferece recarregar e revisar;
- nunca sobrescrever silenciosamente.

## 8.4 Idempotência

Comandos que possam duplicar efeito por repetição de rede recebem uma chave de operação gerada pelo cliente e reutilizada ao repetir a mesma tentativa deliberada.

Aplicar especialmente a operações financeiras e efeitos externos.

## 8.5 Dinheiro

Dinheiro trafega como string decimal.

```json
{
  "principal": "1250.00",
  "open": "500.00"
}
```

Nunca trafegar dinheiro como `float`.

## 8.6 Famílias de rotas

Manter estas famílias, detalhando subrotas apenas conforme cada fatia exigir:

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

Não criar endpoint novo para cada pequena composição de tela. Preferir filtros e projeções coerentes.

---

# 9. Modelo de dados mínimo

Use UUID como identificador primário, timestamps timezone-aware para instantes e `DATE` para datas civis.

Nomes físicos podem variar. As relações abaixo não podem desaparecer.

## 9.1 Globais

- Planos;
- recursos de Plano;
- limites de Plano;
- Administradores da Plataforma;
- catálogos iniciais;
- catálogos referenciais;
- variáveis de Documentos;
- configurações de integração;
- histórico da Plataforma;
- execuções operacionais.

## 9.2 Por escritório

- contas/escritórios;
- usuários;
- permissões;
- convites;
- sessões;
- tokens de confirmação/recuperação;
- Pessoas;
- contatos;
- endereços;
- identificações;
- vínculos entre Pessoas;
- Processos;
- partes;
- responsáveis;
- monitoramento processual;
- buscas processuais;
- Atividades;
- catálogos de Atividade;
- Publicações;
- arquivos;
- Documentos;
- vínculos documentais;
- Modelos DOCX;
- contas financeiras;
- categorias;
- centros de custo;
- formas de pagamento;
- Lançamentos;
- baixas;
- transferências;
- conciliações;
- Notificações;
- preferências de Notificações;
- catálogos da conta;
- fatos de histórico;
- definições salvas de Relatórios quando utilizadas.

## 9.3 Regras transversais

- dado tenant-scoped possui `account_id` direto ou por relação estrutural inequívoca;
- dinheiro usa `NUMERIC`;
- histórico é append-only;
- datas civis não viram meia-noite artificial em UTC;
- texto `Não informado` nunca é persistido como dado;
- relação não duplica entidade;
- exclusão de relação não exclui automaticamente o registro relacionado.

---

# 10. Planos e Teste Grátis

Toda conta possui Plano.

## 10.1 Limites principais

- usuários;
- Processos monitorados;
- armazenamento.

Cada limite tem modo explícito:

- limitado;
- ilimitado;
- pendente, quando uma decisão ainda não existe.

Zero é um limite válido e não significa ilimitado.

## 10.2 Recursos controláveis

No mínimo:

- núcleo;
- Publicações;
- Documentos;
- Modelos de documentos;
- Financeiro;
- Relatórios.

## 10.3 Teste Grátis

- Plano estrutural permanente;
- duração de 7 dias exatos desde a criação da conta;
- padrão do autocadastro;
- ao expirar, suspender a conta se ela ainda estiver nesse Plano;
- mudar para outro Plano encerra o efeito da expiração;
- retornar depois ao Teste Grátis não reinicia os sete dias.

Redução de Plano não apaga dados. Bloqueia apenas novas utilizações incompatíveis e explica a razão.

---

# 11. Gramática comum de UX

## 11.1 Ver é página; agir é Dialog

| Intenção | Superfície |
|---|---|
| visualizar registro principal | página/ficha |
| criar | Dialog |
| editar | Dialog |
| vincular | Dialog |
| reagendar/redesignar | Dialog |
| ação secundária | Menu/ActionMenu |
| ação crítica | confirmação auditável |
| trabalhar em lote | tabela/listagem |
| consultar histórico | seção, aba ou timeline |

Não usar drawer lateral para ficha ou formulário.

## 11.2 Página

- largura útil máxima aproximada de 1440 px;
- centralizada;
- gutters responsivos;
- `min-width: 0` nas regiões flexíveis;
- formulários controlam a própria largura;
- 320 px não pode produzir overflow da página inteira.

## 11.3 Blocos de dados

Não criar um Card por campo.

Padrão:

```text
Bloco
  seção
    rótulo | valor
    rótulo | valor
  divisor
  seção
    ...
```

Card fica reservado para resumo independente, indicador ou composição em que o próprio Spectrum recomende esse padrão.

## 11.4 Listagens

- pesquisa automática após 300 ms;
- Enter antecipa a consulta;
- respostas antigas não substituem respostas novas;
- mudar termo ou filtro volta à página 1;
- `Limpar filtros` restaura os padrões da tela e preserva o tamanho de página;
- paginação na mesma faixa da pesquisa/filtros;
- ordem visual: faixa → tamanho → anterior/próxima;
- `0 a 0 de 0` somente após zero confirmado pelo servidor;
- durante atualização manter conteúdo anterior inerte quando for seguro;
- linha inteira abre a ficha quando representa registro principal;
- controle interativo dentro da linha não navega a linha;
- nome do registro continua acessível por teclado;
- tabela rola horizontalmente dentro do container antes de quebrar a página.

## 11.5 Seleção assistida

Relações grandes usam `ComboBox` com consulta remota:

- mínimo 2 caracteres;
- espera de 300 ms;
- até aproximadamente 10 sugestões;
- identificação principal + contexto curto;
- sem carregar milhares de opções no navegador.

Conjuntos pequenos e fechados usam `Picker`.

## 11.6 Ações críticas

Confirmação mostra:

```text
Título
Registro afetado
Consequência objetiva
Justificativa
[Cancelar] [Confirmar]
```

Justificativa obrigatória quando definida pela ação, entre 5 e 500 caracteres.

Servidor registra ator, instante, ação, alvo e justificativa.

## 11.7 Ações críticas atualmente justificadas

Aplicar ao menos a:

- concluir Atividade;
- cancelar Atividade;
- reabrir Atividade;
- excluir registros principais;
- substituir arquivo vigente;
- alterar permissões;
- suspender/reativar usuários ou contas;
- ações administrativas destrutivas;
- desconexões ou desativações externas que produzam efeito relevante.

Edição comum, reagendamento e redesignação não exigem justificativa apenas por serem edições.

---

# 12. Cabeçalho do App

Esta seção substitui qualquer disposição anterior do cabeçalho.

## 12.1 Regra visual

**O nome do escritório não aparece no cabeçalho.**

Desktop:

```text
┌──────────────────────────────────────────────────────────────────────────────┐
│ [ORVYA]                  [       PESQUISA GLOBAL       ]      [+] [🔔] [◉] │
└──────────────────────────────────────────────────────────────────────────────┘
```

Estrutura de layout:

```text
coluna esquerda  = 1fr
coluna central   = largura controlada da pesquisa
coluna direita   = 1fr
```

A Pesquisa Global fica **geometricamente centralizada no cabeçalho**, independentemente da largura da marca ou da quantidade de ações à direita.

A zona direita usa `justify-content: end`.

## 12.2 Botões do cabeçalho

**Todos os botões do cabeçalho são somente ícones.**

No App, isso inclui:

- Menu, quando necessário em largura estreita;
- `+` global;
- Notificações;
- conta/perfil, preferencialmente Avatar como acionador;
- qualquer outra ação futura do cabeçalho.

Não renderizar texto como `Adicionar`, `Notificações`, `Conta`, `Menu` ou `Sessão` ao lado desses ícones.

Implementar com `ActionButton` ou componente Spectrum equivalente contendo apenas ícone/Avatar.

Todo botão somente de ícone precisa de:

- `aria-label` explícito;
- `Tooltip` em ponteiro/teclado quando útil;
- estado de foco oficial do Spectrum;
- área de toque adequada;
- estado aberto/selecionado perceptível quando aplicável.

Tooltip não substitui nome acessível.

## 12.3 Pesquisa

Usar `SearchField` Spectrum.

- mínima de 2 caracteres;
- 300 ms;
- resultados agrupados;
- até 5 resultados por grupo na visualização rápida;
- setas navegam;
- Enter abre;
- Esc fecha resultado sem perder a capacidade de continuar digitando;
- `Ver todos os resultados` abre `/pesquisa`.

Em telas estreitas, manter a pesquisa dentro do cabeçalho em uma segunda linha de largura disponível, centralizada. Não substituí-la permanentemente por página separada.

## 12.4 Conta

O acionador de conta mostra apenas Avatar ou ícone de pessoa.

Menu:

```text
Meu perfil
Configurações do escritório
Sair
```

O nome do escritório continua disponível onde ele é conteúdo real, como Configurações do escritório e faixa de acesso assistido, mas não no cabeçalho padrão.

---

# 13. Navegação do App

Use `SideNav` Spectrum.

Entradas principais:

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

Subnavegação conceitual:

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

A navegação é filtrada pelas áreas/capacidades recebidas do servidor.

Em largura estreita:

- SideNav fica em painel sobreposto;
- acionador Menu é somente ícone;
- Esc fecha;
- cortina fecha;
- foco retorna ao acionador;
- conteúdo usa largura inteira quando fechada.

## 13.1 Rotas do App

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

Ao abrir uma ficha, preservar no histórico do navegador:

- termo;
- filtros;
- página;
- tamanho;
- ordenação;
- aba;
- visão da Agenda;
- data de referência;
- posição aproximada de rolagem quando útil.

Voltar deve retornar ao contexto anterior, sem refazer mentalmente a consulta.

---

# 14. F0 — Fundação

## Implementar

- estrutura do monorepo;
- Docker Compose;
- PostgreSQL;
- configuração;
- migration inicial vazia/preparada;
- camada comum de erro;
- paginação;
- operação/correlação;
- Spectrum Provider;
- cliente HTTP;
- roteamento de App e Admin;
- health checks.

## API mínima

```text
GET /api/v1/saude
GET /api/v1/saude/pronto
GET /api/v1/saude/dependencias
```

`/saude` mede somente vivacidade.

`/saude/pronto` depende do banco e da revisão de schema exigida.

Integração opcional indisponível não derruba prontidão geral.

## Pronto quando

- `alembic upgrade head` funciona em banco vazio;
- API inicia;
- App vazio inicia;
- Admin vazio inicia;
- Spectrum renderiza nas duas superfícies;
- typecheck passa.

---

# 15. F1 — Conta, acesso, Plano e permissões

## 15.1 Conta

Estados:

- Ativa;
- Suspensa.

Campos principais:

- nome;
- CPF/CNPJ opcional;
- telefone;
- e-mail institucional;
- fuso horário;
- logotipo;
- Plano;
- instante de criação;
- expiração do Teste Grátis quando aplicável.

## 15.2 Usuário

Estados:

- Ativo;
- Suspenso.

Exclusão é ação, não terceiro estado permanente.

Campos:

- nome;
- e-mail;
- senha derivada;
- condição de Administrador do Sistema;
- permissões granulares;
- foto opcional;
- preferências pessoais;
- revisão.

O e-mail de usuário operacional é único enquanto o cadastro existir.

## 15.3 Administrador do Sistema

Administrador do Sistema possui acesso integral ao escritório dentro do Plano.

Permissões individuais continuam armazenadas e voltam a valer se a condição administrativa for removida.

Não criar cargos fixos como Advogado, Coordenador ou Colaborador como fonte automática de autoridade.

## 15.4 Cadastro

Rota visível:

```text
/cadastro
```

Campos iniciais:

- nome;
- e-mail;
- senha;
- nome do escritório.

Fluxo:

1. criar conta;
2. criar primeiro usuário;
3. marcar como Administrador do Sistema;
4. associar Teste Grátis;
5. enviar confirmação de e-mail;
6. somente após confirmação permitir acesso operacional.

Não pedir configuração avançada no onboarding.

## 15.5 Login

```text
[Logo]
Entrar no Orvya
E-mail
Senha
[Entrar]
Esqueci minha senha
Criar escritório
```

Método de entrada: **e-mail e senha**.

## 15.6 Convite

Administrador do Sistema cria usuário com:

- nome;
- e-mail;
- permissões;
- condição administrativa opcional.

Destinatário recebe convite e define senha.

Convite pendente pode ser reenviado.

## 15.7 Exclusão de usuário

Se houver responsabilidades:

- escolher usuário ativo da mesma conta;
- reatribuir Atividades Pendentes, inclusive atrasadas;
- reatribuir Processos em que seja responsável principal;
- fatos históricos permanecem com o autor original.

## 15.8 Meu perfil `/conta/perfil`

Três seções:

```text
Identificação | Notificações | Segurança
```

### Identificação

- nome;
- e-mail;
- foto de perfil;
- demais dados pessoais existentes.

Foto:

- PNG/JPEG/WebP;
- limite de 2 MB;
- usa o armazenamento central;
- outra pessoa da mesma conta pode ler a foto vigente quando autorizado;
- Administrador do Sistema pode remover a foto de usuário da própria conta;
- sem armazenamento configurado, mostrar indisponibilidade real.

### Notificações

Preferências individuais da central de Notificações.

### Segurança

- alterar senha;
- encerrar sessão atual;
- informações de segurança realmente existentes.

## 15.9 Configurações do escritório

Sete seções:

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

Read-first:

```text
Nome do escritório | CPF/CNPJ
Telefone           | E-mail
Fuso horário
Logo
```

Editar abre Dialog.

### Equipe e acesso

Tabela:

```text
| Usuário | Status | Administrador do Sistema | Convite/acesso |
```

Ações:

- Novo usuário;
- editar identificação;
- editar permissões;
- suspender/reativar;
- excluir;
- reenviar convite.

### Agenda

Somente configuração compartilhada real:

- fuso horário;
- atalho para os catálogos de Atividade.

### Plano e utilização

- Plano atual;
- usuários usados/limite;
- monitorados usados/limite;
- armazenamento usado/limite;
- recursos habilitados.

### Pronto quando

- cadastro confirmado entra no App;
- usuário suspenso não entra;
- conta suspensa não entra;
- sessão expira corretamente;
- permissões são decididas no backend;
- convite funciona;
- perfil e Configurações funcionam.

---

# 16. F2 — Pessoas

## 16.1 Entidade

Naturezas:

- Pessoa Física;
- Pessoa Jurídica;
- natureza ainda não identificada pode ser `null`, não uma terceira natureza.

Dados possíveis:

- nome/razão social;
- nome social/nome fantasia;
- CPF/CNPJ;
- nascimento/abertura;
- nacionalidade;
- estado civil;
- profissão;
- classificações;
- observações;
- contatos;
- endereços;
- identificações adicionais;
- vínculos com outras Pessoas.

CPF/CNPJ duplicado no mesmo escritório orienta para o cadastro existente. Nunca sobrescreve automaticamente.

## 16.2 API

Família:

```text
/api/v1/pessoas
```

O tenant é sempre derivado da sessão.

Listagem aceita pesquisa, natureza, paginação e filtros necessários.

## 16.3 Listagem `/pessoas`

```text
[Pessoas]                                             [Adicionar pessoa]
[Pesquisar nome/documento/contato] [Natureza] [paginação]

| Nome | Natureza | Documento | E-mail principal | Telefone principal | Atualizada em |
```

Linha inteira abre ficha.

## 16.4 Ficha `/pessoas/:id`

```text
[← Pessoas] Nome da Pessoa                     [Natureza] [Editar] [...]
            Pessoa Física/Jurídica · documento
[Resumo] [Processos] [Documentos] [Financeiro] [Histórico]
```

Abas não autorizadas são omitidas.

### Resumo

```text
DADOS DA PESSOA
  Identificação
  Classificações
  Observações

CONTATOS, ENDEREÇOS, IDENTIFICAÇÕES E VÍNCULOS
  Contatos        [+]
  Endereços       [+]
  Identificações  [+]
  Vínculos        [+ Vincular pessoa]
```

Tudo em leitura. Criar/editar itens abre Dialog.

Definir principal é ação do item.

### Processos

```text
| Processo | Situação | Responsável principal |
```

### Documentos

Mostra os Documentos reais vinculados à Pessoa.

### Financeiro

```text
| Lançamento | Vencimento | Principal | Em aberto |
```

### Histórico

Timeline real, agrupada por dia.

## Pronto quando

- criar/editar/excluir Pessoa;
- contatos, endereços, identificações e vínculos funcionam;
- principal funciona;
- duplicidade é tratada;
- relações mostram dados reais sem cópia.

---

# 17. F3 — Processos

## 17.1 Naturezas

- Judicial;
- Administrativo.

## 17.2 Judicial

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

Cadastro manual não faz consulta externa automaticamente para decidir se pode salvar.

## 17.3 Administrativo

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

## 17.4 Partes

Polos:

- Ativo;
- Passivo;
- Terceiro interessado.

Participação aponta para Pessoa do mesmo escritório.

## 17.5 Monitoramento

- somente Judicial elegível;
- exige número CNJ válido;
- cadastro manual nasce sem monitoramento;
- falta de vaga no Plano não impede cadastrar o Processo;
- desativar preserva Publicações já recebidas;
- falha externa não muda sozinha o estado de monitoramento.

## 17.6 Buscas processuais

Família:

```text
/api/v1/processos/buscas
```

Modos:

- número CNJ;
- OAB + UF + período quando aplicável.

Busca externa é comando explícito, nunca pesquisa automática de listagem.

Ao concluir:

- mostrar candidatos;
- marcar já cadastrados;
- usuário seleciona quais adicionar;
- não cadastrar todos automaticamente.

## 17.7 Listagem `/processos`

```text
[Processos]                                           [Novo processo]
[Pesquisar] [Natureza] [Monitoramento] [paginação]

| Processo | Situação | Responsável principal | Atualização |
```

Primeira célula:

```text
identificação principal
Parte 1 x Parte 2
Judicial/Administrativo · Monitorado/Não monitorado
```

Quando o usuário não puder ler Pessoas, não vazar nomes de partes.

## 17.8 Ficha `/processos/:id`

```text
[← Processos] Parte 1 x Parte 2                 [Monitoramento] [+] [Editar] [...]
              identificação · natureza · Situação · Tribunal
[Resumo] [Atividades] [Publicações] [Documentos] [Financeiro] [Histórico]
```

`+` contextual:

- Nova atividade;
- Vincular Pessoa;
- Adicionar Documento;
- Novo lançamento.

Cada opção reutiliza o mesmo Dialog do módulo de origem com o Processo já herdado.

`...`:

- Gerar documento;
- ativar/desativar monitoramento;
- excluir.

### Resumo

```text
┌ Próximas atividades, até 5 ┐  ┌ Dados do processo ┐
└────────────────────────────┘  └────────────────────┘

PARTES E RESPONSÁVEIS
  Partes
  Responsáveis

ÚLTIMOS EVENTOS                                      [Ver Histórico]
```

Em largura estreita, empilhar.

### Financeiro do Processo

Somente resumo daquele Processo:

- a receber;
- vencido;
- recebido;
- lançamentos vinculados;
- Novo lançamento;
- Ver no Financeiro.

Não criar segundo motor financeiro na ficha.

## Pronto quando

- Judicial e Administrativo funcionam;
- partes e responsáveis funcionam;
- título por partes funciona;
- monitoramento respeita Plano;
- buscas externas não interferem no cadastro manual;
- ficha agrega relações sem duplicar dados.

---

# 18. F4 — Atividades, Agenda e Área de trabalho

## 18.1 Atividade

Modalidades:

- Audiência;
- Prazo;
- Tarefa;
- Evento.

Estados persistidos:

- Pendente;
- Concluída;
- Cancelada.

`Atrasada` é condição derivada, nunca estado persistido.

Pendentes inclui atrasadas.

Cada Atividade possui:

- item catalogado, que define título;
- modalidade;
- responsável;
- data, quando aplicável;
- horário opcional;
- descrição;
- Processo opcional, salvo origem que o torne obrigatório;
- origem;
- cor do tipo;
- revisão;
- histórico.

Origem:

- Agenda;
- Processo;
- tratamento de Publicação.

Criada no Processo herda esse Processo.

Criada a partir de Publicação permanece vinculada ao Processo da Publicação enquanto essa origem existir.

## 18.2 API

Família:

```text
/api/v1/atividades
```

Servidor calcula:

- `overdue`;
- marco de atraso;
- contagens;
- janela do calendário;
- cores dos tipos;
- transições válidas.

## 18.3 Agenda `/agenda`

```text
[Agenda e Atividades]                            [Nova atividade]
[Lista] [Dia] [Semana] [Mês]
[‹] período [Hoje] [›]
[Pesquisar] [Modalidade] [Recorte] [Responsável] [Limpar]
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

### Lista

```text
| Atividade | Modalidade | Quando | Responsável | Estado | Ações |
```

Agrupar por data.

Linha inteira abre ficha.

Ações disponíveis conforme estado/capacidade:

- concluir/reabrir;
- reagendar;
- redesignar;
- editar;
- cancelar;
- excluir.

### Dia

- largura inteira;
- faixa Sem horário;
- grade temporal;
- criação no horário escolhido quando permitida;
- arraste para reagendar;
- comando Reagendar sempre disponível como alternativa.

### Semana

- sete dias;
- faixa Sem horário;
- linha do horário atual;
- colisões em raias legíveis;
- cabeçalho do dia abre Dia.

### Mês

- sete colunas;
- poucos itens por dia;
- `+ N` abre Dia;
- clicar no dia abre Dia;
- sem painel lateral.

## 18.4 Ficha `/agenda/:id`

```text
[← Agenda] ● Título                   [Estado] [ações] [...]
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

## 18.5 Área de trabalho `/dashboard`

A Área de trabalho é uma **mesa diária**, não Dashboard analítico.

Desktop:

```text
[Área de trabalho]
[Aviso do Teste Grátis, quando aplicável]

┌──────────────────────────────────────────────┬─────────────────────────┐
│ MINHAS ATIVIDADES                            │ CALENDÁRIO              │
│ [Hoje] [Esta semana] [Este mês] [Filtros]   │       ‹ mês ano ›       │
│                                              │  S T Q Q S S D          │
│ VENCIDAS                                     │                         │
│ ● Atividade                     modalidade   │                         │
│   contexto                                   │ RESUMO DO ESCRITÓRIO     │
│   data/hora                      [Concluir]   │ Processos cadastrados N │
│                                              │ Processos monitorados N │
│ HOJE / AMANHÃ / DATA                         │ Pessoas cadastradas N   │
│ ...                                          │ Atividades pendentes N  │
│ + N atividades                              │                         │
│ Ver todas na Agenda                         │                         │
└──────────────────────────────────────────────┴─────────────────────────┘
```

Largura:

- Minhas atividades aproximadamente 67%;
- coluna lateral aproximadamente 33%;
- abaixo de aproximadamente 960 px, empilhar com Minhas atividades primeiro.

### Minhas atividades

- somente Atividades do usuário atual;
- somente Pendentes;
- Hoje é padrão;
- modos: Hoje, Esta semana, Este mês;
- Mais filtros: Modalidade e Sem data;
- modos são mutuamente exclusivos;
- dia escolhido no calendário substitui o modo de período;
- `Voltar para hoje` restaura Hoje;
- vencidas aparecem primeiro;
- mostrar até 12 itens;
- excedente vira `+ N atividades`;
- sem paginação;
- linha inteira abre Atividade;
- única ação rápida: Concluir.

Atividade vencida difere **somente** pela data/hora em cor negativa Spectrum.

Não usar selo de atraso, fundo diferente ou borda diferente na mesa.

### Calendário compacto

- mês;
- semana segunda → domingo;
- cabeçalho apenas `‹ MÊS ANO ›`;
- sem itens escritos dentro dos dias;
- sem horários;
- sem arraste;
- um dia com ao menos uma Atividade Pendente do usuário recebe uma única marca discreta;
- quantidade não altera a marca;
- trocar mês não muda a lista;
- escolher dia filtra a lista na própria Área de trabalho.

### Resumo do escritório

Exatamente quatro linhas:

1. Processos cadastrados;
2. Processos monitorados;
3. Pessoas cadastradas;
4. Atividades pendentes neste mês.

Sem Card por linha, gráfico, ícone decorativo ou número gigante.

Cada linha é atalho para o recorte correspondente.

`Indisponível` nunca vira zero.

## Pronto quando

- CRUD/transições de Atividade funcionam;
- atraso é calculado;
- quatro visões da Agenda funcionam;
- retorno de Dia preserva contexto de Mês/Semana;
- Área de trabalho segue exatamente a mesa diária acima;
- nenhuma métrica removida reaparece na mesa.

---

# 19. F5 — Publicações, Pesquisa e Notificações

# 19.1 Publicações

Publicação nasce somente da integração judicial autorizada.

Condições:

- Nova;
- Tratada.

A condição Tratada é operacional e não declara efeito jurídico.

Conteúdo ausente e falha de carregamento são estados diferentes.

Conteúdo recebido é apresentado como texto seguro.

Ações:

- Criar providência;
- Concluir;
- Concluir e abrir a próxima;
- Descartar.

Criar providência cria Atividade real.

Concluir preserva a Publicação e marca Tratada.

Descartar remove a Publicação sem apagar Atividades independentes já criadas.

## Listagem `/publicacoes`

```text
[Publicações]
[Novas N] [Tratadas N] [Total N]
[Pesquisar] [Condição] [paginação]

| Processo | Tipo | Data da fonte | Recebida em | Condição | Trecho | Ações |
```

Trecho curto de conteúdo, sem despejar texto longo na tabela.

Linha abre Publicação, não Processo.

## Ficha `/publicacoes/:id`

Quando veio da listagem:

```text
[Anterior]                         12 de 48                         [Próxima]
```

```text
[← Publicações] Publicação   [Condição] [Criar providência] [Concluir] [...]
               Processo · Tipo · Tribunal · recebida em...

[nota jurídica]
CONTEÚDO RECEBIDO
PROCESSO
PROVIDÊNCIAS
```

`Concluir e abrir a próxima`:

1. executa a mesma conclusão normal;
2. usa a mesma confirmação/justificativa;
3. relê a fila com o recorte original;
4. navega somente após sucesso;
5. sem próxima, retorna à listagem preservando contexto.

## 19.2 Pesquisa Global

Família:

```text
/api/v1/pesquisa
```

Grupos possíveis conforme capacidade:

- Pessoas;
- Processos;
- Atividades;
- Publicações;
- Documentos;
- Financeiro;
- Relatórios salvos quando aplicável.

Regras:

- mínimo 2 caracteres;
- máximo 200;
- grupo vedado não aparece nem revela quantidade;
- pesquisa é somente consultiva;
- resultado abre registro canônico.

Página `/pesquisa` usa o mesmo termo e semântica do cabeçalho.

## 19.3 Notificações

Notificação pertence ao destinatário.

Tipos iniciais:

- nova Publicação;
- Atividade atribuída;
- Prazo próximo;
- Prazo vencido;
- Audiência próxima;
- aviso interno do escritório.

`Lido` não significa `resolvido`.

Abrir Notificação nova pode marcar a leitura individual.

Ações:

- marcar uma como lida;
- marcar todas como lidas;
- preferências pessoais.

Tela `/alertas`:

- Todos;
- Novos;
- Lidos;
- tipo opcional;
- mensagem;
- contexto;
- instante;
- destino.

## Pronto quando

- ingestão deduplica Publicações;
- sequência de tratamento funciona;
- Pesquisa não vaza grupo proibido;
- Notificações são por destinatário;
- leitura coletiva não altera a causa do alerta.

---

# 20. F6 — Arquivos, Documentos e Modelos

## 20.1 Serviço de arquivos

Todo arquivo persistente passa por um único serviço.

Fluxo:

1. cliente valida formato/tamanho apenas por conveniência;
2. servidor valida cota e reserva;
3. cliente envia bytes;
4. servidor calcula tamanho real e SHA-256;
5. servidor confirma;
6. somente arquivo confirmado pode ser associado ao registro de negócio.

Persistir:

- tenant;
- finalidade;
- chave física;
- nome original;
- tamanho;
- MIME;
- SHA-256;
- estado.

Chave física usa tenant + UUID, nunca nome do escritório.

Download sempre autenticado.

## 20.2 Documento

Documento possui:

- nome;
- Tipo de Documento;
- descrição;
- arquivo vigente;
- revisão;
- vínculos.

Pode se vincular a:

- Pessoa;
- Processo;
- Atividade;
- Publicação;
- Lançamento.

Vincular não copia bytes.

Desvincular não exclui Documento.

## 20.3 Exclusão documental

Excluir Documento remove registro, vínculos e objeto físico.

Se remoção física não for confirmada:

- manter estado de exclusão pendente;
- bloquear edição;
- bloquear download;
- bloquear vínculo;
- bloquear substituição;
- continuar contando espaço;
- oferecer `Retomar exclusão`.

## 20.4 Biblioteca `/documentos/biblioteca`

```text
[Documentos]                       [Gerenciar modelos] [Incluir Documento]
[Requisitos de envio ▾]
[Pesquisar] [Tipo de Documento] [paginação]

| Documento | Tipo | Arquivo | Tamanho | Cadastrado em |
```

## 20.5 Inclusão de Documento

Um único Dialog:

1. selecionar arquivo;
2. transferir e confirmar;
3. nome;
4. tipo;
5. descrição;
6. vínculo opcional quando iniciado em outro registro;
7. cadastrar.

Nunca cadastrar Documento antes da confirmação do arquivo.

## 20.6 Ficha `/documentos/biblioteca/:id`

```text
[← Documentos] Nome             [Visualizar] [Baixar] [Substituir] [...]
               Tipo · arquivo

DOCUMENTO
  Pré-visualização
  divisor
  Dados
  divisor
  Vínculos
  divisor
  Arquivo

HISTÓRICO
```

Prévia local para PDF e imagens suportadas.

Outros formatos mostram indisponibilidade da prévia e oferecem download.

## 20.7 Modelos DOCX

Destino único:

```text
/conta/configuracoes/modelos
```

Contextos:

- Pessoa;
- Processo.

Operações:

- listar;
- cadastrar;
- editar metadados;
- substituir DOCX-base;
- validar;
- excluir;
- consultar inventário de variáveis.

Geração começa na Pessoa ou no Processo, nunca na tela de Modelos.

Sintaxe:

```text
{{contexto.campo}}
```

Variável aberta:

```text
{{aberto.nome}}
```

Fluxo de geração:

1. selecionar Modelo compatível;
2. resolver variáveis oficiais;
3. solicitar valores abertos;
4. gerar DOCX;
5. converter para PDF se solicitado e disponível;
6. entregar bytes;
7. salvar na Biblioteca somente por ação explícita.

Token inválido torna o Modelo inválido até correção.

Substituir tokens também em tabelas, cabeçalhos e rodapés quando a biblioteca permitir com segurança.

## Pronto quando

- reserva/upload/confirmação funcionam;
- cota é aplicada;
- Biblioteca funciona;
- vínculos funcionam;
- substituição preserva cadastro/vínculos;
- exclusão pendente é retomável;
- Modelo válido gera arquivo real;
- Modelo inválido não gera.

---

# 21. F7 — Financeiro

## 21.1 Lançamento

Naturezas:

- Receita;
- Despesa.

Relações opcionais:

- Pessoa;
- Processo;
- Documento quando aplicável.

Situação calculada:

- Em aberto;
- Parcialmente liquidado;
- Liquidado;
- Cancelado.

Situação não é seletor livre.

`Vencido` é condição derivada.

## 21.2 Regras

- baixa reduz saldo em aberto;
- estorno recompõe situação;
- cancelamento preserva histórico;
- reabertura segue regra de estado;
- transferência gera movimentos relacionados e não vira Receita/Despesa operacional comum;
- saldos dependem de abertura + movimentos reais;
- saldo sem base suficiente é `Indeterminado`, nunca `R$ 0,00`;
- servidor calcula todos os totais.

O Orvya registra fatos financeiros declarados. Não executa operação bancária externa por causa de uma baixa ou transferência interna.

## 21.3 Navegação

```text
Lançamentos | Movimentações | Fluxo de caixa | Conciliação bancária | Configurações
```

## 21.4 Lançamentos `/financeiro/lancamentos`

```text
[Financeiro]                                      [Novo lançamento] [...]
[contas/saldos]
[Pesquisa] [Natureza] [Situação] [Período] [Mais filtros] [paginação]

| Lançamento | Natureza | Principal | Em aberto | Vencimento | Situação |

Receitas em aberto: ...      Despesas em aberto: ...
```

`...`:

- Informar saldo de abertura;
- Registrar transferência;
- Atualizar.

Filtros secundários:

- campo de data;
- categoria;
- centro de custo;
- responsável;
- ordenação;
- direção;
- período personalizado.

Totais são do conjunto filtrado inteiro.

## 21.5 Ficha `/financeiro/lancamentos/:id`

Read-first com:

- dados;
- relações;
- parcelas quando existirem;
- baixas;
- Documentos;
- histórico.

Ações conforme situação:

- Editar;
- Baixar;
- Estornar;
- Cancelar;
- Reabrir.

## 21.6 Movimentações

Extrato com:

- pesquisa;
- período efetivo;
- origem;
- forma;
- ordenação;
- saldo corrido somente quando o recorte permite cálculo correto.

## 21.7 Fluxo de caixa

Entradas, saídas e totais temporais calculados pelo servidor.

## 21.8 Conciliação

Tela própria sobre os mesmos fatos financeiros. Não criar domínio financeiro paralelo.

## 21.9 Configurações

Gerenciar:

- contas bancárias e caixas;
- categorias;
- centros de custo;
- formas de pagamento.

Configurações do escritório não replica essas famílias.

## Pronto quando

- valores permanecem decimais exatos;
- baixa/estorno/cancelamento funcionam;
- idempotência impede efeito duplicado;
- transferência fecha contabilmente;
- saldos e totais são reproduzíveis;
- filtros e extrato retornam valores coerentes.

---

# 22. F8 — Relatórios

Relatório é projeção de dados reais, não tabela duplicada.

Fontes iniciais:

- Atividades;
- Publicações;
- Processos;
- Pessoas;
- Documentos;
- Financeiro;
- combinações autorizadas.

Definição pode declarar:

- período;
- dimensão temporal;
- filtros tipados;
- colunas;
- ordenação;
- agrupamento;
- totais.

## 22.1 Tela `/relatorios`

```text
[Relatórios]
[Relatório ▾] [Executar] [Exportar ▾]

[formulário gerado pela definição]

[parâmetros realmente executados]
[tabela paginada]
[totais]
```

Regras:

- o formulário pode mudar depois da execução;
- resultado permanece ligado aos parâmetros executados;
- mostrar aviso quando houver alterações ainda não aplicadas;
- nova execução substitui a referência atual;
- paginação e exportação usam a mesma referência;
- total representa conjunto inteiro.

Exportações:

- PDF;
- XLSX.

Acima de limite técnico, recusar com instrução para restringir filtros/colunas. Não cortar silenciosamente.

## 22.2 Definições salvas

`/relatorios/modelos` administra definições salvas se esse recurso for implementado.

Não criar segundo motor de Relatórios.

## Pronto quando

- definição tipada gera formulário;
- servidor aplica filtros/colunas/ordem;
- tabela, total, paginação e exportação usam a mesma referência;
- PDF/XLSX representam o conjunto executado.

---

# 23. F9 — Administração da Plataforma

Admin é uma aplicação própria em `admin.orvya.net`.

Administrador da Plataforma é identidade global e não pertence a escritório.

Sempre deve existir ao menos um Administrador da Plataforma ativo.

Não permitir suspender ou excluir o último ativo.

# 23.1 Cabeçalho do Admin

Desktop:

```text
[ORVYA · Administração da Plataforma › Página] [ PESQUISA ADMINISTRATIVA ] [◉]
```

A Pesquisa Administrativa fica **centralizada geometricamente no cabeçalho**, usando a mesma estrutura de três colunas do App.

Botões do cabeçalho do Admin também são **somente ícones**:

- Menu em largura estreita;
- conta/sessão;
- qualquer ação futura do cabeçalho.

Não usar botão textual `Sessão` no header.

O acionador da conta é Avatar/ícone com `aria-label` e Tooltip.

# 23.2 Sidebar

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

Uma única casca. Não criar seleção inicial entre painéis.

# 23.3 Dashboard

Ordem:

1. Pendências administrativas;
2. Estado da plataforma;
3. Distribuição por Plano;
4. Atividade recente.

Pendências podem incluir:

- contas que exigem atenção;
- Teste Grátis expirado;
- consumo acima de limite;
- convite com envio pendente;
- integração não configurada/diagnóstico ruim;
- pendência operacional real.

Estado da plataforma:

- contas ativas;
- contas suspensas;
- contas em teste;
- usuários ativos;
- Processos monitorados;
- armazenamento utilizado.

CPU, memória e disco ficam em Operação, não no Dashboard de negócio.

# 23.4 Escritórios

Listagem:

```text
[Escritórios] [Novo escritório]
[Pesquisa] [Status] [Plano] [paginação]

| Escritório | Status | Plano | Usuários | Processos monitorados | Criado em |
```

Ficha:

```text
[← Escritórios] Nome                   [Status] [Plano] [Acessar] [Editar] [...]
[Resumo] [Usuários] [Plano e utilização] [Histórico]
```

Resumo contém metadados administrativos, não conteúdo jurídico.

`Acessar` inicia acesso assistido.

# 23.5 Usuários globais

Pesquisa sobre usuários de contas.

Exibir somente:

- nome;
- e-mail;
- escritório;
- status;
- Administrador do Sistema;
- criação/atualização.

Não expor conteúdo jurídico.

# 23.6 Planos

CRUD de Planos.

Campos:

- nome;
- descrição;
- estrutural;
- recursos;
- limites.

Excluir Plano em uso exige Plano de destino e reatribuição das contas.

# 23.7 Administradores

Ações:

- adicionar;
- editar;
- suspender;
- reativar;
- excluir.

Proteção do último ativo é obrigatória no backend.

# 23.8 Permissões

Mostrar registro real de capacidades.

Campos úteis:

```text
Chave | Rótulo | Operação | Depende de | Recurso do Plano | Situação
```

Concessão de permissão ocorre na ficha do usuário do escritório, não nesta tabela global.

# 23.9 Catálogos

Separar:

- Catálogos Iniciais;
- Catálogos Referenciais;
- Variáveis de Documentos.

Catálogo Inicial fornece valores padrão para novas contas quando a regra pedir.

Catálogo Referencial é global e usado em dados como geografia e referências processuais.

Variável de Documento possui:

- token;
- descrição;
- origem;
- contextos;
- uso.

# 23.10 Integrações

Somente estas famílias externas fazem parte do produto:

1. E-mail;
2. Armazenamento de objetos;
3. Comunica CNJ.

Cada ficha, quando aplicável:

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

Salvar, Testar e Ativar são operações diferentes.

Segredos:

- nunca retornam completos;
- nunca aparecem em HTML;
- leitura mostra apenas presença/configuração;
- substituição de segredo grava novo valor criptografado.

## E-mail

Usado por:

- confirmação de cadastro;
- convite;
- recuperação de senha;
- mensagens transacionais explicitamente implementadas.

## Armazenamento

Compatível com S3 e endpoints equivalentes.

Usado por:

- Documentos;
- Modelos;
- logos;
- fotos de perfil;
- derivados persistidos somente quando a operação pedir salvamento.

## Comunica CNJ

Usado por:

- busca por Processo;
- busca por OAB;
- monitoramento;
- recebimento de Publicações.

Uma rotina central varre monitoramentos elegíveis. Não criar agendador por Processo.

# 23.11 Operação

## Visão operacional

Mostrar:

- API;
- worker;
- banco;
- armazenamento;
- e-mail;
- integração judicial;
- versão da aplicação;
- revisão do schema;
- últimas execuções relevantes.

## Serviços

Listar somente componentes conhecidos.

Comandos são allowlisted. Nunca aceitar shell arbitrário pela API.

## Execuções

Estados:

- Em andamento;
- Concluída;
- Erro.

Mostrar tipo, início, fim, resumo e erro sanitizado.

## Banco de dados

Mostrar estado e metadados seguros.

Nunca exibir DSN completo ou credenciais.

## Migrations

Nesta reconstrução, página somente de leitura:

```text
| Revisão | Descrição | Situação | Aplicada em |
```

Migration é aplicada pelo deploy.

## Capacidade

CPU, memória e disco.

## Operações e Limitações

Mostrar recursos bloqueados e razões objetivas.

# 23.12 Auditoria

Histórico da Plataforma:

```text
| Data/hora | Área | Ação | Autor | Alvo | Resultado |
```

Filtros:

- período;
- área;
- ação;
- autor;
- texto.

Conciliação Técnica mostra inconsistências operacionais detectadas, sem transformar a tabela em editor genérico de banco.

## Pronto quando

- login Admin é separado do App;
- casca única funciona;
- Pesquisa Administrativa funciona;
- contas, usuários, Planos e administradores funcionam;
- integrações mostram estado real;
- operação não aceita comando arbitrário;
- acesso assistido preserva identidade do administrador;
- auditoria registra ações críticas.

---

# 24. Worker

Um único worker atende toda a instalação.

Responsabilidades:

- monitoramento judicial;
- recebimento e deduplicação de Publicações;
- expiração do Teste Grátis;
- envio transacional de e-mail;
- limpeza de reservas de arquivo abandonadas;
- conversões documentais demoradas;
- reconciliação temporal de Notificações;
- demais tarefas persistentes explicitamente exigidas.

Não criar worker por tenant.

Tarefa persistente possui:

- ID;
- tipo;
- payload mínimo;
- estado;
- tentativas;
- próxima tentativa;
- erro resumido;
- timestamps;
- chave de idempotência quando necessária.

Retries são limitados e idempotentes.

---

# 25. Histórico funcional

Histórico do escritório e Histórico da Plataforma são separados.

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

Fatos típicos:

- criação;
- edição relevante;
- mudança de Situação;
- parte adicionada/removida;
- responsável alterado;
- Atividade criada/vinculada;
- Documento vinculado/desvinculado;
- operação financeira vinculada;
- monitoramento alterado.

Não criar botão genérico `Adicionar histórico`.

Um evento manual de caso é Atividade da modalidade Evento.

---

# 26. Estados da interface

Toda consulta trata explicitamente:

- carregando;
- vazio;
- erro;
- indisponível;
- pronto;
- atualizando mantendo conteúdo anterior, quando seguro.

Regras:

- `Indisponível` não é zero;
- horário ausente não vira `00:00`;
- saldo indeterminado não vira zero;
- falta de permissão não vira lista vazia enganosa;
- recurso fora do Plano não é apresentado como falha técnica;
- acervo vazio e filtro sem resultado usam mensagens diferentes.

Use componentes Spectrum adequados para feedback e estado.

---

# 27. Acessibilidade

Preservar os comportamentos oficiais do Spectrum 2.

Obrigatório:

- teclado completo;
- foco visível;
- labels reais;
- nomes acessíveis de botões de ícone;
- `aria-current` na navegação;
- foco contido em Dialog;
- foco devolvido ao acionador ao fechar;
- contraste;
- toque;
- movimento reduzido;
- alto contraste;
- texto ampliado;
- tabela navegável;
- cor nunca como único sinal.

Não remover outline/focus ring para estética.

---

# 28. Deploy

Objetivo: instalação ou atualização controlada em VPS Linux com Docker disponível.

Fluxo:

```text
1. validar .env
2. construir imagens
3. iniciar PostgreSQL
4. aguardar readiness do banco
5. executar alembic upgrade head
6. iniciar API
7. iniciar worker
8. iniciar ops
9. construir App e Admin
10. publicar assets
11. iniciar/recarregar Nginx
12. verificar /api/v1/saude
13. verificar /api/v1/saude/pronto
14. smoke HTTP dos dois hosts
```

Hosts:

```text
app.orvya.net
admin.orvya.net
```

`/api/v1/*` é proxy para a API.

Arquivos de usuário não ficam em diretório público do Nginx.

TLS usa certificado válido e renovação automatizada pela infraestrutura escolhida.

---

# 29. Dados iniciais

Criar somente o necessário para funcionamento:

- identidade da instalação;
- primeiro Administrador da Plataforma por comando seguro;
- Plano estrutural de Teste Grátis;
- recursos padrão;
- catálogos mínimos que impediriam fluxos fundamentais de nascerem travados.

Não criar Pessoas, Processos, Atividades, Publicações ou Lançamentos fictícios.

## 29.1 Catálogos mínimos

Conta:

- Situações de Processo;
- Tipos de Audiência;
- Tipos de Prazo;
- Tipos de Tarefa;
- Tipos de Evento;
- Formas de realização;
- Tipos de Documento;
- Tipos de contato;
- Finalidades de endereço;
- Tipos de identificação;
- Tipos de vínculo entre Pessoas;
- polos processuais se não forem enum estrutural.

Financeiro não recebe categorias comerciais inventadas. Escritório configura contas, categorias, centros e formas.

---

# 30. Estratégia de testes

A qualidade é obrigatória. A ordem é que deve ser econômica.

## Gate A — Fundação

Executar somente:

- migration em banco vazio;
- import/início da API;
- typecheck;
- build App/Admin;
- login mínimo.

## Gate B — Núcleo jurídico

Depois de Pessoas + Processos + Atividades:

- criar conta de teste;
- Pessoa;
- Processo;
- Atividade;
- Agenda;
- isolamento simples entre duas contas.

Corrigir apenas bloqueios estruturais. Continuar.

## Gate C — Conteúdo externo e arquivos

Depois de Publicações + Documentos:

- storage simulado/local compatível;
- upload/confirmar/download;
- geração DOCX;
- ingestão deduplicada de Publicação com duplo controlado.

## Gate D — Financeiro

- Receita;
- Despesa;
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
- proteção do último administrador.

## Gate F — Estabilização final

Somente após o produto inteiro existir:

1. banco totalmente vazio;
2. migration;
3. typecheck;
4. builds;
5. testes de integração de alto valor;
6. stack completa;
7. dois tenants reais de teste;
8. isolamento entre tenants;
9. jornada completa do App;
10. jornada completa do Admin;
11. responsividade 320/375/768/1440;
12. teclado/foco;
13. corrigir todos os defeitos;
14. repetir somente testes afetados + smoke integral final.

Não perseguir porcentagem arbitrária de cobertura.

---

# 31. Testes automatizados mínimos de alto valor

## Backend

- login e expiração de sessão;
- CSRF;
- isolamento entre tenants;
- permissão negada;
- conflito de revisão;
- duplicidade relevante de Pessoa;
- Processo de outro tenant invisível;
- transições de Atividade;
- cálculo de atraso;
- Publicação deduplicada;
- upload/cota;
- exclusão documental pendente;
- dinheiro decimal;
- idempotência financeira;
- expiração do Teste Grátis;
- proteção do último Administrador da Plataforma.

## Frontend E2E

Uma jornada por superfície é suficiente inicialmente.

App:

```text
cadastro → confirmação → login
→ Área de trabalho
→ Pessoa
→ Processo
→ Atividade/Agenda
→ Documento
→ Lançamento
→ Relatório
→ Configurações
```

Admin:

```text
login
→ Dashboard
→ Escritório
→ Plano
→ Integração
→ acesso assistido
→ retorno ao Admin
```

---

# 32. O que não construir

Não adicionar sem nova decisão explícita:

- microserviços por módulo;
- event sourcing;
- CQRS;
- GraphQL;
- busca vetorial;
- editor DOCX interno;
- white-label;
- temas por escritório;
- preços;
- cobrança;
- gateway de pagamento;
- checkout;
- aplicativo mobile nativo;
- chat interno;
- CRM paralelo;
- segundo cadastro de Agenda;
- segundo cadastro de Documento;
- segundo motor Financeiro;
- segundo motor de Relatórios;
- fila por tenant;
- shell remoto arbitrário;
- Design System próprio;
- biblioteca de componentes concorrente ao Spectrum 2;
- paleta CSS paralela;
- suíte enorme de testes antes do produto funcionar.

Recurso não descrito neste arquivo não deve ser criado por simetria ou conveniência.

---

# 33. Definition of Done por fatia

Antes de marcar uma fatia como concluída, confirmar apenas:

```text
[ ] schema/migration existente
[ ] regra de domínio no servidor
[ ] tenant e permissão aplicados
[ ] consultas principais
[ ] comandos principais
[ ] erro estruturado
[ ] cliente frontend
[ ] listagem/ficha/formulário correspondente
[ ] estados carregando/vazio/erro/indisponível
[ ] smoke curto ponta a ponta
```

Não exigir documentação separada ou bateria completa a cada fatia.

---

# 34. Checklist final do produto

## Acesso

- [ ] Cadastro por e-mail e senha.
- [ ] Confirmação de e-mail.
- [ ] Login.
- [ ] Recuperação de senha.
- [ ] Sessão 30 min/8 h.
- [ ] App/Admin com cookies separados.
- [ ] CSRF.
- [ ] Conta Suspensa bloqueada.
- [ ] Usuário Suspenso bloqueado.
- [ ] Convite.
- [ ] Permissões no backend.

## Cabeçalho

- [ ] Nenhum nome de escritório no cabeçalho.
- [ ] Pesquisa Global centralizada geometricamente.
- [ ] Pesquisa Administrativa centralizada geometricamente.
- [ ] Botões do cabeçalho somente ícones.
- [ ] Cada botão de ícone com `aria-label`.
- [ ] Tooltip quando adequado.
- [ ] Avatar/ícone de conta sem texto ao lado.

## Spectrum 2

- [ ] App usa somente Spectrum 2.
- [ ] Admin usa somente Spectrum 2.
- [ ] Provider configurado.
- [ ] SideNav Spectrum.
- [ ] TableView Spectrum onde tabela for adequada.
- [ ] Dialog/Menu/Form Spectrum.
- [ ] custom styling somente por tokens/macros.
- [ ] ícones Spectrum.
- [ ] nenhuma biblioteca visual concorrente.

## Pessoas

- [ ] CRUD.
- [ ] contatos.
- [ ] endereços.
- [ ] identificações.
- [ ] vínculos.
- [ ] principais.
- [ ] ficha read-first.
- [ ] Processos relacionados.
- [ ] Documentos relacionados.
- [ ] Financeiro relacionado quando autorizado.

## Processos

- [ ] Judicial.
- [ ] Administrativo.
- [ ] partes.
- [ ] responsáveis.
- [ ] monitoramento.
- [ ] buscas processuais.
- [ ] ficha-hub.
- [ ] Atividades.
- [ ] Publicações.
- [ ] Documentos.
- [ ] Financeiro.
- [ ] Histórico.

## Atividades

- [ ] Audiência.
- [ ] Prazo.
- [ ] Tarefa.
- [ ] Evento.
- [ ] Pendentes/Concluídas/Canceladas.
- [ ] atraso derivado.
- [ ] Agenda Lista/Dia/Semana/Mês.
- [ ] arraste + alternativa por comando.
- [ ] página própria.
- [ ] reagendar/redesignar.
- [ ] confirmações das transições críticas.

## Área de trabalho

- [ ] Minhas atividades em 67% aproximados.
- [ ] calendário + resumo na coluna lateral.
- [ ] empilhamento mobile correto.
- [ ] Hoje/Esta semana/Este mês.
- [ ] Sem data.
- [ ] filtro por dia.
- [ ] vencidas apenas com data/hora negativa.
- [ ] ação rápida única Concluir.
- [ ] calendário compacto sem conteúdo textual por dia.
- [ ] resumo com quatro linhas exatas.

## Publicações

- [ ] ingestão externa.
- [ ] deduplicação.
- [ ] Nova/Tratada.
- [ ] conteúdo seguro.
- [ ] providência.
- [ ] Concluir.
- [ ] Concluir e abrir a próxima.
- [ ] Descartar.
- [ ] sequência preserva recorte.

## Documentos

- [ ] reserva/upload/confirmação.
- [ ] Biblioteca.
- [ ] vínculos.
- [ ] download autenticado.
- [ ] prévia.
- [ ] substituir arquivo.
- [ ] exclusão retomável.
- [ ] Modelos DOCX.
- [ ] variáveis.
- [ ] geração por Pessoa.
- [ ] geração por Processo.

## Financeiro

- [ ] Receita/Despesa.
- [ ] parcelas.
- [ ] baixa.
- [ ] estorno.
- [ ] cancelamento/reabertura.
- [ ] transferência.
- [ ] saldos.
- [ ] Movimentações.
- [ ] Fluxo.
- [ ] Conciliação.
- [ ] Configurações.
- [ ] decimal exato.
- [ ] idempotência.

## Relatórios

- [ ] catálogo.
- [ ] definição tipada.
- [ ] filtros.
- [ ] colunas.
- [ ] ordenação.
- [ ] agrupamento.
- [ ] paginação por referência.
- [ ] totais.
- [ ] PDF.
- [ ] XLSX.

## Admin

- [ ] casca única.
- [ ] Dashboard.
- [ ] Escritórios.
- [ ] ficha de Escritório.
- [ ] Usuários globais.
- [ ] Planos.
- [ ] Administradores.
- [ ] Permissões.
- [ ] Catálogos.
- [ ] Variáveis.
- [ ] Integrações.
- [ ] Operação.
- [ ] Auditoria.
- [ ] acesso assistido.

## Integrações

- [ ] E-mail configurável/testável.
- [ ] Armazenamento configurável/testável.
- [ ] Comunica CNJ configurável/testável.
- [ ] ausência de configuração não quebra o núcleo.

## Deploy

- [ ] comando único documentado.
- [ ] PostgreSQL.
- [ ] migration controlada.
- [ ] API.
- [ ] worker.
- [ ] ops.
- [ ] Nginx.
- [ ] HTTPS.
- [ ] App.
- [ ] Admin.
- [ ] health/readiness.
- [ ] logs sem segredos.

---

# 35. Ordem de commits sugerida

Manter poucos commits grandes:

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

O nome do commit pode variar. O importante é evitar centenas de commits cerimoniais.

---

# 36. Instrução final para o agente implementador

> Construa o Orvya completo neste repositório seguindo este `ORVYA.md` como especificação única. Implemente por fatias verticais, na ordem de dependência indicada, sempre conectando banco, regra, API e interface antes de avançar. Use Adobe Spectrum 2 exclusivamente no App e no Admin. O cabeçalho do App não mostra o nome do escritório; a Pesquisa Global deve ficar centralizada geometricamente e os botões do cabeçalho devem ser somente ícones com nomes acessíveis. Preserve os contratos canônicos do Orvya em português, o isolamento multi-tenant, as permissões server-side, revisões concorrentes, histórico e precisão financeira. Faça apenas verificações curtas nos grandes marcos e deixe a bateria completa para a estabilização final. Não replique complexidade histórica que não esteja descrita aqui. Termine somente quando a instalação limpa estiver funcional, segura, responsiva, reproduzível e com os smoke tests finais aprovados.
