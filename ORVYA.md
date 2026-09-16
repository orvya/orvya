# ORVYA — especificação única para reconstrução integral

> **Finalidade:** este arquivo é o briefing técnico e funcional único para recriar o Orvya do zero, com o comportamento atual, em uma execução autônoma de codificação.
>
> **Destino:** `orvya/orvya`, branch `main`.
>
> **Base consolidada:** `orvya/orvya-base`, branch `principal`, até o commit `f11abd463f27cbdc3515fc14de272bbd86767d62` de 15/09/2026 no horário do Brasil. Esse recorte já inclui a evolução UX mais recente, inclusive a decisão D-31 da Área de trabalho.
>
> Este documento descreve **o produto que deve existir ao final**, não o caminho histórico usado para construí-lo.

---

## 1. Instrução para a IA que vai construir o sistema

Crie o Orvya inteiro neste repositório, do zero ao deploy, sem solicitar aprovação entre etapas. Trabalhe até existir uma instalação funcional.

Regras de execução:

1. Use este arquivo como especificação principal e suficiente.
2. Não replique a arquitetura histórica do `orvya-base`; replique o **produto e o comportamento atuais**.
3. Prefira a solução mais simples que preserve segurança, isolamento entre escritórios, regras jurídicas/financeiras, UX e integrações descritas aqui.
4. Não crie microserviços sem necessidade. O padrão é um **monólito modular**.
5. Não crie uma coleção de documentos de especificação. Este arquivo continua sendo a referência do produto.
6. Não porte o histórico de migrations. Crie **uma migration inicial limpa** com o schema final e migrations adicionais somente se forem necessárias durante a própria implementação.
7. Não porte harnesses, evidências, scripts de conformidade, fixtures históricas ou testes acumulados do projeto anterior.
8. Não pare a implementação para perseguir cobertura de testes. Faça verificações rápidas nos grandes marcos e uma estabilização completa ao final.
9. Quando um detalhe de implementação não estiver prescrito, escolha a opção convencional, pequena e sustentável.
10. Não invente preços, cobrança, checkout ou regras comerciais que não estejam aqui.
11. Não simule sucesso de integração externa. Quando credenciais não existirem, implemente o contrato e mostre **Não configurado/Indisponível** com a razão.
12. Não coloque segredos no Git. Use variáveis de ambiente.
13. Commits devem acompanhar apenas grandes marcos, sem fragmentar o trabalho em dezenas de commits cerimoniais.
14. Se um erro aparecer durante a implementação e não impedir o avanço estrutural, anote-o e prossiga. Corrija tudo na estabilização final.
15. Ao terminar, o repositório deve subir em ambiente limpo com um comando documentado.

### Critério de conclusão

O trabalho está concluído quando:

- banco vazio sobe e migra sozinho;
- cadastro, login e sessões funcionam;
- isolamento multi-tenant está garantido no servidor;
- App, Admin e Site compilam e funcionam;
- os módulos e páginas abaixo estão implementados;
- os fluxos principais funcionam de ponta a ponta;
- integrações sem credencial aparecem corretamente como não configuradas;
- deploy HTTPS está operacional;
- smoke tests finais passam;
- não há erro de build, typecheck ou migration.

---

## 2. O que é o Orvya

Orvya é um SaaS brasileiro para organização e gestão da rotina jurídica de advogados e escritórios.

O produto conecta em um único contexto:

- Pessoas e clientes;
- Processos judiciais e administrativos;
- Agenda e Atividades;
- Publicações judiciais;
- Documentos e Modelos DOCX;
- Financeiro;
- Relatórios;
- Alertas e Pesquisa Global;
- Configurações do escritório;
- Administração global da plataforma.

Há uma instalação compartilhada e vários escritórios isolados. O escritório é o tenant.

### Superfícies

| Superfície | Domínio esperado | Função |
|---|---|---|
| Site | `orvya.net` | landing page, apresentação, planos sem preço e entrada para teste grátis |
| App | `app.orvya.net` | produto do escritório |
| Admin | `admin.orvya.net` | administração global da plataforma |

A API usa o prefixo `/api/v1`.

---

## 3. Princípios que não podem ser simplificados

A implementação pode ser menor que a anterior. Estas regras não podem ser removidas:

### 3.1 Multi-tenant real

- O `account_id`/escritório atual vem da sessão autenticada.
- O cliente nunca escolhe nem envia um tenant confiável para uma operação normal.
- Toda query tenant-scoped aplica `account_id` no servidor.
- IDs de outro escritório devem resultar em não encontrado/negado sem vazar existência.
- Administrador da Plataforma é uma identidade separada do usuário de escritório.
- Acesso assistido a um escritório exige ação explícita e gera histórico.

### 3.2 Uma fonte por informação

Não duplique semanticamente o mesmo dado em módulos diferentes. Relações devem apontar para o registro original.

Exemplos:

- Atividade vinculada a Processo continua sendo uma Atividade única.
- Documento vinculado a Pessoa/Processo não vira cópia.
- Pessoa usada em um Processo continua sendo a mesma Pessoa.
- Catálogos financeiros são lidos pelo Financeiro, não recriados em formulários isolados.

### 3.3 Autoridade do servidor

O servidor decide:

- permissões;
- limites de Plano;
- situações derivadas;
- atraso;
- valores financeiros e totais;
- tenant atual;
- transições válidas;
- conflitos de revisão;
- ações críticas.

A interface apenas apresenta e solicita operações.

### 3.4 Semântica correta de ausência

- Ausente não vira zero.
- Indisponível não vira vazio silencioso.
- Horário ausente não vira `00:00`.
- Saldo indeterminado não vira `R$ 0,00`.
- Campo ausente deve aparecer como `Não informado` ou `Indisponível`, conforme o caso, mas esses textos nunca são persistidos como dado.

---

## 4. Arquitetura alvo simplificada

Use um **monorepo, monólito modular e um banco PostgreSQL**.

```text
orvya/
├─ ORVYA.md
├─ README.md
├─ .env.example
├─ docker-compose.yml
├─ backend/
│  ├─ pyproject.toml ou requirements.txt
│  ├─ alembic.ini
│  ├─ migrations/
│  └─ app/
│     ├─ main.py
│     ├─ config.py
│     ├─ db.py
│     ├─ auth.py
│     ├─ permissions.py
│     ├─ models/
│     ├─ schemas/
│     ├─ api/
│     ├─ services/
│     ├─ integrations/
│     ├─ worker.py
│     └─ ops.py
├─ frontend/
│  ├─ package.json
│  ├─ apps/
│  │  ├─ site/
│  │  ├─ app/
│  │  └─ admin/
│  └─ shared/
└─ deploy/
   ├─ nginx.conf
   ├─ Dockerfile.backend
   └─ Dockerfile.frontend
```

### Serviços de runtime

Use Docker Compose, salvo impedimento objetivo:

1. `postgres` — PostgreSQL;
2. `api` — FastAPI;
3. `worker` — jobs e sincronizações;
4. `ops` — executor mínimo e allowlisted para operações administrativas que não devem rodar dentro do processo web;
5. `nginx` — arquivos estáticos, três hosts e proxy da API.

Não separar domínios de negócio em serviços independentes.

---

## 5. Stack

Preserve a família tecnológica atual, sem necessidade de reproduzir cada versão patch se uma dependência compatível e estável estiver disponível.

### Backend

- Python 3.13;
- FastAPI;
- Uvicorn;
- SQLAlchemy 2;
- PostgreSQL + psycopg 3;
- Alembic;
- Pydantic 2;
- Argon2id para senha;
- HTTPX para integrações HTTP;
- boto3/S3 para objetos;
- bibliotecas pequenas e maduras para DOCX, XLSX e PDF quando necessárias.

