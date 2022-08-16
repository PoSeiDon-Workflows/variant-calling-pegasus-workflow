# Variant Calling Pegasus Workflow

A Pegasus Workflow for [Automating a Variant Calling Workflow](https://datacarpentry.org/wrangling-genomics/05-automation/index.html) 
from Data Carpentry Lesson [Data Wrangling and Processing for Genomics](https://datacarpentry.org/wrangling-genomics/).
 

Pegasus workflow which downloads and aligns SRA data to the E. coli REL606 reference genome,
and see what differences exist in our reads versus the genome. The workflow also performs perform 
variant calling to see how the population changed over time. 

SRA Tools, samtools and Bowtie2 are all included in a single Docker
container defined in `Dockerfile` and available in the Docker Hub under
`[pegasus/variant-calling](https://hub.docker.com/repository/docker/pegasus/variant-calling)`. The workflow is setup up to use that container
but execute it via Singularity as that maybe a more common container
runtime on HPC machines. The container runtime used can easily be
changed in the workflow definition.

The number of concurrent downloads is limited with a DAGMan
category profile.



To submit a workflow, run:

    ./sra-search.py --sra-id-list tests/10/sra_ids.txt --reference tests/10/crassphage.fna
    


