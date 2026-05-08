from extensao import db
from modelos.assinatura import Assinatura

def criar_assinatura(nome, valor, ciclo, dia_vencimento, usuario_id, categoria_id=None):
    assinatura = Assinatura(
        nome=nome,
        valor=valor,
        ciclo=ciclo,
        dia_vencimento=dia_vencimento,
        usuario_id=usuario_id,
        categoria_id=categoria_id
    )
    db.session.add(assinatura)
    db.session.commit()
    return assinatura

def buscar_por_id(assinatura_id):
    return Assinatura.query.get(assinatura_id)

def listar_assinaturas(usuario_id):
    return Assinatura.query.filter_by(usuario_id=usuario_id).all()

def alterar_status_assinatura(assinatura_id, status):
    assinatura = buscar_por_id(assinatura_id)
    if not assinatura:
        return None
    assinatura.status = status
    db.session.commit()
    return assinatura

def total_assinaturas_ativas(usuario_id):
    return Assinatura.query.filter_by(usuario_id=usuario_id, status='ativa').count()

def atualizar_assinatura(assinatura_id, nome=None, valor=None, ciclo=None, dia_vencimento=None, categoria_id=None):
    assinatura = buscar_por_id(assinatura_id)
    if not assinatura:
        return None
    if nome:
        assinatura.nome = nome
    if valor is not None:
        assinatura.valor = valor
    if ciclo:
        assinatura.ciclo = ciclo
    if dia_vencimento is not None:
        assinatura.dia_vencimento = dia_vencimento
    if categoria_id is not None:
        assinatura.categoria_id = categoria_id
    db.session.commit()
    return assinatura

def deletar_assinatura(assinatura_id):
    assinatura = buscar_por_id(assinatura_id)
    if not assinatura:
        return False
    db.session.delete(assinatura)
    db.session.commit()
    return True