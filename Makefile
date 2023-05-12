default: 
	@pyinstaller --onefile  --add-data "res:res" main.py

.PHONY: default
