#!/bin/bash

#compiling the Sum.g4 in java files
java -jar "antlr-4.7.2-complete.jar" -no-listener -visitor Summer.g4

#exporting the class path
export CLASSPATH=".:antlr-4.7.2-complete.jar:$CLASSPATH"

#compiling the .java generated from Sum.g4 with MyParser.java and AddVisitor.java
javac *.java

test_name="test1.sm"

#execute the implemented visitor
#for i in 1 2 3 4 5 6 7 8; do
(cat $test_name | java MyParser) > result.ll

# BREAK LINE ON SED
#sed -i 's/|END|/\n/g' result.ll

llc result.ll

gcc result.s Printer.c -o printer

./printer


#sed -i 's/S\+/\n&/g' result0.txt
#sed -i '1d' result0.txt

# PRINT TREE

# printing graphical tree for test number 7
#cat $test_name | java org.antlr.v4.gui.TestRig Summer root -gui
