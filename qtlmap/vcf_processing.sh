#!/bin/bash

#SBATCH -J dataset-merge
#SBATCH -N 3
#SBATCH -t 24:00:00
#SBATCH --cpus-per-task=1

/gpfs/space/home/kuklane/bin/bin/bcftools index /gpfs/space/home/kuklane/bakalaureusetoo/data/GEUVADIS_GENCORD_TWINSUK/vcfs/GEUVADIS_GRCh38_DS.vcf.gz && /gpfs/space/home/kuklane/bin/bin/bcftools index /gpfs/space/home/kuklane/bakalaureusetoo/data/GEUVADIS_GENCORD_TWINSUK/vcfs/GENCORD_GRCh38.filtered.vcf.gz && /gpfs/space/home/kuklane/bin/bin/bcftools index /gpfs/space/home/kuklane/bakalaureusetoo/data/GEUVADIS_GENCORD_TWINSUK/vcfs/TwinsUK.MAF001.vcf.gz
/gpfs/space/home/kuklane/bin/bin/bcftools merge /gpfs/space/home/kuklane/bakalaureusetoo/data/GEUVADIS_GENCORD_TWINSUK/vcfs/*vcf.gz -Oz -o GEUVADIS_GENCORD_TwinsUK_GRCh38.vcf.gz
/gpfs/space/home/kuklane/bin/bin/bcftools view -e 'GT~"\."' /gpfs/space/home/kuklane/bakalaureusetoo/data/GEUVADIS_GENCORD_TWINSUK/vcfs/GEUVADIS_GENCORD_TwinsUK_GRCh38.vcf.gz -Oz -o GEUVADIS_GENCORD_TwinsUK_GRCh38.no_missing.vcf.gz
/gpfs/space/home/kuklane/bin/bin/bcftools annotate -x FORMAT/GP /gpfs/space/home/kuklane/bakalaureusetoo/data/GEUVADIS_GENCORD_TWINSUK/vcfs/GEUVADIS_GENCORD_TwinsUK_GRCh38.no_missing.vcf.gz -Oz -o GEUVADIS_GENCORD_TwinsUK_GRCh38.format_gp.vcf.gz
/gpfs/space/home/kuklane/bin/bin/bcftools view -m2 -M2 GEUVADIS_GENCORD_TwinsUK_GRCh38.format_gp.vcf.gz -Oz -o GEUVADIS_GENCORD_TwinsUK_GRCh38.final.vcf.gz
