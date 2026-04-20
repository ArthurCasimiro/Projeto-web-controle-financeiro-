from flask import Blueprint, request, render_template, redirect, url_for, session, flash
from flask_login import login_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
from DAO import usuario_dao

bp_auth = Blueprint('auth', __name__, url_prefix='/auth')


@bp_auth.route('/login', methods=['POST'])
def fazer_login():
    try:
        email = request.form.get('email')
        senha = request.form.get('senha')
        usuario = usuario_dao.buscar_por_email(email)
        if usuario and check_password_hash(usuario.senha, senha):
            login_user(usuario)
            session['usuario_nome'] = usuario.nome
            session['usuario_role'] = usuario.role
            return redirect(url_for('dashboard.painel'))
        flash('E-mail ou senha incorretos.', 'erro')
        return redirect(url_for('home_page'))
    except Exception as e:
        print(f'[ERRO] fazer_login: {e}')
        flash('Erro ao fazer login. Tente novamente.', 'erro')
        return redirect(url_for('home_page'))


@bp_auth.route('/cadastrar', methods=['GET', 'POST'])
def cadastrar():
    if request.method == 'GET':
        return render_template('cadastrar.html')
    try:
        nome      = request.form.get('nome')
        email     = request.form.get('email')
        senha     = request.form.get('senha')
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

        senha_hash = generate_password_hash(senha)
        usuario = usuario_dao.criar_usuario(nome, email, senha_hash)
        if usuario:
            login_user(usuario)
            session['usuario_nome'] = usuario.nome
            session['usuario_role'] = usuario.role
            return redirect(url_for('dashboard.painel'))
        flash('Erro ao cadastrar usuário. Tente novamente.', 'erro')
        return render_template('cadastrar.html')
    except Exception as e:
        print(f'[ERRO] cadastrar_usuario: {e}')
        flash('Erro inesperado ao cadastrar. Tente novamente.', 'erro')
        return render_template('cadastrar.html')


@bp_auth.route('/logout')
def logout():
    try:
        logout_user()
        session.clear()
    except Exception as e:
        print(f'[ERRO] logout: {e}')
    return redirect(url_for('home_page'))
