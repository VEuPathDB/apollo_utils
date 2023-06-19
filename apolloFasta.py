import requests
import sys
from sys import exit
import os
from os import path
from os import environ
import argparse
import logging
import yaml
import gffutils

def apolloDefaults( configFile:str ) -> dict :
    """
    supply default Apollo webservice values
    Args:
        configFile (str): yaml file containing Apollo connection defaults 
    Returns:
        dict: dictionary of Apollo web service defaults
    """

    if not environ.get('ApolloPass'):
        print( "you will need to define the Apollo password as an environment variable ApolloPass=" )
        sys.exit(0)

    with open(configFile, "r" ) as file:
        apollodefs = yaml.load( file , Loader=yaml.FullLoader )
        apollodefs.update( {'pass': environ.get('ApolloPass') } )
        apollodefs.update( {'header': {'Content-type': 'application/json'} } )

    return apollodefs


def getGFF( apollodb, gff_filepath, apolloDefs:dict ):
    """
    Retrieve GFF file for specified apollodb organism entry using the
    Apollo IOService/write() web service
    Args:
        apollodb (string): Apollodb entry (organism name)
        gff_filepath (string): GFF3 file output path
        apolloDefs (dict) : Apollo webservice defaults
    Returns:
        boolean: True/False result of web service and file write
        
    """

    url = apolloDefs.get('base_url') + '/IOService/write'
    params = {'username': apolloDefs.get('user'), 
              'password': apolloDefs.get('pass'),
              'organism': apollodb,
              'type': 'GFF3' , 
              'format': 'text', 
              'output': 'text' 
    }
    header = apolloDefs.get('header')


    try :
        r = requests.post( url, headers=header,  json=params )

        logging.info( "successfully retrieved GFF from Apollo for " +  apollodb )
        with open( gff_filepath , "w" )as foo:
            foo.write( r.text )
        foo.close
        return True

    except requests.HTTPError as e:
        msg = "failed to retrieve data from Apollo " + url  + e
        print( msg)
        logging.critical(msg)
        return False
    except ConnectionError as con_e :
        msg = "connection error for Apollo " + url + con_e
        print( msg)
        logging.critical(msg)
        return False
    except requests.Timeout as t_e :
        msg = "timeout for Apollo " + url + t_e
        print( msg)
        logging.critical(msg)
        return False

def getGFFids( db:gffutils.interface.FeatureDB ) -> dict:
    """
    Retrieve mapping of mRNA:CDS ids from GFF file

    Args:
        db (gffutils.interface.FeatureDB): gfutils FeatureDB handle

    Returns:
        dict: dict of mRNA:CDS ids
        
    """
    unedited = 0
    mrna2cds = {}

    for g in db.features_of_type('CDS'):
        cds = g.attributes
        id_list =  cds.get('ID')
        parent_list = cds.get('Parent')
        cds_id = id_list[0]
        parent_id = parent_list[0]

        parent_genes = db.parents(parent_id)
        for pg in parent_genes:
            p_attribs = pg.attributes
            status_list = p_attribs.get('status') if p_attribs.get('status') else 'unedited'
            status = status_list[0]
            name_list = p_attribs.get('Name') if p_attribs.get('Name') else ''
            name = name_list[0]

            if status == 'Finished' :
                vals = { 'mrna_id': parent_id , 'cds_id': cds_id, 'seq_id': g.seqid, 'name': name }
                mrna2cds.update( {parent_id: vals} )
            elif status == 'unedited':
                unedited += 1

    msg = str(unedited) + " unedited genes detected" 
    logging.info( msg )
    print( msg )

    return mrna2cds

def getPeptide( apollodb:str, mrna2cds:dict, apolloDefs:dict ) -> None :
    """
    Retrieve peptide file for mRNA entry using the Apollo IOService/write() web service
    Write fasta peptide file using the CDS id as the sequence identifier

    Args:
        apollodb (str) : name of Apollodb organism entry
        mrna2cds (dict) : dict of objects mapping mRNA:CDS:sequence ids
        apollodefs (dict) : dict of default Apolllo webservice values
    Returns:
        boolean: True/False result of web service and file write
        
    """