### Frontend

- Node 24+;
- TypeScript;
- React 18;
- Vite;
- npm workspaces;
- MongoDB LeafyGreen como design system do App/Admin;
- fonte Inter self-hosted no App/Admin;
- Site pode manter tipografia editorial própria.

### Identidade visual

- nome sempre **Orvya**;
- usar a logotipo oficial completa e o emblema oficial em SVG;
- não redesenhar nem substituir a marca por texto comum;
- cor primária da interface: família **BLUE** do LeafyGreen;
- o azul principal da identidade atual corresponde a `#016BF8` quando for necessário um valor fixo;
- fundos predominantemente brancos, hierarquia por espaçamento, tipografia, divisores e estados, evitando excesso de caixas.

---

## 6. Configuração e segredos

Forneça `.env.example` sem valores sensíveis.

Variáveis mínimas:

```text
DATABASE_URL=
APP_BASE_URL=https://app.orvya.net
ADMIN_BASE_URL=https://admin.orvya.net
SITE_BASE_URL=https://orvya.net
SESSION_SECRET=
ENCRYPTION_KEY=
SMTP_HOST=
SMTP_PORT=
SMTP_USER=
SMTP_PASSWORD=
SMTP_FROM=
GOOGLE_CLIENT_ID=
GOOGLE_CLIENT_SECRET=
S3_ENDPOINT=
S3_REGION=
S3_BUCKET=
S3_ACCESS_KEY=
S3_SECRET_KEY=
CNJ_BASE_URL=
CNJ_TOKEN=
OPS_TOKEN=
```

Nenhuma integração externa é requisito para o processo local iniciar. Sem configuração, a UI deve explicar a indisponibilidade.

---

## 7. Modelo de segurança e acesso

### 7.1 Sessão

- sessão opaca no servidor;
- cookie `HttpOnly`, `Secure`, `SameSite=Lax` ou mais restritivo quando possível;
- cookies host-only separados para App e Admin;
- expiração por inatividade: 30 minutos;
- duração máxima: 8 horas;
- CSRF server-side em mutações autenticadas.

### 7.2 Senhas

- Argon2id;
- nunca registrar senha ou token em log;
- recuperação por e-mail com token de uso único e expiração curta.

### 7.3 Entradas

App:

- e-mail + senha;
- Google Auth, quando configurado.

Admin:

- sessão e identidade próprias;
- não compartilhar cookie do App.

### 7.4 Papéis

- Administrador do Escritório: acesso completo à conta, sujeito ao Plano;
- Usuário comum: capacidades granulares;
- Administrador da Plataforma: acesso global administrativo;
- acesso assistido: Administrador da Plataforma assume contexto de um escritório de forma explícita, temporária e auditada.

Permissão é sempre verificada na API, mesmo se o botão já estiver oculto.

---

## 8. Planos e Teste Grátis

- O cadastro público cria o primeiro Administrador do Escritório e o escritório.
- Teste grátis estrutural: **7 dias**.
- O Site mostra Planos e recursos/limites, **sem preços**.
- Não existe checkout do escritório nesta versão.
- O Plano é definido pela Administração da Plataforma.
- Limites principais: usuários, Processos monitorados e armazenamento.
- Recursos podem habilitar/desabilitar módulos como Publicações, Documentos, Modelos, Financeiro, Relatórios e Google Calendar.
- Downgrade não deve apagar dados existentes. Bloqueie novas ações que excedam o Plano e explique a razão.
- Ao expirar o teste, a conta pode ser suspensa conforme regra do serviço central.
- A Área de trabalho mostra aviso discreto do Teste Grátis enquanto aplicável.

---

## 9. Banco de dados — famílias de entidades

Use UUID como identificador principal, timestamps timezone-aware para instantes e `DATE` para datas civis.

Não é necessário copiar nomes de tabelas do legado. Mantenha relações e regras.

### 9.1 Globais

- `plans`
- `plan_features`
- `plan_limits`
- `platform_admins`
- `platform_admin_permissions`
- `global_catalogs` / itens referenciais
- `integration_configs`
- `document_variables`
- `platform_audit_events`
- `backup_records`
- `operation_runs`

### 9.2 Tenant

- `accounts`
- `users`
- `user_permissions`
- `invitations`
- `sessions`
- `external_identities`
- `people`
- `person_contacts`
- `person_addresses`
- `person_identifications`
- `person_links`
- `processes`
- `process_parties`
- `process_owners`
- `process_monitoring`
- `judicial_searches`
- `activities`
- `activity_types/catalogs`
- `publications`
- `publication_actions`
- `files`
- `documents`
- `document_links`
- `document_templates`
- `template_variables`
- `financial_accounts`
- `financial_categories`
- `cost_centers`
- `payment_methods`
- `financial_entries`
- `financial_settlements`
- `financial_transfers`
- `bank_reconciliations`
- `alerts`
- `notification_preferences`
- `google_calendar_connections`
- `google_calendar_links`
- `report_definitions` quando houver definição persistida
- `audit_events`

Inclua `account_id` em todas as entidades tenant-scoped em que fizer sentido e índices compostos iniciando por `account_id` nas consultas frequentes.

### 9.3 Revisão otimista

Registros mutáveis importantes recebem inteiro `revision`.

Mutações de edição/substituição enviam `expected_revision`. Divergência retorna `409 Conflict`, nunca sobrescreve silenciosamente.

### 9.4 Dinheiro

- banco: `NUMERIC`, nunca float;
- backend: `Decimal`;
- API: string decimal;
- frontend: string formatada;
- somas e situações são calculadas no servidor.

---

## 10. Convenções da API

Prefixo: `/api/v1`.

### 10.1 Resposta de lista

```json
{
  "items": [],
  "total": 0,
  "page": 1,
  "page_size": 25,
  "as_of": "2026-09-15T21:00:00-03:00"
}
```

### 10.2 Erro

```json
{
  "code": "codigo_estavel",
  "message": "Mensagem legível",
  "field": null,
  "details": null
}
```

### 10.3 Listagens

- pesquisa `q`;
- paginação no servidor;
- filtros no servidor;
- ordenação no servidor quando afeta conjunto completo;
- `as_of` para deixar claro o instante da leitura;
- totais precisam corresponder ao **conjunto filtrado inteiro**, não à página.

### 10.4 Ações críticas

Excluir, cancelar, substituir bytes, desconectar integração e demais ações marcadas como críticas recebem confirmação e, quando indicado, `justification` entre 5 e 500 caracteres. O servidor valida e registra autor + instante + alvo + justificativa.

---

## 11. Mapa de API funcional

Não é obrigatório manter cada URL interna histórica. Mantenha estes recursos e capacidades de forma consistente.

### Público e acesso

```text
GET    /site/planos
POST   /cadastro
POST   /auth/login
POST   /auth/google/iniciar
GET    /auth/google/callback
POST   /auth/logout
POST   /auth/recuperacao
POST   /auth/redefinicao
GET    /sessao
```

### Escritório e equipe

```text
GET/PATCH  /escritorio/configuracoes
GET        /escritorio/configuracoes/utilizacao
GET/POST   /usuarios
GET/PATCH/DELETE /usuarios/{id}
POST       /convites
GET/PATCH  /permissoes
GET/POST/PATCH/DELETE /catalogos/...
```

### Pessoas

```text
GET/POST   /pessoas
GET/PATCH/DELETE /pessoas/{id}
GET/POST/DELETE /pessoas/{id}/vinculos
GET        /pessoas/{id}/historico
```

Contatos, endereços e identificações podem ser sub-recursos.

### Processos

