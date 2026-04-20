from flask import Blueprint, render_template, flash, redirect, url_for
from flask_login import current_user
from utils.decorators import login_required
import DAO.assinatura_dao as assinatura_dao
import DAO.boleto_dao as boleto_dao
from blueprints.bp_dashboard import proximo_vencimento
from datetime import date

bp_alerta = Blueprint('alerta', __name__, url_prefix='/alertas')


@bp_alerta.route('/')
@login_required
def listar():
    try:
        uid   = current_user.id
        today = date.today()

        assinaturas = assinatura_dao.listar_assinaturas(uid)
        alertas = []
        for s in assinaturas:
            if s.status != 'ativa':
                continue
            vencimento = proximo_vencimento(s.dia_vencimento, today)
            dias = (vencimento - today).days
            if dias <= 7:
                alertas.append({'tipo': 'assinatura', 'obj': s, 'dias': dias})

        for b in boleto_dao.listar_urgentes(uid):
            dias = (b.vencimento - today).days
            alertas.append({'tipo': 'boleto', 'obj': b, 'dias': dias})

        alertas.sort(key=lambda a: a['dias'])
        boletos_vencidos = boleto_dao.listar_vencidos(uid)
        todos_pendentes  = boleto_dao.listar_pendentes(uid)

        return render_template('alertas.html',
                               alertas=alertas,
                               boletos_vencidos=boletos_vencidos,
                               todos_pendentes=todos_pendentes,
                               today=today)
    except Exception as e:
        print(f'[ERRO] alerta.listar: {e}')
        flash('Erro ao carregar alertas.', 'erro')
        return redirect(url_for('dashboard.painel'))
