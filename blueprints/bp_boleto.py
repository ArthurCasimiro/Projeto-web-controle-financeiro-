from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import current_user
from utils.decorators import login_required
from modelos.boleto import Boleto
import DAO.boleto_dao as boleto_dao
import DAO.categoria_dao as categoria_dao
from datetime import date, datetime

bp_boleto = Blueprint('boleto', __name__, url_prefix='/boletos')


@bp_boleto.route('/')
@login_required
def listar():
    try:
        uid  = current_user.id
        hoje = date.today()
        boletos   = Boleto.query.filter_by(usuario_id=uid).order_by(Boleto.vencimento).all()
        pendentes = [b for b in boletos if b.status == 'pendente']
        pagos     = [b for b in boletos if b.status == 'pago']
        vencidos  = [b for b in pendentes if b.vencimento < hoje]
        qtd_urgentes   = sum(1 for b in pendentes if 0 <= (b.vencimento - hoje).days <= 7)
        total_urgentes = sum(b.valor for b in pendentes if 0 <= (b.vencimento - hoje).days <= 7)
        total_aberto   = sum(b.valor for b in pendentes)
        total_pago     = sum(b.valor for b in pagos)
        return render_template('boletos.html',
            boletos=boletos, pendentes=pendentes, pagos=pagos, vencidos=vencidos,
            today=hoje, qtd_pendentes=len(pendentes), qtd_urgentes=qtd_urgentes,
            total_urgentes=total_urgentes, qtd_vencidos=len(vencidos),
            qtd_pagos=len(pagos), total_aberto=total_aberto, total_pago=total_pago)
    except Exception as e:
        print(f'[ERRO] boleto.listar: {e}')
        flash('Erro ao carregar boletos.', 'erro')
        return redirect(url_for('dashboard.painel'))


@bp_boleto.route('/cadastrar', methods=['GET', 'POST'])
@login_required
def cadastrar():
    try:
        categorias = categoria_dao.listar_categorias(current_user.id)
        if request.method == 'GET':
            return render_template('cadastrar_boleto.html',
                                   boleto=None, categorias=categorias,
                                   today=date.today().isoformat())

        nome         = request.form.get('nome', '').strip()
        valor        = request.form.get('valor')
        vencimento   = request.form.get('vencimento')
        descricao    = request.form.get('descricao', '').strip() or None
        codigo_barra = request.form.get('codigo_barra', '').strip() or None
        notas        = request.form.get('notas', '').strip() or None
        categoria_id = request.form.get('categoria_id') or None

        if not nome or not valor or not vencimento:
            flash('Preencha os campos obrigatórios.', 'erro')
            return render_template('cadastrar_boleto.html',
                                   boleto=None, categorias=categorias,
                                   today=date.today().isoformat())

        boleto_dao.criar_boleto(
            nome=nome, valor=float(valor),
            vencimento=datetime.strptime(vencimento, '%Y-%m-%d').date(),
            usuario_id=current_user.id,
            categoria_id=int(categoria_id) if categoria_id else None,
            descricao=descricao, codigo_barra=codigo_barra, notas=notas,
        )
        flash('Boleto cadastrado!', 'ok')
        return redirect(url_for('boleto.listar'))
    except Exception as e:
        print(f'[ERRO] boleto.cadastrar: {e}')
        flash('Erro ao cadastrar boleto.', 'erro')
        return redirect(url_for('boleto.listar'))


@bp_boleto.route('/editar/<int:boleto_id>', methods=['GET', 'POST'])
@login_required
def editar(boleto_id):
    try:
        b = boleto_dao.buscar_por_id(boleto_id)
        if not b or b.usuario_id != current_user.id:
            flash('Boleto não encontrado.', 'erro')
            return redirect(url_for('boleto.listar'))

        categorias = categoria_dao.listar_categorias(current_user.id)
        if request.method == 'GET':
            return render_template('cadastrar_boleto.html',
                                   boleto=b, categorias=categorias,
                                   today=date.today().isoformat())

        nome         = request.form.get('nome', '').strip()
        valor        = request.form.get('valor')
        vencimento   = request.form.get('vencimento')
        descricao    = request.form.get('descricao', '').strip() or None
        codigo_barra = request.form.get('codigo_barra', '').strip() or None
        notas        = request.form.get('notas', '').strip() or None
        categoria_id = request.form.get('categoria_id') or None

        if not nome or not valor or not vencimento:
            flash('Preencha os campos obrigatórios.', 'erro')
            return render_template('cadastrar_boleto.html',
                                   boleto=b, categorias=categorias,
                                   today=date.today().isoformat())

        boleto_dao.atualizar_boleto(
            boleto_id=boleto_id, nome=nome, valor=float(valor),
            vencimento=datetime.strptime(vencimento, '%Y-%m-%d').date(),
            categoria_id=int(categoria_id) if categoria_id else None,
            descricao=descricao, codigo_barra=codigo_barra, notas=notas,
        )
        flash('Boleto atualizado!', 'ok')
        return redirect(url_for('boleto.listar'))
    except Exception as e:
        print(f'[ERRO] boleto.editar: {e}')
        flash('Erro ao editar boleto.', 'erro')
        return redirect(url_for('boleto.listar'))


@bp_boleto.route('/pagar/<int:boleto_id>', methods=['POST'])
@login_required
def pagar(boleto_id):
    try:
        b = boleto_dao.buscar_por_id(boleto_id)
        if not b or b.usuario_id != current_user.id:
            flash('Boleto não encontrado.', 'erro')
            return redirect(url_for('boleto.listar'))
        boleto_dao.marcar_como_pago(boleto_id)
        flash('Boleto marcado como pago!', 'ok')
    except Exception as e:
        print(f'[ERRO] boleto.pagar: {e}')
        flash('Erro ao marcar boleto como pago.', 'erro')
    return redirect(url_for('boleto.listar'))


@bp_boleto.route('/reabrir/<int:boleto_id>', methods=['POST'])
@login_required
def reabrir(boleto_id):
    try:
        b = boleto_dao.buscar_por_id(boleto_id)
        if not b or b.usuario_id != current_user.id:
            flash('Boleto não encontrado.', 'erro')
            return redirect(url_for('boleto.listar'))
        boleto_dao.reabrir(boleto_id)
        flash('Boleto reaberto.', 'ok')
    except Exception as e:
        print(f'[ERRO] boleto.reabrir: {e}')
        flash('Erro ao reabrir boleto.', 'erro')
    return redirect(url_for('boleto.listar'))


@bp_boleto.route('/excluir/<int:boleto_id>', methods=['POST'])
@login_required
def excluir(boleto_id):
    try:
        b = boleto_dao.buscar_por_id(boleto_id)
        if not b or b.usuario_id != current_user.id:
            flash('Boleto não encontrado.', 'erro')
            return redirect(url_for('boleto.listar'))
        boleto_dao.deletar_boleto(boleto_id)
        flash('Boleto excluído.', 'ok')
    except Exception as e:
        print(f'[ERRO] boleto.excluir: {e}')
        flash('Erro ao excluir boleto.', 'erro')
    return redirect(url_for('boleto.listar'))