```text
GET/POST   /processos
GET/PATCH/DELETE /processos/{id}
POST/DELETE /processos/{id}/partes
POST/DELETE /processos/{id}/responsaveis
POST       /processos/{id}/monitoramento
GET        /processos/{id}/historico
GET/POST   /processos/buscas
```

### Agenda e Atividades

```text
GET/POST   /atividades
GET/PATCH/DELETE /atividades/{id}
POST       /atividades/{id}/concluir
POST       /atividades/{id}/reabrir
POST       /atividades/{id}/cancelar
GET        /agenda/resumo
GET        /agenda/calendario
```

### Publicações

```text
GET        /publicacoes
GET        /publicacoes/{id}
POST       /publicacoes/{id}/providencias
POST       /publicacoes/{id}/concluir
DELETE     /publicacoes/{id}
POST       /publicacoes/sincronizar
```

Não há cadastro manual de Publicação.

### Arquivos, Documentos e Modelos

```text
POST       /arquivos/reservar
POST/PUT   /arquivos/{id}/conteudo
POST       /arquivos/{id}/confirmar
GET        /arquivos/{id}/conteudo
GET/POST   /documentos
GET/PATCH/DELETE /documentos/{id}
POST       /documentos/{id}/substituir-arquivo
POST/DELETE /documentos/{id}/vinculos
GET        /documentos/{id}/historico
GET/POST   /modelos
GET/PATCH/DELETE /modelos/{id}
POST       /modelos/{id}/substituir-docx
POST       /modelos/{id}/validar
POST       /modelos/{id}/gerar
GET        /variaveis
```

### Financeiro

```text
GET/POST   /financeiro/lancamentos
GET/PATCH  /financeiro/lancamentos/{id}
POST       /financeiro/lancamentos/{id}/baixas
POST       /financeiro/lancamentos/{id}/estorno
POST       /financeiro/lancamentos/{id}/cancelar
POST       /financeiro/lancamentos/{id}/reabrir
GET        /financeiro/saldos
GET        /financeiro/movimentacoes
GET        /financeiro/fluxo
GET/POST   /financeiro/transferencias
GET/POST   /financeiro/conciliacoes
GET/POST/PATCH/DELETE /financeiro/configuracoes/...
```

### Trabalho, alertas e pesquisa

```text
GET        /dashboard
GET        /alertas
POST       /alertas/{id}/ler
POST       /alertas/ler-todos
GET        /pesquisa
GET        /historico/...
```

### Relatórios

```text
GET        /relatorios/catalogo
POST       /relatorios/executar
POST       /relatorios/exportar
```

### Perfil e Google Calendar

```text
GET/PATCH  /perfil
POST/DELETE /perfil/foto
GET/PATCH  /perfil/preferencias-notificacoes
GET        /integracoes/google-calendar/estado
POST       /integracoes/google-calendar/conectar
GET        /integracoes/google-calendar/callback
POST       /integracoes/google-calendar/sincronizar
DELETE     /integracoes/google-calendar
GET        /integracoes/google-calendar/diagnostico
```

### Admin

Use `/admin/...` para contas, usuários globais, Planos, administradores, permissões, catálogos, variáveis, integrações, operações, backups, banco, migrations, histórico e pesquisa administrativa.

### Saúde

```text
GET /saude
GET /saude/pronto
GET /saude/dependencias
```

---

## 12. Regras de negócio por domínio

### 12.1 Pessoas

Pessoa pode ser Física ou Jurídica e possui uma página central.

- Nome é obrigatório.
- Documento pode ser CPF/CNPJ conforme natureza.
- Contatos, endereços e identificações são coleções do mesmo cadastro.
- Um item de coleção pode ser principal.
- Pessoa pode ter vínculos com outras Pessoas.
- Pessoa pode participar de Processos, Documentos e lançamentos financeiros.
- Excluir Pessoa não apaga Processos, Documentos e lançamentos independentes.

### 12.2 Processos

Dois tipos:

- Judicial;
- Administrativo.

Judicial pode ter número CNJ e monitoramento.

Processo é o **hub de trabalho** e reúne, por relação:

- Partes;
- Responsáveis;
- Atividades;
- Publicações;
- Documentos;
- Financeiro;
- Histórico.

Monitoramento só pode ser ativado quando os dados necessários existirem. O servidor controla limite do Plano.

### 12.3 Atividades

Uma tabela/entidade serve à Agenda e ao Processo.

Modalidades:

- Audiência;
- Prazo;
- Tarefa;
- Evento.

Estado básico:

- Pendente;
- Concluída;
- Cancelada.

**Atrasada não é estado.** É condição derivada pelo servidor sobre uma Atividade pendente.

Tipos/itens das modalidades vêm dos Catálogos e possuem cor. Cor é apoio visual, nunca único indicador.

Atividade pode estar sem data quando a modalidade permitir. Sem horário continua sem horário.

### 12.4 Publicações

- chegam por monitoramento/integrador, nunca por cadastro manual;
- condições: `Nova` e `Tratada`;
- descartar remove o registro, não cria estado `Excluída`;
- conteúdo externo é sempre apresentado como texto, nunca HTML executável;
- pode gerar providência/Atividade;
- concluir e descartar são ações auditáveis;
- Publicação vinculada a Processo mantém esse contexto em suas providências.

### 12.5 Documentos

Documento = metadados + um arquivo físico vigente + zero ou mais vínculos.

Upload correto:

1. reservar arquivo;
2. transferir bytes;
3. confirmar hash/tamanho;
4. somente então cadastrar Documento.

Limite atual da Biblioteca: **100 MB por arquivo**.

Um Documento pode vincular-se a:

- Pessoa;
- Processo;
- Atividade;
- Publicação;
- Financeiro.

Remover vínculo não remove Documento.

Substituir arquivo preserva cadastro, vínculos e histórico. O arquivo antigo só é removido depois de o novo estar confirmado como vigente.

Se a remoção física durante exclusão não for confirmada, mantenha `deletion_pending_since`, bloqueie alteração/download e ofereça **Retomar exclusão**. O espaço continua contado até a exclusão terminar.

Pré-visualização local:

- PDF;
- PNG/JPEG/WebP.

Outros formatos: informar indisponibilidade e oferecer download.

### 12.6 Modelos de documentos

- Modelos são DOCX;
- ficam em Configurações do escritório, não como módulo principal;
- possuem contexto `Pessoa` ou `Processo`;
- variáveis usam sintaxe `{{variavel}}`;
- validar tokens antes de habilitar geração;
- Modelo inválido permanece visível, mas não gera;
- geração cria Documento vinculado ao contexto de origem;
- variáveis disponíveis aparecem junto dos Modelos.

### 12.7 Financeiro

Naturezas:

- Receita;
- Despesa.

Situação é derivada pelo servidor:

- Em aberto;
- Parcialmente liquidado;
- Liquidado;
- Cancelado.

A UI não fornece seletor para marcar um lançamento como liquidado diretamente.

Operações:

- abertura de conta;
- lançamento;
- baixa;
- estorno;
- cancelamento/reabertura;
- transferência;
- movimentações;
- fluxo de caixa;
- conciliação;
- configurações.

Saldo de conta sem abertura suficiente é **Indeterminado**, com explicação.

O produto registra operações financeiras internas; não executa movimentação bancária real.

### 12.8 Relatórios

Relatórios são definidos pelo servidor e podem declarar:

- filtros tipados;
- período/dimensão;
- colunas;
- ordenação;
- agrupamento.

Resultado e totais usam a mesma definição executada.

Exportação:

- PDF;
- XLSX.

O arquivo é entregue pela própria resposta autenticada. Não criar URL pública, histórico de exportações, agendamento ou envio por e-mail nesta versão.

Acima do limite, recusar e pedir filtros/colunas mais restritos. Não truncar silenciosamente.

