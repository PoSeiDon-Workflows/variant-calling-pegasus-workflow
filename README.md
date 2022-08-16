# Variant Calling Pegasus Workflow

A Pegasus Workflow for 
[Automating a Variant Calling Workflow](https://datacarpentry.org/wrangling-genomics/05-automation/index.html) 
from Data Carpentry Lesson 
[Data Wrangling and Processing for Genomics](https://datacarpentry.org/wrangling-genomics/).

Pegasus workflow which downloads and aligns SRA data to the E. coli 
REL606 reference genome,and see what differences exist in our reads versus
the genome. The workflow also performs perform  variant calling to see how 
the population changed over time. 

## Container
All tools required to execute the jobs in the container are all included in
a single Docker container defined in `docker/Dockerfile` and available in the
[Docker Hub](https://hub.docker.com/repository/docker/pegasus/variant-calling) under
`pegasus/variant-calling`. The workflow is setup up to use that container
but execute it via Singularity as that maybe a more common container
runtime on HPC machines. The container runtime used can easily be
changed in the workflow definition.

The container comes with the following tools
* Burrows-Wheeler Aligner (BWA) 0.7.17
* SamTools 1.15.1
* Bcftools 1.15.1
* HTSlib   1.15.1
* SRA Tools 3.0.0

The number of concurrent downloads is limited with a DAGMan
category profile.

## Workflow
To submit a workflow, run:
```
    ./variant-calling.py --reference-genome ref_genome/ecoli_rel606.fasta  --sequence-reads-list tests/2/sra_ids.txt 
```
