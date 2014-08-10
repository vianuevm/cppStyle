from app import db

FALSE = 0
TRUE = 1

class User(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    passed_grader = db.Column(db.SmallInteger, Default = FALSE)
    posts = db.relationship('Post', backref = 'passed_grader', lazy = 'dynamic')

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return unicode(self.id)

    def __repr__(self):
        return '<User %r>' % (self.nickname)

class Post(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    passed_grader = db.Column(db.SmallInterger)
    timestamp = db.Column(db.DateTime)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return '<Post %r>' % (self.body)