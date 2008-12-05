# Makefile

SUBDIRS = scripts rcorder test.d

RM = rm -f
INSTALL = echo install

# note: 'all' must come first
ALLGOALS := all $(filter-out all,${MAKECMDGOALS})

define DoMake
  ${MAKE} -C "${1}" ${2} || exit 1;
endef

define TheGoal
.PHONY: ${1}
${1}:
	$(foreach d,$(SUBDIRS),$(call DoMake,${d},${goal}))
endef

$(foreach goal,${ALLGOALS},$(eval $(call TheGoal,${goal})))
