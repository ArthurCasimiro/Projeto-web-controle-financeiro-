from extensao import db


class Meta(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    valor_alvo = db.Column(db.Float, nullable=False)
    prazo = db.Column(db.Date, nullable=True)
    cor = db.Column(db.String(7), nullable=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=True)

    fundos = db.relationship('Fundo', back_populates='meta', lazy=True)

    @property
    def valor_atual(self):
        return sum(f.valor for f in self.fundos)

    def __repr__(self):
        return f'<Meta {self.nome}>'
