from extensao import db

class Gasto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    valor = db.Column(db.Float, nullable=False)
    data = db.Column(db.Date, nullable=False)
    descricao = db.Column(db.String(255), nullable=True)
    recorrente = db.Column(db.Boolean, default=False, nullable=False)
    categoria_id = db.Column(db.Integer, db.ForeignKey('categoria.id'), nullable=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)

    categoria = db.relationship('Categoria', lazy='select', foreign_keys=[categoria_id])

    def __repr__(self):
        return f'<Gasto {self.valor} em {self.data}>'