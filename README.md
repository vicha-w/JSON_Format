# JSON Format for JMAR

This is a repo to produce the JSON format for CMS based on:

[jsonpog-integration](https://gitlab.cern.ch/cms-nanoAOD/jsonpog-integration)

[correctionlib](https://github.com/cms-nanoAOD/correctionlib)

Once you log into a CERN/DESY machine use

```
     source /cvmfs/sft.cern.ch/lcg/views/LCG_100/x86_64-centos7-gcc10-opt/setup.sh
```

to get the correct root version
start a virtual enviorment

```
python -m venv json
source json/bin/activate
```

and install the json format scheme

```
python3 -m pip install correctionlib
```

do not forget to add the directorys to the libary to find all the inputs

```
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:PATH_TO_DIR
```

Each JMAR deliverable has its own directory. In the directory you can run python3 CORRECTION_YOU_WANT_TO_DO.py to create a json.

If you want to print your json you can do:

```
correction summary YOUR.json
```
and it will print a overview of what is stored in your file.
After all json are collected we can merge them by 

```
correction merge YEAR_JSON1.json YEAR_JSON2.json > YEAR_jmar.json
correction merge DeepAK8/2016_DeepAK8_*.json Toptagging/2016*.json QuarkGluon/2016_QuarkGluon.json Wtagging/2016_*.json PUJetID/2016_PUJetID.json > 2016_jmar.json
correction merge DeepAK8/2017_DeepAK8_*.json Toptagging/2017*.json QuarkGluon/2017_QuarkGluon.json Wtagging/2017_*.json PUJetID/2017_PUJetID.json > 2017_jmar.json
correction merge DeepAK8/2018_DeepAK8_*.json Toptagging/2018*.json QuarkGluon/2018_QuarkGluon.json Wtagging/2018_*.json PUJetID/2018_PUJetID.json > 2018_jmar.json
```

afterwards you can look at the summary or also create an html from it

```
correction --html 2016_jmar.html summary 2016_jmar.json
correction --html 2017_jmar.html summary 2017_jmar.json
correction --html 2018_jmar.html summary 2018_jmar.json
```


UL campaign (only includes corrections available so far)

```
correction merge PUJetID/UL2016__PUJetID.json  > UL16postVFP_jmar.json
correction merge PUJetID/UL2016APV_PUJetID.json  > UL16preVFP_jmar.json
correction merge Toptagging/UL17_Toptagging.json PUJetID/UL2017_PUJetID.json  > UL17_jmar.json
correction merge Toptagging/UL18_Toptagging.json PUJetID/UL2018_PUJetID.json  > UL18_jmar.json
```