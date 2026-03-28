from flask import Blueprint, request, render_template, redirect, url_for, session, flash
from DAO import usuario_dao

bp_auth = Blueprint('auth', __name__, url_prefix='/auth')


@bp_auth.route('/login', methods=['POST'])
def fazer_login():
    email = request.form.get('email')
    senha = request.form.get('senha')

    usuario = usuario_dao.buscar_por_email(email)

    if usuario and usuario.senha == senha:
        session['usuario_id'] = usuario.id
        session['usuario_nome'] = usuario.nome
        return redirect(url_for('dashboard.painel'))
    else:
        flash('E-mail ou senha incorretos.', 'erro')
        return redirect(url_for('home_page'))


@bp_auth.route('/cadastrar', methods=['GET', 'POST'])
def cadastrar():
    if request.method == 'GET':
        return render_template('cadastrar.html')

    nome = request.form.get('nome')
    email = request.form.get('email')
    senha = request.form.get('senha')
    confirmar = request.form.get('confirmar')

    if senha != confirmar:
        flash('As senhas não coincidem.', 'erro')
        return render_template('cadastrar.html')

    if len(senha) < 6:
        flash('A senha deve ter pelo menos 6 caracteres.', 'erro')
        return render_template('cadastrar.html')

    if usuario_dao.buscar_por_email(email):
        flash('Este e-mail já está cadastrado.', 'erro')
        return render_template('cadastrar.html')

    usuario = usuario_dao.criar_usuario(nome, email, senha)
    if usuario:
        session['usuario_id'] = usuario.id
        session['usuario_nome'] = usuario.nome
        return redirect(url_for('dashboard.painel'))
    else:
        flash('Erro ao cadastrar usuário. Tente novamente.', 'erro')
        return render_template('cadastrar.html')


@bp_auth.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home_page'))
