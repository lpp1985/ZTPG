ZTPG(Zipper + Total Viewer +Plasmid Finder + Gap liner)
-------------------------------------------------------
This is a ring-shaped genome assembler for Pacbio Reads.It uses HBAR_lpp or spari to do error-correct and then do addtional assembly.Its designed to assemble bacterial genome by one-button process and guess all plasmid.It could also use reference sequence to do reference-assist assembly and trim possible misassembly

Files
-----
* run.py---The main wrapper script
* Config.ini ---- Configure file 
Please Download the total directory and then modify the Config.ini to fullfill you environment!!

Prerequirement
--------------
* Celera Assembler
Please install Celera Assemberl through source file. When you install Celera Assembler, you need to modify the source code. In AS_global.h in src directory of Celera Assembler, change from

   #define AS_READ_MAX_NORMAL_LEN_BITS 11
to

   #define AS_READ_MAX_NORMAL_LEN_BITS 15
to support reads longer than 2048bp
* Bash5 Package
* Pbdagon Package or Sprai Package(http://zombie.cb.k.u-tokyo.ac.jp/sprai/)



