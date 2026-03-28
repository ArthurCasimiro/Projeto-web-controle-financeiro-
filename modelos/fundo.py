from extensao import db


class Fundo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    descricao = db.Column(db.String(255), nullable=True)
    valor = db.Column(db.Float, nullable=False, default=0.0)
    data = db.Column(db.Date, nullable=True)
    tipo = db.Column(db.String(50), nullable=True)
    notas = db.Column(db.String(255), nullable=True)
    meta_id = db.Column(db.Integer, db.ForeignKey('meta.id'), nullable=True)

    def __repr__(self):
        return f'<Fundo {self.nome}>'