PYTHON ?= python3

.PHONY: test check demo

test:
	PYTHONPATH=src $(PYTHON) -m unittest discover -s tests -v

check:
	$(PYTHON) tools/check_style.py src tests tools

demo:
	mkdir -p out
	for name in copy_array sqrt_demo sqrt_vector example_squares \
	        example_arbitrary example_edges; do \
	    ./run.sh asm programs/$$name.asm out/$$name.bin; \
	done
	./run.sh vm out/copy_array.bin out/copy_array.json 300:305
	./run.sh vm out/sqrt_demo.bin out/sqrt_demo.json 1100:1105
	for name in sqrt_vector example_squares example_arbitrary \
	        example_edges; do \
	    ./run.sh vm out/$$name.bin out/$$name.json 1000:1006; \
	done
	cat out/*.json
