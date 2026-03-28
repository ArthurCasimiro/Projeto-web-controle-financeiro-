from extensao import db

class Categoria(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    descricao = db.Column(db.String(255), nullable=True)
    icone = db.Column(db.String(10), nullable=True)
    cor = db.Column(db.String(7), nullable=True)

    gastos = db.relationship('Gasto', backref='categoria', lazy=True)
    boletos = db.relationship('Boleto', backref='categoria', lazy=True)
    assinaturas = db.relationship('Assinatura', backref='categoria', lazy=True)

    def __repr__(self):
        return f'<Categoria {self.nome}>'