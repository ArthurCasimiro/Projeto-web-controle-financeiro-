from flask import Blueprint, render_template, request, redirect, url_for
from datetime import date
from modelos.boleto import Boleto

boleto_bp = Blueprint('boleto', __name__)

@boleto_bp.route('/boleto')
def listar():
    hoje = date.today()
    boletos = Boleto.query.order_by(Boleto.vencimento).all()

    pendentes = [b for b in boletos if b.status == 'pendente']
    pagos = [b for b in boletos if b.status == 'pago']
    vencidos = [b for b in pendentes if b.vencimento < hoje]

    qtd_urgentes = sum(1 for b in pendentes if 0 <= (b.vencimento - hoje).days <= 7)
    total_urgentes = sum(b.valor for b in pendentes if 0 <= (b.vencimento - hoje).days <= 7)
    total_aberto = sum(b.valor for b in pendentes)
    total_pago = sum(b.valor for b in pagos)

    return render_template(
        'boletos.html',
        boletos=boletos,
        pendentes=pendentes,
        pagos=pagos,
        vencidos=vencidos,
        today=hoje,
        qtd_pendentes=len(pendentes),
        qtd_urgentes=qtd_urgentes,
        total_urgentes=total_urgentes,
        qtd_vencidos=len(vencidos),
        qtd_pagos=len(pagos),
        total_aberto=total_aberto,
        total_pago=total_pago,
    )
