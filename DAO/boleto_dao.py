from extensao import db
from modelos.boleto import Boleto

def criar_boleto(valor, data_vencimento, categoria_id, usuario_id):
    boleto = Boleto(valor=valor, data_vencimento=data_vencimento, categoria_id=categoria_id, usuario_id=usuario_id)
    db.session.add(boleto)
    db.session.commit()
    return boleto

def buscar_por_id(boleto_id):
    return Boleto.query.get(boleto_id)

def listar_boletos(usuario_id):
    return Boleto.query.filter_by(usuario_id=usuario_id).all()

def listar_urgentes(usuario_id):
    from datetime import datetime, timedelta
    hoje = datetime.now().date()
    proximos_dias = hoje + timedelta(days=7)
    return Boleto.query.filter_by(usuario_id=usuario_id).filter(
        Boleto.data_vencimento >= hoje,
        Boleto.data_vencimento <= proximos_dias,
        Boleto.status != 'pago'
    ).all()

def listar_vencidos(usuario_id):
    from datetime import datetime
    hoje = datetime.now().date()
    return Boleto.query.filter_by(usuario_id=usuario_id).filter(
        Boleto.data_vencimento < hoje,
        Boleto.status != 'pago'
    ).all()

def marcar_como_pago(boleto_id):
    boleto = buscar_por_id(boleto_id)
    if not boleto:
        return None
    boleto.status = 'pago'
    db.session.commit()
    return boleto

def atualizar_boleto(boleto_id, valor=None, data_vencimento=None, categoria_id=None):
    boleto = buscar_por_id(boleto_id)
    if not boleto:
        return None
    if valor is not None:
        boleto.valor = valor
    if data_vencimento is not None:
        boleto.data_vencimento = data_vencimento
    if categoria_id is not None:
        boleto.categoria_id = categoria_id
    db.session.commit()
    return boleto

def deletar_boleto(boleto_id):
    boleto = buscar_por_id(boleto_id)
    if not boleto:
        return False
    db.session.delete(boleto)
    db.session.commit()
    return True