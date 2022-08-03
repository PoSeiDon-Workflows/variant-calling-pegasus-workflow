#!/bin/bash
set -e
#set -x

BASE_DIR="/opt"
BWA_VERSION="0.7.17"
SAMTOOLS_VERSION="1.15.1"
BCFTOOLS_VERSION="1.15.1"
HTSLIB_VERSION="1.15.1"
SRATOOLKIT_VERSION="3.0.0"
ADDON_PATH=""

mkdir -p ${BASE_DIR}/software/src ${BASE_DIR}/software/install

# install the sratoolkit
PACKAGE="sratoolkit"
(
    cd ${BASE_DIR}/software/src
    mkdir -p ${PACKAGE}
    curl -L -o ${PACKAGE}/${PACKAGE}-${SRATOOLKIT_VERSION}.tar.gz https://ftp-trace.ncbi.nlm.nih.gov/sra/sdk/${SRATOOLKIT_VERSION}/${PACKAGE}.${SRATOOLKIT_VERSION}-centos_linux64.tar.gz
    cd ${PACKAGE}
    tar zxvf ${PACKAGE}-${SRATOOLKIT_VERSION}.tar.gz
    mkdir -p `pwd`/../../install/${PACKAGE}/${SRATOOLKIT_VERSION}
    mv ${PACKAGE}.${SRATOOLKIT_VERSION}-centos_linux64/* `pwd`/../../install/${PACKAGE}/${SRATOOLKIT_VERSION}/
    (cd `pwd`/../../install/${PACKAGE}/ && ln -s ${SRATOOLKIT_VERSION} default)
)
PACKAGE_PATH=`(cd ${BASE_DIR}/software/install/${PACKAGE}/default/ && pwd)`
echo "${PACKAGE} installed at ${PACKAGE_PATH}"
ADDON_PATH=${PACKAGE_PATH}/bin

# fix for vdb-config interactive issue
# https://github.com/ncbi/sra-tools/issues/291
if ! grep "/LIBS/GUID" ~/.ncbi/user-settings.mkfg &> /dev/null;
   then mkdir -p ~/.ncbi && printf '/LIBS/GUID = "%s"\n' `uuidgen` > ~/.ncbi/user-settings.mkfg;
fi

# install bwa
PACKAGE="bwa"
(
    cd ${BASE_DIR}/software/src
    mkdir -p ${PACKAGE}
    curl -L -o ${PACKAGE}/${PACKAGE}-${BWA_VERSION}.tar.bz2 https://downloads.sourceforge.net/project/bio-bwa/bwa-${BWA_VERSION}.tar.bz2
    cd ${PACKAGE}
    bunzip2 bwa-${BWA_VERSION}.tar.bz2
    tar xvf bwa-${BWA_VERSION}.tar
    cd ${PACKAGE}-${BWA_VERSION}
    make
    mkdir -p `pwd`/../../../install/${PACKAGE}/${BWA_VERSION}
    mv bwa `pwd`/../../../install/${PACKAGE}/${BWA_VERSION}
    (cd `pwd`/../../../install/${PACKAGE}/ && ln -s ${BWA_VERSION} default)
    
)
PACKAGE_PATH=`(cd ${BASE_DIR}/software/install/${PACKAGE}/default/ && pwd)`
echo "${PACKAGE} installed at ${PACKAGE_PATH}"
ADDON_PATH=${PACKAGE_PATH}/bin

# install samtools
PACKAGE="samtools"
(
    cd ${BASE_DIR}/software/src
    mkdir -p ${PACKAGE}
    curl -L -o ${PACKAGE}/${PACKAGE}-${SAMTOOLS_VERSION}.tar.bz2 https://github.com/samtools/samtools/releases/download/${SAMTOOLS_VERSION}/samtools-${SAMTOOLS_VERSION}.tar.bz2
    cd ${PACKAGE}
    bunzip2 ${PACKAGE}-${SAMTOOLS_VERSION}.tar.bz2
    tar xvf ${PACKAGE}-${SAMTOOLS_VERSION}.tar
    cd ${PACKAGE}-${SAMTOOLS_VERSION}
    ./configure --prefix=`pwd`/../../../install/${PACKAGE}/${SAMTOOLS_VERSION}/
    make
    make install
    (cd `pwd`/../../../install/${PACKAGE}/ && ln -s ${SAMTOOLS_VERSION} default)
)
PACKAGE_PATH=`(cd ${BASE_DIR}/software/install/${PACKAGE}/default/ && pwd)`
echo "${PACKAGE} installed at ${PACKAGE_PATH}"
ADDON_PATH=${PACKAGE_PATH}/bin

# install bcftools
PACKAGE="bcftools"
(
    cd ${BASE_DIR}/software/src
    mkdir -p ${PACKAGE}
    curl -L -o ${PACKAGE}/${PACKAGE}-${BCFTOOLS_VERSION}.tar.bz2 https://github.com/samtools/bcftools/releases/download/${BCFTOOLS_VERSION}/bcftools-${BCFTOOLS_VERSION}.tar.bz2
    cd ${PACKAGE}
    bunzip2 ${PACKAGE}-${BCFTOOLS_VERSION}.tar.bz2
    tar xvf ${PACKAGE}-${BCFTOOLS_VERSION}.tar
    cd ${PACKAGE}-${BCFTOOLS_VERSION}
    ./configure --prefix=`pwd`/../../../install/${PACKAGE}/${BCFTOOLS_VERSION}/
    make
    make install
    (cd `pwd`/../../../install/${PACKAGE}/ && ln -s ${BCFTOOLS_VERSION} default)
)
PACKAGE_PATH=`(cd ${BASE_DIR}/software/install/${PACKAGE}/default/ && pwd)`
echo "${PACKAGE} installed at ${PACKAGE_PATH}"
ADDON_PATH=${PACKAGE_PATH}/bin

# install htslib
PACKAGE="htslib"
(
    cd ${BASE_DIR}/software/src
    mkdir -p ${PACKAGE}
    curl -L -o ${PACKAGE}/${PACKAGE}-${HTSLIB_VERSION}.tar.bz2 https://github.com/samtools/htslib/releases/download/${HTSLIB_VERSION}/htslib-${HTSLIB_VERSION}.tar.bz2
    cd ${PACKAGE}
    bunzip2 ${PACKAGE}-${HTSLIB_VERSION}.tar.bz2
    tar xvf ${PACKAGE}-${HTSLIB_VERSION}.tar
    cd ${PACKAGE}-${HTSLIB_VERSION}
    ./configure --prefix=`pwd`/../../../install/${PACKAGE}/${HTSLIB_VERSION}/
    make
    make install
    (cd `pwd`/../../../install/${PACKAGE}/ && ln -s ${HTSLIB_VERSION} default)
)
PACKAGE_PATH=`(cd ${BASE_DIR}/software/install/${PACKAGE}/default/ && pwd)`
echo "${PACKAGE} installed at ${PACKAGE_PATH}"
ADDON_PATH=${PACKAGE_PATH}/bin

#cleanup the source directory
rm -rf ${BASE_DIR}/software/src