---

## 13. Design e comportamento global do App/Admin

### 13.1 Layout

- conteúdo com largura máxima aproximada de 1440 px;
- gutters: 32 px padrão, 24 px abaixo de 1024, 16 px abaixo de 600;
- páginas usam muito espaço branco e divisores leves;
- títulos sem faixa decorativa lateral;
- uma página de registro usa **um bloco principal de dados com seções**, não um cartão para cada campo;
- grade de leitura cresce de 1 para 2/3/4 colunas conforme largura;
- abas ficam no cabeçalho e conteúdo começa cerca de 16 px abaixo.

### 13.2 Header do App

Estrutura:

```text
[ORVYA] [Escritório]        [Pesquisa global]   [+]   [Sino]   [Conta]
```

Pesquisa Global:

- automática a partir de 2 caracteres;
- agrupada por tipo de resultado;
- nunca revela grupos sem permissão;
- `Ver todos os resultados` abre página própria.

`+` global reutiliza os mesmos formulários/modais de origem e mostra somente ações permitidas:

- Nova atividade;
- Novo processo;
- Nova Pessoa;
- Novo Documento;
- Novo lançamento.

Sino:

- novos/lidos;
- ação `Marcar todas como lidas`;
- abrir alerta leva ao registro relacionado.

### 13.3 Navegação principal do App

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

Conta/menu dá acesso a:

- Meu perfil;
- Configurações do escritório, conforme permissão;
- Sair.

Em largura estreita, sidebar vira overlay. `Esc` e backdrop fecham e o foco retorna ao botão Menu.

### 13.4 Listagens

Padrão:

```text
[Título]                                      [ação primária] [...]
[Pesquisa................] [Filtro] [Filtro] [Mais filtros] [paginação]
──────────────────────────────────────────────────────────────────────
| coluna | coluna | coluna | coluna |
| linha inteira clicável                                      [ações] |
| linha inteira clicável                                      [ações] |
──────────────────────────────────────────────────────────────────────
[leitura/as_of]
```

Regras:

- pesquisa automática após ~300 ms; Enter executa imediatamente;
- filtro mostra seu próprio rótulo;
- `Limpar` retorna aos padrões da tela;
- paginação na mesma faixa de consulta;
- `0 a 0 de 0` somente quando zero estiver confirmado;
- linha inteira abre o registro;
- ações rápidas não deslocam colunas quando aparecem;
- ações destrutivas/sensíveis ficam em menu `...` textual;
- área de tabela pode rolar horizontalmente;
- linhas naturais com mínimo aproximado de 36 px;
- células centralizadas verticalmente;
- divisores horizontais leves;
- texto não deve ser truncado à força quando puder quebrar adequadamente.

### 13.5 Modais e confirmação

Formulários de criação/edição usam modal sempre que o fluxo não precisa virar contexto próprio.

Ação crítica:

```text
Título
Registro afetado
Consequência objetiva
Justificativa [5..500]
[Cancelar] [Confirmar ação]
```

Rejeição do servidor permanece no modal.

---

# 14. APP — páginas e wireframes textuais

## 14.1 Área de trabalho `/dashboard`

Esta é a versão **D-31**, mais recente. Não recriar a versão antiga com faixa `Exigem atenção`, `Próximos compromissos` e cartões de indicadores.

### Layout

Desktop ≥ 960 px:

```text
[Área de trabalho]
[aviso discreto do Teste Grátis, quando aplicável]

┌────────────────────────────── 67% ──────────────────────────────┐  ┌──── 33% ────┐
│ MINHAS ATIVIDADES                                               │  │ CALENDÁRIO    │
│ [Hoje] [Esta semana] [Este mês]          [Mais filtros]         │  │ ‹ mês ano ›   │
│                                                                 │  │ seg ... dom   │
│ HOJE / VENCIDAS / datas                                         │  │ • por dia     │
│ • Título                      Modalidade                         │  │              │
│   Processo/contexto            data · hora             [Concluir]│  ├──────────────┤
│ ... até 12 linhas                                               │  │ RESUMO        │
│ + N atividades                                                  │  │ Processos...  │
│ Ver todas na Agenda                                             │  │ Monitorados.. │
└─────────────────────────────────────────────────────────────────┘  │ Pessoas...... │
                                                                     │ Atividades... │
                                                                     └──────────────┘
```

Abaixo de 960 px, empilhar com **Minhas atividades primeiro**.

### Minhas atividades

- `Hoje` é o modo inicial;
- modos principais mutuamente exclusivos: Hoje, Esta semana, Este mês;
- `Mais filtros`: modalidade e `Sem data`;
- escolher dia no calendário vira recorte daquele dia;
- `Voltar para hoje` restaura Hoje;
- mostrar no máximo 12 itens e indicar `+ N atividades` quando houver mais;
- `Ver todas na Agenda` preserva o contexto/recorte;
- itens são linhas de trabalho, sem cartão individual;
- marcador de cor + título + contexto + data/hora + modalidade discreta;
- vencidas permanecem na lista, agrupadas em `Vencidas`; **somente data/hora usa cor semântica de erro**. Sem selo vermelho, sem fundo ou borda especial;
- única ação rápida na mesa: `Concluir`, no hover/foco, com confirmação e justificativa.

### Calendário compacto

- mês atual inicialmente;
- única navegação `‹ mês ano ›`;
- uma bolinha em cada dia que possua Atividade pendente do usuário;
- mudar mês não altera o recorte da lista;
- clicar em dia filtra a lista na própria Área de trabalho.

### Resumo do escritório

Exatamente quatro linhas de texto, nesta ordem, cada uma clicável para o recorte correspondente:

1. Processos cadastrados;
2. Processos monitorados;
3. Pessoas cadastradas;
4. Atividades pendentes neste mês.

Sem cartões de KPI.

---

## 14.2 Agenda `/agenda`

Uma mesma coleção de Atividades em quatro visões:

```text
[Agenda e Atividades]                                  [Nova atividade]
[‹ período ›]               [Lista] [Dia] [Semana] [Mês]
[Pesquisa] [Modalidade] [Recorte] [Responsável] [paginação se Lista]
Pendentes N   Atrasadas N   Sem data N   Concluídas N
```

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
| Atividade | Modalidade | Quando | Responsável | Estado | ações |
```

- separadores de data;
- título + Processo na segunda linha;
- marcador de cor;
- linha inteira abre ficha;
- ações rápidas à direita.

### Dia/Semana/Mês

- mesmo conjunto de Atividades;
- sem painel lateral do dia;
- clicar em um dia no Mês/Semana abre a visão Dia;
- voltar restaura visão, data, filtros e posição;
- drag/reagendamento quando permitido;
- Atividades sem data não aparecem no calendário; oferecer atalho para Lista/Sem data.

### Ficha da Atividade `/agenda/:id`

```text
[← Agenda]  • Título da atividade     [Estado] [Concluir/Reabrir] [Reagendar] [...] 
            Modalidade · Processo · quando · Responsável

INFORMAÇÕES DA ATIVIDADE
  Descrição
  ─────────────────────
  Dados
  Quando | Responsável | Marco de atraso | Origem | Fuso | campos da modalidade
  ─────────────────────
  Processo
  vínculo atual [Trocar/Vincular] [... Remover]
  ─────────────────────
  Histórico
  linha do tempo
```

Providência criada de Publicação permanece vinculada ao Processo da Publicação enquanto essa origem existir.

---

## 14.3 Pessoas `/pessoas`

```text
[Pessoas]                                             [Adicionar pessoa]
[Pesquisar nome/documento/contato] [Natureza] [paginação]

