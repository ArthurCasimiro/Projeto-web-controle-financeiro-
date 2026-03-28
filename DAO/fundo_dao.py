from extensao import db
from modelos.fundo import Fundo

def criar_fundo(descricao, valor, data, tipo, usuario_id, meta_id=None):
    fundo = Fundo(
        descricao=descricao,
        valor=valor,
        data=data,
        tipo=tipo,
        usuario_id=usuario_id,
        meta_id=meta_id
    )
    db.session.add(fundo)
    db.session.commit()
    return fundo

def buscar_por_id(fundo_id):
    return Fundo.query.get(fundo_id)

def listar_fundos(usuario_id):
    return Fundo.query.filter_by(usuario_id=usuario_id).all()

def atualizar_fundo(fundo_id, nome=None):
    fundo = buscar_por_id(fundo_id)
    if not fundo:
        return None
    if nome:
        fundo.nome = nome
    db.session.commit()
    return fundo

def total_por_meta(usuario_id, meta_id):
    return db.session.query(db.func.sum(Fundo.valor)).filter_by(
        usuario_id=usuario_id, meta_id=meta_id
    ).scalar() or 0

def total_geral(usuario_id):
    return db.session.query(db.func.sum(Fundo.valor)).filter_by(
        usuario_id=usuario_id
    ).scalar() or 0

def deletar_fundo(fundo_id):
    fundo = buscar_por_id(fundo_id)
    if not fundo:
        return False
    db.session.delete(fundo)
    db.session.commit()
    return True