from flask import Blueprint, render_template, redirect, url_for, session
from dao.assinatura_dao import AssinaturaDao
from dao.boleto_dao import BoletoDao
from datetime import date

assinatura_dao = AssinaturaDao()
boleto_dao = BoletoDao()
bp_alerta = Blueprint('alerta', __name__, url_prefix='/alertas')


def login_required():
    return 'usuario_id' in session


@bp_alerta.route('/')
def listar():
    if not login_required():
        return redirect(url_for('home_page'))
    uid = session['usuario_id']
    today = date.today()
    today_day = today.day

    # Assinaturas vencendo em 7 dias
    assinaturas = assinatura_dao.listar_por_usuario(uid)
    alertas = []
    for s in assinaturas:
        if s.status != 'ativa':
            continue
        dias = s.dia_vencimento - today_day
        if dias < 0:
            dias = 30 + dias
        if dias <= 7:
            alertas.append({'tipo': 'assinatura', 'obj': s, 'dias': dias})

    # Boletos vencendo em 7 dias
    for b in boleto_dao.listar_urgentes(uid):
        dias = (b.vencimento - today).days
        alertas.append({'tipo': 'boleto', 'obj': b, 'dias': dias})

    alertas.sort(key=lambda a: a['dias'])

    boletos_vencidos = boleto_dao.listar_vencidos(uid)
    todos_pendentes = boleto_dao.listar_pendentes(uid)

    return render_template('alertas.html',
        alertas=alertas,
        boletos_vencidos=boletos_vencidos,
        todos_pendentes=todos_pendentes,
        today=today
    )
