/*
 * igtree.c -- 
 *
 *   Last build: 07/14/17 17:25:32
*/

#include "lhdefine.h"

#include <string.h>
#if !defined(_LH_QSORT_)
#include <stdlib.h>
#endif

#include "igtree.h"

#if !defined(_LH_QSORT_)
#define  lh_qsort qsort
#else
void lh_qsort(void  *abase,size_t nmemb,size_t size,int (*compar)(const void *, const void *));
#endif

#define to_int(arg1,arg2) (LH_U32)(arg1<<16|arg2)

extern const char * dstring[];
extern const LH_U32 table0[];
extern const LH_U32 table1[];
extern const LH_U32 table2[];
extern const LH_U32 table3[];
extern const LH_U32 table4[];
extern const LH_U32 table5[];
extern const LH_U32 table6[];

char* igtree(featTreeStruct *f)
{
LH_S32 i,j,nrpath,oldnrpath;
LH_U32 *p,*lim,*defval;
LH_U8 found;
LH_U32 *path[100],*oldpath[100];

defval=NULL;
nrpath=1;
path[0]=(LH_U32 *)table0;

/*going through table0*/
for (i=0;i<nrpath;i++)
  oldpath[i]=path[i];
oldnrpath=nrpath;
nrpath=0;
found=0;
for (j=0;j<oldnrpath;j++)
{
  p=oldpath[j];
  lim=p+2*(*p);
  for (p++;p<lim;p+=2)
  {
      if (*p==USHRT_MAX)
      {
          path[nrpath]=(LH_U32 *)table1;
          while (*(p+1)==USHRT_MAX){path[nrpath]=(LH_U32 *)path[nrpath]+*(p+1);p++;lim++;}
          path[nrpath]=(LH_U32 *)path[nrpath]+*(p+1);nrpath++;
      }
      else if (strcmp(f->f0, dstring[*p])==0)
      {
          path[nrpath]=(LH_U32 *)table1;
          while (*(p+1)==USHRT_MAX){path[nrpath]=(LH_U32 *)path[nrpath]+*(p+1);p++;lim++;}
          path[nrpath]=(LH_U32 *)path[nrpath]+*(p+1);nrpath++;
          found=1;
      }
    while (*(p+1)==USHRT_MAX){p++;lim++;}
  }
  if (j==0 && found==0 && defval==NULL)
    defval=p;
}
if (found==0 && nrpath==0)
return dstring[*defval];

/*going through table1*/
for (i=0;i<nrpath;i++)
  oldpath[i]=path[i];
oldnrpath=nrpath;
nrpath=0;
found=0;
for (j=0;j<oldnrpath;j++)
{
  p=oldpath[j];
  lim=p+2*(*p);
  for (p++;p<lim;p+=2)
  {
      if (*p==USHRT_MAX)
      {
          path[nrpath]=(LH_U32 *)table2;
          while (*(p+1)==USHRT_MAX){path[nrpath]=(LH_U32 *)path[nrpath]+*(p+1);p++;lim++;}
          path[nrpath]=(LH_U32 *)path[nrpath]+*(p+1);nrpath++;
      }
      else if (strcmp(f->f1, dstring[*p])==0)
      {
          path[nrpath]=(LH_U32 *)table2;
          while (*(p+1)==USHRT_MAX){path[nrpath]=(LH_U32 *)path[nrpath]+*(p+1);p++;lim++;}
          path[nrpath]=(LH_U32 *)path[nrpath]+*(p+1);nrpath++;
          found=1;
      }
    while (*(p+1)==USHRT_MAX){p++;lim++;}
  }
  if (j==0 && found==0 && defval==NULL)
    defval=p;
}
if (found==0 && nrpath==0)
return dstring[*defval];

/*going through table2*/
for (i=0;i<nrpath;i++)
  oldpath[i]=path[i];
oldnrpath=nrpath;
nrpath=0;
found=0;
for (j=0;j<oldnrpath;j++)
{
  p=oldpath[j];
  lim=p+2*(*p);
  for (p++;p<lim;p+=2)
  {
      if (*p==USHRT_MAX)
      {
          path[nrpath]=(LH_U32 *)table3;
          while (*(p+1)==USHRT_MAX){path[nrpath]=(LH_U32 *)path[nrpath]+*(p+1);p++;lim++;}
          path[nrpath]=(LH_U32 *)path[nrpath]+*(p+1);nrpath++;
      }
      else if (strcmp(f->f2, dstring[*p])==0)
      {
          path[nrpath]=(LH_U32 *)table3;
          while (*(p+1)==USHRT_MAX){path[nrpath]=(LH_U32 *)path[nrpath]+*(p+1);p++;lim++;}
          path[nrpath]=(LH_U32 *)path[nrpath]+*(p+1);nrpath++;
          found=1;
      }
    while (*(p+1)==USHRT_MAX){p++;lim++;}
  }
  if (j==0 && found==0 && defval==NULL)
    defval=p;
}
if (found==0 && nrpath==0)
return dstring[*defval];

/*going through table3*/
for (i=0;i<nrpath;i++)
  oldpath[i]=path[i];
oldnrpath=nrpath;
nrpath=0;
found=0;
for (j=0;j<oldnrpath;j++)
{
  p=oldpath[j];
  lim=p+2*(*p);
  for (p++;p<lim;p+=2)
  {
      if (*p==USHRT_MAX)
      {
          path[nrpath]=(LH_U32 *)table4;
          while (*(p+1)==USHRT_MAX){path[nrpath]=(LH_U32 *)path[nrpath]+*(p+1);p++;lim++;}
          path[nrpath]=(LH_U32 *)path[nrpath]+*(p+1);nrpath++;
      }
      else if (strcmp(f->f3, dstring[*p])==0)
      {
          path[nrpath]=(LH_U32 *)table4;
          while (*(p+1)==USHRT_MAX){path[nrpath]=(LH_U32 *)path[nrpath]+*(p+1);p++;lim++;}
          path[nrpath]=(LH_U32 *)path[nrpath]+*(p+1);nrpath++;
          found=1;
      }
    while (*(p+1)==USHRT_MAX){p++;lim++;}
  }
  if (j==0 && found==0 && defval==NULL)
    defval=p;
}
if (found==0 && nrpath==0)
return dstring[*defval];

/*going through table4*/
for (i=0;i<nrpath;i++)
  oldpath[i]=path[i];
oldnrpath=nrpath;
nrpath=0;
found=0;
for (j=0;j<oldnrpath;j++)
{
  p=oldpath[j];
  lim=p+2*(*p);
  for (p++;p<lim;p+=2)
  {
      if (*p==USHRT_MAX)
      {
          path[nrpath]=(LH_U32 *)table5;
          while (*(p+1)==USHRT_MAX){path[nrpath]=(LH_U32 *)path[nrpath]+*(p+1);p++;lim++;}
          path[nrpath]=(LH_U32 *)path[nrpath]+*(p+1);nrpath++;
      }
      else if (strcmp(f->f4, dstring[*p])==0)
      {
          path[nrpath]=(LH_U32 *)table5;
          while (*(p+1)==USHRT_MAX){path[nrpath]=(LH_U32 *)path[nrpath]+*(p+1);p++;lim++;}
          path[nrpath]=(LH_U32 *)path[nrpath]+*(p+1);nrpath++;
          found=1;
      }
    while (*(p+1)==USHRT_MAX){p++;lim++;}
  }
  if (j==0 && found==0 && defval==NULL)
    defval=p;
}
if (found==0 && nrpath==0)
return dstring[*defval];

/*going through table5*/
for (i=0;i<nrpath;i++)
  oldpath[i]=path[i];
oldnrpath=nrpath;
nrpath=0;
found=0;
for (j=0;j<oldnrpath;j++)
{
  p=oldpath[j];
  lim=p+2*(*p);
  for (p++;p<lim;p+=2)
  {
      if (*p==USHRT_MAX)
      {
          path[nrpath]=(LH_U32 *)table6;
          while (*(p+1)==USHRT_MAX){path[nrpath]=(LH_U32 *)path[nrpath]+*(p+1);p++;lim++;}
          path[nrpath]=(LH_U32 *)path[nrpath]+*(p+1);nrpath++;
      }
      else if (strcmp(f->f5, dstring[*p])==0)
      {
          path[nrpath]=(LH_U32 *)table6;
          while (*(p+1)==USHRT_MAX){path[nrpath]=(LH_U32 *)path[nrpath]+*(p+1);p++;lim++;}
          path[nrpath]=(LH_U32 *)path[nrpath]+*(p+1);nrpath++;
          found=1;
      }
    while (*(p+1)==USHRT_MAX){p++;lim++;}
  }
  if (j==0 && found==0 && defval==NULL)
    defval=p;
}
if (found==0 && nrpath==0)
return dstring[*defval];

/*going through table6*/
return dstring[*path[0]];

}
