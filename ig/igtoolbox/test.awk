extern cdecl dll "igtest" char * igtest(char*)

{
str=substr($0,3)
#print str
res=igtest(str)
printf("%s %s\n",$1,res)


}