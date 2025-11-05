import streamlit as st
import pandas as pd
from dataclasses import dataclass, asdict
from datetime import date, datetime
from typing import Optional, Literal

# ============================================================
# HELPERS DE SESSÃO / "BANCO DE DADOS" EM MEMÓRIA
# ============================================================

def get_list(key: str):
    if key not in st.session_state:
        st.session_state[key] = []
    return st.session_state[key]

def get_counter(key: str):
    if key not in st.session_state:
        st.session_state[key] = 1
    return st.session_state[key]

def inc_counter(key: str):
    st.session_state[key] = get_counter(key) + 1
    return st.session_state[key]

def log_event(description: str, entity_type: str = "GENERIC", entity_id: Optional[int] = None):
    events = get_list("events")
    event_id = get_counter("event_id")
    events.append({
        "id": event_id,
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "entity_type": entity_type,
        "entity_id": entity_id,
        "description": description,
    })
    inc_counter("event_id")

# ============================================================
# MODELOS CORE – ENTIDADES PRINCIPAIS
# ============================================================

@dataclass
class Company:
    id: int
    name: str
    cnpj: str
    regime: Literal["Simples", "Presumido", "Real"]

@dataclass
class CostCenter:
    id: int
    code: str
    name: str

@dataclass
class Account:
    id: int
    code: str
    name: str
    type: Literal["Ativo", "Passivo", "Receita", "Despesa", "Patrimônio"]

@dataclass
class Customer:
    id: int
    name: str
    doc: str
    kind: Literal["PF", "PJ"]
    company_id: int

@dataclass
class Product:
    id: int
    name: str
    sku: str
    ncm: str
    unit: str
    company_id: int

@dataclass
class FinancialTitle:
    id: int
    company_id: int
    kind: Literal["AP", "AR"]  # AP = a pagar, AR = a receber
    party_name: str
    doc_number: str
    issue_date: date
    due_date: date
    amount: float
    cost_center_id: Optional[int]
    account_id: Optional[int]
    status: Literal["Aberto", "Pago", "Cancelado"] = "Aberto"

@dataclass
class LedgerEntry:
    id: int
    company_id: int
    date: date
    account_code: str
    cost_center_id: Optional[int]
    debit: float
    credit: float
    history: str
    origin_type: str
    origin_id: Optional[int]

@dataclass
class TaxRule:
    id: int
    name: str
    tax_type: Literal["ICMS", "PIS", "COFINS", "ISS"]
    aliquot: float  # %
    cfop: str
    cst: str

@dataclass
class WorkflowRule:
    id: int
    name: str
    entity_type: str
    min_value: float
    approvals_required: int

@dataclass
class User:
    id: int
    name: str
    role: str
    is_admin: bool = False

@dataclass
class AuditLog:
    id: int
    timestamp: str
    user_name: str
    action: str
    entity_type: str
    entity_id: Optional[int]

# ============================================================
# FUNÇÕES DE CRUD SIMPLES
# ============================================================

def add_company(name: str, cnpj: str, regime: str):
    companies = get_list("companies")
    new_id = get_counter("company_id")
    companies.append(Company(id=new_id, name=name, cnpj=cnpj, regime=regime))
    inc_counter("company_id")
    log_event(f"Empresa criada: {name}", "Company", new_id)

def add_cost_center(code: str, name: str):
    ccs = get_list("cost_centers")
    new_id = get_counter("cost_center_id")
    ccs.append(CostCenter(id=new_id, code=code, name=name))
    inc_counter("cost_center_id")
    log_event(f"Centro de custo criado: {code} - {name}", "CostCenter", new_id)

def add_account(code: str, name: str, acc_type: str):
    accs = get_list("accounts")
    new_id = get_counter("account_id")
    accs.append(Account(id=new_id, code=code, name=name, type=acc_type))
    inc_counter("account_id")
    log_event(f"Conta criada: {code} - {name}", "Account", new_id)

def add_customer(name: str, doc: str, kind: str, company_id: int):
    custs = get_list("customers")
    new_id = get_counter("customer_id")
    custs.append(Customer(id=new_id, name=name, doc=doc, kind=kind, company_id=company_id))
    inc_counter("customer_id")
    log_event(f"Cliente criado: {name}", "Customer", new_id)

def add_product(name: str, sku: str, ncm: str, unit: str, company_id: int):
    prods = get_list("products")
    new_id = get_counter("product_id")
    prods.append(Product(id=new_id, name=name, sku=sku, ncm=ncm, unit=unit, company_id=company_id))
    inc_counter("product_id")
    log_event(f"Produto criado: {name}", "Product", new_id)

