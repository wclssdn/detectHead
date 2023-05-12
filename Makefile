default: 
	@pyinstaller --onefile  --add-data "res:res" -n detectHead main.py

release: 
	@cp -r config dist
	@cp start.sh README.md dist
	@rm -rf release
	@mkdir release
	@tar -zcvf release/detectHead.tar.gz -C dist .

clean: 
	@rm -rf dist build *.spec

.PHONY: default clean release
