from flask import Blueprint, render_template, flash, redirect, url_for
from flask_login import current_user
from DAO.assinatura_dao import listar_assinaturas
from DAO.gasto_dao import listar_gastos, total_mes_atual
from DAO.meta_dao import listar_metas
from DAO.categoria_dao import listar_categorias
from DAO.boleto_dao import listar_boletos
from DAO.fundo_dao import listar_fundos, total_geral
from utils.decorators import login_required
from datetime import date
import calendar

bp_dashboard = Blueprint('dashboard', __name__, url_prefix='/dashboard')


def proximo_vencimento(dia: int, hoje: date) -> date:
    ultimo_dia_mes_atual = calendar.monthrange(hoje.year, hoje.month)[1]
    dia_efetivo = min(dia, ultimo_dia_mes_atual)
    if dia_efetivo >= hoje.day:
        return hoje.replace(day=dia_efetivo)
    if hoje.month == 12:
        ano, mes = hoje.year + 1, 1
    else:
        ano, mes = hoje.year, hoje.month + 1
    ultimo_dia_prox_mes = calendar.monthrange(ano, mes)[1]
    dia_efetivo = min(dia, ultimo_dia_prox_mes)
    return date(ano, mes, dia_efetivo)


@bp_dashboard.route('/')
@login_required
def painel():
    try:
        uid  = current_user.id
        hoje = date.today()

        assinaturas = listar_assinaturas(uid)
        gastos      = listar_gastos(uid)
        metas       = listar_metas(uid)
        categorias  = listar_categorias(uid)
        boletos     = listar_boletos(uid)
        fundos      = listar_fundos(uid)

        total_assinaturas      = sum(a.valor_mensal() for a in assinaturas if a.status == 'ativa')
        total_gastos_mes       = total_mes_atual(uid)
        total_mensal           = total_assinaturas + total_gastos_mes
        total_entradas         = total_geral(uid)
        total_boletos_val      = sum(b.valor for b in boletos if b.status == 'pendente')
        qtd_fundos             = len(fundos)
        qtd_boletos_pendentes  = len([b for b in boletos if b.status == 'pendente'])
        qtd_assinaturas_ativas = len([a for a in assinaturas if a.status == 'ativa'])
        saldo                  = total_entradas - total_mensal

        alertas = []
        for b in boletos:
            if b.status == 'pendente':
                dias = (b.vencimento - hoje).days
                if dias <= 7:
                    alertas.append({'tipo': 'boleto', 'obj': b, 'dias': dias, 'vencimento': b.vencimento})
        for a in assinaturas:
            if a.status == 'ativa' and a.dia_vencimento:
                vencimento = proximo_vencimento(a.dia_vencimento, hoje)
                dias = (vencimento - hoje).days
                if dias <= 7:
                    alertas.append({'tipo': 'assinatura', 'obj': a, 'dias': dias, 'vencimento': vencimento})
        alertas.sort(key=lambda x: x['dias'])

        boletos_urgentes = sorted(
            [b for b in boletos if b.status == 'pendente' and (b.vencimento - hoje).days <= 7],
            key=lambda b: b.vencimento
        )

        fundos_recentes = fundos[:5]
        gastos_recentes = sorted(gastos, key=lambda g: g.data, reverse=True)[:5]

        gasto_categoria = {}
        for a in assinaturas:
            if a.status == 'ativa' and a.categoria:
                chave = a.categoria.nome
                gasto_categoria[chave] = gasto_categoria.get(chave, 0) + a.valor_mensal()
        for g in gastos:
            if g.categoria:
                chave = g.categoria.nome
                gasto_categoria[chave] = gasto_categoria.get(chave, 0) + g.valor

        chart_labels = list(gasto_categoria.keys())
        chart_values = list(gasto_categoria.values())
        cores_padrao = ['#4f8ef7','#3ecf8e','#f59e0b','#f7645a','#a78bfa',
                        '#20d9d2','#fb923c','#e879f9','#34d399','#f472b6']
        chart_colors = [c.cor if c.cor else cores_padrao[i % len(cores_padrao)]
                        for i, c in enumerate(categorias)][:len(chart_labels)]
        if not chart_colors:
            chart_colors = cores_padrao[:len(chart_labels)]

        return render_template('dashboard.html',
            assinaturas=assinaturas,
            gastos_recentes=gastos_recentes,
            metas=metas,
            alertas=alertas,
            boletos_urgentes=boletos_urgentes,
            fundos_recentes=fundos_recentes,
            today=hoje,
            total_mensal=total_mensal,
            total_assinaturas=total_assinaturas,
            total_gastos_mes=total_gastos_mes,
            total_entradas=total_entradas,
            total_boletos=total_boletos_val,
            qtd_fundos=qtd_fundos,
            qtd_boletos_pendentes=qtd_boletos_pendentes,
            qtd_boletos_urgentes=len(boletos_urgentes),
            qtd_assinaturas_ativas=qtd_assinaturas_ativas,
            saldo=saldo,
            gasto_categoria=gasto_categoria,
            chart_labels=chart_labels,
            chart_values=chart_values,
            chart_colors=chart_colors,
            qtd_alertas=len(alertas),
        )
    except Exception as e:
        import traceback
        traceback.print_exc()
        flash('Erro ao carregar dashboard.', 'erro')
        return redirect(url_for('home_page'))