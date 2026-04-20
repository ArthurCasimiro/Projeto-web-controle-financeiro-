from extensao import db
from modelos.fundo import Fundo
from datetime import date


def criar_fundo(nome, valor, usuario_id, descricao=None, data=None, tipo=None, notas=None, meta_id=None):
    fundo = Fundo(
        nome=nome,
        descricao=descricao,
        valor=valor,
        data=data or date.today(),
        tipo=tipo,
        meta_id=meta_id,
        notas=notas,
        usuario_id=usuario_id
    )
    db.session.add(fundo)
    db.session.commit()
    return fundo


def buscar_por_id(fundo_id):
    return Fundo.query.get(fundo_id)


def listar_fundos(usuario_id):
    return Fundo.query.filter_by(usuario_id=usuario_id).order_by(Fundo.data.desc()).all()


def atualizar_fundo(fundo_id, nome=None, descricao=None, valor=None,
                    data=None, tipo=None, meta_id=None, notas=None):
    fundo = buscar_por_id(fundo_id)
    if not fundo:
        return None
    if nome is not None: fundo.nome = nome
    if descricao is not None: fundo.descricao = descricao
    if valor is not None: fundo.valor = valor
    if data is not None: fundo.data = data
    if tipo is not None: fundo.tipo = tipo
    if meta_id is not None: fundo.meta_id = meta_id
    if notas is not None: fundo.notas = notas
    db.session.commit()
    return fundo


def deletar_fundo(fundo_id):
    fundo = buscar_por_id(fundo_id)
    if not fundo:
        return False
    db.session.delete(fundo)
    db.session.commit()
    return True


def total_por_meta(usuario_id, meta_id):
    return db.session.query(db.func.sum(Fundo.valor)).filter_by(
        usuario_id=usuario_id, meta_id=meta_id
    ).scalar() or 0


def total_geral(usuario_id):
    return db.session.query(db.func.sum(Fundo.valor)).filter_by(
        usuario_id=usuario_id
    ).scalar() or 0


def total_mes_atual(usuario_id):
    hoje = date.today()
    return db.session.query(db.func.sum(Fundo.valor)).filter_by(
        usuario_id=usuario_id
    ).filter(
        db.extract('month', Fundo.data) == hoje.month,
        db.extract('year', Fundo.data) == hoje.year
    ).scalar() or 0
