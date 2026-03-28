from extensao import db
from modelos.usuario import Usuario


def criar_usuario(nome, email, senha):
    usuario = Usuario(nome=nome, email=email, senha=senha)
    db.session.add(usuario)
    db.session.commit()
    return usuario


def buscar_por_id(usuario_id):
    return Usuario.query.get(usuario_id)


def buscar_por_email(email):
    return Usuario.query.filter_by(email=email).first()


def listar_usuarios():
    return Usuario.query.all()


def atualizar_usuario(usuario_id, nome=None, email=None, senha=None):
    usuario = buscar_por_id(usuario_id)
    if not usuario:
        return None
    if nome:
        usuario.nome = nome
    if email:
        usuario.email = email
    if senha:
        usuario.senha = senha
    db.session.commit()
    return usuario


def deletar_usuario(usuario_id):
    usuario = buscar_por_id(usuario_id)
    if not usuario:
        return False
    db.session.delete(usuario)
    db.session.commit()
    return True
