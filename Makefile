.PHONY: run process-kb install

install:
	pip install -r requirements.txt

run:
	python3 main.py

process-kb:
	python3 -m knowledge_base.process --input .samples/raw --output knowledge_base/processed

process-kb-local:
	python3 -m knowledge_base.process --input knowledge_base/raw --output knowledge_base/processed