#curl -X POST -H "Content-Type: application/json" --data '{"username":"api@local.host","password":"GFERsVNiX5BQ09uN", "organismString":"Culex quinquefasciatus JHB 2020 [Dec 04, 2020]", "sequenceName":"CM027411.1", "featureName":"5448bf02-c6b6-4ec6-9800-519cb2b64640", "type":"peptide"  }' https://apollo-api.veupathdb.org/sequence/sequenceByName

    errors =[]

    for k in mrna2cds.keys():

        ob = mrna2cds.get(k)


        url = apolloDefs.get('base_url') + '/sequence/sequenceByName'
        params = {
            'username': apolloDefs.get('user'),
            'password': apolloDefs.get('pass'), 
            'organismString': apollodb,
            'sequenceName': ob.get('seq_id'), 
            'featureName': ob.get('mrna_id') , 
            'type': 'peptide', 
            'output': 'text' 
        }
        header = apolloDefs.get('header')


        try :
            r = requests.post( url, headers=header,  json=params )

            logging.info( "successfully retrieved peptide sequence from Apollo for " +  ob.get('cds_id') )
            ob.update({ 'peptide': r.text } )

        except requests.HTTPError as e:
            msg = "failed to retrieve data from Apollo " + url  + e
            errors.add( ob.get('mrna_id') )
            logging.critical(msg)

        except ConnectionError as con_e :
            msg = "connection error for Apollo " + url + con_e
            errors.add( ob.get('mrna_id') )
            logging.critical(msg)

        except requests.Timeout as t_e :
            msg = "timeout for Apollo " + url + t_e
            errors.add( ob.get('mrna_id') )
            logging.critical(msg)

    return errors


def main():
    parser = argparse.ArgumentParser(description='Retrieve peptide fasta from VEuPath Apollo server for EBI patch build).')
    parser.add_argument('--organism', help='Apollo organism to retrieve', required=True )
    parser.add_argument('--gff', help='output path of organism GFF file', required=True )
    parser.add_argument('--pep', help='output path of peptide file', required=True )
    parser.add_argument('--logfile', help='path for logfile output' , required=True )
    parser.add_argument('--sqlite', help='path for gffutils sqlite db' , required=False )
    parser.add_argument('--config', help='path for yaml config file for Apollo connection details' , required=True )

    args = parser.parse_args()

    if not os.path.exists( os.path.dirname(args.logfile)):
        print( "directory path for logfile is invalid - please fix this to proceed")
        sys.exit(1)

    logging.basicConfig( filename=args.logfile, level=logging.DEBUG, format='%(asctime)s %(message)s' )
    logging.info('start')
    logging.info('organism = ' + args.organism )
    logging.info('output gff = ' + args.gff )
    logging.info('output fasta = ' + args.pep )

    ap_defs = apolloDefaults( args.config )
    
    database_filename = args.sqlite if args.sqlite else ':memory:'

    if os.path.exists( database_filename ):
        msg = "existing database detected - using that file " + database_filename
        print(msg)
        logging.info(msg)
        db = gffutils.FeatureDB( database_filename)
    else:
        msg = "no existing database found - downloading GFF from Apollo and building db"
        print(msg)
        logging.info(msg)
        getGFF( args.organism, args.gff, ap_defs )
        db = gffutils.create_db( args.gff, database_filename, merge_strategy='create_unique')


    mrna2cds = getGFFids(db)

    print( str(len( mrna2cds ) ) + " mRNA identified with parent gene status=Finished")
    errors = getPeptide( args.organism, mrna2cds, ap_defs)

    if len(errors) > 0 :
        print( str( len(errors)) + " errors encountered in peptide fasta retrieval - see logfile")

    logging.info( "writing peptide sequences to file" + args.pep )
    with open( args.pep , "w" ) as fh:

        for k in mrna2cds.keys():
            o = mrna2cds.get(k)
            fh.write( ">" + o.get('cds_id') + " | " + o.get('name') +  "\n" )
            fh.write( o.get('peptide') + "\n" )
    fh.close()

    logging.info('stop')

############################
        
if __name__ == '__main__':
    main()
    exit(0)
