default: 
	@pyinstaller --onefile  --add-data "res:res" -n detectHead main.py

.PHONY: default
