#!/bin/bash

sed -i "/TEST/d" $1

sed -i "s/\bVOID\b/void/g" $1
sed -i "s/\bINT\b/int/g" $1
sed -i "s/\bFLOAT\b/float/g" $1
sed -i "s/\bCHAR\b/char/g" $1
sed -i "s/\bLONG\b/long/g" $1
sed -i "s/\bDOUBLE\b/double/g" $1
sed -i "s/\bENUM\b/enum/g" $1

sed -i "s/\bSIGNED\b/signed/g" $1
sed -i "s/\bUNSIGNED\b/unsigned/g" $1

sed -i "s/\bSTRUCT\b/struct/g" $1
sed -i "s/\bTYPEDEF\b/typedef/g" $1

sed -i "s/\bIF\b/if/g" $1
sed -i "s/\bELSE\b/else/g" $1
sed -i "s/\bFOR\b/for/g" $1
sed -i "s/\bDO\b/do/g" $1
sed -i "s/\bWHILE\b/while/g" $1
sed -i "s/\bSWITCH\b/switch/g" $1
sed -i "s/\bCASE\b/case/g" $1
sed -i "s/\bBREAK\b/break/g" $1
sed -i "s/\bCONTINUE\b/continue/g" $1
sed -i "s/\bDEFAULT\b/default/g" $1

sed -i "s/\bUNION\b/union/g" $1
sed -i "s/\bSTATIC\b/static/g" $1
sed -i "s/\bVOLATILE\b/volatile/g" $1
sed -i "s/\bSIZEOF\b/sizeof/g" $1
sed -i "s/\bRETURN\b/return/g" $1

