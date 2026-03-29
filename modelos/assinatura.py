from extensao import db


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

    def __repr__(self):
        return f'<Assinatura {self.nome}>'