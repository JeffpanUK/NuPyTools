set CLC=D:\\repos\\clc\\clc_sh_dev
set ExecPath=%CLC%\\tools\\tbox
set VEG=D:\\programs\\software\\vautomotive\\rls
set VER=D:\\programs\\software\\vautomotive\\rls
set OUTFILE=D:\\programs\\rtest
set CURDIR=%cd%

cd %ExecPath%

tbox_rtest.exe -L shc -V ding-ding -C cfg5 --spt -t ve -G %VEG% -g %VER% -O %OUTFILE% -R %CLC%

cd %CURDIR%