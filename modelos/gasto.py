from extensao import db
from extensao import login_manager

class Gasto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    valor = db.Column(db.Float, nullable=False)
    data = db.Column(db.Date, nullable=False)
    descricao = db.Column(db.String(255), nullable=True)
    categoria_id = db.Column(db.Integer, db.ForeignKey('categoria.id'), nullable=False)
    fundo_id = db.Column(db.Integer, db.ForeignKey('fundo.id'), nullable=False)

    categoria = db.relationship('Categoria')
    fundo = db.relationship('Fundo')

    def __repr__(self):
        return f'<Gasto {self.valor} em {self.data}>'