def add_financial_title(company_id: int, kind: str, party_name: str, doc_number: str,
                        issue_date: date, due_date: date, amount: float,
                        cost_center_id: Optional[int], account_id: Optional[int]):
    titles = get_list("titles")
    new_id = get_counter("title_id")
    titles.append(FinancialTitle(
        id=new_id,
        company_id=company_id,
        kind=kind,
        party_name=party_name,
        doc_number=doc_number,
        issue_date=issue_date,
        due_date=due_date,
        amount=amount,
        cost_center_id=cost_center_id,
        account_id=account_id
    ))
    inc_counter("title_id")
    log_event(f"Título financeiro criado: {kind} {doc_number} - {amount}", "FinancialTitle", new_id)
    return new_id

def add_ledger_entry(company_id: int, date_: date, account_code: str,
                     cost_center_id: Optional[int], debit: float, credit: float,
                     history: str, origin_type: str, origin_id: Optional[int]):
    entries = get_list("ledger")
    new_id = get_counter("ledger_id")
    entries.append(LedgerEntry(
        id=new_id,
        company_id=company_id,
        date=date_,
        account_code=account_code,
        cost_center_id=cost_center_id,
        debit=debit,
        credit=credit,
        history=history,
        origin_type=origin_type,
        origin_id=origin_id
    ))
    inc_counter("ledger_id")
    log_event(f"Lançamento contábil criado: {account_code} D={debit} C={credit}", "LedgerEntry", new_id)

def add_tax_rule(name: str, tax_type: str, aliquot: float, cfop: str, cst: str):
    rules = get_list("tax_rules")
    new_id = get_counter("tax_rule_id")
    rules.append(TaxRule(
        id=new_id, name=name, tax_type=tax_type,
        aliquot=aliquot, cfop=cfop, cst=cst
    ))
    inc_counter("tax_rule_id")
    log_event(f"Regra fiscal criada: {name}", "TaxRule", new_id)

def add_workflow_rule(name: str, entity_type: str, min_value: float, approvals_required: int):
    rules = get_list("workflow_rules")
    new_id = get_counter("workflow_rule_id")
    rules.append(WorkflowRule(
        id=new_id, name=name, entity_type=entity_type,
        min_value=min_value, approvals_required=approvals_required
    ))
    inc_counter("workflow_rule_id")
    log_event(f"Workflow criado: {name}", "WorkflowRule", new_id)

def add_user(name: str, role: str, is_admin: bool):
    users = get_list("users")
    new_id = get_counter("user_id")
    users.append(User(id=new_id, name=name, role=role, is_admin=is_admin))
    inc_counter("user_id")
    log_event(f"Usuário criado: {name}", "User", new_id)

def add_audit(user_name: str, action: str, entity_type: str, entity_id: Optional[int]):
    logs = get_list("audit_logs")
    new_id = get_counter("audit_id")
    logs.append(AuditLog(
        id=new_id,
        timestamp=datetime.now().isoformat(timespec="seconds"),
        user_name=user_name,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id
    ))
    inc_counter("audit_id")

# ============================================================
# PÁGINAS / NÚCLEOS
# ============================================================

