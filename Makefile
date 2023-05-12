default: 
	@rm -rf dist/*
	@pyinstaller --onefile  --add-data "res:res" -n detectHead main.py
	@cp -r config dist
	@cp start.sh README.md dist
	@rm -rf release
	@mkdir release
	@tar -zcvf release/detectHead.tar.gz dist/*

clean: 
	@rm -rf dist build *.spec

.PHONY: default clean
