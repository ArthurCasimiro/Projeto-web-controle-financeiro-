from flask import Blueprint, render_template, flash, redirect, url_for
from utils.decorators import login_required, admin_required
from extensao import db
from modelos.usuario import Usuario
from modelos.boleto import Boleto
from modelos.assinatura import Assinatura
from modelos.gasto import Gasto
from modelos.fundo import Fundo
from modelos.meta import Meta

bp_admin = Blueprint('admin', __name__, url_prefix='/admin')


@bp_admin.route('/')
@login_required
@admin_required
def painel():
    try:
        total_usuarios    = Usuario.query.count()
        total_boletos     = Boleto.query.count()
        total_assinaturas = Assinatura.query.count()
        total_gastos      = Gasto.query.count()
        total_metas       = Meta.query.count()

        volume_boletos     = db.session.query(db.func.sum(Boleto.valor)).scalar()     or 0
        volume_assinaturas = db.session.query(db.func.sum(Assinatura.valor)).scalar() or 0
        volume_gastos      = db.session.query(db.func.sum(Gasto.valor)).scalar()      or 0
        volume_fundos      = db.session.query(db.func.sum(Fundo.valor)).scalar()      or 0
        volume_total       = volume_boletos + volume_assinaturas + volume_gastos + volume_fundos
        usuarios_ativos    = db.session.query(Gasto.usuario_id).distinct().count()

        return render_template('admin/painel.html',
                               total_usuarios=total_usuarios,
                               total_boletos=total_boletos,
                               total_assinaturas=total_assinaturas,
                               total_gastos=total_gastos,
                               total_metas=total_metas,
                               volume_boletos=volume_boletos,
                               volume_assinaturas=volume_assinaturas,
                               volume_gastos=volume_gastos,
                               volume_fundos=volume_fundos,
                               volume_total=volume_total,
                               usuarios_ativos=usuarios_ativos)
    except Exception as e:
        print(f'[ERRO] admin.painel: {e}')
        flash('Erro ao carregar painel admin.', 'erro')
        return redirect(url_for('dashboard.painel'))
