#!/usr/bin/env python3
##!/usr/bin/python3

'''
Sample Pegasus workflow for Automating a Variant Calling Workflow
Based on Lesson Data Wrangling and Processing for Genomics from
the Data Carpentry Workshop
https://datacarpentry.org/wrangling-genomics/05-automation/index.html
'''

import argparse
import logging
import os
import shutil
import sys

from Pegasus.api import *

logging.basicConfig(level=logging.DEBUG)
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

# need to know where Pegasus is installed for notifications
PEGASUS_HOME = shutil.which('pegasus-version')
PEGASUS_HOME = os.path.dirname(os.path.dirname(PEGASUS_HOME))

def generate_wf():
    '''
    Main function that parses arguments and generates the pegasus
    workflow
    '''

    parser = argparse.ArgumentParser(description="generate a pegasus workflow")
    parser.add_argument('--sequence-reads-list', dest='sequence_reads_list', default=None, required=True,
                        help='Specifies list of samples from which reads are aligned')
    parser.add_argument('--reference-genome', dest='reference_genome', default=None, required=True,
                        help='Specifies the reference genome file')
    parser.add_argument('--job-env-file', dest='job_env_file', default=None, required=False,
                        help='Path to setup file that gets sourced when job starts on a worker node')
    args = parser.parse_args(sys.argv[1:])
    
    wf = Workflow('variant-calling')
    tc = TransformationCatalog()
    rc = ReplicaCatalog()
    
    # --- Properties ----------------------------------------------------------
    
    # set the concurrency limit for the download jobs, and send some extra usage
    # data to the Pegasus developers
    props = Properties()
    props['pegasus.catalog.workflow.amqp.url'] = 'amqp://friend:donatedata@msgs.pegasus.isi.edu:5672/prod/workflows'
    props['pegasus.data.configuration'] = 'nonsharedfs'
    props.write() 
    
    # --- Event Hooks ---------------------------------------------------------

    # get emails on all events at the workflow level
    wf.add_shell_hook(EventType.ALL, '{}/share/pegasus/notification/email'.format(PEGASUS_HOME))
    
    # --- Transformations -----------------------------------------------------
    
    container = Container(
                   'variant-calling',
                   Container.SINGULARITY,
                   'docker://pegasus/variant-calling:latest'
                )
    tc.add_containers(container)

    fasterq_dump = Transformation(
        'fasterq-dump',
        site='local',
        container=container,
        pfn=BASE_DIR + '/tools/fasterq_dump_wrapper',
        is_stageable=True
    )
    fasterq_dump.add_profiles(Namespace.CONDOR, key='request_memory', value='1 GB')
    # this one is used to limit the number of concurrent downloads
    fasterq_dump.add_profiles(Namespace.DAGMAN, key='category', value='fasterq-dump')
    tc.add_transformations(fasterq_dump)

    bwa = Transformation(
                       'bwa',
                       site='incontainer',
                       container=container,
                       pfn='/opt/software/install/bwa/default/bwa',
                       is_stageable=False
                    )
    bwa.add_profiles(Namespace.CONDOR, key='request_memory', value='1 GB')
    tc.add_transformations(bwa)

    # we use the simple bash wrapper to convert to bam,
    # sort and index the generated bam file
    samtools = Transformation(
        'samtools',
        site='local',
        container=container,
        pfn=BASE_DIR + '/tools/samtools_wrapper',
        is_stageable=True
    )
    samtools.add_profiles(Namespace.CONDOR, key='request_memory', value='2 GB')
    tc.add_transformations(samtools)

    bcftools = Transformation(
        'bcftools',
        site='incontainer',
        container=container,
        pfn='/opt/software/install/bcftools/default/bin/bcftools',
        is_stageable=False
    )
    bcftools.add_profiles(Namespace.CONDOR, key='request_memory', value='1 GB')
    tc.add_transformations(bcftools)

    vcfutils = Transformation(
        'vcfutils',
        site='incontainer',
        container=container,
        pfn='/opt/software/install/bcftools/default/bin/vcfutils.pl',
        is_stageable=False
    )
    vcfutils.add_profiles(Namespace.CONDOR, key='request_memory', value='1 GB')
    tc.add_transformations(vcfutils)

    # --- Site Catalog -------------------------------------------------
    sc = SiteCatalog()
    osn = Site("osn", arch=Arch.X86_64, os_type=OS.LINUX)

    # create and add a bucket in OSN to use for your workflows
    osn_shared_scratch_dir = Directory(Directory.SHARED_SCRATCH, path="/asc190064-bucket01/pegasus-workflows/variant") \
        .add_file_servers(
        FileServer("s3://vahi@osn/asc190064-bucket01/pegasus-workflows/variant", Operation.ALL),
    )
    osn.add_directories(osn_shared_scratch_dir)
    sc.add_sites(osn)

    # add a local site with an optional job env file to use for compute jobs
    shared_scratch_dir = "{}/work".format(BASE_DIR)
    local_storage_dir = "{}/storage".format(BASE_DIR)
    local = Site("local") \
        .add_directories(
        Directory(Directory.SHARED_SCRATCH, shared_scratch_dir)
            .add_file_servers(FileServer("file://" + shared_scratch_dir, Operation.ALL)),
        Directory(Directory.LOCAL_STORAGE, local_storage_dir)
            .add_file_servers(FileServer("file://" + local_storage_dir, Operation.ALL)))

    if(args.job_env_file):
        job_env_file = os.path.abspath(args.job_env_file)
        local.add_pegasus_profile(pegasus_lite_env_source=job_env_file)

    sc.add_sites(local)

    # --- Workflow -----------------------------------------------------
    # set up the reference genome and what files need to be generated by the index job
    ref_genome_lfn=os.path.basename(args.reference_genome)
    ref_genome = File(ref_genome_lfn)
    rc.add_replica('local', ref_genome_lfn, os.path.abspath(args.reference_genome))
    index_files = []
    for suffix in ['amb', 'ann', 'bwt', 'pac', 'sa']:
        index_files.append(File(ref_genome.lfn + "." + suffix))

    # index the reference file
    index_job = Job('bwa', node_label="ref_genome_index")
    index_job.add_args('index', ref_genome.lfn)
    index_job.add_inputs(ref_genome)
    index_job.add_outputs(*index_files, stage_out=False)
    wf.add_jobs(index_job)

    # create jobs for each trimmed fastq trim.sub.fastq
    fh = open(args.sequence_reads_list)
    for line in fh:
        sra_id = line.strip()
        if len(sra_id) < 5:
            continue


        """
        # files for this id
        # commented out as we download files from NCBI as part of fasterq-dump job
        fastq_1 = File('{}_1.trim.sub.fastq'.format(sra_id))
        fastq_2 = File('{}_2.trim.sub.fastq'.format(sra_id))
        rc.add_replica('local', fastq_1, os.path.join(os.path.abspath(args.fastq_dir), fastq_1.lfn))
        rc.add_replica('local', fastq_2, os.path.join(os.path.abspath(args.fastq_dir), fastq_2.lfn))
        """

        sam=File('{}.aligned.sam'.format(sra_id))
        bam=File('{}.aligned.bam'.format(sra_id))
        sorted_bam=File('{}.aligned.sorted.bam'.format(sra_id))

        raw_bcf=File('{}_raw.bcf'.format(sra_id))
        variants=File('{}_variants.bcf'.format(sra_id))
        final_variants=File('{}_final_variants.bcf'.format(sra_id))

        """
        bwa mem $genome $fq1 $fq2 > $sam
        samtools view -S -b $sam > $bam
        samtools sort -o $sorted_bam $bam 
        samtools index $sorted_bam
        bcftools mpileup -O b -o $raw_bcf -f $genome $sorted_bam
        bcftools call --ploidy 1 -m -v -o $variants $raw_bcf 
        vcfutils.pl varFilter $variants > $final_variants
        """

        # files for this id
        fastq_1 = File('{}_1.fastq'.format(sra_id))
        fastq_2 = File('{}_2.fastq'.format(sra_id))

        # download job
        j = Job('fasterq-dump', node_label="fasterq_dump")
        j.add_args('--split-files', sra_id)
        j.add_outputs(fastq_1, fastq_2, stage_out=False)
        wf.add_jobs(j)

        # align reads tp reference genome job
        j = Job('bwa', node_label="align_reads")
        j.add_args('mem', ref_genome, fastq_1, fastq_2)
        j.add_inputs(*index_files, ref_genome, fastq_1, fastq_2)
        j.set_stdout(sam, stage_out=False)
        wf.add_jobs(j)

        # samtools_wrapper for doing alignment to genome
        j = Job('samtools', node_label="sam_2_bam_converter")
        j.add_args(sra_id)
        j.add_inputs(sam)
        j.add_outputs(bam, sorted_bam, stage_out=False)
        wf.add_jobs(j)

        # Variant calling
        # bcftools for calculating the read coverage of positions in the genome
        j = Job('bcftools', node_label="calculate_read_coverage")
        j.add_args('mpileup -O b -o', raw_bcf, '-f', ref_genome, sorted_bam)
        j.add_inputs(ref_genome, sorted_bam)
        j.add_outputs(raw_bcf, stage_out=False)
        wf.add_jobs(j)

        # bcftools for Detect the single nucleotide variants (SNVs)
        j = Job('bcftools', node_label="detect_snv")
        j.add_args('call --ploidy 1 -m -v -o', variants, raw_bcf)
        j.add_inputs(raw_bcf)
        j.add_outputs(variants, stage_out=False)
        wf.add_jobs(j)

        # vcfutils Filter and report the SNV variants in variant calling format (VCF)
        j = Job('vcfutils', node_label="variant_calling")
        j.add_args('varFilter', variants)
        j.add_inputs(variants)
        j.set_stdout(final_variants, stage_out=True)
        wf.add_jobs(j)

    try:
        wf.add_transformation_catalog(tc)
        wf.add_site_catalog(sc)
        wf.add_replica_catalog(rc)
        wf.plan(staging_sites={"condorpool": "osn"}, sites=["condorpool"], verbose=3, submit=True)
    except PegasusClientError as e:
        print(e.output)


if __name__ == '__main__':
    generate_wf()

