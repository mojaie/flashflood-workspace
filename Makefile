
serve:
	python3 app.py --debug=True --port=8889

test:
	python3 -m unittest discover -s apitest

chem:
	python3 ./scripts/chem_workflow_demo.py

assay:
	python3 ./scripts/exp_workflow_demo.py
