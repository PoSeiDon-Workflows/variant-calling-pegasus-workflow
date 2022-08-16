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

The Pegasus workflow downloads SRA data from NCBI repository using
`fasterq-dump` in the SRA toolkit and aligns it against the reference 
genome.

![Pegasus Variant Calling Workflow for 2 SRA reads ](/images/workflow.png)

The tools used for various jobs in the worklfow are listed in table below

| Job Label                 | Tool Used        |
| --------------------------|----------------- |
| fasterq_dump              | fasterq_dump     |
| align_reads               | bwa              |
| sam_2_bam_converter       | samtools         |
| calculate_read_coverage   | bcftools         |
| detect_snv                | bcftools         |
| variant_calling           | vcfutils         |

### Running the Workflow

The workflow is set to run on a local HTCondor Pool in the nonsharedfs
data configuration mode, where Open Storage Network(OSN) is used as
a staging site. You need to specify your OSN credentials in the Pegasus
Credentials file (~/.pegasus/credentials.conf). 

Details on how to do it can be found in the 
[user guide](https://pegasus.isi.edu/docs/5.0.3dev/reference-guide/data-management.html#open-storage-network-osn-osn)

To submit a workflow, run:
```
    ./variant-calling.py --reference-genome ref_genome/ecoli_rel606.fasta  --sequence-reads-list tests/2/sra_ids.txt 
```
