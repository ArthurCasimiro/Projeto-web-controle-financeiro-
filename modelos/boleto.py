from extensao import db


class Boleto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    valor = db.Column(db.Float, nullable=False)
    vencimento = db.Column(db.Date, nullable=False)
    descricao = db.Column(db.String(255), nullable=True)
    codigo_barra = db.Column(db.String(60), nullable=True)
    notas = db.Column(db.String(255), nullable=True)
    status = db.Column(db.String(20), nullable=False, default='pendente')
    categoria_id = db.Column(db.Integer, db.ForeignKey('categoria.id'), nullable=True)
    fundo_id = db.Column(db.Integer, db.ForeignKey('fundo.id'), nullable=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)

    categoria = db.relationship('Categoria', lazy='select', foreign_keys=[categoria_id])

    def __repr__(self):
        return f'<Boleto {self.nome} - R$ {self.valor}>'