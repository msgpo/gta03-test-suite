# Makefile

PROGRAM = rcorder
SOURCES = ealloc.c hash.c rcorder.c fparseln.c fgetln.c
OBJECTS = $(addsuffix .o,$(basename ${SOURCES}))
MAN = rcorder.8 fparseln.3

RM = rm -f
INSTALL = install


CFLAGS+= -DORDER -I. -Wall -Werror

.PHONY: all
all: ${PROGRAM}

${PROGRAM}: ${OBJECTS}
	${CC} -o $@ ${LDFLAGS} ${OBJECTS}


.PHONY:install
install: all
	${INSTALL} -d "${DESTDIR}/sbin"
	${INSTALL} -m 0755 "${PROGRAM}" ${DESTDIR}/sbin/


.PHONY:clean
clean:
	${RM} "${PROGRAM}" *.core *~ *.o


.PHONY: depend
depend:
	makedepend -Y ${CFLAGS} ${SOURCES}

# DO NOT DELETE

ealloc.o: ealloc.h
hash.o: sprite.h hash.h ealloc.h
rcorder.o: ./libutil.h ealloc.h sprite.h hash.h
fparseln.o: ./libutil.h
