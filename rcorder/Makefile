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

depend:
	makedepend -Y ${CFLAGS} ${SOURCES}

# DO NOT DELETE

ealloc.o: ealloc.h
hash.o: sprite.h hash.h ealloc.h
rcorder.o: ./libutil.h ealloc.h sprite.h hash.h
fparseln.o: ./libutil.h
