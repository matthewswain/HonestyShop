SHELL = /bin/bash

db:
	@rm -f honesty.db
	@source "./venv/bin/activate" && python -c "from database import init_db; init_db()"
