from flask import Blueprint, render_template, redirect, url_for, session, request, flash
from DAO.assinatura_dao import (
    listar_assinaturas, criar_assinatura, buscar_por_id,
    atualizar_assinatura, alterar_status_assinatura, deletar_assinatura
)
from DAO.categoria_dao import listar_categorias
from datetime import date

bp_assinatura = Blueprint('assinatura', __name__, url_prefix='/assinaturas')


def _uid():
    return session.get('usuario_id')


def _requer_login():
    if not _uid():
        return redirect(url_for('home_page'))


@bp_assinatura.route('/')
def listar():
    redir = _requer_login()
    if redir:
        return redir

    assinaturas = listar_assinaturas(_uid())

    total_mensal = sum(
        s.valor if s.ciclo == 'mensal' else s.valor / 12
        for s in assinaturas if s.status == 'ativa'
    )

    return render_template('assinaturas.html', assinaturas=assinaturas, total_mensal=total_mensal)


@bp_assinatura.route('/cadastrar', methods=['GET', 'POST'])
def cadastrar():
    redir = _requer_login()
    if redir:
        return redir

    if request.method == 'GET':
        categorias = listar_categorias(_uid())
        return render_template('cadastrar_assinatura.html', assinatura=None, categorias=categorias)

    nome = request.form.get('nome', '').strip()
    valor = request.form.get('valor')
    ciclo = request.form.get('ciclo', 'mensal')
    dia_vencimento = request.form.get('dia_vencimento')
    categoria_id = request.form.get('categoria_id') or None
    desde_str = request.form.get('desde')
    notas = request.form.get('notas', '').strip() or None

    if not nome or not valor or not dia_vencimento:
        flash('Preencha os campos obrigatórios.', 'erro')
        return redirect(url_for('assinatura.cadastrar'))

    assinatura = criar_assinatura(
        nome=nome,
        valor=float(valor),
        ciclo=ciclo,
        dia_vencimento=int(dia_vencimento),
        usuario_id=_uid(),
        categoria_id=int(categoria_id) if categoria_id else None,
    )
    assinatura.desde = date.fromisoformat(desde_str) if desde_str else None
    assinatura.notas = notas

    from extensao import db
    db.session.commit()

    flash('Assinatura cadastrada com sucesso.', 'ok')
    return redirect(url_for('assinatura.listar'))


@bp_assinatura.route('/editar/<int:assinatura_id>', methods=['GET', 'POST'])
def editar(assinatura_id):
    redir = _requer_login()
    if redir:
        return redir

    s = buscar_por_id(assinatura_id)
    if not s or s.usuario_id != _uid():
        flash('Assinatura não encontrada.', 'erro')
        return redirect(url_for('assinatura.listar'))

    if request.method == 'GET':
        categorias = listar_categorias(_uid())
        return render_template('cadastrar_assinatura.html', assinatura=s, categorias=categorias)

    nome = request.form.get('nome', '').strip()
    valor = request.form.get('valor')
    ciclo = request.form.get('ciclo', 'mensal')
    dia_vencimento = request.form.get('dia_vencimento')
    categoria_id = request.form.get('categoria_id') or None
    desde_str = request.form.get('desde')
    notas = request.form.get('notas', '').strip() or None

    if not nome or not valor or not dia_vencimento:
        flash('Preencha os campos obrigatórios.', 'erro')
        return redirect(url_for('assinatura.editar', assinatura_id=assinatura_id))

    atualizar_assinatura(
        assinatura_id=assinatura_id,
        nome=nome,
        valor=float(valor),
        ciclo=ciclo,
        dia_vencimento=int(dia_vencimento),
        categoria_id=int(categoria_id) if categoria_id else None,
    )
    s.desde = date.fromisoformat(desde_str) if desde_str else None
    s.notas = notas

    from extensao import db
    db.session.commit()

    flash('Assinatura atualizada.', 'ok')
    return redirect(url_for('assinatura.listar'))


@bp_assinatura.route('/status/<int:assinatura_id>', methods=['POST'])
def alternar_status(assinatura_id):
    redir = _requer_login()
    if redir:
        return redir

    s = buscar_por_id(assinatura_id)
    if not s or s.usuario_id != _uid():
        flash('Assinatura não encontrada.', 'erro')
        return redirect(url_for('assinatura.listar'))

    novo_status = 'pausada' if s.status == 'ativa' else 'ativa'
    alterar_status_assinatura(assinatura_id, novo_status)

    return redirect(url_for('assinatura.listar'))


@bp_assinatura.route('/excluir/<int:assinatura_id>', methods=['POST'])
def excluir(assinatura_id):
    redir = _requer_login()
    if redir:
        return redir

    s = buscar_por_id(assinatura_id)
    if not s or s.usuario_id != _uid():
        flash('Assinatura não encontrada.', 'erro')
        return redirect(url_for('assinatura.listar'))

    deletar_assinatura(assinatura_id)
    flash('Assinatura excluída.', 'ok')
    return redirect(url_for('assinatura.listar'))
