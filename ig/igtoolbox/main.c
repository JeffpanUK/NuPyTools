#include <stdio.h>
#include <string.h>
#include <stdlib.h>

extern char * igtest (char * szInput);

void PrintOutput (char *szOutput)
{
char *ptr;

if (strchr (szOutput, ' ') == NULL) // no spaces --> result comes from an igtree, not a nigtree
    printf ("%s\n",szOutput);
else
{
    ptr=strtok(szOutput, " ");
    while (ptr!=NULL)
        {
            printf ("Candidate %s:", ptr);
            ptr=strtok(NULL, " ");
            if (ptr != NULL) 
                { printf ("\t%s", ptr);
                  ptr=strtok(NULL, " ");
                  if (ptr != NULL)
                  {         
                    printf ("\t%s\n", ptr);
                    ptr=strtok(NULL, " ");  
                  }
                }
        }
}

}

void main (int argc, char **argv)
{
char    input[256];
long    position;
int     argno;
char    *szOutput;

if (argc==1)
{
    position=ftell(stdin);
    do
    {
        if (position==-1)
            fprintf(stderr,"\nigtest:> ");
        if (fgets ((char *)input, 256, stdin)!=NULL) 
        {
            if (input[strlen((char *)input)-1] == '\n')
                (input[strlen((char *)input)-1] = '\0');
            if (strlen (input) == 0)\
                break;
            szOutput=igtest (input);
            if (szOutput != NULL)
                PrintOutput (szOutput);                
            else 
                printf("wrong input format\n");
        } 
        else 
            break;
    }
    while (1);
}
else
{
    strcpy(input,"");
    for (argno = 1; argno < argc; argno++)
    {
        strcat(input,argv[argno]);
        strcat(input," ");
    }
    input[strlen((char *)input)-1] = '\0';
    szOutput=igtest (input);
    if (szOutput != NULL)
        PrintOutput (szOutput);    
    else 
        printf("wrong input format\n");

}
exit(0);
}

