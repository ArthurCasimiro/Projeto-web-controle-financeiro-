from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import current_user
from DAO.assinatura_dao import (
    listar_assinaturas, criar_assinatura, buscar_por_id,
    atualizar_assinatura, alterar_status_assinatura, deletar_assinatura
)
from DAO.categoria_dao import listar_categorias
from utils.decorators import login_required
from datetime import date
from extensao import db

bp_assinatura = Blueprint('assinatura', __name__, url_prefix='/assinaturas')


@bp_assinatura.route('/')
@login_required
def listar():
    try:
        assinaturas = listar_assinaturas(current_user.id)
        total_mensal = sum(s.valor_mensal() for s in assinaturas if s.status == 'ativa')
        return render_template('assinaturas.html',
                               assinaturas=assinaturas, total_mensal=total_mensal)
    except Exception as e:
        print(f'[ERRO] assinatura.listar: {e}')
        flash('Erro ao carregar assinaturas.', 'erro')
        return redirect(url_for('dashboard.painel'))


@bp_assinatura.route('/cadastrar', methods=['GET', 'POST'])
@login_required
def cadastrar():
    if request.method == 'GET':
        categorias = listar_categorias(current_user.id)
        return render_template('cadastrar_assinatura.html',
                               assinatura=None, categorias=categorias)
    try:
        nome           = request.form.get('nome', '').strip()
        valor          = request.form.get('valor')
        ciclo          = request.form.get('ciclo', 'mensal')
        dia_vencimento = request.form.get('dia_vencimento')
        categoria_id   = request.form.get('categoria_id') or None
        desde_str      = request.form.get('desde')
        notas          = request.form.get('notas', '').strip() or None

        if not nome or not valor or not dia_vencimento:
            flash('Preencha os campos obrigatórios.', 'erro')
            return redirect(url_for('assinatura.cadastrar'))

        assinatura = criar_assinatura(
            nome=nome, valor=float(valor), ciclo=ciclo,
            dia_vencimento=int(dia_vencimento), usuario_id=current_user.id,
            categoria_id=int(categoria_id) if categoria_id else None,
        )
        assinatura.desde = date.fromisoformat(desde_str) if desde_str else None
        assinatura.notas = notas
        db.session.commit()
        flash('Assinatura cadastrada com sucesso.', 'ok')
        return redirect(url_for('assinatura.listar'))
    except Exception as e:
        db.session.rollback()
        print(f'[ERRO] assinatura.cadastrar: {e}')
        flash('Erro ao cadastrar assinatura.', 'erro')
        return redirect(url_for('assinatura.cadastrar'))


@bp_assinatura.route('/editar/<int:assinatura_id>', methods=['GET', 'POST'])
@login_required
def editar(assinatura_id):
    try:
        s = buscar_por_id(assinatura_id)
        if not s or s.usuario_id != current_user.id:
            flash('Assinatura não encontrada.', 'erro')
            return redirect(url_for('assinatura.listar'))

        if request.method == 'GET':
            categorias = listar_categorias(current_user.id)
            return render_template('cadastrar_assinatura.html',
                                   assinatura=s, categorias=categorias)

        nome           = request.form.get('nome', '').strip()
        valor          = request.form.get('valor')
        ciclo          = request.form.get('ciclo', 'mensal')
        dia_vencimento = request.form.get('dia_vencimento')
        categoria_id   = request.form.get('categoria_id') or None
        desde_str      = request.form.get('desde')
        notas          = request.form.get('notas', '').strip() or None

        if not nome or not valor or not dia_vencimento:
            flash('Preencha os campos obrigatórios.', 'erro')
            return redirect(url_for('assinatura.editar', assinatura_id=assinatura_id))

        atualizar_assinatura(
            assinatura_id=assinatura_id, nome=nome, valor=float(valor),
            ciclo=ciclo, dia_vencimento=int(dia_vencimento),
            categoria_id=int(categoria_id) if categoria_id else None,
        )
        s.desde = date.fromisoformat(desde_str) if desde_str else None
        s.notas = notas
        db.session.commit()
        flash('Assinatura atualizada.', 'ok')
        return redirect(url_for('assinatura.listar'))
    except Exception as e:
        db.session.rollback()
        print(f'[ERRO] assinatura.editar: {e}')
        flash('Erro ao editar assinatura.', 'erro')
        return redirect(url_for('assinatura.listar'))


@bp_assinatura.route('/status/<int:assinatura_id>', methods=['POST'])
@login_required
def alternar_status(assinatura_id):
    try:
        s = buscar_por_id(assinatura_id)
        if not s or s.usuario_id != current_user.id:
            flash('Assinatura não encontrada.', 'erro')
            return redirect(url_for('assinatura.listar'))
        novo_status = 'pausada' if s.status == 'ativa' else 'ativa'
        alterar_status_assinatura(assinatura_id, novo_status)
    except Exception as e:
        print(f'[ERRO] assinatura.alternar_status: {e}')
        flash('Erro ao alterar status.', 'erro')
    return redirect(url_for('assinatura.listar'))


@bp_assinatura.route('/excluir/<int:assinatura_id>', methods=['POST'])
@login_required
def excluir(assinatura_id):
    try:
        s = buscar_por_id(assinatura_id)
        if not s or s.usuario_id != current_user.id:
            flash('Assinatura não encontrada.', 'erro')
            return redirect(url_for('assinatura.listar'))
        deletar_assinatura(assinatura_id)
        flash('Assinatura excluída.', 'ok')
    except Exception as e:
        print(f'[ERRO] assinatura.excluir: {e}')
        flash('Erro ao excluir assinatura.', 'erro')
    return redirect(url_for('assinatura.listar'))
