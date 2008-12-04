# Makefile

PROGRAM = rcorder
SOURCES = ealloc.c hash.c rcorder.c fparseln.c fgetln.c
OBJECTS = $(addsuffix .o,$(basename ${SOURCES}))
MAN = rcorder.8 fparseln.3

RM = rm -f


CFLAGS+= -DORDER -I. -Wall -Werror

all: ${PROGRAM}

${PROGRAM}: ${OBJECTS}
	${CC} -o $@ ${LDFLAGS} ${OBJECTS}


clean:
	${RM} "${PROGRAM}" *.core *~ *.o