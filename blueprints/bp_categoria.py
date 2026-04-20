from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import current_user
from utils.decorators import login_required
import DAO.categoria_dao as categoria_dao

bp_categoria = Blueprint('categoria', __name__, url_prefix='/categorias')


@bp_categoria.route('/')
@login_required
def listar():
    try:
        categorias = categoria_dao.listar_categorias(current_user.id)
        return render_template('categorias.html', categorias=categorias)
    except Exception as e:
        print(f'[ERRO] categoria.listar: {e}')
        flash('Erro ao carregar categorias.', 'erro')
        return redirect(url_for('dashboard.painel'))


@bp_categoria.route('/cadastrar', methods=['GET', 'POST'])
@login_required
def cadastrar():
    if request.method == 'GET':
        return render_template('cadastrar_categoria.html', categoria=None)
    try:
        nome  = request.form.get('nome', '').strip()
        icone = request.form.get('icone', '📌').strip()
        cor   = request.form.get('cor', '#2dd4bf').strip()

        if not nome:
            flash('Nome é obrigatório.', 'erro')
            return render_template('cadastrar_categoria.html', categoria=None)

        categoria_dao.criar_categoria(nome, current_user.id, icone, cor)
        flash('Categoria criada!', 'ok')
        return redirect(url_for('categoria.listar'))
    except Exception as e:
        print(f'[ERRO] categoria.cadastrar: {e}')
        flash('Erro ao criar categoria.', 'erro')
        return render_template('cadastrar_categoria.html', categoria=None)


@bp_categoria.route('/editar/<int:categoria_id>', methods=['GET', 'POST'])
@login_required
def editar(categoria_id):
    try:
        categoria = categoria_dao.buscar_por_id(categoria_id)
        if not categoria or categoria.usuario_id != current_user.id:
            flash('Categoria não encontrada.', 'erro')
            return redirect(url_for('categoria.listar'))

        if request.method == 'GET':
            return render_template('cadastrar_categoria.html', categoria=categoria)

        nome  = request.form.get('nome', '').strip()
        icone = request.form.get('icone', '📌').strip()
        cor   = request.form.get('cor', '#2dd4bf').strip()

        if not nome:
            flash('Nome é obrigatório.', 'erro')
            return render_template('cadastrar_categoria.html', categoria=categoria)

        categoria_dao.atualizar_categoria(categoria_id, nome, icone, cor)
        flash('Categoria atualizada!', 'ok')
        return redirect(url_for('categoria.listar'))
    except Exception as e:
        print(f'[ERRO] categoria.editar: {e}')
        flash('Erro ao editar categoria.', 'erro')
        return redirect(url_for('categoria.listar'))


@bp_categoria.route('/excluir/<int:categoria_id>', methods=['POST'])
@login_required
def excluir(categoria_id):
    try:
        categoria = categoria_dao.buscar_por_id(categoria_id)
        if not categoria or categoria.usuario_id != current_user.id:
            flash('Categoria não encontrada.', 'erro')
            return redirect(url_for('categoria.listar'))
        categoria_dao.deletar_categoria(categoria_id)
        flash('Categoria excluída.', 'ok')
    except Exception as e:
        print(f'[ERRO] categoria.excluir: {e}')
        flash('Erro ao excluir categoria.', 'erro')
    return redirect(url_for('categoria.listar'))