| Nome | Natureza | Documento | E-mail principal | Telefone principal | Atualizada em |
```

### Ficha `/pessoas/:id`

Cabeçalho:

```text
[← Pessoas] Nome da Pessoa                     [Natureza] [Editar] [...]
            Pessoa Física/Jurídica · documento
[Resumo] [Processos] [Documentos] [Financeiro] [Histórico]
```

Abas dependem das permissões.

#### Resumo

```text
DADOS DA PESSOA
  Identificação
  Documento | Nome social/fantasia | datas | nacionalidade/estado civil/profissão
  Classificações
  Observações

CONTATOS, ENDEREÇOS, IDENTIFICAÇÕES E VÍNCULOS
  Contatos        [+]   item principal ...
  Endereços       [+]   item principal ...
  Identificações  [+]   item ...
  Vínculos        [+ Vincular pessoa] item ...
```

Leitura permanente; adicionar/editar em modal.

Aba Processos:

```text
| Processo | Situação | Responsável principal |
```

Aba Financeiro:

```text
| Lançamento | Vencimento | Principal | Em aberto |
```

Documentos mostra vínculos do mesmo Documento real. Histórico usa linha do tempo.

---

## 14.4 Processos `/processos`

```text
[Processos]                                           [Novo processo]
[Pesquisar número/título/protocolo] [Natureza] [Monitoramento] [paginação]

| Processo | Situação | Responsável principal | Atualização |
```

Célula `Processo`:

- identificação principal;
- `Parte 1 x Parte 2` quando disponível;
- segunda linha `Judicial/Administrativo · Monitorado/Não monitorado`.

### Ficha `/processos/:id`

```text
[← Processos] Parte 1 x Parte 2                  [Monitoramento] [+] [Editar] [...]
              identificação · Judicial/Admin · Situação · Tribunal
[Resumo] [Atividades] [Publicações] [Documentos] [Financeiro] [Histórico]
```

`+` contextual:

- Nova atividade;
- Vincular pessoa;
- Adicionar documento;
- Novo lançamento.

`...`:

- Gerar documento;
- ativar/desativar monitoramento;
- excluir.

#### Resumo

```text
┌ Próximas atividades, até 5 ┐  ┌ Dados do processo ┐
└────────────────────────────┘  └────────────────────┘

PARTES E RESPONSÁVEIS
  Partes
  Responsáveis

ÚLTIMOS EVENTOS                                      [Ver Histórico]
  linha do tempo curta
```

Em tela estreita, empilhar.

Judicial: número CNJ, tribunal, grau, classe, assunto, valor da causa, distribuição, monitoramento.

Administrativo: protocolo, tipo, órgão, início, valor de referência.

---

## 14.5 Publicações `/publicacoes`

```text
[Publicações]                                  [Sincronizar agora, se permitido]
[Novas N] [Tratadas N] [Total N]
[Pesquisar número/tipo/tribunal/texto] [Condição] [paginação]

| Processo | Tipo | Data da fonte | Recebida em | Condição | Trecho | Ações |
```

- condições somente Nova/Tratada;
- linha abre Publicação, não ficha do Processo;
- Processo continua acessível dentro da ficha;
- não existe importação manual.

### Ficha `/publicacoes/:id`

Quando aberta da listagem:

```text
[Anterior]                         12 de 48                         [Próxima]
```

Cabeçalho:

```text
[← Publicações] Publicação   [Nova/Tratada] [Criar providência] [Concluir] [Concluir e abrir a próxima] [...]
               Processo · Tipo · Tribunal · recebida em...
```

Corpo:

```text
[nota sobre efeito jurídico]
PUBLICAÇÃO
  Conteúdo recebido
  ─────────────────
  Processo
  ─────────────────
  Providências
```

Concluir e abrir a próxima só navega depois de conclusão confirmada com sucesso.

---

## 14.6 Documentos `/documentos/biblioteca`

```text
[Documentos]                       [Gerenciar modelos] [Incluir Documento]
[Requisitos de envio ▾]
[Pesquisar nome/descrição/tipo] [Tipo de Documento] [paginação]

| Documento | Tipo | Arquivo | Tamanho | Cadastrado em |
```

Sinalizar `Exclusão não concluída` quando aplicável.

### Ficha `/documentos/biblioteca/:id`

```text
[← Documentos] Nome do Documento      [Visualizar] [Baixar] [Substituir arquivo] [...]
               Tipo · arquivo original

DOCUMENTO
  Pré-visualização
  ─────────────────
  Dados
  Tipo | Descrição
  ─────────────────
  Vínculos                                      [+ Vincular]
  ─────────────────
  Arquivo
  Nome | tamanho | MIME | SHA-256

HISTÓRICO
```

Se exclusão estiver pendente:

- banner explicando;
- ocultar download/edição/vínculo/substituição;
- ação visível `Retomar exclusão`.

---

## 14.7 Financeiro

Navegação interna:

```text
Lançamentos | Movimentações | Fluxo de caixa | Conciliação bancária | Configurações
```

### Lançamentos `/financeiro/lancamentos`

```text
[Financeiro]                                      [Novo lançamento] [...]
[contas/saldos]
[Pesquisa] [Natureza] [Situação] [Período] [Mais filtros] [paginação]

| Lançamento | Natureza | Principal | Em aberto | Vencimento | Situação |

Receitas em aberto: ...      Despesas em aberto: ...
```

`...` do cabeçalho:

- Informar abertura;
- Registrar transferência;
- Atualizar.

Filtros secundários:

- data de referência;
- categoria;
- centro de custo;
- responsável;
- ordenação/direção;
- período personalizado.

### Ficha do lançamento `/financeiro/lancamentos/:id`

Leitura do lançamento, vínculos com Pessoa/Processo/Documento, parcelas/baixas, ações de editar, baixar, estornar, cancelar/reabrir conforme estado e histórico.

### Movimentações `/financeiro/movimentacoes`

Extrato com pesquisa, período efetivo, origem, forma e ordenação. Saldo corrido aparece somente quando o recorte permite calculá-lo corretamente.

### Fluxo de caixa `/financeiro/fluxo`

Visão temporal de entradas/saídas e totais do recorte, usando valores do servidor.

### Conciliação `/financeiro/conciliacao`

Conciliação bancária como tela própria com registros e estados, sem inventar relatório duplicado.

### Configurações `/financeiro/configuracoes`

Gerenciar:

- contas bancárias/caixa;
- categorias;
- centros de custo;
- formas de pagamento.

---

## 14.8 Relatórios `/relatorios`

```text
[Relatórios]
[Relatório ▾] [Executar] [Exportar ▾]

[formulário da definição selecionada]
  período/dimensão
  filtros tipados
  colunas
  ordenar por / ordem / agrupar

