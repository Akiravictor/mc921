#!/bin/bash
set -x
#compiling the Sum.g4 in java files
java -jar "antlr-4.7.2-complete.jar" -no-listener -visitor Summer.g4
#exporting the class path
export CLASSPATH=".:antlr-4.7.2-complete.jar:$CLASSPATH"
#compiling the .java generated from Sum.g4 with MyParser.java and AddVisitor.java
javac *.java

java MyParser < test1.sm > result1.out
java MyParser < test2.sm > result2.out
java MyParser < test3.sm > result3.out
java MyParser < test4.sm > result4.out
java MyParser < test5.sm > result5.out
java MyParser < test6.sm > result6.out
java MyParser < test7.sm > result7.out
java MyParser < test8.sm > result8.out

diff result1.out result1.txt
diff result2.out result2.txt
diff result3.out result3.txt
diff result4.out result4.txt
diff result5.out result5.txt
diff result6.out result6.txt
diff result7.out result7.txt
diff result8.out result8.txt
