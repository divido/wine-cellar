
def confirmAndCommit(db, logger):
	"""This prints all changes that will be made to the database and asks the
	user to confirm them. If they do, the session is committed, otherwise it is
	rolled back.
	"""

	logger.printChanges()

	while True:
		confirm = input("Commit [y/n]? ")
		if confirm == 'n':
			db.session.rollback()
			break

		if confirm == 'y':
			db.session.commit()
			break