[parâmetros executados]
[tabela paginada]
[totais]
```

Exportar só fica disponível após existir execução. Se o usuário alterar filtros depois, resultado continua representando a última definição executada e a tela avisa que há mudanças não aplicadas.

`/relatorios/modelos` pode administrar definições salvas somente se a funcionalidade atual exigir; não criar um segundo sistema de relatórios.

---

## 14.9 Pesquisa Global `/pesquisa`

- campo grande;
- mínimo 2 caracteres;
- resultado agrupado por entidade disponível ao usuário;
- cada linha abre o registro;
- nada sobre entidades sem permissão deve ser revelado.

---

## 14.10 Alertas `/alertas`

- filtros Todos/Novos/Lidos;
- lista com tipo, mensagem, contexto e instante;
- clicar abre destino;
- marcar como lido é do destinatário e não conclui a causa do alerta;
- `Marcar todas como lidas` permitido;
- preferências de notificação ficam no Perfil.

---

## 14.11 Meu perfil `/conta/perfil`

Quatro abas, exatamente nesta ordem:

```text
Identificação | Notificações | Agenda e conexões | Segurança
```

### Identificação

- dados pessoais do usuário;
- foto de perfil;
- edição em fluxo simples;
- foto depende do armazenamento de objetos e deve mostrar indisponibilidade real quando não configurado.

### Notificações

- preferências pessoais de alertas.

### Agenda e conexões

Google Calendar:

- estado da conexão;
- conta Google autorizadora;
- conectar/reautorizar;
- sincronizar agora;
- desconectar com confirmação auditável;
- último sucesso;
- próxima tentativa;
- diagnóstico opcional das Atividades sincronizadas.

Google Auth e Google Calendar são integrações diferentes. Conectar Calendar não altera a forma de login.

Nunca exibir tokens.

### Segurança

- troca de senha e informações de segurança aplicáveis.

---

## 14.12 Configurações do escritório

Casca única com sete áreas conceituais:

1. Escritório;
2. Equipe e acesso;
3. Agenda;
4. Catálogos;
5. Modelos de documentos;
6. Plano e utilização;
7. Ações críticas.

### Escritório `/conta/configuracoes`

Read-first:

```text
Nome do escritório | CPF/CNPJ
Telefone           | E-mail
Fuso horário
Logo
```

`Editar` abre modal.

### Equipe e acesso `/conta/configuracoes/usuarios`

Lista usuários, status, papel/permissões, convite e ações de suspender/reativar/remover conforme regra.

### Agenda `/conta/configuracoes/agenda`

Somente configuração compartilhada do escritório:

- fuso horário;
- atalho para Catálogos de tipos de Atividade.

Preferências pessoais não entram aqui.

### Catálogos `/conta/configuracoes/catalogos`

Gerenciar catálogos tenant-scoped usados por Pessoas, Processos, Agenda, Documentos e outros módulos. Famílias financeiras apontam para Financeiro > Configurações quando essa for a fonte central.

### Modelos `/conta/configuracoes/modelos`

Modelos DOCX + variáveis disponíveis + validação.

### Plano e utilização `/conta/configuracoes/plano`

- Plano atual;
- utilização;
- limites;
- recursos habilitados/não incluídos;
- sem preço, cobrança, checkout ou troca de Plano pelo escritório.

### Ações críticas `/conta/configuracoes/acoes-criticas`

Operações destrutivas/irreversíveis da conta devidamente confirmadas e auditadas.

---

## 14.13 Buscas processuais `/processos/buscas`

Histórico/controle de buscas processuais externas, com status e resultados quando o recurso estiver habilitado. A fonte externa pode estar indisponível sem quebrar Processos locais.

---

# 15. Site público

Objetivo: apresentar o produto atual e levar a cadastro/login, sem inventar preço.

Header:

```text
[ORVYA]  Soluções ▾  Para você ▾  Planos  Por que Orvya?    Entrar  [Experimente grátis]
```

Conteúdo principal atual:

- faixa de anúncio de 7 dias grátis;
- hero `Mais clareza. Mais tempo. Mais Orvya.`;
- apresentação integrada de Processos, Agenda, Pessoas, Documentos, Financeiro e Publicações/Alertas;
- benefícios/contexto;
- seções de soluções;
- seção por público;
- Planos reais carregados de `GET /api/v1/site/planos`;
- CTA para `https://app.orvya.net/cadastro`;
- CTA Entrar para `https://app.orvya.net/`;
- rodapé institucional.

Planos:

- mostrar nome, descrição, recursos e limites vindos da API;
- plano estrutural de teste pode ser destacado;
- dizer `7 dias` no teste;
- nunca inventar preço.

O Site é responsivo, com menu móvel e mega menus simples. As imagens de interface podem ser ilustrativas, sempre identificadas como dados fictícios.

---

# 16. Entrada, cadastro e recuperação

## 16.1 Login

```text
[Logo]
Entrar no Orvya
E-mail
Senha
[Entrar]
[Continuar com Google]
Esqueci minha senha
Criar escritório / experimentar grátis
```

Google só aparece funcional quando configurado.

## 16.2 Cadastro

Cadastro público cria:

1. usuário inicial;
2. escritório;
3. vínculo como Administrador do Escritório;
4. Teste Grátis de 7 dias;
5. confirmação de e-mail quando o fluxo tradicional exigir.

Não pedir configuração avançada no onboarding. O escritório deve conseguir entrar e completar o restante depois.

## 16.3 Recuperação

Solicitação por e-mail, resposta neutra para evitar enumeração de contas e token de uso único.

---

# 17. ADMIN — Administração da Plataforma

Uma única aplicação e uma única casca. Não recriar a seleção histórica entre três painéis.

## 17.1 Header

```text
[ORVYA]  Administração da Plataforma › Página atual     [Pesquisa administrativa] [Conta admin]
```

## 17.2 Sidebar

Grupos:

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
  Catálogos iniciais
  Catálogos referenciais
  Variáveis de documentos

INTEGRAÇÕES
  Integrações e conexões
  Domínios e endpoints
  APIs utilizadas

OPERAÇÃO
  Visão operacional
  Serviços
  Execuções
  Banco de dados
    Principal
    Operações
    Migrations
  Recuperação / Backups / Chaves
  Capacidade
  Operações e limitações

AUDITORIA
  Histórico da Plataforma
  Conciliação Técnica

CONFIGURAÇÕES
  Configurações globais
