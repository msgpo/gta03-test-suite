# Makefile

PROGRAM = GraphicTestShell
SOURCES =
OBJECTS =
MAN =

RM = rm -f
INSTALL = install
SETUP = python setup.py build


CFLAGS+=

.PHONY: all
all: ${PROGRAM}

.PHONY: ${PROGRAM}
${PROGRAM}:
	${SETUP} build


.PHONY:install
install: all
	${SETUP} install --root="${DESTDIR}"


.PHONY:clean
clean:
	${RM} *.core *~ *.o *.pyc *.pyo
	${RM} -r build
