# Makefile

PROGRAM = makedevs

SOURCE = ${PROGRAM}.c

DEVICE_TABLE = device_table-minimal.txt

RM = rm -f

all: ${PROGRAM}




${PROGRAM}: ${SOURCE}


clean:
	${RM} *~ *.o "${PROGRAM}"


program-name:
	@echo "${CURDIR}/${PROGRAM}"

device-table-name:
	@echo "${CURDIR}/${DEVICE_TABLE}"
