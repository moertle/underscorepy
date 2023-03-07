
all:
	@make -C protobuf
	@make -C src

run: all
	PYTHONPATH=.. python3 -m skeleton --debug