def page_master_data():
    st.header("Núcleo 3 – Cadastros Mestre (MDM)")

    st.subheader("Empresas")
    with st.form("form_company"):
        c_name = st.text_input("Nome da empresa")
        c_cnpj = st.text_input("CNPJ")
        c_regime = st.selectbox("Regime tributário", ["Simples", "Presumido", "Real"])
        submitted = st.form_submit_button("Cadastrar empresa")
        if submitted and c_name:
            add_company(c_name, c_cnpj, c_regime)
            st.success("Empresa cadastrada com sucesso.")

    companies = [asdict(c) for c in get_list("companies")]
    if companies:
        st.dataframe(pd.DataFrame(companies))

    st.markdown("---")
    st.subheader("Centros de Custo")
    with st.form("form_cc"):
        cc_code = st.text_input("Código do centro de custo")
        cc_name = st.text_input("Nome do centro de custo")
        submitted_cc = st.form_submit_button("Cadastrar CC")
        if submitted_cc and cc_code:
            add_cost_center(cc_code, cc_name)
            st.success("Centro de custo cadastrado.")

    ccs = [asdict(c) for c in get_list("cost_centers")]
    if ccs:
        st.dataframe(pd.DataFrame(ccs))

    st.markdown("---")
    st.subheader("Plano de Contas (Core Contábil)")
    with st.form("form_account"):
        acc_code = st.text_input("Código da conta (ex: 1.1.1.01)")
        acc_name = st.text_input("Nome da conta")
        acc_type = st.selectbox("Tipo", ["Ativo", "Passivo", "Receita", "Despesa", "Patrimônio"])
        submitted_acc = st.form_submit_button("Cadastrar conta")
        if submitted_acc and acc_code:
            add_account(acc_code, acc_name, acc_type)
            st.success("Conta cadastrada.")

    accs = [asdict(a) for a in get_list("accounts")]
    if accs:
        st.dataframe(pd.DataFrame(accs))

    st.markdown("---")
    st.subheader("Clientes")
    companies_list = get_list("companies")
    if not companies_list:
        st.info("Cadastre ao menos uma empresa antes de cadastrar clientes.")
        return

    company_options = {f"{c.id} - {c.name}": c.id for c in companies_list}

    with st.form("form_customer"):
        cust_name = st.text_input("Nome do cliente")
        cust_doc = st.text_input("Doc (CPF/CNPJ)")
        cust_kind = st.selectbox("Tipo", ["PF", "PJ"])
        cust_company = st.selectbox("Empresa", list(company_options.keys()))
        submitted_cust = st.form_submit_button("Cadastrar cliente")
        if submitted_cust and cust_name:
            add_customer(cust_name, cust_doc, cust_kind, company_options[cust_company])
            st.success("Cliente cadastrado.")

    customers = [asdict(c) for c in get_list("customers")]
    if customers:
        st.dataframe(pd.DataFrame(customers))


def page_financial_core():
    st.header("Núcleo 1 – Financeiro-Contábil")

    companies = get_list("companies")
    accs = get_list("accounts")
    ccs = get_list("cost_centers")

    if not companies or not accs:
        st.warning("Cadastre pelo menos uma empresa e o plano de contas no módulo de Cadastros Mestre.")
        return

    companies_map = {f"{c.id} - {c.name}": c.id for c in companies}
    acc_map = {f"{a.code} - {a.name}": a for a in accs}
    cc_map = {"(Nenhum)": None}
    cc_map.update({f"{c.code} - {c.name}": c.id for c in ccs})

    st.subheader("Lançamento de Títulos (AP/AR)")
    with st.form("form_title"):
        company_label = st.selectbox("Empresa", list(companies_map.keys()))
        kind = st.selectbox("Tipo de título", ["AP", "AR"])
        party = st.text_input("Nome do cliente/fornecedor")
        doc_number = st.text_input("Número do documento")
        issue = st.date_input("Data de emissão", value=date.today())
        due = st.date_input("Data de vencimento", value=date.today())
        amount = st.number_input("Valor", min_value=0.0, step=100.0)
        cc_label = st.selectbox("Centro de custo", list(cc_map.keys()))
        acc_label = st.selectbox("Conta contábil padrão", list(acc_map.keys()))
        submitted = st.form_submit_button("Criar título")
        if submitted and amount > 0:
            title_id = add_financial_title(
                company_id=companies_map[company_label],
                kind=kind,
                party_name=party,
                doc_number=doc_number,
                issue_date=issue,
                due_date=due,
                amount=amount,
                cost_center_id=cc_map[cc_label],
                account_id=acc_map[acc_label].id
            )
            # lançamento contábil simples: débito/credito direto na conta informada
            acc = acc_map[acc_label]
            if kind == "AR":
                # D: Clientes / C: Receita (simplificado – aqui creditamos a própria conta escolhida)
                add_ledger_entry(
                    company_id=companies_map[company_label],
                    date_=issue,
                    account_code=acc.code,
                    cost_center_id=cc_map[cc_label],
                    debit=0.0,
                    credit=amount,
                    history=f"Reconhecimento de receita ref. título {doc_number}",
                    origin_type="FinancialTitle",
                    origin_id=title_id
                )
            else:
                # AP: D: Despesa / C: Fornecedores (simplificado – aqui debitamos a conta escolhida)
                add_ledger_entry(
                    company_id=companies_map[company_label],
                    date_=issue,
                    account_code=acc.code,
                    cost_center_id=cc_map[cc_label],
                    debit=amount,
                    credit=0.0,
                    history=f"Reconhecimento de despesa ref. título {doc_number}",
                    origin_type="FinancialTitle",
                    origin_id=title_id
                )
            st.success("Título criado e lançamento contábil de reconhecimento registrado.")

    st.markdown("---")
    st.subheader("Títulos cadastrados")
    titles = [asdict(t) for t in get_list("titles")]
    if titles:
        df_titles = pd.DataFrame(titles)
        st.dataframe(df_titles)

    st.markdown("---")
    st.subheader("Livro Razão (simplificado)")
    ledger = [asdict(l) for l in get_list("ledger")]
    if ledger:
        df_ledger = pd.DataFrame(ledger)
        st.dataframe(df_ledger)

        st.markdown("### Balancete por conta")
        bal = (
            df_ledger
            .groupby("account_code")[["debit", "credit"]]
            .sum()
            .reset_index()
        )
        bal["saldo"] = bal["debit"] - bal["credit"]
        st.dataframe(bal)


