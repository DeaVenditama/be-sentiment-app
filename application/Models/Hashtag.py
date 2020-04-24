from .. import db

class Hashtag(db.Model):
    """Data model for Hashtag."""

    __tablename__ = 'hashtag'
    id = db.Column(db.Integer,
                   primary_key=True)
    hashtag = db.Column(db.String(64),
                         index=False,
                         unique=True,
                         nullable=False)

    def __repr__(self):
        return '<Hashtag {}>'.format(self.hashtag)
 