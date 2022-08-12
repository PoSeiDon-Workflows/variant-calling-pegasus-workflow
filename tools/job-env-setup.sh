/bin/env

export PATH=/usr/bin:/bin
export USER=`whoami`

# initialize modules
. /etc/profile.d/z01_lmod.sh

module load tacc-singularity