def page_fiscal_core():
    st.header("Núcleo 2 – Fiscal / Tributário")

    st.subheader("Regras fiscais")
    with st.form("form_tax_rule"):
        name = st.text_input("Nome da regra (ex: ICMS interno SP)")
        tax_type = st.selectbox("Tipo de tributo", ["ICMS", "PIS", "COFINS", "ISS"])
        aliquot = st.number_input("Alíquota (%)", min_value=0.0, max_value=100.0, step=0.5)
        cfop = st.text_input("CFOP")
        cst = st.text_input("CST/CSOSN")
        submitted = st.form_submit_button("Cadastrar regra")
        if submitted and name:
            add_tax_rule(name, tax_type, aliquot, cfop, cst)
            st.success("Regra fiscal cadastrada.")

    rules = [asdict(r) for r in get_list("tax_rules")]
    if rules:
        st.dataframe(pd.DataFrame(rules))

    st.markdown("---")
    st.subheader("Simulador tributário simples")
    rules_objs = get_list("tax_rules")
    if not rules_objs:
        st.info("Cadastre ao menos uma regra para simular.")
        return

    rule_map = {f"{r.id} - {r.name} ({r.tax_type} {r.aliquot}%)": r for r in rules_objs}

    base_value = st.number_input("Base de cálculo (R$)", min_value=0.0, step=100.0)
    rule_label = st.selectbox("Regra", list(rule_map.keys()))
    if base_value > 0:
        rule = rule_map[rule_label]
        tax_amount = base_value * (rule.aliquot / 100.0)
        st.metric("Imposto calculado", f"R$ {tax_amount:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))


def page_workflow_core():
    st.header("Núcleo 4 – Processos / Workflow")

    st.subheader("Definição de Workflows")
    with st.form("form_workflow"):
        name = st.text_input("Nome do workflow (ex: Aprovação de pedido de compra)")
        entity_type = st.text_input("Tipo de entidade (ex: PurchaseOrder)")
        min_value = st.number_input("Valor mínimo para disparar fluxo", min_value=0.0, step=100.0)
        approvals_required = st.number_input("Qtd. de aprovações necessárias", min_value=1, max_value=10, step=1)
        submitted = st.form_submit_button("Cadastrar workflow")
        if submitted and name:
            add_workflow_rule(name, entity_type, min_value, int(approvals_required))
            st.success("Workflow cadastrado.")

    rules = [asdict(r) for r in get_list("workflow_rules")]
    if rules:
        st.dataframe(pd.DataFrame(rules))

    st.markdown("---")
    st.subheader("Simulador de roteamento (conceitual)")
    rules_objs = get_list("workflow_rules")
    if rules_objs:
        entity = st.text_input("Entidade (ex: PurchaseOrder)")
        value = st.number_input("Valor da operação", min_value=0.0, step=100.0)
        if value > 0 and entity:
            applicable = [
                r for r in rules_objs
                if r.entity_type == entity and value >= r.min_value
            ]
            if applicable:
                st.write("Workflows aplicáveis:")
                st.dataframe(pd.DataFrame([asdict(r) for r in applicable]))
            else:
                st.info("Nenhum workflow aplicável para este cenário ainda.")


def page_security_core():
    st.header("Núcleo 5 – Segurança & Auditoria")

    st.subheader("Usuários")
    with st.form("form_user"):
        name = st.text_input("Nome do usuário")
        role = st.text_input("Papel (ex: CFO, Controller, Analista)")
        is_admin = st.checkbox("Administrador?")
        submitted = st.form_submit_button("Cadastrar usuário")
        if submitted and name:
            add_user(name, role, is_admin)
            st.success("Usuário cadastrado.")

    users = [asdict(u) for u in get_list("users")]
    if users:
        st.dataframe(pd.DataFrame(users))

    st.markdown("---")
    st.subheader("Logs de auditoria (conceito)")
    st.info("Neste MVP, vamos registrar manualmente um exemplo de ação de auditoria.")
    with st.form("form_audit_example"):
        user_name = st.text_input("Usuário (texto livre)")
        action = st.text_input("Ação (ex: Alterou limite de crédito do cliente X)")
        entity_type = st.text_input("Entidade impactada (ex: Customer)")
        entity_id = st.number_input("ID da entidade (opcional)", min_value=0, step=1)
        submitted = st.form_submit_button("Registrar log")
        if submitted and user_name and action:
            add_audit(
                user_name=user_name,
                action=action,
                entity_type=entity_type or "GENERIC",
                entity_id=entity_id if entity_id > 0 else None
            )
            st.success("Log de auditoria registrado.")

    audits = [asdict(a) for a in get_list("audit_logs")]
    if audits:
        st.dataframe(pd.DataFrame(audits))


def page_integration_core():
    st.header("Núcleo 6 – Integração & Eventos")

    st.subheader("Eventos gerados pelo core")
    events = get_list("events")
    if events:
        st.dataframe(pd.DataFrame(events))
    else:
        st.info("Nenhum evento registrado ainda. Crie empresas, títulos, etc. nos outros módulos.")

    st.markdown("---")
    st.subheader("Webhooks / APIs (conceitual)")
    st.info(
        "Neste MVP não estamos expondo APIs reais, mas o modelo de eventos "
        "já está pronto para ser usado como base de webhooks e integrações externas."
    )


def page_analytics_core():
    st.header("Núcleo 7 – Analytics & Painel Estratégico")

    titles = [asdict(t) for t in get_list("titles")]
    ledger = [asdict(l) for l in get_list("ledger")]

    col1, col2, col3 = st.columns(3)
    if titles:
        df_t = pd.DataFrame(titles)
        total_ar = df_t[df_t["kind"] == "AR"]["amount"].sum()
        total_ap = df_t[df_t["kind"] == "AP"]["amount"].sum()
        col1.metric("Carteira a receber (AR)", f"R$ {total_ar:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
        col2.metric("Carteira a pagar (AP)", f"R$ {total_ap:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
        col3.metric("Exposição líquida (AR - AP)", f"R$ {(total_ar - total_ap):,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
    else:
        col1.metric("Carteira a receber (AR)", "R$ 0,00")
        col2.metric("Carteira a pagar (AP)", "R$ 0,00")
        col3.metric("Exposição líquida (AR - AP)", "R$ 0,00")

    st.markdown("---")
    st.subheader("Análise por conta contábil")
    if ledger:
        df_l = pd.DataFrame(ledger)
        bal = (
            df_l
            .groupby("account_code")[["debit", "credit"]]
            .sum()
            .reset_index()
        )
        bal["saldo"] = bal["debit"] - bal["credit"]
        st.dataframe(bal)
        st.bar_chart(bal.set_index("account_code")["saldo"])
    else:
        st.info("Sem lançamentos contábeis ainda.")


# ============================================================
# MAIN / LAYOUT
# ============================================================

def init_counters():
    keys = [
        "company_id", "cost_center_id", "account_id", "customer_id",
        "product_id", "title_id", "ledger_id", "tax_rule_id",
        "workflow_rule_id", "user_id", "audit_id", "event_id"
    ]
    for k in keys:
        get_counter(k)  # apenas garante inicialização


def main():
    st.set_page_config(
        page_title="ERP Core – MVP",
        layout="wide"
    )

    init_counters()

    st.sidebar.title("ERP Core – Núcleos")
    page = st.sidebar.radio(
        "Selecione o núcleo",
        [
            "Cadastros Mestre",
            "Financeiro-Contábil",
            "Fiscal / Tributário",
            "Processos & Workflow",
            "Segurança & Auditoria",
            "Integração & Eventos",
            "Analytics & Painel"
        ]
    )

    if page == "Cadastros Mestre":
        page_master_data()
    elif page == "Financeiro-Contábil":
        page_financial_core()
    elif page == "Fiscal / Tributário":
        page_fiscal_core()
    elif page == "Processos & Workflow":
        page_workflow_core()
    elif page == "Segurança & Auditoria":
        page_security_core()
    elif page == "Integração & Eventos":
        page_integration_core()
    elif page == "Analytics & Painel":
        page_analytics_core()


if __name__ == "__main__":
    main()
