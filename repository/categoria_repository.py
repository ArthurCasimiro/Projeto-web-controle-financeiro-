from extensao import db
from modelos.categoria import Categoria

def criar_categoria(nome, usuario_id, icone='📌', cor='#2dd4bf'):
    categoria = Categoria(nome=nome, icone=icone, cor=cor, usuario_id=usuario_id)
    db.session.add(categoria)
    db.session.commit()
    return categoria

def buscar_por_id(categoria_id):
    return Categoria.query.get(categoria_id)

def listar_categorias(usuario_id):
    return Categoria.query.filter_by(usuario_id=usuario_id).all()

def atualizar_categoria(categoria_id, nome=None, icone=None, cor=None):
    categoria = buscar_por_id(categoria_id)
    if not categoria:
        return None
    if nome:
        categoria.nome = nome
    if icone:
        categoria.icone = icone
    if cor:
        categoria.cor = cor
    db.session.commit()
    return categoria

def deletar_categoria(categoria_id):
    categoria = buscar_por_id(categoria_id)
    if not categoria:
        return False
    db.session.delete(categoria)
    db.session.commit()
    return True