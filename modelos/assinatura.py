from extensao import db
import calendar


class Assinatura(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    valor = db.Column(db.Float, nullable=False)
    ciclo = db.Column(db.String(20), nullable=True)
    dia_vencimento = db.Column(db.Integer, nullable=True)
    status = db.Column(db.String(20), nullable=False, default='ativa')
    desde = db.Column(db.Date, nullable=True)
    data_fim = db.Column(db.Date, nullable=True)
    notas = db.Column(db.String(255), nullable=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    categoria_id = db.Column(db.Integer, db.ForeignKey('categoria.id'), nullable=True)

    categoria = db.relationship('Categoria', lazy='select', foreign_keys=[categoria_id])

    def valor_mensal(self):
        ciclos = {
            'mensal': 1, 'bimestral': 2, 'trimestral': 3,
            'semestral': 6, 'anual': 12, 'semanal': None,
        }
        if self.ciclo == 'semanal':
            return round(self.valor * 52 / 12, 2)
        divisor = ciclos.get(self.ciclo, 1)
        return round(self.valor / divisor, 2)

    def __repr__(self):
        return f'<Assinatura {self.nome}>'