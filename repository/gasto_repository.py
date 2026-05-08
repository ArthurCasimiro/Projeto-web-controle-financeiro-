from extensao import db
from modelos.gasto import Gasto

def criar_gasto(descricao, valor, data, recorrente, categoria_id, usuario_id):
    gasto = Gasto(
        descricao=descricao,
        valor=valor,
        data=data,
        recorrente=recorrente,
        categoria_id=categoria_id,
        usuario_id=usuario_id
    )
    db.session.add(gasto)
    db.session.commit()
    return gasto

def buscar_por_id(gasto_id):
    return Gasto.query.get(gasto_id)

def listar_gastos(usuario_id):
    return Gasto.query.filter_by(usuario_id=usuario_id).all()

def atualizar_gasto(gasto_id, descricao=None, valor=None, data=None,
                    recorrente=None, categoria_id=None):
    gasto = buscar_por_id(gasto_id)
    if not gasto:
        return None
    if descricao is not None:
        gasto.descricao = descricao
    if valor is not None:
        gasto.valor = valor
    if data is not None:
        gasto.data = data
    if recorrente is not None:
        gasto.recorrente = recorrente
    if categoria_id is not None:
        gasto.categoria_id = categoria_id
    db.session.commit()
    return gasto

def listar_mes_atual(usuario_id):
    from datetime import datetime
    agora = datetime.now()
    return Gasto.query.filter_by(usuario_id=usuario_id).filter(db.extract('month', Gasto.data) == agora.month, db.extract('year', Gasto.data) == agora.year).all()

def total_mes_atual(usuario_id):
    from datetime import datetime
    agora = datetime.now()
    return db.session.query(db.func.sum(Gasto.valor)).filter_by(usuario_id=usuario_id).filter(db.extract('month', Gasto.data) == agora.month, db.extract('year', Gasto.data) == agora.year).scalar() or 0

def deletar_gasto(gasto_id):
    gasto = buscar_por_id(gasto_id)
    if not gasto:
        return False
    db.session.delete(gasto)
    db.session.commit()
    return True