# ORVYA — especificação única para reconstrução integral

> **Finalidade:** este arquivo é o briefing técnico e funcional único para recriar o Orvya do zero, com o comportamento atual, em uma execução autônoma de codificação.
>
> **Destino:** `orvya/orvya`, branch `main`.
>
> **Base funcional consolidada:** `orvya/orvya-base`, branch `principal`, até o commit `f11abd463f27cbdc3515fc14de272bbd86767d62`, incorporando a versão mais recente da Área de trabalho como mesa diária.
>
> Este documento descreve **o produto que deve existir ao final**, não o caminho histórico usado para construí-lo.

---

# 1. Instrução para a IA implementadora

Crie o Orvya inteiro neste repositório, do zero ao deploy, sem solicitar aprovação entre etapas. Trabalhe até existir uma instalação funcional.

## Regras de execução

1. Use este arquivo como especificação principal e suficiente.
2. Não replique a arquitetura histórica do `orvya-base`; replique o **produto e o comportamento atuais**.
3. Prefira a solução mais simples que preserve segurança, isolamento entre escritórios, regras jurídicas e financeiras, UX e integrações descritas aqui.
4. Use um **monólito modular**. Não crie microserviços sem necessidade objetiva.
5. Não crie uma coleção paralela de documentos funcionais ou técnicos. Este arquivo permanece como referência do produto.
6. Não porte o histórico de migrations. Crie **uma migration inicial limpa** com o schema final e migrations adicionais somente se surgirem alterações reais durante a própria implementação.
7. Não porte harnesses históricos, evidências, fixtures ou milhares de verificações acumuladas do projeto anterior.
8. Não interrompa a implementação para perseguir cobertura de testes. Faça verificações curtas nos grandes marcos e estabilização completa ao final.
9. Quando um detalhe técnico não estiver prescrito, escolha a alternativa convencional, pequena, segura e sustentável.
10. Não invente preços, cobrança, checkout ou regras comerciais não descritas aqui.
11. Não simule sucesso de integração externa. Sem configuração válida, apresente **Não configurado** ou **Indisponível**, com razão objetiva.
12. Não coloque segredos no Git. Use variáveis de ambiente ou armazenamento restrito da instalação.
13. Commits devem acompanhar grandes marcos, sem fragmentar o trabalho em dezenas de commits cerimoniais.
14. Se um erro não bloquear o avanço estrutural, registre-o e prossiga. Corrija o conjunto na estabilização final.
15. Ao terminar, o repositório deve subir em ambiente limpo com comando único documentado.

## Critério de conclusão

O trabalho está concluído quando:

- banco vazio sobe e migra sozinho;
- cadastro, login, sessões e recuperação de senha funcionam;
- isolamento multi-tenant está garantido no servidor;
- Site, App e Admin compilam e funcionam;
- todos os módulos e páginas abaixo estão implementados;
- os fluxos principais funcionam ponta a ponta;
- integrações sem credencial exibem indisponibilidade real;
- deploy HTTPS está operacional;
- smoke tests finais passam;
- não existe erro de build, typecheck ou migration;
- o repositório não contém arquitetura histórica desnecessária para reproduzir o produto atual.

---

# 2. O que é o Orvya

Orvya é um SaaS brasileiro para organização e gestão da rotina jurídica de advogados e escritórios.

O produto conecta em um único contexto:

- Pessoas e clientes;
- Processos judiciais e administrativos;
- Agenda e Atividades;
- Publicações judiciais;
- Documentos e Modelos DOCX;
- Financeiro;
- Relatórios;
- Notificações e Pesquisa Global;
- Configurações do escritório;
- Administração global da plataforma.

Há uma instalação compartilhada e vários escritórios isolados. O escritório é o tenant.

## Superfícies

| Superfície | Domínio esperado | Função |
|---|---|---|
| Site | `orvya.net` | landing page, apresentação, planos sem preço e entrada para teste grátis |
| App | `app.orvya.net` | produto utilizado pelos escritórios |
| Admin | `admin.orvya.net` | administração global da plataforma |

A API usa o prefixo `/api/v1`.

---

# 3. Princípios que não podem ser simplificados

A implementação pode ser muito menor que a anterior. As regras abaixo permanecem obrigatórias.

## 3.1 Multi-tenant real

- O escritório atual vem da sessão autenticada.
- O cliente não escolhe um tenant confiável para uma operação normal.
- Toda consulta tenant-scoped aplica `account_id` no servidor.
- IDs de outro escritório devem resultar em não encontrado ou acesso negado sem vazar existência.
- Administrador da Plataforma é identidade separada do usuário de escritório.
- Acesso assistido a um escritório exige ação explícita, contexto visual claro e histórico.

## 3.2 Uma fonte por informação

Não duplique semanticamente o mesmo dado em módulos diferentes.

Exemplos:

- Atividade vinculada a Processo continua sendo uma Atividade única.
- Documento vinculado a Pessoa, Processo ou Financeiro continua sendo um Documento único.
- Pessoa usada em um Processo continua sendo a mesma Pessoa.
- Agenda é uma visualização das Atividades, não outro cadastro.
- Dashboard consulta fontes reais, não mantém cópias.
- Catálogos financeiros são compartilhados com o Financeiro, não recriados em formulários isolados.

## 3.3 Autoridade do servidor

O servidor decide:

- permissões;
- limites do Plano;
- tenant atual;
- situações derivadas;
- atraso;
- totais financeiros;
- transições válidas;
- conflitos de revisão;
- ações críticas;
- disponibilidade das integrações;
- recortes e totais usados em Relatórios.

A interface apresenta informações e solicita comandos, mas não substitui as regras do servidor.

## 3.4 Semântica correta de ausência

- Ausente não vira zero.
- Indisponível não vira lista silenciosamente vazia.
- Horário ausente não vira `00:00`.
- Saldo indeterminado não vira `R$ 0,00`.
- Campo ausente aparece como `Não informado` ou `Indisponível`, conforme o caso, sem persistir esse texto como dado.

## 3.5 Revisões concorrentes

Registros editáveis importantes possuem `revision` inteiro.

Em atualização:

- cliente envia `expected_revision`;
- servidor atualiza somente se a revisão ainda for a esperada;
- conflito retorna `409`;
- a UI oferece recarregar e revisar, sem sobrescrever silenciosamente.

---

# 4. Arquitetura alvo simplificada

Use um **monorepo, monólito modular e um único PostgreSQL principal**.

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

## Serviços de runtime

Use Docker Compose, salvo impedimento objetivo:

1. `postgres` — PostgreSQL;
2. `api` — FastAPI;
3. `worker` — filas, sincronizações e rotinas recorrentes;
4. `ops` — executor mínimo e allowlisted para operações administrativas que não devem ocorrer dentro do processo HTTP;
5. `nginx` — três hosts, arquivos estáticos e proxy da API.

Não separar domínios de negócio em serviços independentes.

---

# 5. Stack

## 5.1 Backend

- Python 3.13;
- FastAPI;
- Uvicorn;
- SQLAlchemy 2;
- PostgreSQL;
- psycopg 3;
- Alembic;
- Pydantic 2;
- Argon2id para senha;
- HTTPX para integrações HTTP;
- boto3 para armazenamento compatível com S3;
- bibliotecas pequenas e maduras para DOCX, XLSX e PDF somente onde necessárias.

## 5.2 Frontend

- TypeScript;
- React em versão compatível com a versão vigente do Spectrum 2;
- Vite;
- npm workspaces;
- **Adobe Spectrum 2 como único Design System**;
- pacote principal: `@react-spectrum/s2`;
- styling adicional somente com `@react-spectrum/s2/style` e tokens oficiais;
- ícones somente do catálogo Spectrum 2, por imports de `@react-spectrum/s2/icons/*`;
- componentes de acessibilidade usados pelo Spectrum 2 podem ser utilizados quando o próprio ecossistema oficial exigir.

## 5.3 Regra visual obrigatória

Spectrum 2 é a única fonte de:

- componentes;
- cores de interface;
- tipografia de interface;
- espaçamentos;
- raios;
- elevação;
- estados;
- foco;
- ícones;
- tamanhos adaptativos;
- comportamento de toque;
- padrões de navegação;
- componentes de formulário;
- tabelas;
- diálogos;
- menus;
- tooltips;
- feedback de carregamento e erro.

Não introduzir outro Design System nem biblioteca visual concorrente.

Para componentes que não existirem prontos:

