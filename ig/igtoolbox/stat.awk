{



if ($1==$2)
{
nrtruepos[$1]++
nrok++

}
else
{
nrfalsepos[$2]++
nrfalseneg[$1]++

}

nrref[$1]++
nrpred[$2]++
nrtot++

}


END
{

print

print "Global accuracy: " nrok*100/nrtot "%"

print

print "PRM Precision Recall F-measure"
for (i=0;i<3;i++)
{
precision[i]=nrtruepos[i]/(nrtruepos[i]+nrfalsepos[i])
recall[i]=nrtruepos[i]/(nrtruepos[i]+nrfalseneg[i])
fmeas[i]=2*precision[i]*recall[i]/(precision[i]+recall[i])

printf("%s %d%% %d%% %d%%\n",i,precision[i]*100,recall[i]*100,fmeas[i]*100)  

}

print

print "PRM Reference Prediction"
for (i=0;i<3;i++)
{

printf("%s %d%% %d%%\n",i,nrref[i]*100/nrtot,nrpred[i]*100/nrtot)

}




}