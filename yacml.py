"""yacml.py: 

"""
    
__author__           = "Dilawar Singh"
__copyright__        = "Copyright 2015, Dilawar Singh and NCBS Bangalore"
__credits__          = ["NCBS Bangalore"]
__license__          = "GNU GPL"
__version__          = "1.0.0"
__maintainer__       = "Dilawar Singh"
__email__            = "dilawars@ncbs.res.in"
__status__           = "Development"


import yacml2moose
import config
import moose.print_utils as pu
import moose
from yparser import yparser
from yparser import pre_processor

logger_ = config.logger_

def loadYACML(yacml_file, **kwargs):
    """loadYACML Load YACML model into MOOSE.

    :param modelFile: Path of model.
    :param **kwargs:
    """
    networkxG = yacml_to_networkx( yacml_file )
    # Once graph is preprocess, load it in moose.
    model = networkx2moose( networkxG, **kwargs)
    return model

def yacml_to_networkx( yacml_file, **kwargs ):
    """yacml_to_networkx Convert yacml model to equivalent networkx graph.

    :param yacml_file: path of yacml file.
    """
    nxG = yparser.create_graph( yacml_file, **kwargs )
    pre_processor.pre_process( nxG )
    return nxG

def networkx2moose( nxg, **kwargs ):
    model = yacml2moose.DotModel( nxg, **kwargs )
    return model

def setup_solver( compartment, solver, **kwargs ):
    """setup_solver Use a given solver 'solver' on compartment 'compartment'

    :param compartment: moose.Compartment type.
    :param solver: deterministic or stochastic
    :param **kwargs: TODO
    """
    pu.info("Adding a solver %s to compartment %s" % (solver, compartment.path))
    s = None
    enableDiffusion = kwargs.get('enable_diffusion', False)

    if enableDiffusion:
        pu.info('Diffusion in compartment %s is enabled' % compartment.name )


    if solver == "deterministic":
        pu.info('[INFO] Using deterministic solver')
        s = moose.Ksolve('%s/ksolve' % compartment.path)
    elif solver == 'stochastic':
        pu.info('Using stochastic solver')
        s = moose.Gsolve('%s/gsolve' % compartment.path)
        pu.info("Setting up useClockedUpdate = True")
        s.useClockedUpdate = True
    else:
        msg = "Unknown solver: %s. Using 'deterministic' solver." % solver
        msg += "\n Choices: 'stochastic' and 'deterministic' (default)'"
        pu.warn(msg)
        s = moose.Ksolve('%s/ksolve' % compartment.path)

    if enableDiffusion:
        pu.info( 'Setting up diffusion solver' )
        dsolvePath = '%s/dsolve' % compartment.path
        if moose.exists( dsolvePath ):
            mu.warn( 'Already exists %s. Doing nothing. ' % dsolvePath )
        else:
            dsolve = moose.Dsolve( '%s/dsolve' % compartment.path )

    stoich = moose.Stoich('%s/stoich' % compartment.path)
    stoich.ksolve = s
    if enableDiffusion:
        pu.info('Added diffusion solver')
        stoich.dsolve = dsolve

    # NOTE: must be set before compartment or path.
    stoich.compartment = compartment
    stoich.path = '%s/##' % compartment.path
    return stoich


def main(args):
    """Main entry function
    """
    config.args_ = args
    modelFile = args['model_file']
    if args['solver'] == 'moose':
        model = yacml2moose.DotModel(modelFile)
        model.run(args)
        return model
    elif args['solver'] == "scipy":
        logger_.error("Solver scipy is still not supported")
    else:
        logger_.error("Invalid solver: %s " % args['solver'])
    return None

if __name__ == '__main__':
    import argparse
    # Argument parser.
    description = '''YACML: Yet Another Chemical Markup Language'''
    argp = argparse.ArgumentParser(description=description)
    argp.add_argument('--model_file', '-f'
            , required = True
            , type = str
            , help = 'Model file'
            )
    
    argp.add_argument('--sim_time', '-st'
            , metavar='variable'
            , default = 10.0
            , type = float
            , help = 'A generic option'
            )

    argp.add_argument('--solver', '-s'
            , default = 'moose'
            , type = str
            , help = "Which solver to use: moose | scipy"
            )

    argp.add_argument('--outfile', '-o'
            , default = None
            , type = str
            , help = "Name of the plot file"
            )

    argp.add_argument('--log', '-l'
            , default = 'warning'
            , type = str
            , help = 'Debug levels: [debug, info, warning, error, critical]'
            )

    class Args: pass 
    args = Args()
    argp.parse_args(namespace=args)
    main(vars(args))
