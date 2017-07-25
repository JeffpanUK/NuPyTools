##################
# ig.mak CB 05-03
# igtree toolbox v6
# build test programs for igtree
# gnumake 3.76
###########################

          
# define macros for used tools

IG = ig
CL = $(join $(CCOMP),\bin\cl)
LINK = $(join $(CCOMP),\bin\link)
MT = $(join $(CCOMP),\bin\mt)



# define macros for ig options

ifeq ($(wildcard ig.mk.local),) 
  include ig.mk
else 
  include ig.mk.local
endif


#target
ifeq ($(strip $(TGTEXT)),exe)
TGT = igtest.exe
else
TGT = igtest.dll
endif


#compiler options
ifeq ($(strip $(TGTEXT)),exe)
COPT = /nologo /MD /O2 /c /DWIN32 /I$(join $(CCOMP),\include) /Zm1000
LOPT = /OUT:$(TGT)
else
COPT = /nologo /MD /O2 /c /DWIN32 /I$(join $(CCOMP),\include) /Zm1000
LOPT = /OUT:$(TGT) /DLL /DEF:igtest.def
endif
LIBS = $(join $(CCOMP),\lib\msvcrt.lib) $(join $(CCOMP),\lib\oldnames.lib) $(join $(CCOMP),\lib\kernel32.lib)


#intermediate and generated files

OBJS1 = digtree.obj igtree.obj genmain.obj
GENSRC1 = digtree.c igtree.c genmain.c

ifeq ($(strip $(ALG)),nigtree)
OBJS2=$(OBJS1) igdist.obj
GENSRC= $(GENSRC1) igdist.c
else
OBJS2=$(OBJS1)
GENSRC = $(GENSRC1)
endif

ifeq ($(strip $(TGTEXT)),exe)
OBJS=$(OBJS2) main.obj
else
OBJS=$(OBJS2)
endif


#ig options
ifeq ($(strip $(ORDER)),)
IGOPT1 = -a $(ALG) -n $(NCAND) -f $(DATA) -w $(WILDCHAR)
else
IGOPT1 = -a $(ALG) -n $(NCAND) -f $(DATA) -e $(ORDER) -w $(WILDCHAR)
endif

ifeq ($(strip $(RF)),)
IGOPT2=$(IGOPT1)
else
IGOPT2=$(IGOPT1) -rf $(RF)
endif

ifeq ($(strip $(LF)),)
IGOPT3=$(IGOPT2)
else
IGOPT3=$(IGOPT2) -lf $(LF)
endif


ifeq ($(strip $(ACCENTABLE)),)
IGOPT=$(IGOPT3)
else
IGOPT=$(IGOPT3) -p $(ACCENTABLE)
endif

ifeq ($(wildcard ig.ini),) 
    INI =
else 
    INI = ig.ini
endif

DX = $(subst db,dx,$(DATA))

ifeq ($(wildcard $(DX)),) 
    XTRA =
else 
    XTRA = $(DX)
endif


ifeq ($(wildcard $(MT).exe),) 
	MTCMD =
else 
	MTCMD = $(MT) -manifest igtest.dll.manifest -outputresource:igtest.dll;2 >>link.log
endif

#rules
      
all : $(TGT)
	

$(TGT) : $(OBJS)
	@echo LINKING $(OBJS1) $(OBJS2) $(OBJS) $(TGT)
	@$(LINK) $(LIBS) $(LOPT) $(OBJS) >link.log
	@$(MTCMD) 


%.obj : %.c
	@echo COMPILING $< TO $@
	@echo $(CL) $(COPT) $< >>c.log
	@$(CL) $(COPT) $< >>c.log


genmain.c digtree.c igtree.c: $(DATA) ig.mk
$(GENSRC) : $(DATA) $(XTRA) $(INI)
	@echo ++++$(GENSRC)++++
	@echo LAUNCHING IG $(TGTEXT) $(IGOPT)
	@$(IG) $(IGOPT) >ig.log
	@-del c.log


clean :
	@-del digtree.c
	@-del igtree.c
	@-del igtree.h
	@-del genmain.c
	@-del igdist.c
	@-del *.obj
	@-del igtest.exe
	@-del igtest.exe.manifest
	@-del igtest.dll
	@-del igtest.dll.manifest
	@-del igtest.exp
	@-del igtest.lib
	@-del *.log
	@-del igtree.dat
	@-del igtree.map
	


