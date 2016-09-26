#!/usr/bin/env python

import re
import os
import sys
import wave

if len(sys.argv) != 2:
    print "Usage:%s pcm file" % (sys.argv[0])
    print "A wave will be created use same name. For example, input file is a.pcm, a.wav will be generated"
    sys.exit(1)

if not os.path.isfile(sys.argv[1]):
    print "input param is not a file"
    sys.exit(1)

fA = re.split("[.]", sys.argv[1])
if fA[-1] != "pcm":
    print "input file is not a pcm file"
    sys.exit(1)

pcmf = open(sys.argv[1], 'rb')
pcmdata = pcmf.read()
pcmf.close()

wavName = ".".join(fA[:-1])
wavName += ".wav"

wavfile = wave.open(wavName, 'wb')
wavfile.setparams((1, 2, 22050, 0, 'NONE', 'NONE'))
wavfile.writeframes(pcmdata)
wavfile.close()
