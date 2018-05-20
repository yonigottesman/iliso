from app import db


class Feed(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128))
    samples = db.relationship('Sample', backref='Feed', lazy='dynamic',
                              cascade='delete')

    
class Sample(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    feed_id = db.Column(db.Integer, db.ForeignKey('feed.id'))
    value = db.Column(db.Float)
    time = db.Column(db.DateTime)
