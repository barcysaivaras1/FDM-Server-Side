from app.extensions import db

class Receipt(db.Model):
	__tablename__ = "receipt"
	id = db.Column(
		db.Integer, 
		db.ForeignKey("Claim.id"), 
		primary_key=True, 
		autoincrement="auto"
	)
	title = db.Column(db.String(144))
	image_uri = db.Column(db.Text)

	def __repr__(self):
		return f"Receipt ID: {self.id}"
	#
#

# End of File