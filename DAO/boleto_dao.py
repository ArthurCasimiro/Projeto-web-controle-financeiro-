from extensao import db
from modelos.boleto import Boleto
from datetime import date, timedelta


def criar_boleto(nome, valor, vencimento, usuario_id, categoria_id=None,
                 descricao=None, codigo_barra=None, notas=None):
    boleto = Boleto(
        nome=nome,
        valor=valor,
        vencimento=vencimento,
        usuario_id=usuario_id,
        categoria_id=categoria_id,
        descricao=descricao,
        codigo_barra=codigo_barra,
        notas=notas
    )
    db.session.add(boleto)
    db.session.commit()
    return boleto


def buscar_por_id(boleto_id):
    return Boleto.query.get(boleto_id)


def listar_boletos(usuario_id):
    return Boleto.query.filter_by(usuario_id=usuario_id).order_by(Boleto.vencimento).all()


def listar_pendentes(usuario_id):
    return Boleto.query.filter_by(usuario_id=usuario_id, status='pendente').order_by(Boleto.vencimento).all()


def listar_urgentes(usuario_id):
    hoje = date.today()
    proximos = hoje + timedelta(days=7)
    return Boleto.query.filter_by(usuario_id=usuario_id).filter(
        Boleto.vencimento >= hoje,
        Boleto.vencimento <= proximos,
        Boleto.status != 'pago'
    ).all()


def listar_vencidos(usuario_id):
    hoje = date.today()
    return Boleto.query.filter_by(usuario_id=usuario_id).filter(
        Boleto.vencimento < hoje,
        Boleto.status != 'pago'
    ).all()


def marcar_como_pago(boleto_id):
    boleto = buscar_por_id(boleto_id)
    if not boleto:
        return None
    boleto.status = 'pago'
    db.session.commit()
    return boleto


def reabrir(boleto_id):
    boleto = buscar_por_id(boleto_id)
    if not boleto:
        return None
    boleto.status = 'pendente'
    db.session.commit()
    return boleto


def atualizar_boleto(boleto_id, nome=None, valor=None, vencimento=None,
                     categoria_id=None, descricao=None, codigo_barra=None, notas=None):
    boleto = buscar_por_id(boleto_id)
    if not boleto:
        return None
    if nome is not None: boleto.nome = nome
    if valor is not None: boleto.valor = valor
    if vencimento is not None: boleto.vencimento = vencimento
    if categoria_id is not None: boleto.categoria_id = categoria_id
    if descricao is not None: boleto.descricao = descricao
    if codigo_barra is not None: boleto.codigo_barra = codigo_barra
    if notas is not None: boleto.notas = notas
    db.session.commit()
    return boleto


def deletar_boleto(boleto_id):
    boleto = buscar_por_id(boleto_id)
    if not boleto:
        return False
    db.session.delete(boleto)
    db.session.commit()
    return True