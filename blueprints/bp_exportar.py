import csv
import io
import zipfile
from datetime import date, datetime
from flask import Blueprint, render_template, request, make_response, flash, redirect, url_for
from flask_login import current_user
from utils.decorators import login_required
import DAO.gasto_dao as gasto_dao
import DAO.boleto_dao as boleto_dao
import DAO.assinatura_dao as assinatura_dao
import DAO.fundo_dao as fundo_dao
import DAO.meta_dao as meta_dao

bp_exportar = Blueprint('exportar', __name__, url_prefix='/exportar')


def _csv_gastos(gastos):
    out = io.StringIO()
    w = csv.writer(out)
    w.writerow(['ID', 'Valor', 'Data', 'Descrição', 'Categoria', 'Recorrente'])
    for g in gastos:
        w.writerow([g.id, g.valor,
                    g.data.isoformat() if g.data else '',
                    g.descricao or '',
                    g.categoria.nome if g.categoria else '',
                    'Sim' if g.recorrente else 'Não'])
    return out.getvalue()


def _csv_boletos(boletos):
    out = io.StringIO()
    w = csv.writer(out)
    w.writerow(['ID', 'Nome', 'Valor', 'Vencimento', 'Status', 'Descrição', 'Categoria'])
    for b in boletos:
        w.writerow([b.id, b.nome, b.valor,
                    b.vencimento.isoformat() if b.vencimento else '',
                    b.status, b.descricao or '',
                    b.categoria.nome if b.categoria else ''])
    return out.getvalue()


def _csv_assinaturas(assinaturas):
    out = io.StringIO()
    w = csv.writer(out)
    w.writerow(['ID', 'Nome', 'Valor', 'Ciclo', 'Dia Vencimento', 'Status', 'Desde', 'Categoria'])
    for a in assinaturas:
        w.writerow([a.id, a.nome, a.valor, a.ciclo, a.dia_vencimento, a.status,
                    a.desde.isoformat() if a.desde else '',
                    a.categoria.nome if a.categoria else ''])
    return out.getvalue()


def _csv_fundos(fundos):
    out = io.StringIO()
    w = csv.writer(out)
    w.writerow(['ID', 'Nome', 'Valor', 'Data', 'Tipo', 'Descrição', 'Meta'])
    for f in fundos:
        w.writerow([f.id, f.nome, f.valor,
                    f.data.isoformat() if f.data else '',
                    f.tipo or '', f.descricao or '',
                    f.meta.nome if f.meta else ''])
    return out.getvalue()


def _csv_metas(metas):
    out = io.StringIO()
    w = csv.writer(out)
    w.writerow(['ID', 'Nome', 'Valor Alvo', 'Valor Atual', 'Prazo', 'Cor'])
    for m in metas:
        w.writerow([m.id, m.nome, m.valor_alvo, m.valor_atual,
                    m.prazo.isoformat() if m.prazo else '', m.cor or ''])
    return out.getvalue()


@bp_exportar.route('/')
@login_required
def index():
    try:
        hoje     = date.today()
        hoje_ini = hoje.replace(day=1).isoformat()
        return render_template('exportar.html', tab='all',
                               hoje=hoje.isoformat(), hoje_ini=hoje_ini)
    except Exception as e:
        print(f'[ERRO] exportar.index: {e}')
        flash('Erro ao carregar página de exportação.', 'erro')
        return redirect(url_for('dashboard.painel'))


@bp_exportar.route('/tudo', methods=['POST'])
@login_required
def exportar_tudo():
    try:
        uid     = current_user.id
        modulos = request.form.getlist('modulos')
        tipo    = request.form.get('tipo', 'separados')

        dados = {}
        if 'gastos' in modulos:
            dados['gastos'] = _csv_gastos(gasto_dao.listar_gastos(uid))
        if 'boletos' in modulos:
            dados['boletos'] = _csv_boletos(boleto_dao.listar_boletos(uid))
        if 'assinaturas' in modulos:
            dados['assinaturas'] = _csv_assinaturas(assinatura_dao.listar_assinaturas(uid))
        if 'fundos' in modulos:
            dados['fundos'] = _csv_fundos(fundo_dao.listar_fundos(uid))
        if 'metas' in modulos:
            dados['metas'] = _csv_metas(meta_dao.listar_metas(uid))

        if tipo == 'unico':
            out = io.StringIO()
            for nome, conteudo in dados.items():
                out.write(f'# {nome.upper()}\n')
                out.write(conteudo)
                out.write('\n')
            response = make_response(out.getvalue())
            response.headers['Content-Disposition'] = 'attachment; filename=fintrack_completo.csv'
            response.headers['Content-Type'] = 'text/csv; charset=utf-8'
            return response
        else:
            buf = io.BytesIO()
            with zipfile.ZipFile(buf, 'w', zipfile.ZIP_DEFLATED) as zf:
                for nome, conteudo in dados.items():
                    zf.writestr(f'{nome}.csv', conteudo.encode('utf-8'))
            buf.seek(0)
            response = make_response(buf.read())
            response.headers['Content-Disposition'] = 'attachment; filename=fintrack_export.zip'
            response.headers['Content-Type'] = 'application/zip'
            return response
    except Exception as e:
        print(f'[ERRO] exportar.tudo: {e}')
        flash('Erro ao exportar dados.', 'erro')
        return redirect(url_for('exportar.index'))


