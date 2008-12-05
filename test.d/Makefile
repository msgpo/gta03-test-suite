# Makefile

DEST_SUBDIR = /etc/test.d
SCRIPT_SOURCES = *.sh *.py
DATA_SOURCES =  *.cfg test-functions

RM = rm -f
INSTALL = install

VERIFY = ../scripts/VerifyMetadata

.PHONY: all
all:
	${VERIFY} ${SCRIPT_SOURCES} ${DATA_SOURCES}


.PHONY: install
install: all
	${INSTALL} -d "${DESTDIR}/${DEST_SUBDIR}"
	for f in ${SCRIPT_SOURCES}; \
	do \
	  ${INSTALL} -m 0755 "$${f}" "${DESTDIR}/${DEST_SUBDIR}/"; \
	done
	for f in ${DATA_SOURCES}; \
	do \
	  ${INSTALL} -m 0644 "$${f}" "${DESTDIR}/${DEST_SUBDIR}/"; \
	done


.PHONY: clean
clean:
	${RM} *.core *~


.PHONY: depend
depend:
