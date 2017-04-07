
PROTOC = protoc
PROTOFLAGS = -I. -I/usr/local/include -I/usr/include

PROTO_FILES := $(shell find _/pb -type f -name \*.proto)
PB2_FILES   := $(patsubst %.proto, %_pb2.py, $(PROTO_FILES))
PBCC_FILES  := $(patsubst %.proto, %.pb.cc,  $(PROTO_FILES))

all: $(PB2_FILES) $(PBCC_FILES)

_/pb/%_pb2.py: _/pb/%.proto
	@echo $< '=>' $@
	@(cd _/pb; $(PROTOC) $(PROTOFLAGS) --python_out=. `basename $<`)

_/pb/%.pb.cc: _/pb/%.proto
	@echo $< '=>' $@
	@$(PROTOC) $(PROTOFLAGS) --cpp_out=. $<

install: all
	@pip install .

upgrade: all
	@pip install --upgrade --no-deps .

dist: all
	@python setup.py sdist

clean:
	@find . -type d -name __pycache__ -exec rm -r {} +

distclean: clean
	@rm -f _/pb/*_pb2.py
	@rm -f _/pb/*.pb.cc
	@rm -f _/pb/*.pb.h
	@rm -rf MANIFEST build/ dist/
