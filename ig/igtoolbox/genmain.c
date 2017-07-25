/*
 * genmain.c -- 
 *
 *   Last build: Aug 31 2016 12:58:52
*/

#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include "igtree.h"

static char gszOutput[640];

char* igtest (char * szInput)
{
char f0[256];
char f1[256];
char f2[256];
char f3[256];
char f4[256];
char f5[256];
featTreeStruct f;
char output[256];


if (sscanf(szInput,"%s %s %s %s %s %s",f0,f1,f2,f3,f4,f5)!=6)
    return NULL;
else
{
    f.f0=f0;
    f.f1=f1;
    f.f2=f2;
    f.f3=f3;
    f.f4=f4;
    f.f5=f5;
    strcpy(output,igtree(&f));
    sprintf(gszOutput,"%s",output);
    return gszOutput;
}
}
