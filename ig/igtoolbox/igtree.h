/*
 * igtree.h -- 
 *
 *   Last build: 07/14/17 17:25:32
*/

#if !defined(IGTREE_H_INCLUDED)
#define IGTREE_H_INCLUDED
#include "lhtypes.h"

#include "context.h"

typedef struct featTreeStruct {
char* f0;
char* f1;
char* f2;
char* f3;
char* f4;
char* f5;
} featTreeStruct;

typedef struct candTreeStruct {
char* c0;
} candTreeStruct;

char * igtree(featTreeStruct * f);

#endif
