THISDIR:=$(abspath $(dir $(realpath $(lastword ${MAKEFILE_LIST}))))
CFLAGS+= -O3 -Wall -Wextra -fno-strict-aliasing -Wno-unused-result
CPPFLAGS+= -MMD -MP
LDLIBS+= -lm
LDFLAGS+=
ALL = fasta2DB DB2fasta quiva2DB DB2quiva DBsplit DBdust Catrack DBshow DBstats DBrm simulator \
      fasta2DAM DAM2fasta DBdump rangen
ALL = fasta2DB DB2fasta DBsplit DBdust Catrack DBshow DBstats DBrm simulator \
      fasta2DAM DAM2fasta DBdump rangen
#quiva2DB would require -DINTERACTIVE, and we do not need quiva support.
vpath %.c ${THISDIR}

all: ${ALL}
${ALL}: libdazzdb.a

libdazzdb.a: DB.o QV.o
	${AR} -rcv $@ $^

# Shared libs are not used yet, but maybe someday.
%.os: %.c
	${CC} -o $@ -c $< -fPIC ${CFLAGS} ${CPPFLAGS}
libdazzdb.so: DB.os QV.os
	${CC} -o $@ $^ -shared ${LDFLAGS}
install:
	rsync -av ${ALL} ${PREFIX}/bin
	rsync -av libdazzdb.* ${PREFIX}/lib
	rsync -av $(wildcard ${THISDIR}/*.h) ${PREFIX}/include
symlink:
	ln -sf $(addprefix ${CURDIR}/,${ALL}) ${PREFIX}/bin
	ln -sf $(addprefix ${CURDIR}/,$(wildcard libdazzdb.*)) ${PREFIX}/lib
	ln -sf $(wildcard ${THISDIR}/*.h) ${PREFIX}/include
clean:
	rm -f ${ALL}
	rm -f ${DEPS}
	rm -fr *.dSYM *.o *.a *.so *.os
	rm -f DBupgrade.Sep.25.2014 DBupgrade.Dec.31.2014 DUSTupgrade.Jan.1.2015
	rm -f dazz.db.tar.gz

SRCS:=$(notdir $(wildcard ${THISDIR}/*.c))
DEPS:=$(patsubst %.c,%.d,${SRCS})
-include ${DEPS}
