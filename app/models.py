# from app import db

# FALSE = 0
# TRUE = 1

# class User(db.Model):
#     id = db.Column(db.Integer, primary_key = True)
#     name = db.Column(db.String(65))
#     passed_grader = db.Column(db.SmallInteger, default = FALSE)
#     email = db.Column(db.String(120), unique = True)
#     umich_id = db.Column(db.Integer, unique = True)
#     posts = db.relationship('Submission')

#     def is_authenticated(self):
#         return True

#     def is_active(self):
#         return True

#     def is_anonymous(self):
#         return False

#     def get_id(self):
#         return unicode(self.id)

#     def __repr__(self):
#         return '<User %r>' % (self.name)

# class Submission(db.Model):
#     id = db.Column(db.Integer, primary_key = True)
#     name = db.Column(db.String(65))
#     umich_id = db.Column(db.Integer, unique = True)
#     passed_grader = db.Column(db.SmallInteger, default = False)
#     timestamp = db.Column(db.DateTime)
#     user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

#     def __repr__(self):
#         return '<Post %r>' % (self.umich_id)