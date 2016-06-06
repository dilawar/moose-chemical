"""yacml_bnf.py: 

BNFC grammar of YACML.

"""
    
__author__           = "Dilawar Singh"
__copyright__        = "Copyright 2016, Dilawar Singh"
__credits__          = ["NCBS Bangalore"]
__license__          = "GNU GPL"
__version__          = "1.0.0"
__maintainer__       = "Dilawar Singh"
__email__            = "dilawars@ncbs.res.in"
__status__           = "Development"

from .pyparsing import *
import networkx as nx

# Function to generate graph.
network_ = nx.MultiDiGraph( name = 'yacml' )

def add_species( tokens, **kwargs ):
    return None
    print('Adding %s' % tokens )

def add_recipe( tokens, **kwargs):
    return None
    print( 'Adding recipe %s' % tokens )

# YACML BNF.
yacmlBNF_ = None
currXMLElem_ = None

pIdentifier = pyparsing_common.identifier
COMPT_BEGIN = Keyword("compartment")
RECIPE_BEGIN = Keyword( "recipe" )
HAS = Keyword("has")
IS = Keyword( "is" )
END = Keyword("end") + Optional( pIdentifier )
SPECIES = Keyword( "species" ) | Keyword( "pool" ) | Keyword( "enzyme" )
REACTION = Keyword( "reaction" ) | Keyword( "reac" ) | Keyword( "enz_reac" )
GEOMETRY = Keyword("cylinder") | Keyword( "cube" ) | Keyword( "Spine" )
VAR = Keyword( "var" ) 
CONST = Keyword( "const" )

pComptName = pIdentifier
pSpeciesName = pIdentifier
pEOS = Literal( ";" ) 
LBRAC = Literal("[")
RBRAC = Literal("]")
LCBRAC = Literal("{")
RCBRAC = Literal("}")
EQUAL = Literal('=')
RREAC = Literal( "->" )
LREAC = Literal( "<-" )

pNumVal = pyparsing_common.numeric \
        | pyparsing_common.integer \
        | pyparsing_common.number | Regex( r'\.\d+' )

pNumVal.setParseAction( lambda t: float(t[0]) )

# Parser for key = value expression.
pValue = ( pNumVal | pIdentifier | quotedString() )

pKeyVals = pIdentifier + EQUAL + pValue 

pKeyValList = LBRAC + Group( delimitedList( pKeyVals )) + RBRAC
pSpeciesExpr = SPECIES + Group( pSpeciesName + pKeyValList) + pEOS
pSpeciesExpr.setParseAction( add_species )

# Species name with stoichiometry coefficient e.g 2a + 3b 
pStoichNumber = Optional(Word(nums), '1') 
pStoichNumber.setParseAction( lambda x: int(x[0] ) )
pSpeciesNameWithStoichCoeff = Group( pStoichNumber + pSpeciesName )

# Expression for reactions.
pSubstrasteList = Group( delimitedList( pSpeciesNameWithStoichCoeff, '+' ) )
pProductList = Group( delimitedList( pSpeciesNameWithStoichCoeff, '+' ) )

pReacName = pIdentifier
pReacDecl = REACTION + pReacName + pKeyValList + pEOS
pReacSetup = pSubstrasteList + LREAC + pReacName + RREAC + pProductList + pEOS
pReacExpr = pReacDecl | pReacSetup 

pTypeExpr = CONST | VAR
pVariableExpr = Optional(pTypeExpr) + pKeyVals + pEOS

# Name of the recipe
pRecipeName = pIdentifier

# Recipe instantiation expression
pRecipeType = pIdentifier 
pInstExpr = pRecipeType + pRecipeName + END

# Valid YAXML expression
pYACMLExpr = pSpeciesExpr | pReacExpr | pVariableExpr | pInstExpr
pGeometry = GEOMETRY + Optional( pKeyValList )

# Compartment 
pCompartmentBody = OneOrMore( pYACMLExpr )
pCompartment = COMPT_BEGIN + pComptName + IS + pGeometry + HAS \
        + pCompartmentBody + END

# Recipe 
pRecipeBody = Group( OneOrMore( pYACMLExpr ) )
pRecipeBody.setResultsName( 'recepe_body' )
pRecipe =  RECIPE_BEGIN + pRecipeName + IS  + pRecipeBody + END 
pRecipe.setParseAction( add_recipe )

yacmlBNF_ = OneOrMore( pRecipe | pCompartment  ) 
yacmlBNF_.ignore( javaStyleComment )

if __name__ == '__main__':
    main()
