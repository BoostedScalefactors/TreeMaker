# B2GTTbar


##B2G2016 TreeV4 recipe:
```
cmsrel CMSSW_8_0_22
cd CMSSW_8_0_22/src/
cmsenv
git cms-init
git cms-merge-topic -u cms-met:CMSSW_8_0_X-METFilterUpdate
git cms-merge-topic cms-met:METRecipe_8020
git cms-merge-topic ikrav:egm_id_80X_v1
git clone https://github.com/rappoccio/PredictedDistribution.git Analysis/PredictedDistribution
git clone -b TreeV4 git@github.com:UBParker/B2GTTbar.git Analysis/B2GTTbar
git clone git@github.com:cms-jet/JetToolbox.git JMEAnalysis/JetToolbox -b jetToolbox_80X

cd ../..
scram b -j 12


cd Analysis/B2GTTbar/test/
cp JECs/Spring16_25nsV6*AK4PFchs* .
cp JECs/Spring16_25nsV6*AK4PFPuppi* .
cp JECs/Spring16_25nsV6*AK8PFchs* .
cp JECs/Spring16_25nsV6*AK8PFPuppi* .
cp JERs/* .
```
for MC:

`cmsRun run_B2GTTbarTreeMaker_MC_Toolbox.py`   # for QCD, Wjets

`cmsRun run_B2GTTbarTreeMaker_Zprime_Toolbox.py`

`cmsRun run_B2GTTbarTreeMaker_RSG_Toolbox.py`

`cmsRun run_B2GTTbarTreeMaker_ttbar_Toolbox.py`

for data:

`cmsRun run_B2GTTbarTreeMaker_data_Toolbox.py`


**For analysis with Loop tree, you must also checkout the btag package and remove one line:**

```
cd CMSSW_8_0_22/src/
git cms-addpkg CondFormats/BTauObjects
```
*Edit CondFormats/BTauObjects/src/classes.h  and comment out line 30 (it says BTagCalibration btc1;)* 
```
cd CondFormats/BTauObjects 
scramv1 b
cd ../../
```


##B2G2016 TreeV3 recipe:
```
cmsrel CMSSW_8_0_20
cmsenv
git cms-init
git cms-merge-topic -u cms-met:CMSSW_8_0_X-METFilterUpdate
git cms-merge-topic ikrav:egm_id_80X_v1
git clone https://github.com/rappoccio/PredictedDistribution.git Analysis/PredictedDistribution
git clone https://github.com/cmsb2g/B2GTTbar.git Analysis/B2GTTbar -b TreeV3
git clone git@github.com:cms-jet/JetToolbox.git JMEAnalysis/JetToolbox -b jetToolbox_80X
cd B2GTTbar/test/
```
for MC:

`cmsRun run_B2GTTbarTreeMaker_MC_Toolbox.py`

for data:

`cmsRun run_B2GTTbarTreeMaker_data_Toolbox.py`



##B2G2016 TreeV2 recipe:
```
cmsrel CMSSW_8_0_13
cd CMSSW_8_0_13/src/
cmsenv
git cms-init
git cms-merge-topic -u cms-met:CMSSW_8_0_X-METFilterUpdate
git cms-merge-topic ikrav:egm_id_80X_v1
git clone https://github.com/rappoccio/PredictedDistribution.git Analysis/PredictedDistribution
git clone https://github.com/cmsb2g/B2GTTbar.git Analysis/B2GTTbar
git clone git@github.com:cms-jet/JetToolbox.git JMEAnalysis/JetToolbox -b jetToolbox_763
cd B2GTTbar/test/
```
for MC: 

`cmsRun run_B2GTTbarTreeMaker_MC_Toolbox.py`

for data: 

`cmsRun run_B2GTTbarTreeMaker_data.py`

The new miniOAD->TTree maker is here:

https://github.com/cmsb2g/B2GTTbar/blob/master/plugins/B2GTTbarTreeMaker.cc


##2015 recipe:

From your CMSSW release area : 

To use the "PredictedDistribution" class : 

git clone https://github.com/rappoccio/PredictedDistribution.git Analysis/PredictedDistribution

git clone https://github.com/cmsb2g/B2GTTbar.git Analysis/B2GTTbar

To run on the files from FNAL :

```
python NtupleReader_fwlite.py --files singlemu_v74x_v6_dataset4_local.txt --outname singlemu_v74x_v6_dataset4_wtags_jecv5.root --
selection 1 --stMin 100.0 --minAK8Pt 200. --applyFilters --applyTriggers >& singlemu_v74x_v6_dataset4_wtags_output.txt &
python NtupleReader_fwlite.py --files singleel_v74x_v6_dataset4_local.txt --outname singleel_v74x_v6_dataset4_wtags_jecv5.root --
selection 1 --stMin 100.0 --minAK8Pt 200. --applyFilters --applyTriggers >& singleel_v74x_v6_dataset4_wtags_output.txt &
python NtupleReader_fwlite.py --files ttjets_b2ganafw_v6.txt --outname ttjets_b2ganafw_v6_wtags_jecv5.root --selection 1 --stMin 100.0 --
minAK8Pt 200. --applyFilters --isMC >& ttjets_b2ganafw_v6_wtags_output.txt &
python NtupleReader_fwlite.py  --files wjets_b2ganafw_v5.txt --outname wjets_b2ganafw_v5_sel1_extracats_wtags_jecv5.root --selection 1 -
-stMin 100.0  --minAK8Pt 200. --isMC  --applyFilters >& wjets_b2ganafw_v5_output.txt &
python NtupleReader_fwlite.py  --files FileLists/DYJetsToLL_M-50_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8_B2GAnaFW_V4_local.txt  
--outname zjets_b2ganafw_v4_sel1_extracats_wtags_jecv5.root --selection 1 --stMin 100.0  --minAK8Pt 200. --isMC   >& 
zjets_b2ganafw_v4_sel1_extracats_wtags_output.txt &
python NtupleReader_fwlite.py  --files FileLists/singletop_v74x_v4.3_tchan_local.txt  --outname 
singletop_v74x_v4.3_tchan_local_sel1_extracats_wtags_jecv5.root --selection 1 --stMin 100.0  --minAK8Pt 200. --isMC    >& 
singletop_v74x_v4.3_tchan_local_sel1_extracats_wtags_output.txt &
python NtupleReader_fwlite.py  --files FileLists/singletop_v74x_v4.3_tWtop_local.txt  --outname 
singletop_v74x_v4.3_tWtop_local_sel1_extracats_wtags_jecv5.root --selection 1 --stMin 100.0  --minAK8Pt 200. --isMC    >& 
singletop_v74x_v4.3_tWtop_local_sel1_extracats_wtags_output.txt &
python NtupleReader_fwlite.py  --files FileLists/singletop_v74x_v4.3_tWantitop_local.txt  --outname 
singletop_v74x_v4.3_tWantitop_local_sel1_extracats_wtags_jecv5.root --selection 1 --stMin 100.0  --minAK8Pt 200. --isMC    >& 
singletop_v74x_v4.3_tWantitop_local_sel1_extracats_wtags_output.txt &
```