@bp_exportar.route('/periodo', methods=['POST'])
@login_required
def exportar_periodo():
    try:
        uid        = current_user.id
        modulos    = request.form.getlist('modulos')
        data_ini_s = request.form.get('data_inicio')
        data_fim_s = request.form.get('data_fim')
        data_ini   = datetime.strptime(data_ini_s, '%Y-%m-%d').date() if data_ini_s else date(2000, 1, 1)
        data_fim   = datetime.strptime(data_fim_s, '%Y-%m-%d').date() if data_fim_s else date.today()

        out = io.StringIO()
        w   = csv.writer(out)

        if 'gastos' in modulos:
            gastos = [g for g in gasto_dao.listar_gastos(uid)
                      if g.data and data_ini <= g.data <= data_fim]
            w.writerow(['# GASTOS'])
            w.writerow(['ID', 'Valor', 'Data', 'Descrição', 'Categoria'])
            for g in gastos:
                w.writerow([g.id, g.valor, g.data.isoformat(),
                            g.descricao or '', g.categoria.nome if g.categoria else ''])
            w.writerow([])

        if 'fundos' in modulos:
            fundos = [f for f in fundo_dao.listar_fundos(uid)
                      if f.data and data_ini <= f.data <= data_fim]
            w.writerow(['# FUNDOS'])
            w.writerow(['ID', 'Nome', 'Valor', 'Data', 'Tipo'])
            for f in fundos:
                w.writerow([f.id, f.nome, f.valor,
                            f.data.isoformat() if f.data else '', f.tipo or ''])
            w.writerow([])

        if 'boletos' in modulos:
            boletos = [b for b in boleto_dao.listar_boletos(uid)
                       if b.vencimento and data_ini <= b.vencimento <= data_fim]
            w.writerow(['# BOLETOS'])
            w.writerow(['ID', 'Nome', 'Valor', 'Vencimento', 'Status'])
            for b in boletos:
                w.writerow([b.id, b.nome, b.valor, b.vencimento.isoformat(), b.status])
            w.writerow([])

        response = make_response(out.getvalue())
        response.headers['Content-Disposition'] = (
            f'attachment; filename=fintrack_{data_ini_s}_a_{data_fim_s}.csv'
        )
        response.headers['Content-Type'] = 'text/csv; charset=utf-8'
        return response
    except Exception as e:
        print(f'[ERRO] exportar.periodo: {e}')
        flash('Erro ao exportar período.', 'erro')
        return redirect(url_for('exportar.index'))


@bp_exportar.route('/gastos')
@login_required
def exportar_gastos():
    try:
        response = make_response(_csv_gastos(gasto_dao.listar_gastos(current_user.id)))
        response.headers['Content-Disposition'] = 'attachment; filename=gastos.csv'
        response.headers['Content-Type'] = 'text/csv; charset=utf-8'
        return response
    except Exception as e:
        print(f'[ERRO] exportar.gastos: {e}')
        flash('Erro ao exportar gastos.', 'erro')
        return redirect(url_for('exportar.index'))


@bp_exportar.route('/boletos')
@login_required
def exportar_boletos():
    try:
        response = make_response(_csv_boletos(boleto_dao.listar_boletos(current_user.id)))
        response.headers['Content-Disposition'] = 'attachment; filename=boletos.csv'
        response.headers['Content-Type'] = 'text/csv; charset=utf-8'
        return response
    except Exception as e:
        print(f'[ERRO] exportar.boletos: {e}')
        flash('Erro ao exportar boletos.', 'erro')
        return redirect(url_for('exportar.index'))


@bp_exportar.route('/assinaturas')
@login_required
def exportar_assinaturas():
    try:
        response = make_response(_csv_assinaturas(assinatura_dao.listar_assinaturas(current_user.id)))
        response.headers['Content-Disposition'] = 'attachment; filename=assinaturas.csv'
        response.headers['Content-Type'] = 'text/csv; charset=utf-8'
        return response
    except Exception as e:
        print(f'[ERRO] exportar.assinaturas: {e}')
        flash('Erro ao exportar assinaturas.', 'erro')
        return redirect(url_for('exportar.index'))
