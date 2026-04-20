from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import current_user
from utils.decorators import login_required
import DAO.fundo_dao as fundo_dao
import DAO.meta_dao as meta_dao
import DAO.gasto_dao as gasto_dao
from datetime import date, datetime

bp_fundo = Blueprint('fundo', __name__, url_prefix='/fundos')


@bp_fundo.route('/')
@login_required
def listar():
    try:
        uid    = current_user.id
        hoje   = date.today()
        fundos = fundo_dao.listar_fundos(uid)
        metas  = meta_dao.listar_metas(uid)
        total_geral     = sum(f.valor for f in fundos)
        fundos_mes      = [f for f in fundos if f.data and f.data.month == hoje.month and f.data.year == hoje.year]
        total_mes       = sum(f.valor for f in fundos_mes)
        qtd_mes         = len(fundos_mes)
        fundos_com_meta = [f for f in fundos if f.meta_id]
        total_metas     = sum(f.valor for f in fundos_com_meta)
        qtd_com_meta    = len(fundos_com_meta)
        saldo           = total_mes - gasto_dao.total_mes_atual(uid)
        return render_template('fundos.html',
                               fundos=fundos, metas=metas,
                               total_geral=total_geral, total_mes=total_mes,
                               qtd_mes=qtd_mes, total_metas=total_metas,
                               qtd_com_meta=qtd_com_meta, saldo=saldo)
    except Exception as e:
        print(f'[ERRO] fundo.listar: {e}')
        flash('Erro ao carregar fundos.', 'erro')
        return redirect(url_for('dashboard.painel'))


@bp_fundo.route('/cadastrar', methods=['GET', 'POST'])
@login_required
def cadastrar():
    try:
        metas = meta_dao.listar_metas(current_user.id)
        if request.method == 'GET':
            meta_pre = request.args.get('meta_id')
            return render_template('cadastrar_fundo.html',
                                   fundo=None, metas=metas,
                                   meta_pre=meta_pre,
                                   today=date.today().isoformat())

        nome      = request.form.get('nome', '').strip()
        valor     = request.form.get('valor')
        data_str  = request.form.get('data') or None
        tipo      = request.form.get('tipo', '').strip() or None
        descricao = request.form.get('descricao', '').strip() or None
        notas     = request.form.get('notas', '').strip() or None
        meta_id   = request.form.get('meta_id') or None

        if not nome or not valor:
            flash('Preencha os campos obrigatórios.', 'erro')
            return render_template('cadastrar_fundo.html',
                                   fundo=None, metas=metas,
                                   today=date.today().isoformat())

        fundo_dao.criar_fundo(
            nome=nome, valor=float(valor), usuario_id=current_user.id,
            descricao=descricao,
            data=datetime.strptime(data_str, '%Y-%m-%d').date() if data_str else date.today(),
            tipo=tipo, notas=notas,
            meta_id=int(meta_id) if meta_id else None,
        )
        flash('Fundo cadastrado!', 'ok')
        return redirect(url_for('fundo.listar'))
    except Exception as e:
        print(f'[ERRO] fundo.cadastrar: {e}')
        flash('Erro ao cadastrar fundo.', 'erro')
        return redirect(url_for('fundo.listar'))


@bp_fundo.route('/editar/<int:fundo_id>', methods=['GET', 'POST'])
@login_required
def editar(fundo_id):
    try:
        f = fundo_dao.buscar_por_id(fundo_id)
        if not f or f.usuario_id != current_user.id:
            flash('Fundo não encontrado.', 'erro')
            return redirect(url_for('fundo.listar'))

        metas = meta_dao.listar_metas(current_user.id)
        if request.method == 'GET':
            return render_template('cadastrar_fundo.html',
                                   fundo=f, metas=metas,
                                   today=date.today().isoformat())

        nome      = request.form.get('nome', '').strip()
        valor     = request.form.get('valor')
        data_str  = request.form.get('data') or None
        tipo      = request.form.get('tipo', '').strip() or None
        descricao = request.form.get('descricao', '').strip() or None
        notas     = request.form.get('notas', '').strip() or None
        meta_id   = request.form.get('meta_id') or None

        if not nome or not valor:
            flash('Preencha os campos obrigatórios.', 'erro')
            return render_template('cadastrar_fundo.html',
                                   fundo=f, metas=metas,
                                   today=date.today().isoformat())

        fundo_dao.atualizar_fundo(
            fundo_id=fundo_id, nome=nome, valor=float(valor),
            descricao=descricao,
            data=datetime.strptime(data_str, '%Y-%m-%d').date() if data_str else None,
            tipo=tipo, notas=notas,
            meta_id=int(meta_id) if meta_id else None,
        )
        flash('Fundo atualizado!', 'ok')
        return redirect(url_for('fundo.listar'))
    except Exception as e:
        print(f'[ERRO] fundo.editar: {e}')
        flash('Erro ao editar fundo.', 'erro')
        return redirect(url_for('fundo.listar'))


@bp_fundo.route('/excluir/<int:fundo_id>', methods=['POST'])
@login_required
def excluir(fundo_id):
    try:
        f = fundo_dao.buscar_por_id(fundo_id)
        if not f or f.usuario_id != current_user.id:
            flash('Fundo não encontrado.', 'erro')
            return redirect(url_for('fundo.listar'))
        fundo_dao.deletar_fundo(fundo_id)
        flash('Fundo excluído.', 'ok')
    except Exception as e:
        print(f'[ERRO] fundo.excluir: {e}')
        flash('Erro ao excluir fundo.', 'erro')
    return redirect(url_for('fundo.listar'))
