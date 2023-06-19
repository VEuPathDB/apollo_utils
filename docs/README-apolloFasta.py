*README - apolloFasta.py
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

The GFF file can be saved to disk if desired (see usage) - if a file with the
existing name is found this will be used instead of downloading the GFF file from
source. Check stdout and the logfile for the details of which source is being used.

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

**Typical script usage

```
python3 apolloFasta.py \
 --gff speciesX.gff \
 --logfile speciesX.log \
 --organism "speciesX" \
 --pep peptide.fa \
 --config apolloConfig.yaml
```

* gff      - write the retrieved GFF3 file to disk
* logfile  - log of operations
* organism - name in Apollo orgaism to retrieve
* pep      - output fasta prpetide file
* confif   - apollo webservice config file
