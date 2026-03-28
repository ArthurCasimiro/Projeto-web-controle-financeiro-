from extensao import db
from modelos.meta import Meta

def criar_meta(nome, valor_alvo, usuario_id, valor_atual=0, prazo=None, cor='#2dd4bf'):
    meta = Meta(
        nome=nome,
        valor_alvo=valor_alvo,
        valor_atual=valor_atual,
        prazo=prazo,
        cor=cor,
        usuario_id=usuario_id
    )
    db.session.add(meta)
    db.session.commit()
    return meta

def buscar_por_id(meta_id):
    return Meta.query.get(meta_id)

def listar_metas(usuario_id):
    return Meta.query.filter_by(usuario_id=usuario_id).all()

def atualizar_meta(meta_id, nome=None, valor_alvo=None, valor_atual=None, prazo=None, cor=None):
    meta = buscar_por_id(meta_id)
    if not meta:
        return None
    if nome:
        meta.nome = nome
    if valor_alvo is not None:
        meta.valor_alvo = valor_alvo
    if valor_atual is not None:
        meta.valor_atual = valor_atual
    if prazo is not None:
        meta.prazo = prazo
    if cor:
        meta.cor = cor
    db.session.commit()
    return meta

def deletar_meta(meta_id):
    meta = buscar_por_id(meta_id)
    if not meta:
        return False
    db.session.delete(meta)
    db.session.commit()
    return True