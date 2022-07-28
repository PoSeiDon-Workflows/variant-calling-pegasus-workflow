FROM rockylinux:8

RUN dnf -y update && \
    dnf -y install 'dnf-command(config-manager)' && \
    dnf -y config-manager --set-enabled powertools && \
    dnf -y config-manager --add-repo=https://download.docker.com/linux/centos/docker-ce.repo && \
    dnf -y install epel-release

RUN dnf -y install --allowerasing --nobest \
     gcc \
     make \
     emacs-nox \
#     vim \
#     nano \
#     glibc-langpack-en \
#     langpacks-en \
     perl-Getopt-Long \
     python36 \
     sudo \
     tar \
     wget \
     curl \
     unzip \
     bzip2

# packages required for compiling samtools htslib
RUN dnf -y install --allowerasing --nobest \
    zlib-devel \
    ncurses-devel \
    bzip2-devel \
    xz-devel
     
ADD install_software.sh /opt

RUN /opt/install_software.sh

ENV PATH="/opt/software/install/bwa/default/:/opt/software/install/bcftools/default/bin:/opt/software/install/samtools/default/bin:/opt/software/install/htslib/default/bin":${PATH}
