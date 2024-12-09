parse_wat.py: wat.g
	python -m lark.tools.standalone -s module $< -o $@

