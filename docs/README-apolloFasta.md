* README - apolloFasta.py
This script retrieves and formats peptide fasta sequences from an Apollo2 server.

Data is retrieved via call to the [Apollo webservice API](http://demo.genomearchitect.io/Apollo2/jbrowse/web_services/api). Two API calls are used,

1. write          - obtains a GFF file for an organism on the Apollo server
2. sequenceByName - export a fasta sequence for a requested sequence

The full GFF record is retrieved from the Apollo server using the organims name
and the mRNA features that have the `status=Finished` GFF attribute set are then
retrieved. By default the Apollo mRNA id used for the fasta sequence returned by
the web service, but this is changed to the corresponding CDS id so that there is
no clash between the mRNA and peptide ids.

The GFF file is read into an in memory SQLite database using [gffutils](https://daler.github.io/gffutils/)

The GFF file can be saved to disk if desired (see usage --sqlite option) - 
if a sqlite file with the existing name is found this will be used instead of 
downloading the GFF file from source. Check stdout and the logfile for the 
details of which source is being used.

**Configuration
***Apollo
Access to an Apollo server is configured via an apolloConfig.yaml file. This file
contains entries for the base URL of the Apollo server and the user id that should
be used for access.

```
base_url: https://apollo-api.your-server.org
user: user123@some.host
```

The password for access to the Apollo server should be set in the apolloPass 
environment variable, e.g.

`ApolloPass=SomeS3cretPazzW0rd`

***Python
All requirements are listed in requirements.txt

`pip install requirements.txt`

**Usage
Obtain and install repo

```
git clone https://github.com/VEuPathDB/apollo_utils.git
python3 -m venv ./apolloFasta
. ./apolloFasta/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

```
Update the apolloConfig.yaml file with the correct defaults for your server
(see configuration section above)
Set the ApolloPass env variable

```
ApolloPass=vi3r3
export ApolloPass
```

Run code.

```
usage: apolloFasta.py [-h] --organism ORGANISM --gff GFF --pep PEP --logfile LOGFILE
                      [--sqlite SQLITE] --config CONFIG

Retrieve peptide fasta from VEuPath Apollo server for EBI patch build).

optional arguments:
  -h, --help           show this help message and exit
  --organism ORGANISM  Apollo organism to retrieve
  --gff GFF            output path of organism GFF file
  --pep PEP            output path of peptide file
  --logfile LOGFILE    path for logfile output
  --sqlite SQLITE      path for gffutils sqlite db
  --config CONFIG      path for yaml config file for Apollo connection details
```

* gff      - write the retrieved GFF3 file to disk
* logfile  - log of operations
* organism - name in Apollo orgaism to retrieve
* pep      - output fasta prpetide file
* confif   - apollo webservice config file

*** Example: GFF retrieval - in memory sqlite generated

python3 apolloFasta.py \
--gff culexq.gff \
--logfile culexq.log \
--organism "Culex quinquefasciatus JHB 2020 [Dec 04, 2020]" \
--pep culexq_peptide.fa \
--config apolloConfig.yaml

*** Example: GFF retrieval - file based sqlite generated
python3 apolloFasta.py \
--gff culexq.gff \
--logfile culexq.log \
--organism "Culex quinquefasciatus JHB 2020 [Dec 04, 2020]" \
--pep culexq_peptide.fa \
--config apolloConfig.yaml 
--sqlite ofcourse

*** Example: reuse of existing sqlite database
python3 apolloFasta.py \
--gff culexq.gff \
--logfile culexq.log \
--organism "Culex quinquefasciatus JHB 2020 [Dec 04, 2020]" \
--pep culexq_peptide.fa \
--config apolloConfig.yaml 
--sqlite ofcourse

existing database detected - using that file ofcourse
0 unedited genes detected
476 mRNA identified with parent gene status=Finished

