from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import current_user
from utils.decorators import login_required
from datetime import date
import DAO.meta_dao as meta_dao

bp_meta = Blueprint('meta', __name__, url_prefix='/metas')


def _parse_date(s):
    """Converte string 'YYYY-MM-DD' para date, ou None se vazia."""
    if s:
        try:
            return date.fromisoformat(s)
        except ValueError:
            return None
    return None


@bp_meta.route('/')
@login_required
def listar():
    try:
        metas = meta_dao.listar_metas(current_user.id)
        return render_template('metas.html', metas=metas, today=date.today())
    except Exception as e:
        print(f'[ERRO] meta.listar: {e}')
        flash('Erro ao carregar metas.', 'erro')
        return redirect(url_for('dashboard.painel'))


@bp_meta.route('/cadastrar', methods=['GET', 'POST'])
@login_required
def cadastrar():
    if request.method == 'GET':
        return render_template('cadastrar_meta.html', meta=None)
    try:
        nome       = request.form.get('nome', '').strip()
        valor_alvo = request.form.get('valor_alvo')
        prazo      = request.form.get('prazo') or None
        cor        = request.form.get('cor', '#2dd4bf').strip()

        if not nome or not valor_alvo:
            flash('Preencha os campos obrigatórios.', 'erro')
            return render_template('cadastrar_meta.html', meta=None)

        meta_dao.criar_meta(nome, float(valor_alvo), current_user.id,
                            prazo=_parse_date(prazo), cor=cor)
        flash('Meta criada!', 'ok')
        return redirect(url_for('meta.listar'))
    except Exception as e:
        print(f'[ERRO] meta.cadastrar: {e}')
        flash('Erro ao criar meta.', 'erro')
        return render_template('cadastrar_meta.html', meta=None)


@bp_meta.route('/editar/<int:meta_id>', methods=['GET', 'POST'])
@login_required
def editar(meta_id):
    try:
        m = meta_dao.buscar_por_id(meta_id)
        if not m or m.usuario_id != current_user.id:
            flash('Meta não encontrada.', 'erro')
            return redirect(url_for('meta.listar'))

        if request.method == 'GET':
            return render_template('cadastrar_meta.html', meta=m)

        nome       = request.form.get('nome', '').strip()
        valor_alvo = request.form.get('valor_alvo')
        prazo      = request.form.get('prazo') or None
        cor        = request.form.get('cor', '#2dd4bf').strip()

        if not nome or not valor_alvo:
            flash('Preencha os campos obrigatórios.', 'erro')
            return render_template('cadastrar_meta.html', meta=m)

        meta_dao.atualizar_meta(meta_id, nome=nome, valor_alvo=float(valor_alvo),
                                prazo=_parse_date(prazo), cor=cor)
        flash('Meta atualizada!', 'ok')
        return redirect(url_for('meta.listar'))
    except Exception as e:
        print(f'[ERRO] meta.editar: {e}')
        flash('Erro ao editar meta.', 'erro')
        return redirect(url_for('meta.listar'))


@bp_meta.route('/excluir/<int:meta_id>', methods=['POST'])
@login_required
def excluir(meta_id):
    try:
        m = meta_dao.buscar_por_id(meta_id)
        if not m or m.usuario_id != current_user.id:
            flash('Meta não encontrada.', 'erro')
            return redirect(url_for('meta.listar'))
        meta_dao.deletar_meta(meta_id)
        flash('Meta excluída.', 'ok')
    except Exception as e:
        print(f'[ERRO] meta.excluir: {e}')
        flash('Erro ao excluir meta.', 'erro')
    return redirect(url_for('meta.listar'))
