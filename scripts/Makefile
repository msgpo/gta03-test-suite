# Makefile

DEST_SUBDIR = /sbin
SCRIPT_SOURCES = test-runner.sh

RM = rm -f
INSTALL = install

.PHONY: all
all:


.PHONY: install
install: all
	${INSTALL} -d "${DESTDIR}/${DEST_SUBDIR}"
	for f in ${SCRIPT_SOURCES}; \
	do \
	  ${INSTALL} -m 0755 "$${f}" "${DESTDIR}/${DEST_SUBDIR}/$${f%.sh}"; \
	done


.PHONY: clean
clean:
	${RM} *.core *~


.PHONY: depend
depend:
