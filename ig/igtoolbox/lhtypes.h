#ifndef __LHTYPES_H
#define __LHTYPES_H
/* ****************************************************************************
**                   Lernout & Hauspie Speech Products N.V. (TM)             **
** ************************************************************************* */

/* *************************** COPYRIGHT INFORMATION **************************
** This program contains proprietary information which is a trade secret of  **
** Lernout & Hauspie Speech Products N.V. (TM) and also is protected as an   **
** unpublished  work under applicable Copyright laws. Recipient is to retain **
** this program in confidence and is not permitted to use or make copies     **
** thereof other than as permitted in a written agreement with Lernout &     **
** Hauspie Speech Products N.V. (TM).                                        **
** All rights reserved. Company confidential.                                **
** ************************************************************************* */

/* ****************************************************************************
** Project       : none
** Module        : none
** File name     : lhtypes.h
** Description   : This file sets the standard l&h types. 
**                 It will be maintained for all projects.
**                 Compiler preprocessor defines are used to differentiate
**                 between several platforms.   
** Reference(s)  : 
** Status        : very first version
** ****************************************************************************
** History
** Date       Rev.  By         Comment
**   7/22/99    0    jde        Created
** ************************************************************************* */

/* **************************** COMPILE DIRECTIVES ****************************
** 
** ************************************************************************* */

/* ****************************************************************************
**   HEADER (INCLUDE) SECTION                                                **
** ************************************************************************* */

/* none */


/* ****************************************************************************
**   MACROS                                                                  **
** ************************************************************************* */

/* ****************************************************************************
**   TYPE DEFINITIONS                                                        **
** ************************************************************************* */

#ifdef WIN32

#define LH_EXPORT __declspec (dllexport)

typedef unsigned char     LH_U8;
typedef signed char	      LH_S8;
typedef unsigned short    LH_U16;
typedef signed short	    LH_S16; 
typedef unsigned long     LH_U32;
typedef signed long	      LH_S32;
typedef float             LH_F32;

#define LH_S16_MAX   (((LH_U16)-1) >> 1)    /* 0111 1111 1111 1111 */ 
#define LH_S16_MIN   (~LH_S16_MAX)          /* 1000 0000 0000 0000 */ /*  The following MAX/MIN definitions require that the machine*/
#define LH_U16_MAX   ((LH_U16)-1)           /* 1111 1111 1111 1111 */ /*  represents a negative number (-x), x > 0 internally by the*/
#define LH_U16_MIN   (~LH_U16_MAX)                                    /*  2-complement of x = 2^M - x, where M is the number of bits*/
                                                                   /*  used to represent numbers of the type of x.*/
#define LH_S32_MAX   (((LH_U32)-1) >> 1)
#define LH_S32_MIN   (~LH_S32_MAX)
#define LH_U32_MAX   ((LH_U32)-1)
#define LH_U32_MIN   (~LH_U32_MAX)

#define LH_S8_MAX    (((LH_U8)-1) >> 1)     /* 0111 1111  */
#define LH_S8_MIN    (~LH_S8_MAX)           /* 1000 0000  */
#define LH_U8_MAX    ((LH_U8)-1)            /* 1111 1111  */
#define LH_U8_MIN    (~LH_U8_MAX)

#if APPROVED
#define LH_F32_MAX              3.402823466e+38
#define LH_F32MIN               1.175494351e-38
#define LH_F32MAX_10_EXP        38
#endif

#endif


#ifdef IDT_XIOX
#define LH_EXPORT
typedef unsigned char     LH_U8;
typedef signed char	      LH_S8;
typedef unsigned short    LH_U16;
typedef signed short	    LH_S16; 
typedef unsigned long     LH_U32;
typedef signed long	      LH_S32;
typedef float             LH_F32;
#define LH_S16_MAX   (((LH_U16)-1) >> 1)    /* 0111 1111 1111 1111 */ 
#define LH_S16_MIN   (~LH_S16_MAX)          /* 1000 0000 0000 0000 */ /*  The following MAX/MIN definitions require that the machine*/
#define LH_U16_MAX   ((LH_U16)-1)           /* 1111 1111 1111 1111 */ /*  represents a negative number (-x), x > 0 internally by the*/
#define LH_U16_MIN   (~LH_U16_MAX)                                    /*  2-complement of x = 2^M - x, where M is the number of bits*/
                                                                   /*  used to represent numbers of the type of x.*/
#define LH_S32_MAX   (((LH_U32)-1) >> 1)
#define LH_S32_MIN   (~LH_S32_MAX)
#define LH_U32_MAX   ((LH_U32)-1)
#define LH_U32_MIN   (~LH_U32_MAX)

#define LH_S8_MAX    (((LH_U8)-1) >> 1)     /* 0111 1111  */
#define LH_S8_MIN    (~LH_S8_MAX)           /* 1000 0000  */
#define LH_U8_MAX    ((LH_U8)-1)            /* 1111 1111  */
#define LH_U8_MIN    (~LH_U8_MAX)

#endif

#ifdef ACU_LAB
#define LH_EXPORT
typedef unsigned char     LH_U8;
typedef signed char	      LH_S8;
typedef unsigned short    LH_U16;
typedef signed short	    LH_S16; 
typedef unsigned long     LH_U32;
typedef signed long	      LH_S32;
typedef float             LH_F32;
#define LH_S16_MAX   (((LH_U16)-1) >> 1)    /* 0111 1111 1111 1111 */ 
#define LH_S16_MIN   (~LH_S16_MAX)          /* 1000 0000 0000 0000 */ /*  The following MAX/MIN definitions require that the machine*/
#define LH_U16_MAX   ((LH_U16)-1)           /* 1111 1111 1111 1111 */ /*  represents a negative number (-x), x > 0 internally by the*/
#define LH_U16_MIN   (~LH_U16_MAX)                                    /*  2-complement of x = 2^M - x, where M is the number of bits*/
                                                                   /*  used to represent numbers of the type of x.*/
#define LH_S32_MAX   (((LH_U32)-1) >> 1)
#define LH_S32_MIN   (~LH_S32_MAX)
#define LH_U32_MAX   ((LH_U32)-1)
#define LH_U32_MIN   (~LH_U32_MAX)

#define LH_S8_MAX    (((LH_U8)-1) >> 1)     /* 0111 1111  */
#define LH_S8_MIN    (~LH_S8_MAX)           /* 1000 0000  */
#define LH_U8_MAX    ((LH_U8)-1)            /* 1111 1111  */
#define LH_U8_MIN    (~LH_U8_MAX)
#endif



typedef enum{
	LH_FALSE=0,
	LH_TRUE=1
}LH_BOOL;


/* ****************************************************************************
**   EXTERNAL DATA (+ meaning)                                               **
** ************************************************************************* */

/* none */


/* ****************************************************************************
**   GLOBAL FUNCTION PROTOTYPES                                              **
** ************************************************************************* */


/* none */

/* ****************************************************************************
**   END                                                                     **
** ************************************************************************* */
#endif /* #ifndef __LHTYPES_H */
