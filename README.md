# NuPyTools
python tools for Nuance

## pcm2wav.py

**usage:** `pcm2wav.py [input pcm] [output wav]`

**description**: convert .pcm file into audio file .wav

## ferup-format.py

**usage:**`ferup-format.py [-h] [--version] [-c COMB] fpath out task`

**description:** convert corpus from Nuance linguistic team into FERUP format. 

##### Two task modes:

1. ws - word segmentation format
2. pw - prosody word format

##### Two generation ways:

1. non-combination [default] - generate same-name file as inputs
2. combination [c = 1] - generate one large file