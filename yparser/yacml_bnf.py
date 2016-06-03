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

from pyparsing import *
from lxml import etree

# YACML BNF.
yacmlBNF_ = None
yacmlXML_ = etree.Element('yacml')
currXMLElem_ = None

pIdentifier = pyparsing_common.identifier
COMPT_BEGIN = Keyword("compartment")
HAS = Keyword("has")
IS = Keyword( "is" )
END = Keyword("end") + Optional( pIdentifier )
SPECIES = Keyword( "species" ) | Keyword( "pool" )
REACTION = Keyword( "reaction" ) | Keyword( "reac" )
GEOMETRY = Keyword("cylinder") | Keyword( "cube" ) | Keyword( "Spine" )

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

pNumVal = pyparsing_common.numeric | pyparsing_common.integer \
    | pyparsing_common.number | Regex( r'\.\d+' )
pNumVal.setParseAction( lambda t: float(t[0]) )

# Parser for key = value expression.
pValue = ( pNumVal | pIdentifier | quotedString() )

pKeyVals = pIdentifier + EQUAL + pValue 

pKeyValList = LBRAC + delimitedList( pKeyVals ) + RBRAC
pSpeciesExpr = SPECIES + pSpeciesName + pKeyValList + pEOS

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

pVariableExpr = pKeyVals + pEOS

# Valid YAXML expression
pYACMLExpr = pSpeciesExpr | pReacExpr | pVariableExpr 

pGeometry = GEOMETRY + Optional( pKeyValList )

pCompartmentBody = OneOrMore( pYACMLExpr )
pCompartment = COMPT_BEGIN + pComptName + IS + pGeometry + HAS \
        + pCompartmentBody + END

yacmlBNF_ = OneOrMore( pCompartment) 
yacmlBNF_.ignore( javaStyleComment )

def main( ):
    print('Testing ' )
    print pKeyVals.parseString( 'AV = 6.023e23' )
    print pCompartment.parseString( 
        '''compartment PSD has
            AV = 6.023e23;
        end PSD
        '''
        )
    print pNumVal.parseString( "1.5111" )
    print pNumVal.parseString( ".5111" )
    print pNumVal.parseString( "-1.35e13" )
    print pNumVal.parseString( "1e-2" )
    print pReacExpr.parseString( '2a + 3b <- r0 -> c + 9d;' )

if __name__ == '__main__':
    main()
