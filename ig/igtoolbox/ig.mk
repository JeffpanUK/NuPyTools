##################
# ig.mk CB 05-03 
# igtree toolbox v6
# configuration file for ig.mak
###########################


# define macros for ig options

CCOMP = \\gh-srvfile03\Realvoice\tools\VoiceBuild\VC
MAIN = genmain  # root of main c source file
DATA = igbase.db   # database
ALG =  grtree	# prediction algorithm
NCAND = 1	# number of candidates
#ORDER = 1 2 
TGTEXT = exe	# build model
WILDCHAR = *	# wildchar to be used in rules
ACCENTABLE = " CD FW JJ JJR JJS LS NN NNS NNP NNPS NNT PDT PRPH RB RBH RBR RBS RBT RBL RBN RP SYM UH VB VBD VBG VBN VBP VBZ VD VDD VDG VDN VDP VDZ WRB UNK "