```

Em tela estreita, sidebar sobreposta com Menu, backdrop e fechamento por Esc.

## 17.3 Pesquisa administrativa

- automática a partir de 2 caracteres;
- resultados agrupados;
- `Ver todos` abre página completa;
- linha inteira navega para o recurso.

## 17.4 Dashboard Admin

Ordem:

### 1. Pendências administrativas

Dois resumos principais:

- Escritórios que exigem atenção;
- Integrações desativadas ou com diagnóstico pendente.

Tabela quando houver pendências:

```text
| Escritório | Condição | Ação |
```

### 2. Estado da plataforma

Indicadores atuais da plataforma, como contas ativas/suspensas/em teste, usuários ativos, Processos monitorados e armazenamento tenant. Se fonte não estiver disponível, mostrar `Indisponível`, nunca zero falso.

### 3. Distribuição por Plano

```text
| Plano | Contas |
```

### 4. Atividade recente

```text
| Data/hora | Área | Ação | Autor | Alvo |
```

Não transformar Dashboard de negócio em painel de CPU/RAM/disco.

## 17.5 Escritórios

Listagem administrativa com pesquisa/filtros e ficha.

Ficha:

```text
[Nome do escritório] [Status] [Plano]        [Acessar escritório] [Editar] [...]
[Resumo] [Usuários] [Plano e utilização] [Histórico]
```

`...`:

- alterar Plano;
- suspender/reativar;
- excluir, quando permitido.

Resumo administrativo mostra metadados da conta. Dados jurídicos do escritório só devem ser acessados via acesso assistido.

## 17.6 Usuários

Pesquisa global de usuários, escritório, status, acesso e ações administrativas permitidas.

## 17.7 Planos

CRUD de Planos, limites e recursos. Manter um Plano estrutural de teste de 7 dias. Não adicionar preço por conta própria.

## 17.8 Administradores e Permissões

Administradores globais separados dos usuários de escritório. Proteger contra remoção/desativação do último administrador ativo com acesso configurado.

## 17.9 Catálogos globais

- iniciais;
- referenciais;
- variáveis de documentos.

Variável em uso não deve desaparecer por exclusão simples. Substituição deve conferir usos e consistência.

## 17.10 Integrações

Página/fichas globais separadas para:

- Google Auth;
- Google Calendar;
- Armazenamento de objetos;
- SMTP/E-mail;
- Comunica CNJ.

Cada ficha possui, conforme aplicável:

- configuração;
- salvar;
- verificar;
- ativar/desativar;
- último diagnóstico;
- erro/pendência.

Salvar, verificar e ativar são efeitos diferentes.

## 17.11 Domínios/endpoints e APIs utilizadas

Inventário legível dos destinos configurados e integrações. Não expor segredos.

## 17.12 Operação

Fornecer visibilidade mínima e comandos seguros para:

- status dos serviços;
- execuções/jobs;
- banco principal;
- migrations e revisão atual;
- backup/restauração;
- capacidade/armazenamento;
- reinício de serviços/VPS somente via executor `ops`, allowlist e interruptor explícito.

Operação perigosa exige confirmação, autorização e histórico.

Não permitir shell arbitrário pela interface.

## 17.13 Backups

- PostgreSQL para armazenamento configurado;
- catálogo de backups;
- criação manual;
- restauração protegida;
- status e erro claros.

## 17.14 Auditoria

Histórico global por autor/área/alvo/período. Conciliação Técnica serve a verificações operacionais específicas sem duplicar o histórico.

---

# 18. Integrações

## 18.1 SMTP

Usos:

- confirmação de cadastro;
- convite;
- recuperação de senha;
- comunicações técnicas previstas.

Sem SMTP, o restante da aplicação sobe. A UI administrativa explica a falta.

## 18.2 Google Auth

OAuth para login. É global e independente de Google Calendar.

## 18.3 Google Calendar

Conexão por usuário.

- OAuth com refresh token quando concedido;
- sincronização incremental;
- Atividade ↔ evento remoto por vínculo persistente;
- desconectar remove autorização/tokens locais, não apaga Atividades nem eventos remotos já criados;
- falhas pausam/registram tentativa sem corromper Atividade;
- Plano pode pausar recurso preservando conexão.

## 18.4 Comunica CNJ

Integração para obtenção de Publicações/monitoramento. Implementar adapter isolado atrás de interface de serviço. Persistir identificadores externos e idempotência para não duplicar Publicações.

## 18.5 Armazenamento de objetos

S3 ou compatível.

- arquivos de Documentos;
- Modelos;
- logos/fotos quando aplicável;
- bytes nunca ficam públicos por URL permanente;
- download via endpoint autenticado ou URL assinada curta, conforme implementação;
- SHA-256 e tamanho confirmados.

## 18.6 Geração documental

- ler DOCX-base;
- validar/substituir variáveis;
- gerar DOCX final;
- PDF quando suportado pela infraestrutura;
- cadastrar resultado como Documento e vincular ao contexto.

---

# 19. Worker e jobs

Um único worker é suficiente.

Jobs principais:

- sincronização de Publicações/CNJ;
- Google Calendar;
- manutenção de alertas derivados;
- limpeza segura de reservas de upload abandonadas;
- continuidade de exclusões físicas pendentes;
- backups agendados, se configurados;
- expiração/suspensão do Teste Grátis conforme regra.

Use tabela de jobs/locks no PostgreSQL quando suficiente. Não introduza Kafka/Redis/RabbitMQ sem necessidade real.

Jobs devem ser idempotentes.

---

# 20. Histórico e auditoria

Há dois níveis:

1. histórico tenant de registros e ações relevantes;
2. histórico global da plataforma.

Evento mínimo:

```text
id
account_id opcional
actor_type
actor_id
area
entity_type
entity_id
action
occurred_at
justification opcional
detail JSON pequeno
```

Histórico de registro é apresentado como linha do tempo, com referências navegáveis quando o usuário tiver permissão.

Não usar auditoria como substituto do estado atual da entidade.

---

# 21. Rotas do App

Implementar pelo menos:

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

Use React Router ou roteamento equivalente simples. Preserve filtros, data de referência, aba e posição relevante ao abrir uma ficha e voltar.

---

# 22. Estados de interface

Toda consulta precisa ter estados coerentes:

- carregando;
- vazio;
- erro;
- indisponível;
- dados.

Durante atualização de listagem, prefira manter os dados anteriores visíveis e inertes em vez de desmontar a tabela inteira.

Mensagens devem explicar o próximo passo quando houver ação possível.

---

# 23. Responsividade e acessibilidade essencial

Não faça uma rodada gigantesca de certificação durante o desenvolvimento, mas construa corretamente desde o início:

- navegação por teclado;
- foco visível;
- labels acessíveis;
- ícones com nomes quando forem controles;
- linha clicável também acionável por teclado;
- modais com foco contido e retorno ao acionador;
- contraste adequado;
- sidebar responsiva;
- tabelas com rolagem horizontal;
- touch target de aproximadamente 44 px quando a interface estiver em dispositivo de toque;
- botão de ícone ~36 px no desktop;
- não usar somente cor para transmitir estado.

---

# 24. Operação e deploy

## 24.1 Docker Compose

Fluxo esperado:

```bash
docker compose up -d --build
```

Na primeira subida:

1. aguardar PostgreSQL;
2. aplicar Alembic `upgrade head`;
3. iniciar API;
4. iniciar worker e ops;
5. servir builds do Site/App/Admin pelo Nginx.

## 24.2 Nginx

Roteamento por `Host`:

```text
orvya.net       -> site estático + /api/v1/site/* para API
app.orvya.net   -> app estático + /api/v1/* para API
admin.orvya.net -> admin estático + /api/v1/* para API
```

SPA fallback para App/Admin.

## 24.3 HTTPS

Produção precisa de TLS válido. Pode usar Certbot/Let's Encrypt ou TLS do provedor/cloud, escolhendo o caminho mais simples do ambiente.

## 24.4 Migrations

Nova instalação começa em uma migration de baseline do schema final. Não reproduzir dezenas de revisões históricas.

Deploy subsequente:

```text
pull/build -> migration -> restart -> health check
```

## 24.5 Logs

Logs estruturados o suficiente para operação:

- request id;
- job id;
- integração;
- status/erro;
- nunca segredo/token/senha/bytes de documento.

---

# 25. Plano de implementação autônoma

A IA deve executar nesta ordem, sem pedir confirmação entre fases.

## Fase 1 — fundação

- criar estrutura do monorepo;
- Docker Compose;
- config/env;
- PostgreSQL/Alembic;
- modelos essenciais;
- sessão/auth/CSRF;
- tenant scoping;
- permissões;
- seeds estruturais mínimos: Plano de teste, catálogos globais indispensáveis.

**Checkpoint curto:** subir banco/API e testar `/saude`, migration e um login local.

## Fase 2 — backend funcional

Implementar APIs e serviços de:

1. conta/equipe/Planos;
2. Pessoas;
3. Processos;
4. Atividades/Agenda;
5. Publicações;
6. arquivos/Documentos/Modelos;
7. Financeiro;
8. dashboard/alertas/pesquisa/histórico;
9. Relatórios;
10. Admin;
11. integrações e worker.

Não criar testes unitários para cada função neste momento.

**Checkpoint curto:** smoke API dos domínios principais + validação da migration em banco vazio.

## Fase 3 — shared UI e cascas

- identidade visual;
- componentes LeafyGreen;
- shell do App;
- shell único do Admin;
- modais, tabelas, filtros, paginação, estados, histórico;
- cliente HTTP e sessão.

## Fase 4 — App

Construir na ordem da navegação e reutilizar componentes/formulários:

1. Área de trabalho D-31;
2. Agenda;
3. Pessoas;
4. Processos;
5. Publicações;
6. Documentos;
7. Financeiro;
8. Relatórios;
9. Pesquisa/Alertas;
10. Perfil e Configurações.

Não duplicar formulário para `+` global. Abrir o mesmo modal do módulo.

## Fase 5 — Admin e Site

- Administração da Plataforma completa;
- Site responsivo;
- cadastro/login/recuperação;
- catálogo real de Planos sem preço.

**Checkpoint curto:** `typecheck` + build das três superfícies. Corrigir apenas erros que impedem build/uso estrutural.

## Fase 6 — integrações e deploy

- SMTP;
- Google Auth;
- Google Calendar;
- S3;
- CNJ;
- geração documental;
- backups;
- Nginx/TLS;
- worker/ops.

Sem credencial, validar o estado `Não configurado` e seguir.

## Fase 7 — estabilização final

Agora, e somente agora, fazer a rodada concentrada de correções:

1. banco limpo + migration;
2. backend start;
3. frontend typecheck;
4. builds Site/App/Admin;
5. smoke API;
6. smoke de navegador;
7. correção dos erros encontrados;
8. repetir até ficar verde;
9. subir stack final e checar `/saude`, `/saude/pronto` e hosts.

---

# 26. Testes: poucos, grandes e úteis

Não reproduzir a bateria histórica de centenas de roteiros.

## 26.1 Durante desenvolvimento

Somente:

- migration em banco vazio;
- health;
- 1 ou 2 requests de cada grande domínio;
- typecheck/build depois do backend e do frontend completos.

## 26.2 Suite final de API

Cobrir aproximadamente estes fluxos:

1. cadastro + login + logout;
2. isolamento entre dois escritórios;
3. Pessoa CRUD;
4. Processo + parte + responsável;
5. Atividade + concluir/reabrir;
6. Publicação recebida/idempotente + concluir;
7. upload + Documento + download + vínculo;
8. Modelo + geração;
9. lançamento + baixa + estorno;
10. pesquisa/alerta;
11. relatório + exportação;
12. Admin: criar/alterar conta/Plano e acesso assistido.

## 26.3 Smoke de navegador

Cobrir somente jornadas representativas:

- login;
- Área de trabalho D-31;
- criar e concluir Atividade;
- cadastrar Pessoa;
- cadastrar Processo e navegar pelas abas;
- tratar Publicação;
- incluir e abrir Documento;
- criar lançamento;
- executar Relatório;
- abrir Perfil/Configurações;
- Admin Dashboard + ficha de escritório;
- Site + Planos + CTA.

Não buscar cobertura de cada estado visual antes de o produto estar pronto.

---

# 27. Dados iniciais e desenvolvimento

Seeds devem ser mínimos e idempotentes.

Criar automaticamente apenas o que o sistema precisa estruturalmente, por exemplo:

- Plano de Teste Grátis de 7 dias;
- chaves de recursos/limites;
- catálogos referenciais indispensáveis;
- registro de configuração global vazia.

Não criar Pessoas, Processos, lançamentos ou Publicações demonstrativas em produção.

Para desenvolvimento, fixtures opcionais podem existir em comando explícito `dev-seed`, nunca no bootstrap normal.

---

# 28. O que deliberadamente não deve ser recriado

Para manter a reconstrução rápida e limpa, **não portar**:

- documentos normativos históricos;
- EFs/ETs antigas como arquivos separados;
- matriz de conformidade;
- pastas de evidências;
- centenas de scripts de validação;
- cadeias antigas de migrations;
- bootstrap operacional histórico;
- scripts específicos da VPS antiga que não sejam necessários ao novo deploy;
- duplicações de páginas antigas substituídas pelas decisões D-15 a D-31;
- três shells/painéis administrativos antigos;
- dashboard antigo da Área de trabalho com `Exigem atenção` e cartões;
- Painel do Dia lateral da Agenda;
- página principal separada de Modelos fora das Configurações;
- preços/cobrança/checkout;
- microserviços, filas externas, event sourcing, CQRS ou Kubernetes sem necessidade;
- testes exaustivos antes de a implementação terminar.

---

# 29. Regras de qualidade do código

- nomes claros e domínio explícito;
- funções pequenas onde melhora leitura, sem fragmentação artificial;
- Pydantic na fronteira da API;
- SQLAlchemy em camada de persistência/serviço sem repository pattern obrigatório para cada tabela;
- transações explícitas para operações multi-etapa;
- integrações atrás de adapters;
- frontend compartilha componentes e contratos;
- nenhuma lógica de autorização existe apenas no React;
- nenhuma soma financeira relevante existe apenas no React;
- nenhuma query tenant depende de filtro enviado pelo cliente;
- nenhuma mutação crítica ocorre por GET;
- nenhum segredo chega ao bundle frontend.

---

# 30. Checklist final de equivalência funcional

Antes de considerar pronto, conferir:

### Produto

- [ ] Site, App e Admin existem nos três hosts.
- [ ] Cadastro cria escritório em Teste Grátis de 7 dias.
- [ ] Login por senha funciona; Google funciona quando configurado.
- [ ] Multi-tenant não vaza dados.
- [ ] Planos e permissões bloqueiam no servidor.

### App

- [ ] Área de trabalho é a mesa diária D-31.
- [ ] Agenda tem Lista/Dia/Semana/Mês.
- [ ] Pessoa é página read-first com abas e coleções.
- [ ] Processo é hub com seis abas.
- [ ] Publicação tem fila sequencial e providências.
- [ ] Documento tem preview, vínculos, substituição e exclusão retomável.
- [ ] Modelos ficam em Configurações.
- [ ] Financeiro tem cinco áreas e Decimal ponta a ponta.
- [ ] Relatórios executam e exportam PDF/XLSX.
- [ ] Pesquisa Global e Alertas funcionam.
- [ ] Perfil tem quatro seções.
- [ ] Configurações do escritório têm sete áreas.

### Admin

- [ ] uma casca única `Administração da Plataforma`;
- [ ] Dashboard na ordem atual;
- [ ] Escritórios/Usuários/Planos;
- [ ] Administradores/Permissões;
- [ ] Catálogos/Variáveis;
- [ ] Integrações;
- [ ] Operação/Banco/Migrations/Backups;
- [ ] Auditoria;
- [ ] acesso assistido auditado.

### Infra

- [ ] migration limpa funciona;
- [ ] Docker Compose sobe;
- [ ] worker e ops funcionam;
- [ ] armazenamento externo tem fallback `Não configurado`;
- [ ] TLS e proxy funcionam;
- [ ] health/readiness passam;
- [ ] logs não vazam segredo.

### Verificação

- [ ] backend smoke verde;
- [ ] typecheck verde;
- [ ] três builds verdes;
- [ ] browser smoke verde;
- [ ] nenhum erro crítico conhecido deixado para depois.

---

# 31. Política de decisão durante a implementação

Quando surgir uma escolha não especificada, use esta ordem:

1. preservar o comportamento descrito neste arquivo;
2. preservar segurança e isolamento;
3. escolher o caminho com menos componentes;
4. preferir convenções da stack;
5. evitar criar uma nova abstração se duas implementações diretas resolvem de modo legível;
6. não pedir decisão humana para detalhes técnicos reversíveis.

Só interrompa por informação externa impossível de inferir, como credencial/secreto necessário para ativar uma integração real. Mesmo nesse caso, implemente todo o restante e deixe a integração claramente não configurada.

---

# 32. Resultado esperado do agente de código

Ao terminar a sessão, a IA deve deixar:

```text
1. código completo no repositório;
2. commits na branch main;
3. README curto com instalação e deploy;
4. .env.example;
5. migration inicial;
6. Docker Compose;
7. builds reproduzíveis;
8. smoke tests finais;
9. aplicação implantável;
10. ORVYA.md atualizado apenas se uma decisão técnica necessária tiver sido consolidada.
```

A meta não é reproduzir o processo de construção antigo. A meta é chegar, pelo caminho mais curto e seguro, ao **Orvya atual funcionando**.
