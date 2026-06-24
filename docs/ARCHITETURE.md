# BarguesAPP — Architecture Decision Record

> Documento de decisões de arquitetura e engenharia do BarguesAPP.  
> Última atualização: Junho 2026

---

## Stack

| Camada    | Tecnologia                             |
| --------- | -------------------------------------- |
| Runtime   | Python 3.12                            |
| API       | FastAPI 0.138                          |
| Frontend  | HTML5 / CSS / JS                       |
| ORM       | SQLAlchemy 2.0 — Mapped, mapped_column |
| Validação | Pydantic 2.0                           |
| Banco     | SQLite                                 |
| Logs      | logging nativo                         |

---

## Estrutura de pastas

```
barguesAPP/
├── main.py                  # Ponto de entrada da aplicação
├── bargues.db               # Banco de dados local
│
├── docs/
│   ├── ARCHITECTURE.md      # Decisões pré-código
│   ├── FEEDBACK.md          # Experiência do usuário em beta
│   └── erd.png              # Representação gráfica do banco
│
├── backend/
│   ├── database.py          # Engine e sessão
│   ├── logger.py            # Setup centralizado do logger
│   │
│   ├── models/              # Tabelas SQLAlchemy
│   │   ├── caixa.py
│   │   ├── item.py
│   │   ├── categoria.py
│   │   ├── drinks.py
│   │   ├── valor.py
│   │   └── pedidos.py
│   │
│   ├── schemas/             # Contratos Pydantic (Input / Response)
│   │   ├── caixa.py
│   │   ├── item.py
│   │   ├── categoria.py
│   │   ├── drinks.py
│   │   ├── valor.py
│   │   └── pedidos.py
│   │
│   ├── crud/
│   │   ├── crud.py          # Operações com o banco de dados
│   │   ├── helpers.py       # Funções auxiliares e regras de negócio
│   │   └── relatorios.py    # Modelagem e extração de relatórios
│   │
│   └── routes/              # Conexão entre API e CRUD
│
└── frontend/
    └── app.py               # Consome a API e serve o frontend
```

---

## Camadas e responsabilidades

| Arquivo       | Responsabilidade                                |
| ------------- | ----------------------------------------------- |
| `database.py` | Conecta o engine, cria a sessão, expõe `get_db` |
| `models/`     | Define as tabelas — fonte de verdade do banco   |
| `schemas/`    | Contratos de entrada e saída do CRUD            |
| `crud.py`     | Única camada que toca o banco                   |
| `helpers.py`  | Normalização, validações e regras de negócio    |
| `logger.py`   | Configuração centralizada do logging            |
| `routes/`     | Liga os endpoints FastAPI ao CRUD               |
| `frontend/`   | Consome a API REST e serve o HTML               |

---

## Decisões de arquitetura

**FastAPI como API REST**  
O frontend HTML/JS consome a API via fetch. Separação clara entre backend e frontend permite evoluir os dois independentemente.

**Quantidade, não valor**  
O caixa e a sangria recebem contagem de cédulas e moedas. O sistema calcula o total — elimina uso de calculadora e reduz erro humano.

**Linhas vivas**  
O Bargues opera 24 horas. Caixa e pedidos nunca fecham em horário fixo — cada operação é um registro com tipo (registro, sangria, adição), permitindo auditoria completa por período.

**Redundância voluntária**  
Cada operação armazena o estado atual do caixa ou estoque no momento do registro. Facilita relatórios por período sem recalcular a cadeia de operações.

**Valores nullable em valor**  
A tabela `valor` tem `item_id` e `categoria_id` anuláveis. Um valor pode pertencer a um item ou a uma categoria — nunca aos dois ao mesmo tempo.

**Valor preferencial**  
Se um item tiver um valor próprio cadastrado para um drink, esse valor tem prioridade sobre o valor da categoria. A lógica de resolução fica no `helpers.py`.

**Tabela de média de consumo**  
Tabela auxiliar que acumula quantidades pedidas por item. Usada nos relatórios de itens mais e menos vendidos, sem precisar recalcular o histórico completo.

---

## Regras de negócio

| Regra                      | Descrição                                                                       |
| -------------------------- | ------------------------------------------------------------------------------- |
| Valores negativos          | Nenhum valor monetário ou de estoque pode ser negativo — validado no Pydantic   |
| Nome duplicado             | Itens e categorias não podem ter o mesmo nome — `warning` no log + `ValueError` |
| Valor preferencial         | Valor do item tem prioridade sobre valor da categoria para o mesmo drink        |
| Item inativo com estoque   | Continua aparecendo no sumário de estoque, mas não entra no pedido              |
| Valor de item ou categoria | Nunca permitir os dois campos simultaneos                                       |

---

## Regras de operações

| Módulo  | Operação         | Comportamento                                                           |
| ------- | ---------------- | ----------------------------------------------------------------------- |
| Caixa   | Registro         | Registra o valor atual do caixa, soma no caixa diário                   |
| Caixa   | Sangria          | Subtrai do caixa atual, registra no caixa diário                        |
| Caixa   | Adição           | Adiciona dinheiro ao caixa, registra no caixa diário                    |
| Estoque | Quantidade atual | Compara com quantidade recomendada — se abaixo e ativo, entra no pedido |
| Pedido  | Gerar pedido     | Gera documento formatado para realização do pedido                      |

---

## Logging

| Situação                               | Nível       |
| -------------------------------------- | ----------- |
| Registro criado ou editado com sucesso | `INFO`      |
| Nome duplicado rejeitado               | `WARNING`   |
| Falha no `db.commit()`                 | `EXCEPTION` |
| Erro de infraestrutura                 | `ERROR`     |

---

## Testes

| Dado                                    | Quando                                  | Então                                            |
| --------------------------------------- | --------------------------------------- | ------------------------------------------------ |
| `total_cartao_real` negativo            | Registrar valor negativo                | Perguntar confirmação ou converter para positivo |
| Valor xupito Whisky cadastrado          | Registrar valor xupito JB no mesmo item | Verificar prioridade do item sobre a categoria   |
| `"Baileys"` existente                   | Criar outro registro com o mesmo nome   | Rejeitar com `ValueError`                        |
| `"Ron Conqueridor"` inativo com estoque | Consultar estoque                       | Aparece no sumário, não entra no pedido          |
| `Xupito` registrado                     | Item e categoria id registrados         | Anular categoria_id                              |

---

## Relatórios

**Itens totais e ativos**  
Contagem de todos os itens cadastrados, separando ativos e inativos.

**Caixa por período**  
Filtra operações do período e gera resumo comparativo:

- Dinheiro real, cartão real, sangria realizada
- Dinheiro sistema, cartão sistema
- Discrepância dinheiro, discrepância cartão

**Dias sem registro**  
Compara a data atual com o último registro no banco.

**Pedido**  
Tabela formatada: `Nome | Categoria | Quantidade recomendada | Quantidade atual | A pedir`

**Itens mais e menos vendidos**  
Consulta a tabela de média de consumo e gera ranking.

---

## Roadmap

- [ ] Criar `database.py`
- [ ] Configurar `logger.py`
- [ ] Modelar banco em `models/`
- [ ] Criar schemas Pydantic com validações
- [ ] Criar `crud/` básico
- [ ] Testes unitários por módulo
- [ ] Testes de regras de negócio
- [ ] Gerar e conferir relatórios
- [ ] Criar frontend HTML/JS
- [ ] Lançar beta — preencher `FEEDBACK.md`