1. usar primitivas compatíveis com o ecossistema Spectrum;
2. estilizar exclusivamente com `style()` e tokens Spectrum 2;
3. preservar acessibilidade, estados de interação e responsividade do sistema.

Não usar CSS reset global agressivo. Não sobrescrever internamente cores, paddings e estados de componentes Spectrum para “aproximar” outra estética.

## 5.4 Tipografia

A interface segue a tipografia oficial fornecida pelo Spectrum 2. Não carregar uma família tipográfica externa para App ou Admin.

O Site também usa a escala, tokens e princípios tipográficos Spectrum, podendo compor títulos editoriais maiores apenas com os tokens disponíveis no sistema.

## 5.5 Marca

- nome sempre **Orvya**;
- usar logotipo completa oficial em SVG onde houver espaço;
- usar emblema oficial nos contextos compactos e favicon;
- a marca mantém suas cores próprias;
- cores da marca não viram automaticamente tokens de UI;
- não reconstruir a logotipo com texto;
- não rasterizar quando SVG puder ser usado.

---

# 6. Configuração e segredos

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
S3_ENDPOINT=
S3_REGION=
S3_BUCKET=
S3_ACCESS_KEY=
S3_SECRET_KEY=
CNJ_BASE_URL=
CNJ_TOKEN=
OPS_TOKEN=
```

Nenhuma integração externa é requisito para o processo local iniciar. Sem configuração, a UI explica a indisponibilidade.

---

# 7. Segurança e acesso

## 7.1 Sessão

- sessão opaca armazenada no servidor;
- cookie `HttpOnly`;
- cookie `Secure` em produção;
- `SameSite=Lax` ou mais restritivo quando possível;
- cookies host-only separados para App e Admin;
- 30 minutos de inatividade;
- 8 horas de duração absoluta;
- CSRF server-side em mutações autenticadas.

## 7.2 Senhas

- Argon2id;
- nunca registrar senha ou token em log;
- recuperação por e-mail com token aleatório de uso único e expiração curta.

## 7.3 Entrada

App:

- e-mail + senha.

Admin:

- e-mail + senha;
- identidade administrativa própria;
- não compartilhar cookie do App.

## 7.4 Papéis

- **Administrador do Escritório:** acesso completo à conta, sujeito ao Plano;
- **Usuário comum:** capacidades granulares;
- **Administrador da Plataforma:** acesso administrativo global;
- **Acesso assistido:** Administrador da Plataforma entra explicitamente no contexto de um escritório, sem criar usuário local fictício.

Permissão é sempre verificada na API, mesmo quando o botão estiver oculto na interface.

## 7.5 Ações críticas

Ações destrutivas ou relevantes exigem confirmação auditável.

Padrão:

```text
Título
Registro afetado
Consequência objetiva
Justificativa obrigatória quando a regra exigir, 5 a 500 caracteres
[Cancelar] [Confirmar]
```

Servidor registra:

- ator;
- instante;
- ação;
- alvo;
- justificativa;
- tenant, quando aplicável.

---

# 8. Planos e Teste Grátis

- O cadastro público cria o primeiro Administrador do Escritório e a conta.
- Teste grátis estrutural: **7 dias** a partir do instante de criação.
- O Site mostra Planos e seus recursos/limites, **sem preços**.
- Não existe checkout do escritório nesta versão.
- O Plano é definido pela Administração da Plataforma.
- Limites principais: usuários, Processos monitorados e armazenamento.
- Recursos podem habilitar ou desabilitar módulos como Publicações, Documentos, Modelos, Financeiro e Relatórios.
- Redução de Plano não apaga dados existentes.
- Quando um limite impedir nova ação, preserve o que já existe e explique a razão.
- Ao expirar o Teste Grátis, a conta pode ser suspensa automaticamente se continuar no Plano estrutural.
- A Área de trabalho mostra aviso discreto do Teste Grátis enquanto aplicável.

Estados de Conta:

- Ativa;
- Suspensa.

Estados de usuário do escritório:

- Ativo;
- Suspenso;
- exclusão é ação separada, não um terceiro estado permanente.

---

# 9. Banco de dados — famílias de entidades

Use UUID como identificador principal, timestamps timezone-aware para instantes e `DATE` para datas civis.

Não é necessário copiar nomes de tabelas do projeto anterior. Preserve relações, invariantes e comportamento.

## 9.1 Entidades globais

- `plans`
- `plan_features`
- `plan_limits`
- `platform_admins`
- `platform_admin_permissions`
- `global_catalogs`
- `global_catalog_items`
- `integration_configs`
- `document_variables`
- `platform_audit_events`
- `operation_runs`
- `schema_migrations_view` ou projeção equivalente

## 9.2 Entidades de tenant

- `accounts`
- `users`
- `user_permissions`
- `invitations`
- `sessions`
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
- `activity_catalog_items`
- `publications`
- `files`
- `documents`
- `document_links`
- `document_templates`
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
- `account_catalog_items`
- `audit_events`
- `saved_report_definitions`

## 9.3 Regras transversais

- toda entidade do escritório tem `account_id` direto ou relação inequívoca que permita aplicar tenant;
- relações cruzadas entre tenants são proibidas;
- valores monetários usam `NUMERIC`, nunca `float`;
- datas civis não são convertidas em instantes artificiais;
- valores exibidos como dinheiro são formatados apenas na borda da UI;
- eventos de auditoria são append-only;
- exclusões relevantes preservam a autoria histórica quando a regra exigir.

---

# 10. Domínios funcionais

## 10.1 Escritórios e usuários

Escritório possui:

- nome;
- CPF/CNPJ opcional;
- telefone;
- e-mail institucional;
- fuso horário;
- logotipo;
- Plano;
- status;
- data de criação.

Usuário possui:

- nome;
- e-mail único entre usuários operacionais existentes;
- senha;
- status;
- indicador de Administrador do Escritório;
- permissões granulares;
- foto opcional;
- preferências pessoais.

Convite:

- criado por Administrador do Escritório;
- destinatário define senha;
- entra no mesmo escritório;
- pode ser reenviado enquanto pendente.

Ao excluir usuário com responsabilidades:

- exigir reatribuição de Atividades pendentes;
- exigir reatribuição de Processos em que seja responsável principal;
- fatos históricos continuam atribuídos ao ator original.

## 10.2 Pessoas

Naturezas:

- Pessoa Física;
- Pessoa Jurídica;
- ausência temporária da natureza pode ser representada como dado incompleto, não como terceira natureza.

Pessoa pode possuir:

- nome ou razão social;
- nome social ou fantasia;
- CPF/CNPJ;
- nascimento ou abertura;
- nacionalidade;
- estado civil;
- profissão;
- classificações;
- observações;
- contatos;
- endereços;
- identificações adicionais;
- vínculos com outras Pessoas.

CPF/CNPJ duplicado no mesmo escritório deve orientar para o registro existente, nunca sobrescrevê-lo.

## 10.3 Processos

Naturezas:

- Judicial;
- Administrativo.

Judicial pode ter:

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

Administrativo pode ter:

- título;
- protocolo;
- tipo;
- órgão;
- data de início;
- valor de referência;
- Situação;
- responsável principal;
- partes ou envolvidos conforme contexto.

Polos:

- Ativo;
- Passivo;
- Terceiro interessado.

Partes apontam para Pessoas reais do mesmo escritório.

### Monitoramento

- aplica-se somente ao Processo Judicial elegível;
- cadastro manual nasce sem monitoramento;
- cadastro originado da busca externa pode ativar automaticamente se houver limite disponível;
- falta de vaga não impede o cadastro do Processo;
- desativar preserva Publicações já recebidas;
- reativar não precisa retroagir ao período desligado;
- falha externa não altera automaticamente o estado de monitoramento.

## 10.4 Atividades e Agenda

Modalidades exclusivas:

- Audiência;
- Prazo;
- Tarefa;
- Evento.

Cada Atividade possui:

- item catalogado, que define o título;
- modalidade;
- responsável;
- data e horário quando aplicáveis;
- descrição;
- Processo opcional, salvo quando origem obrigar;
- estado;
- cor visual definida pelo tipo catalogado;
- origem;
- revisão;
- histórico de transições.

Estados reais:

- Pendente;
- Concluída;
- Cancelada.

`Atrasada` é condição calculada de Pendente, não estado persistido.

Criação pode partir de:

- Agenda;
- Processo;
- tratamento de Publicação.

Criada no Processo, herda o Processo.

Criada no tratamento de Publicação, herda obrigatoriamente o Processo daquela Publicação.

Criada pela Agenda, o Processo é opcional.

## 10.5 Publicações

Publicação nasce apenas da integração judicial autorizada.

Condições:

- Nova;
- Tratada.

Ações:

- Criar providência;
- Concluir;
- Descartar.

Criar providência cria Atividade real.

Ao criar a primeira providência, a Publicação pode passar para Tratada conforme regra do serviço.

Concluir:

- preserva a Publicação;
- marca Tratada;
- remove alerta pendente correspondente;
- não impede providências posteriores.

Descartar:

- remove definitivamente a Publicação;
- não apaga Atividades independentes já criadas.

Não existe cadastro manual de Publicação.

## 10.6 Documentos

Documento pertence ao escritório e possui um único arquivo vigente.

Pode se vincular a:

- Pessoa;
- Processo;
- Atividade;
- Publicação;
- Financeiro.

Remover vínculo não exclui Documento.

Excluir Documento remove:

- registro;
- vínculos;
- arquivo físico.

Se a remoção física não puder ser confirmada:

- manter estado de exclusão pendente;
- impedir download, edição, novos vínculos e substituição;
- oferecer `Retomar exclusão`;
- continuar contando armazenamento até conclusão real.

## 10.7 Arquivos

Todo arquivo persistente passa por serviço central.

Fluxo de upload:

1. validar contrato localmente apenas como conveniência;
2. reservar capacidade no servidor;
3. transferir bytes;
4. servidor confirma tamanho e hash;
5. somente então criar ou substituir o registro de negócio.

Banco guarda:

- propriedade;
- metadados;
- chave física;
- tamanho;
- MIME;
- hash.

Objetos ficam no armazenamento configurado.

## 10.8 Modelos e geração

Modelos são DOCX do escritório.

Contextos:

- Pessoa;
- Processo.

Sintaxe de variável:

```text
{{contexto.campo}}
```

Variáveis oficiais vêm do registro central da Plataforma.

Variáveis abertas podem usar:

```text
{{aberto.nome}}
```

Ao gerar:

1. escolher Modelo compatível;
2. resolver variáveis oficiais;
3. pedir valores abertos;
4. gerar DOCX;
5. permitir PDF quando conversão estiver disponível;
6. entregar arquivo;
7. salvar na Biblioteca somente por ação explícita do usuário.

Geração não altera o DOCX-base.

## 10.9 Financeiro

Naturezas:

- Receita;
- Despesa.

Lançamento pode se relacionar opcionalmente com:

- Pessoa;
- Processo.

Situações calculadas:

- Em aberto;
- Parcialmente liquidado;
- Liquidado;
- Cancelado.

Regras:

- situação não é campo de seleção livre;
- vencido é condição derivada;
- dinheiro usa decimal exato;
- baixa reduz saldo em aberto;
- estorno recompõe a situação;
- transferência gera movimentos relacionados sem virar Receita ou Despesa operacional comum;
- saldos dependem de abertura e movimentos reais;
- saldo sem base suficiente aparece como indeterminado.

Catálogos financeiros:

- contas bancárias e caixas;
- categorias;
- centros de custo;
- formas de pagamento.

## 10.10 Relatórios

Relatórios são consultas sobre dados reais.

Fontes iniciais:

- Atividades;
- Publicações;
- Processos;
- Pessoas;
- Documentos;
- Financeiro;
- combinações autorizadas entre essas fontes.

Cada definição pode declarar:

- período;
- dimensão temporal;
- filtros tipados;
- colunas;
- ordenação;
- agrupamento;
- totais.

A execução devolve referência imutável daquele recorte para paginação e exportação.

Exportações iniciais:

- PDF;
- XLSX.

O total sempre representa o conjunto filtrado inteiro, não a página atual.

## 10.11 Pesquisa Global

Pesquisa no contexto do escritório.

Pode encontrar, conforme permissão:

- Pessoas;
- Processos;
- Atividades;
- Publicações;
- Documentos;
- Financeiro;
- definições salvas de Relatório quando aplicável.

Mínimo: 2 caracteres.

A API aplica antes de responder:

- tenant;
- permissões;
- disponibilidade pelo Plano.

Um grupo sem acesso não deve revelar contador, título ou existência.

## 10.12 Notificações

Notificação pertence ao destinatário.

Exemplos:

- nova Publicação;
- Atividade atribuída;
- Prazo próximo;
- Prazo vencido;
- Audiência próxima;
- aviso interno do escritório.

Lido não significa resolvido.

Marcar como lido altera somente a leitura do destinatário.

---

# 11. API

Use REST JSON sob `/api/v1`.

## Convenções

Coleção paginada:

```json
{
  "items": [],
  "page": 1,
  "page_size": 25,
  "total": 0,
  "as_of": "2026-09-15T12:00:00Z"
}
```

Erro:

```json
{
  "code": "codigo_estavel",
  "message": "Mensagem compreensível.",
  "field": "campo_opcional"
}
```

HTTP:

- `400` entrada inválida;
- `401` sem sessão;
- `403` sem capacidade;
- `404` não encontrado ou fora do tenant;
- `409` conflito de revisão ou regra de concorrência;
- `422` regra de domínio;
- `503` dependência necessária indisponível.

## Famílias de rotas

```text
/api/v1/auth/*
/api/v1/signup/*
/api/v1/account/*
/api/v1/users/*
/api/v1/people/*
/api/v1/processes/*
/api/v1/judicial-searches/*
/api/v1/activities/*
/api/v1/agenda/*
/api/v1/publications/*
/api/v1/files/*
/api/v1/documents/*
/api/v1/templates/*
/api/v1/finance/*
/api/v1/reports/*
/api/v1/search/*
/api/v1/alerts/*
/api/v1/site/*
/api/v1/admin/*
/api/v1/integrations/*
/api/v1/operations/*
/api/v1/health
/api/v1/health/ready
```

Evite endpoints excessivamente especializados quando filtros na coleção resolverem com clareza.

---

# 12. Fundação visual e UX

## 12.1 Spectrum 2 como única linguagem visual

Todo App, Admin e Site devem partir dos componentes e tokens do **Adobe Spectrum 2**.

Use componentes oficiais para:

- Button e ActionButton;
- TextField e SearchField;
- ComboBox e Picker;
- Checkbox, Radio, Switch;
- DatePicker e componentes de data/hora;
- Dialog;
- AlertDialog quando adequado;
- Menu e ActionMenu;
- Tabs;
- TableView;
- SideNav;
- Badge/StatusLight equivalentes disponíveis;
- Toast;
- ProgressCircle/Skeleton ou padrões oficiais equivalentes;
- Tooltip;
- Breadcrumbs quando aplicável.

Customização visual deve ser mínima e orientada por layout.

## 12.2 Styling

Para composição adicional:

```ts
import {style, focusRing} from '@react-spectrum/s2/style' with {type: 'macro'};
```

Use tokens Spectrum para:

- `backgroundColor`;
- `color`;
- `borderColor`;
- `borderRadius`;
- `boxShadow`;
- `font`;
- `gap`;
- espaçamentos;
- breakpoints;
- estados interativos.

Não usar valores arbitrários quando existir token correspondente.

## 12.3 Página

Área de conteúdo:

- centralizada;
- largura máxima aproximada entre 1360 e 1440 px;
- gutters responsivos;
- sem excesso de cartões;
- formulários limitam sua própria largura;
- conteúdo denso continua legível em 320 px.

## 12.4 Cabeçalhos

Estrutura:

```text
Retorno opcional
Título
Descrição somente quando acrescenta contexto real
Abas opcionais
Ações alinhadas à direita
```

Evitar repetir o título em descrições.

## 12.5 Tabelas

- linha inteira é destino quando fizer sentido;
- controles internos não disparam navegação da linha;
- cabeçalho claro;
- linhas com densidade confortável;
- valores monetários à direita;
- sem truncar dado essencial;
- container rola horizontalmente antes de quebrar a página;
- pesquisa e filtros ficam acima da tabela;
- paginação na mesma faixa das ferramentas;
- estado vazio diferencia acervo vazio de filtro sem resultado.

## 12.6 Pesquisa e filtros

Listagens internas:

- pesquisa automática após cerca de 300 ms;
- Enter pode antecipar;
- mudar filtro retorna à página 1;
- `Limpar filtros` volta aos padrões daquela tela;
- filtros principais visíveis;
- filtros secundários em `Mais filtros`;
- estado da consulta deve sobreviver à ida para uma ficha e ao retorno.

Seletores de relacionamento:

- pesquisa a partir de 2 caracteres;
- cerca de 300 ms;
- até 10 sugestões relevantes;
- não carregar milhares de itens apenas para preencher ComboBox.

## 12.7 Blocos de leitura

Não criar um cartão por campo.

Um registro usa:

```text
Bloco de dados
  Seção
    rótulo: valor
    rótulo: valor
  ─────────────
  Seção seguinte
```

Grades responsivas:

- 1 coluna estreita;
- 2 colunas em tablet;
- 3 ou 4 quando a largura realmente permitir.

## 12.8 Modais

Criação e edição comuns usam Dialog.

Regras:

- cabeçalho, corpo e rodapé claros;
- Cancelar e ação principal;
- não perder o primeiro valor digitado;
- avisar ao fechar rascunho modificado quando necessário;
- erro da API permanece no diálogo;
- não fechar em caso de recusa do servidor.

## 12.9 Responsividade

- abaixo de 768 px a navegação lateral vira sobreposição;
- botão Menu abre e fecha;
- cortina fecha;
- Esc fecha;
- foco retorna ao acionador;
- conteúdo volta a usar largura inteira quando a navegação estiver fechada.

Spectrum já fornece comportamento adaptativo para ponteiro, toque, contraste e preferências de movimento; não substitua esse comportamento por soluções locais.

---

# 13. APP — casca principal

## Cabeçalho

```text
[ORVYA] [Nome do escritório]        [Pesquisa Global] [+] [Notificações] [Conta]
```

### `+` global

Exibir somente ações permitidas e habilitadas pelo Plano:

- Nova atividade;
- Novo processo;
- Nova Pessoa;
- Novo Documento;
- Novo lançamento.

Cada item abre o mesmo formulário usado pelo módulo correspondente.

Não duplicar formulários.

## Navegação principal

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

Menu da conta:

```text
Meu perfil
Configurações do escritório
Sair
```

A navegação e ações são filtradas pelas capacidades retornadas pelo servidor.

---

# 14. APP — páginas

# 14.1 Área de trabalho `/dashboard`

A Área de trabalho é uma **mesa diária**, não um painel de KPIs.

Estrutura desktop:

```text
[Área de trabalho]
[Aviso Teste Grátis, se aplicável]

┌──────────────────────────────────────────────┬─────────────────────────┐
│ MINHAS ATIVIDADES                            │ CALENDÁRIO              │
│ [Hoje] [Esta semana] [Este mês] [Filtros]   │       ‹ mês ano ›       │
│                                              │  S T Q Q S S D          │
│ HOJE / VENCIDAS / demais grupos             │  · · · · · · ·          │
│ marcador | Atividade              modalidade│                         │
│           Processo                          │ RESUMO DO ESCRITÓRIO     │
│           data/hora               [Concluir]│ Processos cadastrados N │
│ ...                                          │ Processos monitorados N │
│ + N atividades                              │ Pessoas cadastradas N   │
│ [Ver todas na Agenda]                       │ Atividades pendentes N  │
└──────────────────────────────────────────────┴─────────────────────────┘
```

Em largura menor que aproximadamente 960 px, empilhar com `Minhas atividades` primeiro.

## Minhas atividades

- somente Atividades do usuário atual;
- somente pendentes no fluxo de trabalho da mesa;
- modos principais mutuamente exclusivos: Hoje, Esta semana, Este mês;
- `Mais filtros`: Modalidade e Sem data;
- dia escolhido no calendário filtra a lista naquela data;
- `Voltar para hoje` restaura Hoje;
- mostrar até 12 itens;
- excedente vira `+ N atividades`;
- não usar paginação nesta tela;
- linha abre a página da Atividade;
- marcador usa cor catalogada do tipo;
- Atividade vencida difere apenas pelo texto de data/hora em estado negativo Spectrum;
- não colocar selo “Atrasada” nessa mesa;
- ação rápida única na linha: `Concluir`, com confirmação exigida pela regra de transição.

## Calendário compacto

- mensal;
- navegação simples anterior/próximo;
- ponto ou indicação mínima em dias com Atividade pendente do usuário;
- trocar mês não altera automaticamente o filtro da lista;
- escolher dia filtra a lista;
- sem painel lateral.

## Resumo do escritório

Somente quatro linhas, nessa ordem:

1. Processos cadastrados;
2. Processos monitorados;
3. Pessoas cadastradas;
4. Atividades pendentes neste mês.

Cada linha abre o módulo já filtrado quando houver destino aplicável.

Sem gráficos, personalização de widgets ou drag-and-drop na Área de trabalho.

---

# 14.2 Agenda `/agenda`

Título: `Agenda e Atividades`.

Topo:

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

Agrupar visualmente por data.

Ações rápidas:

- concluir/reabrir;
- reagendar;
- redesignar;
- editar;
- cancelar;
- excluir, conforme capacidade e estado.

### Dia

- uma coluna temporal;
- faixa `Sem horário`;
- grade por hora;
- criação em horário clicado quando permitido;
- arraste para reagendar quando permitido;
- alternativa por ação `Reagendar` sempre disponível.

### Semana

- sete colunas;
- faixa `Sem horário`;
- linha de horário atual;
- colisões organizadas sem sobreposição ilegível;
- clicar no cabeçalho de um dia abre visão Dia.

### Mês

- grade de sete colunas;
- poucos itens visíveis por dia;
- `+ N` abre visão Dia daquele dia;
- clicar no dia abre visão Dia;
- não usar painel lateral.

### Ficha da Atividade `/agenda/:id`

```text
[← Agenda] ● Título                  [Estado] [ações rápidas] [...]
           Modalidade · Processo · Quando · Responsável

INFORMAÇÕES DA ATIVIDADE
  Descrição
  ─────────────────────
  Dados
  Quando | Responsável | Marco de atraso | Origem | Fuso
  campos específicos da modalidade
  ─────────────────────
  Processo
  vínculo atual [Trocar/Vincular] [... Remover]
  ─────────────────────
  Histórico
  linha do tempo
```

Providência criada de Publicação permanece vinculada ao Processo da Publicação enquanto essa origem existir.

---

# 14.3 Pessoas `/pessoas`

```text
[Pessoas]                                             [Adicionar pessoa]
[Pesquisar nome/documento/contato] [Natureza] [paginação]

| Nome | Natureza | Documento | E-mail principal | Telefone principal | Atualizada em |
```

Linha inteira abre a ficha.

### Ficha `/pessoas/:id`

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

A ficha é read-first. Adicionar e editar abre Dialog.

Aba Processos:

```text
| Processo | Situação | Responsável principal |
```

Aba Financeiro:

```text
| Lançamento | Vencimento | Principal | Em aberto |
```

Documentos mostra vínculos do mesmo Documento real. Histórico usa linha do tempo.

Menu `...`:

- Gerar documento, se autorizado;
- Excluir Pessoa, com confirmação auditável.

---

# 14.4 Processos `/processos`

```text
[Processos]                                           [Novo processo]
[Pesquisar número/título/protocolo] [Natureza] [Monitoramento] [paginação]

| Processo | Situação | Responsável principal | Atualização |
```

Célula `Processo`:

- identificação principal;
- `Parte 1 x Parte 2` quando disponível;
- segunda linha `Judicial/Administrativo · Monitorado/Não monitorado`.

### Cadastro

Fluxo inicial oferece somente as formas realmente implementadas:

- localizar Judicial por número CNJ;
- busca em lote por OAB quando a integração judicial estiver configurada;
- cadastro manual Judicial;
- cadastro Administrativo.

Sem Situação padrão configurada, impedir cadastro e indicar o que falta.

### Ficha `/processos/:id`

```text
[← Processos] Parte 1 x Parte 2                  [Monitoramento] [+] [Editar] [...]
              identificação · Judicial/Admin · Situação · Tribunal
[Resumo] [Atividades] [Publicações] [Documentos] [Financeiro] [Histórico]
```

`+` contextual:

- Nova atividade;
- Vincular pessoa;
- Adicionar Documento;
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

Judicial mostra:

- número CNJ;
- tribunal;
- grau;
- classe;
- assunto;
- valor da causa;
- distribuição;
- monitoramento.

Administrativo mostra:

- protocolo;
- tipo;
- órgão;
- início;
- valor de referência.

### Financeiro do Processo

Resumo apenas do Processo:

- a receber;
- vencido;
- recebido;
- lançamentos vinculados;
- `Novo lançamento`;
- `Ver no Financeiro`.

Não criar mini sistema financeiro dentro da ficha.

---

# 14.5 Publicações `/publicacoes`

```text
[Publicações]
[Novas N] [Tratadas N] [Total N]
[Pesquisar número/tipo/tribunal/texto] [Condição] [paginação]

| Processo | Tipo | Data da fonte | Recebida em | Condição | Trecho | Ações |
```

- condições somente Nova/Tratada;
- linha abre Publicação, não ficha do Processo;
- Processo continua acessível dentro da ficha;
- não existe importação manual;
- mostrar indisponibilidade da fonte quando integração judicial não estiver operacional.

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

`Concluir e abrir a próxima` só navega depois de conclusão confirmada com sucesso e preserva o recorte original.

`Descartar` fica em `...` e exige confirmação auditável.

---

# 14.6 Documentos `/documentos/biblioteca`

```text
[Documentos]                       [Gerenciar modelos] [Incluir Documento]
[Requisitos de envio ▾]
[Pesquisar nome/descrição/tipo] [Tipo de Documento] [paginação]

| Documento | Tipo | Arquivo | Tamanho | Cadastrado em |
```

Sinalizar `Exclusão não concluída` quando aplicável.

### Inclusão

Dialog único:

1. escolher arquivo;
2. transferir e confirmar;
3. nome;
4. Tipo de Documento;
5. descrição;
6. vínculo opcional quando iniciado fora da Biblioteca;
7. cadastrar.

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

Prévia:

- PDF;
- imagens suportadas;
- demais formatos informam indisponibilidade e oferecem download.

Se exclusão estiver pendente:

- banner explicando;
- ocultar download, edição, vínculo e substituição;
- ação visível `Retomar exclusão`.

---

# 14.7 Financeiro

Navegação interna:

```text
Lançamentos | Movimentações | Fluxo de caixa | Conciliação bancária | Configurações
```

## Lançamentos `/financeiro/lancamentos`

```text
[Financeiro]                                      [Novo lançamento] [...]
[contas/saldos]
[Pesquisa] [Natureza] [Situação] [Período] [Mais filtros] [paginação]

| Lançamento | Natureza | Principal | Em aberto | Vencimento | Situação |

Receitas em aberto: ...      Despesas em aberto: ...
```

`...` do cabeçalho:

- Informar saldo de abertura;
- Registrar transferência;
- Atualizar.

Filtros secundários:

- data de referência;
- categoria;
- centro de custo;
- responsável;
- ordenação e direção;
- período personalizado.

Totais são do conjunto filtrado inteiro.

### Ficha do lançamento `/financeiro/lancamentos/:id`

Leitura do lançamento, vínculos com Pessoa, Processo e Documento, parcelas, baixas, ações de editar, baixar, estornar, cancelar/reabrir conforme estado e histórico.

## Movimentações `/financeiro/movimentacoes`

Extrato com:

- pesquisa;
- período efetivo;
- origem;
- forma;
- ordenação;
- saldo corrido somente quando o recorte permitir cálculo correto.

## Fluxo de caixa `/financeiro/fluxo`

Visão temporal de entradas e saídas e totais do recorte, usando valores calculados pelo servidor.

## Conciliação `/financeiro/conciliacao`

Conciliação bancária como tela própria, sem duplicar como segundo domínio.

## Configurações `/financeiro/configuracoes`

Gerenciar:

- contas bancárias e caixas;
- categorias;
- centros de custo;
- formas de pagamento.

---

# 14.8 Relatórios `/relatorios`

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

Exportar só fica disponível após execução.

Se filtros forem alterados depois de executar:

- manter resultado anterior;
- avisar que existem mudanças ainda não aplicadas;
- nova execução substitui a referência ativa.

`/relatorios/modelos` administra definições salvas quando habilitado. Não criar segundo motor de relatório.

---

# 14.9 Pesquisa Global `/pesquisa`

- campo grande;
- mínimo de 2 caracteres;
- resultado agrupado por entidade disponível;
- cada linha abre o registro;
- não revelar existência de entidades sem permissão;
- mesma semântica da pesquisa compacta do cabeçalho.

---

# 14.10 Notificações `/alertas`

- filtros Todos, Novos e Lidos;
- tipo opcional em filtros secundários;
- lista com mensagem, contexto e instante;
- clicar abre destino;
- abrir item novo marca leitura individual;
- `Marcar todas como lidas` permitido com confirmação curta;
- preferências ficam no Perfil.

---

# 14.11 Meu perfil `/conta/perfil`

Três seções, nesta ordem:

```text
Identificação | Notificações | Segurança
```

## Identificação

- nome;
- e-mail;
- foto de perfil;
- demais dados pessoais realmente existentes;
- edição simples;
- foto depende do armazenamento de objetos e mostra indisponibilidade real quando esse serviço não estiver configurado.

## Notificações

Preferências pessoais dos alertas internos.

## Segurança

- alterar senha;
- informações de sessão e segurança aplicáveis;
- encerrar a própria sessão.

Preferências pessoais nunca ficam nas Configurações do escritório.

---

# 14.12 Configurações do escritório

Casca única com sete áreas conceituais:

1. Escritório;
2. Equipe e acesso;
3. Agenda;
4. Catálogos;
5. Modelos de documentos;
6. Plano e utilização;
7. Ações críticas.

## Escritório `/conta/configuracoes`

Read-first:

```text
Nome do escritório | CPF/CNPJ
Telefone           | E-mail
Fuso horário
Logo
```

`Editar` abre Dialog.

## Equipe e acesso `/conta/configuracoes/usuarios`

Lista:

```text
| Nome | E-mail | Status | Administrador | Atualização |
```

Ações:

- convidar usuário;
- editar permissões;
- tornar/remover Administrador do Escritório;
- suspender/reativar;
- excluir com reatribuição quando necessária;
- reenviar convite pendente.

## Agenda `/conta/configuracoes/agenda`

Somente configuração compartilhada do escritório:

- fuso horário;
- atalho para Catálogos de tipos de Atividade.

## Catálogos `/conta/configuracoes/catalogos`

Gerenciar catálogos tenant-scoped usados por:

- Pessoas;
- Processos;
- Agenda;
- Documentos;
- outras áreas funcionais.

Famílias financeiras apontam para Financeiro > Configurações quando essa for a fonte central.

Tipos de Atividade incluem cor visual escolhida entre tokens fechados do Spectrum definidos pelo produto.

## Modelos `/conta/configuracoes/modelos`

- lista de Modelos DOCX;
- cadastrar;
- editar metadados;
- substituir DOCX-base;
- validar variáveis;
- excluir;
- consultar variáveis disponíveis.

## Plano e utilização `/conta/configuracoes/plano`

- Plano atual;
- usuários utilizados/limite;
- Processos monitorados utilizados/limite;
- armazenamento utilizado/limite;
- recursos habilitados e não incluídos;
- sem preço, cobrança, checkout ou troca de Plano pelo escritório.

## Ações críticas `/conta/configuracoes/acoes-criticas`

Área separada para ações destrutivas ou irreversíveis da conta efetivamente suportadas.

---

# 14.13 Buscas processuais `/processos/buscas`

Histórico e controle das consultas externas judiciais.

Exibir:

- tipo de busca;
- parâmetro;
- estado;
- início;
- conclusão;
- quantidade de resultados;
- falha quando existir.

Ao concluir:

- mostrar encontrados;
- indicar os já cadastrados;
- permitir seleção;
- `Adicionar selecionados` cria apenas os escolhidos;
- nunca cadastrar tudo automaticamente só porque a fonte retornou.

---

# 15. Site público

O Site usa **Spectrum 2 exclusivamente** para componentes e tokens de interface.

Objetivo: apresentar o produto atual e levar a cadastro/login, sem inventar preço.

Header:

```text
[ORVYA]  Soluções ▾  Para você ▾  Planos  Por que Orvya?    Entrar  [Experimente grátis]
```

Conteúdo principal:

- faixa de anúncio de 7 dias grátis;
- hero `Mais clareza. Mais tempo. Mais Orvya.`;
- apresentação integrada de Processos, Agenda, Pessoas, Documentos, Financeiro e Publicações;
- benefícios e contexto;
- seções de soluções;
- seção por público;
- Planos reais carregados de `GET /api/v1/site/planos`;
- CTA para `https://app.orvya.net/cadastro`;
- CTA Entrar para `https://app.orvya.net/`;
- rodapé institucional.

Planos:

- nome;
- descrição;
- recursos;
- limites;
- destaque do Teste Grátis quando aplicável;
- dizer `7 dias`;
- nunca inventar preço.

O Site é responsivo e pode usar navegação expandida no desktop e Dialog/Popover/Menu Spectrum no mobile.

Demonstrações de interface usam dados fictícios identificados como ilustrativos.

Não criar uma segunda linguagem visual para marketing.

---

# 16. Entrada, cadastro e recuperação

# 16.1 Login

```text
[Logo]
Entrar no Orvya
E-mail
Senha
[Entrar]
Esqueci minha senha
Criar escritório / experimentar grátis
```

Sem método alternativo de identidade externa.

# 16.2 Cadastro

Cadastro público cria:

1. usuário inicial;
2. escritório;
3. vínculo como Administrador do Escritório;
4. Teste Grátis de 7 dias;
5. confirmação de e-mail por código ou token antes do primeiro acesso operacional.

Campos iniciais:

- nome do usuário;
- e-mail;
- senha;
- nome do escritório.

Não pedir configuração avançada no onboarding.

# 16.3 Recuperação de senha

- solicitar e-mail;
- resposta neutra para evitar enumeração;
- enviar token ou código de uso único;
- validar expiração;
- permitir nova senha;
- invalidar token após uso.

---

# 17. ADMIN — Administração da Plataforma

Uma única aplicação e uma única casca.

Não recriar seleção entre painéis separados.

# 17.1 Header

```text
[ORVYA] Administração da Plataforma › Página atual   [Pesquisa administrativa] [Conta admin]
```

# 17.2 Sidebar

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
  E-mail
  Armazenamento
  Comunica CNJ
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

Abaixo de 768 px a SideNav Spectrum vira painel sobreposto.

---

# 17.3 Dashboard do Admin

Ordem:

1. Pendências administrativas;
2. Estado da plataforma;
3. Distribuição por Plano;
4. Atividade recente.

## Pendências administrativas

Pode incluir:

- escritórios que exigem atenção;
- Teste Grátis expirado;
- consumo acima de limite;
- convite com entrega pendente;
- integrações não configuradas ou com diagnóstico ruim;
- pendências operacionais relevantes.

## Estado da plataforma

Indicadores:

- Contas ativas;
- Contas suspensas;
- Contas em teste;
- Usuários ativos;
- Processos monitorados;
- armazenamento utilizado pelos escritórios.

Não misturar CPU, RAM ou disco neste bloco.

## Distribuição por Plano

```text
| Plano | Contas |
```

## Atividade recente

```text
| Data/hora | Área | Ação | Autor | Alvo |
```

---

# 17.4 Escritórios

Listagem:

```text
[Escritórios] [Novo escritório]
[Pesquisa] [Status] [Plano] [paginação]

| Escritório | Status | Plano | Usuários | Processos monitorados | Criado em |
```

### Ficha do Escritório

```text
[← Escritórios] Nome                [Status] [Plano] [Acessar escritório] [Editar] [...]
[Resumo] [Usuários] [Plano e utilização] [Histórico]
```

Resumo:

- identificação;
- contato;
- fuso;
- criação;
- metadados administrativos.

Usuários:

- listagem do tenant;
- estado;
- Administrador do Escritório;
- sem mostrar conteúdo jurídico.

Plano e utilização:

- Plano;
- limites;
- consumo;
- monitoramento;
- armazenamento.

`Acessar escritório` abre fluxo assistido auditado.

Menu `...`:

- Alterar Plano;
- Suspender/Reativar;
- Excluir, conforme regra e confirmação auditável.

---

# 17.5 Usuários globais

Pesquisa administrativa sobre usuários de escritórios.

Exibir somente metadados necessários à administração da plataforma:

- nome;
- e-mail;
- escritório;
- status;
- Administrador do Escritório;
- criação/atualização.

Não transformar essa página em visualização de dados jurídicos.

---

# 17.6 Planos

CRUD de Planos.

Campos:

- nome;
- descrição;
- estrutural de teste;
- recursos;
- limites.

Limites:

- usuários;
- Processos monitorados;
- armazenamento.

Recursos:

- núcleo;
- Publicações;
- Documentos;
- Modelos de documentos;
- Financeiro;
- Relatórios.

Plano estrutural de Teste Grátis:

- sempre existe;
- 7 dias;
- padrão do autocadastro;
- não pode ser eliminado sem substituição funcional expressamente definida.

Excluir Plano em uso exige escolher destino e reatribuir contas antes da remoção.

---

# 17.7 Administradores da Plataforma

Listagem:

```text
| Nome | E-mail | Status | Último acesso | Atualização |
```

Ações:

- adicionar;
- editar;
- suspender;
- reativar;
- excluir.

Nunca suspender ou excluir o último Administrador da Plataforma ativo.

---

# 17.8 Catálogos globais

Separar:

- Catálogos Iniciais: modelos copiados ou usados na criação de escritórios;
- Catálogos Referenciais: dados globais usados em Processos e integrações;
- Variáveis de Documentos: registro técnico central.

Variável de Documento:

- token;
- descrição;
- origem;
- contextos;
- estado/uso.

Substituição global de variável só deve existir se implementada de forma transacional, previsível e auditada.

---

# 17.9 Integrações e conexões

Somente três famílias externas fazem parte desta reconstrução:

1. E-mail;
2. Armazenamento de objetos;
3. Comunica CNJ.

Cada ficha administrativa possui, quando fizer sentido:

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

Segredos:

- nunca retornam completos pela API;
- não aparecem no HTML;
- alteração de segredo substitui o valor armazenado;
- leitura mostra apenas presença/configuração.

## E-mail

Usado para:

- confirmação de cadastro;
- convite;
- recuperação de senha;
- mensagens transacionais futuras explicitamente implementadas.

Configuração inclui:

- host;
- porta;
- usuário;
- senha;
- remetente;
- TLS conforme servidor.

## Armazenamento

Compatível inicialmente com Amazon S3 e endpoints S3 equivalentes.

Usado por:

- Documentos;
- Modelos DOCX;
- logos;
- fotos de perfil;
- arquivos derivados persistidos quando houver decisão explícita de salvamento.

## Comunica CNJ

Usado para:

- busca por Processo;
- busca por OAB;
- monitoramento de Processos;
- recebimento de Publicações.

Uma rotina central processa monitoramentos elegíveis. Não criar agendador por Processo.

---

# 17.10 Operação

## Visão operacional

Mostrar:

- API;
- worker;
- banco;
- armazenamento configurado ou não;
- integração judicial;
- serviço de e-mail;
- últimas execuções relevantes;
- versão da aplicação;
- versão do schema.

## Serviços

Listar componentes conhecidos e seu estado.

Comandos operacionais devem ser fechados e allowlisted. Nunca aceitar comando shell arbitrário pela API.

## Execuções

Tarefas persistentes internas:

- Em andamento;
- Concluída;
- Erro.

Exibir tipo, início, fim, resultado resumido e erro seguro.

## Banco de dados

Mostrar estado e metadados seguros do banco principal.

Não expor senha, DSN completo ou chave.

## Migrations

Página somente de leitura nesta versão simplificada:

```text
| Revisão | Descrição | Situação | Aplicada em |
```

Aplicação de migration ocorre pelo deploy, não por botão genérico do painel.

## Capacidade

Exibir CPU, memória e disco na área operacional, separados dos indicadores de negócio do Dashboard.

## Operações e limitações

Registrar:

- recursos desabilitados;
- integrações não configuradas;
- operações administrativas bloqueadas;
- razão objetiva.

---

# 17.11 Auditoria

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

Conciliação Técnica pode mostrar inconsistências detectadas entre estado esperado e estado operacional, sem editar dados diretamente pela tabela.

---

# 18. Componentes compartilhados

Criar um pacote compartilhado enxuto, por exemplo `frontend/shared`.

Ele deve concentrar:

- Provider Spectrum;
- marca;
- shell do App;
- shell do Admin;
- cliente HTTP;
- tratamento de erros;
- sessão;
- permissões;
- roteamento;
- formatação de data e dinheiro;
- componentes de domínio realmente reutilizados;
- abstrações pequenas sobre Dialog, TableView, SideNav e Menu somente quando evitarem duplicação de regra.

Não construir um Design System próprio acima do Spectrum.

Uma abstração compartilhada deve resolver comportamento, não redesenhar o componente oficial.

---

# 19. Navegação e estado de página

Usar roteamento client-side convencional.

Rotas canônicas do App:

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

Ao abrir uma ficha a partir de listagem, preservar:

- termo;
- filtros;
- paginação;
- ordenação;
- visão da Agenda;
- data de referência;
- posição aproximada de rolagem quando útil.

Voltar retorna ao mesmo contexto.

---

# 20. Pesquisa no cabeçalho

## App

Campo Pesquisa Global:

- 2 caracteres;
- 300 ms;
- painel agrupado;
- setas percorrem resultados;
- Enter abre;
- Esc fecha e devolve foco;
- `Ver todos os resultados` abre `/pesquisa`.

## Admin

Mesma mecânica para Pesquisa Administrativa.

Grupos possíveis:

- escritórios;
- usuários;
- Planos;
- integrações;
- serviços;
- registros administrativos.

Em mobile, pode iniciar como ícone e expandir o mesmo campo Spectrum.

---

# 21. Worker

Um único worker atende rotinas assíncronas.

Responsabilidades iniciais:

- monitoramento judicial;
- recebimento e deduplicação de Publicações;
- expiração do Teste Grátis;
- envio transacional de e-mail quando desacoplamento for útil;
- limpeza de reservas de arquivo abandonadas;
- conversões documentais demoradas;
- outras tarefas persistentes explicitamente necessárias.

Não criar um worker por escritório.

Tarefas importantes possuem:

- id;
- tipo;
- payload mínimo;
- estado;
- tentativas;
- próxima tentativa;
- erro resumido;
- timestamps.

Retries devem ser limitados e idempotentes.

---

# 22. Arquivos e geração documental

## Upload

- validar extensão e MIME no servidor;
- limitar tamanho por contrato;
- validar cota do Plano antes da confirmação final;
- calcular SHA-256 no servidor;
- usar chave física baseada em `account_id` + UUID, nunca nome do escritório;
- downloads sempre autenticados.

## Pré-visualização

- servir bytes autenticados;
- navegador cria URL temporária local;
- revogar URL ao desmontar;
- não persistir cópia desnecessária no dispositivo.

## DOCX

Processador deve substituir tokens também onde possível em:

- parágrafos;
- tabelas;
- cabeçalhos;
- rodapés.

Se token inválido existir, Modelo fica inválido e não gera até ser corrigido.

## PDF

Conversão pode utilizar ferramenta instalada no container ou biblioteca apropriada, mantendo arquivos temporários fora do acervo permanente.

---

# 23. Financeiro — precisão

Nunca converter dinheiro para `float` no backend nem no frontend.

API trafega dinheiro como string decimal.

Exemplo:

```json
{
  "principal": "1250.00",
  "open": "500.00"
}
```

Servidor calcula:

- saldo;
- total recebido;
- total pago;
- totais do recorte;
- fluxo;
- vencimento;
- situação.

Frontend apenas formata em `pt-BR`.

Operações financeiras mutáveis devem aceitar chave de idempotência quando repetição acidental puder duplicar efeito.

---

# 24. Histórico

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

Histórico do Processo aparece como timeline agrupada por dia.

Pode registrar:

- criação;
- edição relevante;
- mudança de Situação;
- parte adicionada/removida;
- responsável alterado;
- Atividade criada/vinculada;
- Documento vinculado/desvinculado;
- fatos financeiros vinculados;
- monitoramento alterado.

Não existe botão genérico `Adicionar histórico`.

Evento manual do caso é Atividade modalidade Evento.

---

# 25. Acessibilidade

A implementação deve aproveitar os comportamentos do Spectrum 2 e preservar:

- navegação por teclado;
- focus ring oficial;
- labels reais;
- nomes acessíveis de botões por ícone;
- `aria-current` na navegação;
- Dialog com foco contido;
- retorno do foco ao fechar menu/Dialog;
- contraste do sistema;
- escala para toque;
- preferência de movimento reduzido;
- alto contraste;
- texto ampliado;
- tabelas navegáveis;
- cor nunca como único indicador.

Não remover foco visível para fins estéticos.

---

# 26. Deploy

Objetivo: um comando instalar ou atualizar a aplicação em uma VPS Linux limpa com Docker disponível.

Fluxo recomendado:

```text
1. validar .env
2. construir imagens
3. iniciar PostgreSQL
4. aguardar readiness do banco
5. executar migration
6. iniciar API
7. iniciar worker
8. iniciar ops
9. construir/publicar Site, App e Admin
10. iniciar/recarregar Nginx
11. verificar /api/v1/health
12. verificar /api/v1/health/ready
13. smoke HTTP dos três hosts
```

## Nginx

Hosts:

```text
orvya.net
app.orvya.net
admin.orvya.net
```

Cada host entrega seu frontend.

`/api/v1/*` faz proxy para API.

Uploads não passam por diretório público.

## TLS

Usar certificados válidos e renovação automatizada pela infraestrutura escolhida.

Não colocar chave privada no repositório.

---

# 27. Health checks

## `GET /api/v1/health`

Somente vivacidade:

```json
{"status":"ok"}
```

Não consultar dependências.

## `GET /api/v1/health/ready`

Prontidão:

- banco acessível;
- schema na revisão esperada;
- aplicação apta a atender.

Integração opcional indisponível não derruba readiness geral.

## Diagnóstico administrativo

Endpoint autenticado separado pode apresentar situação de:

- banco;
- armazenamento;
- e-mail;
- integração judicial;
- worker.

Sem expor segredo.

---

# 28. Estratégia de implementação em uma sessão

A IA deve executar em grandes blocos, evitando ciclos de especificar-testar-documentar a cada detalhe.

## Fase 1 — Fundação

Implementar de uma vez:

- monorepo;
- Docker;
- banco;
- migration inicial;
- configuração;
- sessão;
- autenticação por e-mail e senha;
- CSRF;
- tenants;
- Planos;
- permissões;
- Spectrum 2;
- shells de App e Admin;
- health checks.

Verificação curta:

- migration sobe;
- API importa;
- login básico funciona;
- frontend compila.

Não abrir bateria extensa de testes.

## Fase 2 — Núcleo jurídico

Implementar em sequência contínua:

- Pessoas;
- Processos;
- Atividades;
- Agenda;
- Área de trabalho;
- Pesquisa;
- Notificações;
- Histórico.

Verificação curta por chamadas manuais/smoke.

## Fase 3 — Conteúdo e integrações

Implementar:

- serviço de arquivos;
- Documentos;
- Modelos;
- geração DOCX/PDF;
- e-mail;
- armazenamento;
- integração judicial;
- Publicações;
- buscas processuais.

Sem exigir credenciais externas para continuar a construção.

## Fase 4 — Financeiro e Relatórios

Implementar:

- Lançamentos;
- baixas;
- transferências;
- Movimentações;
- Fluxo;
- Conciliação;
- Configurações financeiras;
- Relatórios;
- exportações.

Verificar operações financeiras principais e seguir.

## Fase 5 — Administração

Implementar:

- Dashboard Admin;
- Escritórios;
- Usuários globais;
- Planos;
- Administradores;
- Catálogos;
- Variáveis;
- Integrações;
- Operação;
- Auditoria;
- acesso assistido.

## Fase 6 — Site e deploy

Implementar:

- Site Spectrum 2;
- Planos reais;
- CTAs;
- cadastro;
- Nginx;
- HTTPS;
- Docker final;
- comando de instalação/atualização.

## Fase 7 — Estabilização final

Somente agora executar a rodada completa:

1. migration limpa em banco vazio;
2. typecheck;
3. builds de Site/App/Admin;
4. testes rápidos de API;
5. subir stack completa;
6. smoke dos hosts;
7. criar escritório real de teste;
8. login;
9. Pessoa;
10. Processo;
11. Atividade;
12. Agenda;
13. Documento, se armazenamento estiver configurado;
14. Lançamento;
15. Relatório;
16. Admin;
17. permissões;
18. isolamento entre dois escritórios;
19. corrigir todos os defeitos encontrados;
20. repetir somente a bateria necessária até ficar verde.

---

# 29. Testes mínimos

Não construir um projeto de testes maior que o produto.

## Backend

Poucos testes de integração de alto valor:

- login;
- isolamento entre tenants;
- permissão negada;
- conflito de revisão;
- transição de Atividade;
- duplicidade de Processo/Pessoa relevante;
- financeiro decimal e idempotência;
- upload e cota com storage simulado;
- deduplicação de Publicação;
- expiração do Teste Grátis.

## Frontend

Priorizar smoke E2E:

```text
login
Área de trabalho
Pessoas lista → ficha → edição
Processos lista → ficha
Agenda lista → atividade
Publicações lista → ficha
Documentos lista → ficha
Financeiro lista → ficha
Relatórios executar
Perfil
Configurações
Admin Dashboard → Escritório
```

Não perseguir cobertura percentual arbitrária.

---

# 30. Dados iniciais

O bootstrap deve criar somente o necessário para a instalação funcionar:

- instalação;
- Administrador da Plataforma inicial via variável segura ou comando interativo;
- Plano estrutural de Teste Grátis;
- recursos padrão do Plano;
- catálogos mínimos indispensáveis declarados pelo produto.

Não criar:

- clientes fictícios;
- Processos fictícios;
- Atividades fictícias;
- Publicações fictícias;
- lançamentos fictícios;
- dashboards demonstrativos persistidos.

Dados do Site podem ser ilustrativos apenas no HTML e claramente identificados como fictícios.

---

# 31. Catálogos mínimos

Não exagerar no seed. Criar somente famílias necessárias para o fluxo não nascer travado.

Famílias de conta esperadas:

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
- polos processuais quando não forem enum estrutural.

Financeiro:

- não inventar categorias comerciais por conveniência;
- permitir que o escritório configure contas, categorias, centros e formas.

Catálogos referenciais judiciais são alimentados pela integração ou por carga administrativa própria.

---

# 32. Estados da interface

Toda tela que consulta API trata explicitamente:

- carregando;
- vazio;
- erro;
- indisponível;
- pronto;
- atualizando mantendo conteúdo anterior, quando adequado.

Não apagar a tabela e mostrar spinner a cada filtro se os dados anteriores puderem permanecer inertes até a resposta.

Sem permissão:

- remover área da navegação quando apropriado;
- não mostrar `0` como substituto da falta de acesso.

Sem recurso no Plano:

- área pode desaparecer da navegação;
- quando um contexto relacionado precisar explicar, mostrar `Recurso não incluído no Plano`.

---

# 33. Convenções de texto

Idioma principal: português brasileiro.

Usar termos consistentes:

- `Pessoa`;
- `Processo`;
- `Atividade`;
- `Publicação`;
- `Documento`;
- `Lançamento`;
- `Escritório`;
- `Administrador da Plataforma`;
- `Administrador do Escritório`;
- `Área de trabalho`;
- `Configurações do escritório`;
- `Notificações` na experiência visível.

Evitar:

- jargão técnico em mensagem de usuário;
- IDs internos como identificação principal;
- descrições redundantes;
- textos enormes onde um rótulo claro resolve.

---

# 34. O que não construir

Para manter a reconstrução objetiva, não adicionar sem demanda posterior:

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
- armazenamento duplicado por módulo;
- segundo cadastro de Agenda;
- segundo cadastro de Documento;
- segundo motor financeiro;
- segundo motor de Relatórios;
- fila por tenant;
- shell remoto arbitrário;
- Design System próprio;
- bibliotecas de componentes concorrentes ao Spectrum 2;
- CSS com paleta paralela;
- suíte gigantesca de testes antes do produto funcionar.

---

# 35. Checklist final funcional

## Conta e acesso

- [ ] Cadastro cria escritório e Administrador do Escritório.
- [ ] Confirmação de e-mail funciona.
- [ ] Login por e-mail e senha funciona.
- [ ] Recuperação de senha funciona.
- [ ] Sessão expira corretamente.
- [ ] Conta Suspensa não entra.
- [ ] Usuário Suspenso não entra.
- [ ] Convite de usuário funciona.
- [ ] Permissões são aplicadas no backend.

## Spectrum 2

- [ ] Site usa Spectrum 2.
- [ ] App usa Spectrum 2.
- [ ] Admin usa Spectrum 2.
- [ ] Não há biblioteca visual concorrente.
- [ ] Custom styling usa tokens/macros Spectrum.
- [ ] Ícones são Spectrum.
- [ ] Focus e estados acessíveis estão preservados.

## Área de trabalho

- [ ] Mesa diária em duas colunas no desktop.
- [ ] Minhas atividades antes da coluna lateral no mobile.
- [ ] Hoje/Esta semana/Este mês.
- [ ] filtro por dia do calendário.
- [ ] Sem data.
- [ ] conclusão rápida.
- [ ] resumo em quatro linhas.

## Pessoas

- [ ] CRUD principal.
- [ ] contatos.
- [ ] endereços.
- [ ] identificações.
- [ ] vínculos.
- [ ] ficha read-first.
- [ ] Processos relacionados.
- [ ] Documentos relacionados.
- [ ] Financeiro relacionado quando permitido.

## Processos

- [ ] Judicial.
- [ ] Administrativo.
- [ ] partes.
- [ ] responsáveis.
- [ ] monitoramento.
- [ ] ficha-hub.
- [ ] Atividades.
- [ ] Publicações.
- [ ] Documentos.
- [ ] Financeiro.
- [ ] Histórico.

## Agenda

- [ ] Lista.
- [ ] Dia.
- [ ] Semana.
- [ ] Mês.
- [ ] filtros.
- [ ] arraste com alternativa por comando.
- [ ] página própria da Atividade.
- [ ] concluir/reabrir/cancelar.
- [ ] reagendar/redesignar.

## Publicações

- [ ] recebimento externo.
- [ ] deduplicação.
- [ ] Nova/Tratada.
- [ ] providências.
- [ ] Concluir.
- [ ] Concluir e abrir a próxima.
- [ ] Descartar.
- [ ] navegação sequencial preserva recorte.

## Documentos

- [ ] upload confirmado antes do cadastro.
- [ ] Biblioteca.
- [ ] vínculos.
- [ ] download autenticado.
- [ ] prévia.
- [ ] substituir arquivo.
- [ ] exclusão retomável.
- [ ] Modelos DOCX.
- [ ] geração por Pessoa.
- [ ] geração por Processo.

## Financeiro

- [ ] Receita/Despesa.
- [ ] parcelas.
- [ ] baixa.
- [ ] estorno.
- [ ] transferência.
- [ ] saldos.
- [ ] Movimentações.
- [ ] Fluxo.
- [ ] Conciliação.
- [ ] Configurações.
- [ ] decimal exato.

## Relatórios

- [ ] catálogo.
- [ ] filtros tipados.
- [ ] colunas.
- [ ] ordenação.
- [ ] agrupamento.
- [ ] paginação consistente.
- [ ] totais.
- [ ] PDF.
- [ ] XLSX.

## Admin

- [ ] casca única.
- [ ] Dashboard.
- [ ] Escritórios.
- [ ] ficha do Escritório.
- [ ] acesso assistido.
- [ ] usuários globais.
- [ ] Planos.
- [ ] Administradores.
- [ ] catálogos.
- [ ] variáveis.
- [ ] integrações.
- [ ] serviços.
- [ ] execuções.
- [ ] banco.
- [ ] migrations.
- [ ] capacidade.
- [ ] histórico da Plataforma.

## Integrações

- [ ] e-mail configurável/testável.
- [ ] armazenamento configurável/testável.
- [ ] Comunica CNJ configurável/testável.
- [ ] ausência de configuração não quebra o núcleo.

## Deploy

- [ ] `docker compose up` ou comando documentado equivalente.
- [ ] migration automática controlada.
- [ ] HTTPS.
- [ ] três hosts.
- [ ] health.
- [ ] readiness.
- [ ] logs sem segredos.

---

# 36. Prompt final de execução

A IA implementadora deve interpretar todo o conteúdo acima como uma tarefa única:

> **Construa o Orvya completo no repositório `orvya/orvya`, implementando o produto descrito neste `ORVYA.md` do banco ao frontend e ao deploy. Use Adobe Spectrum 2 exclusivamente como Design System em Site, App e Admin. Trabalhe de forma autônoma, sem interromper a construção para pedir validações intermediárias. Priorize uma arquitetura simples, modular e funcional. Faça verificações curtas apenas nos grandes marcos e deixe a estabilização completa para o final. Não importe a complexidade histórica do projeto anterior. O resultado esperado é uma instalação limpa, funcional, segura, responsiva e reproduzível, fiel ao Orvya atual descrito neste arquivo.**
