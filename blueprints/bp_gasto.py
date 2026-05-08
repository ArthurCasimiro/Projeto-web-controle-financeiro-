from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import current_user
from utils.decorators import login_required
import repository.gasto_repository as gasto_repository
import repository.categoria_repository as categoria_repository
from datetime import date, datetime

bp_gasto = Blueprint('gasto', __name__, url_prefix='/gastos')


@bp_gasto.route('/')
@login_required
def listar():
    try:
        gastos = gasto_repository.listar_gastos(current_user.id)
        total_mes = gasto_repository.total_mes_atual(current_user.id)
        return render_template('gastos.html', gastos=gastos, total_mes=total_mes)
    except Exception as e:
        print(f'[ERRO] gasto.listar: {e}')
        flash('Erro ao carregar gastos.', 'erro')
        return redirect(url_for('dashboard.painel'))


@bp_gasto.route('/cadastrar', methods=['GET', 'POST'])
@login_required
def cadastrar():
    try:
        categorias = categoria_repository.listar_categorias(current_user.id)
        if request.method == 'GET':
            return render_template('cadastrar_gasto.html',
                                   gasto=None, categorias=categorias,
                                   today=date.today().isoformat())

        valor        = request.form.get('valor')
        data_str     = request.form.get('data')
        descricao    = request.form.get('descricao', '').strip() or None
        categoria_id = request.form.get('categoria_id') or None

        if not valor or not data_str:
            flash('Preencha os campos obrigatórios.', 'erro')
            return render_template('cadastrar_gasto.html',
                                   gasto=None, categorias=categorias,
                                   today=date.today().isoformat())

        recorrente = request.form.get('recorrente') == 'on'

        gasto_repository.criar_gasto(
            descricao=descricao,
            valor=float(valor),
            data=datetime.strptime(data_str, '%Y-%m-%d').date(),
            recorrente=recorrente,
            categoria_id=int(categoria_id) if categoria_id else None,
            usuario_id=current_user.id,
        )
        flash('Gasto cadastrado!', 'ok')
        return redirect(url_for('gasto.listar'))
    except Exception as e:
        print(f'[ERRO] gasto.cadastrar: {e}')
        flash('Erro ao cadastrar gasto.', 'erro')
        return redirect(url_for('gasto.listar'))


@bp_gasto.route('/editar/<int:gasto_id>', methods=['GET', 'POST'])
@login_required
def editar(gasto_id):
    try:
        g = gasto_repository.buscar_por_id(gasto_id)
        if not g or g.usuario_id != current_user.id:
            flash('Gasto não encontrado.', 'erro')
            return redirect(url_for('gasto.listar'))

        categorias = categoria_repository.listar_categorias(current_user.id)
        if request.method == 'GET':
            return render_template('cadastrar_gasto.html',
                                   gasto=g, categorias=categorias,
                                   today=date.today().isoformat())

        valor        = request.form.get('valor')
        data_str     = request.form.get('data')
        categoria_id = request.form.get('categoria_id') or None

        if not valor or not data_str:
            flash('Preencha os campos obrigatórios.', 'erro')
            return render_template('cadastrar_gasto.html',
                                   gasto=g, categorias=categorias,
                                   today=date.today().isoformat())

        gasto_repository.atualizar_gasto(
            gasto_id=gasto_id,
            valor=float(valor),
            data=datetime.strptime(data_str, '%Y-%m-%d').date(),
            categoria_id=int(categoria_id) if categoria_id else None,
        )
        flash('Gasto atualizado!', 'ok')
        return redirect(url_for('gasto.listar'))
    except Exception as e:
        print(f'[ERRO] gasto.editar: {e}')
        flash('Erro ao editar gasto.', 'erro')
        return redirect(url_for('gasto.listar'))


@bp_gasto.route('/excluir/<int:gasto_id>', methods=['POST'])
@login_required
def excluir(gasto_id):
    try:
        g = gasto_repository.buscar_por_id(gasto_id)
        if not g or g.usuario_id != current_user.id:
            flash('Gasto não encontrado.', 'erro')
            return redirect(url_for('gasto.listar'))
        gasto_repository.deletar_gasto(gasto_id)
        flash('Gasto excluído.', 'ok')
    except Exception as e:
        print(f'[ERRO] gasto.excluir: {e}')
        flash('Erro ao excluir gasto.', 'erro')
    return redirect(url_for('gasto.listar'))
