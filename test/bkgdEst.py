#! /usr/bin/env python
import ROOT
from math import *
import copy
# ROOT.gSystem.Load("libAnalysisPredictedDistribution")

date = "121415"
jecSys = 1  # jecDn = -1; jecNom = 0; jecUp = +1

if jecSys == 0:
  syst = "jec_nom"
elif jecSys == 1:
  syst = "jec_up"
elif jecSys == -1:
  syst = "jec_dn"

OUT =  ROOT.TFile("outBkgdEst_TTpowheg_B2Gv8p4_reader5a85e65_all_"+date+"_"+syst+".root","RECREATE");
F1   =  ROOT.TFile("/eos/uscms/store/user/jdolen/B2GAnaFW/Trees/tree_TTpowheg_B2Gv8p4_reader5a85e65_all.root");
Tree = F1.Get("TreeAllHad");
entries = Tree.GetEntries();
print 'entries '+str(entries)  


Fmistag = ROOT.TFile("MistagRate_nbins_121415_8_Substract_outAntiTag_JetHT_BothParts_B2GAnaFW_v74x_V8p4_25ns_Nov13silverJSON_reader5a85e65_121415_"+syst+".root")

post = ["_jetPt_dRapHi_inclusive_"+ syst, "_jetPt_dRapHi_2btag_"+ syst, "_jetPt_dRapHi_1btag_"+ syst, "_jetPt_dRapHi_0btag_"+ syst,   
        "_jetPt_dRapLo_inclusive_"+ syst, "_jetPt_dRapLo_2btag_"+ syst, "_jetPt_dRapLo_1btag_"+ syst, "_jetPt_dRapLo_0btag_"+ syst]

#^ Hadronic mtt selection and background estimaion
h_mttMass_tagMassSDTau32_dRapHi_inclusive = ROOT.TH1D("h_mttMass_tagMassSDTau32_dRapHi_inclusive_" + syst  , "", 700, 0, 7000 )
h_mttMass_tagMassSDTau32_dRapHi_0btag     = ROOT.TH1D("h_mttMass_tagMassSDTau32_dRapHi_0btag_" + syst      , "", 700, 0, 7000 )
h_mttMass_tagMassSDTau32_dRapHi_1btag     = ROOT.TH1D("h_mttMass_tagMassSDTau32_dRapHi_1btag_" + syst      , "", 700, 0, 7000 )
h_mttMass_tagMassSDTau32_dRapHi_2btag     = ROOT.TH1D("h_mttMass_tagMassSDTau32_dRapHi_2btag_" + syst      , "", 700, 0, 7000 )
h_mttMass_tagMassSDTau32_dRapLo_inclusive = ROOT.TH1D("h_mttMass_tagMassSDTau32_dRapLo_inclusive_" + syst  , "", 700, 0, 7000 )
h_mttMass_tagMassSDTau32_dRapLo_0btag     = ROOT.TH1D("h_mttMass_tagMassSDTau32_dRapLo_0btag_" + syst      , "", 700, 0, 7000 )
h_mttMass_tagMassSDTau32_dRapLo_1btag     = ROOT.TH1D("h_mttMass_tagMassSDTau32_dRapLo_1btag_" + syst      , "", 700, 0, 7000 )
h_mttMass_tagMassSDTau32_dRapLo_2btag     = ROOT.TH1D("h_mttMass_tagMassSDTau32_dRapLo_2btag_" + syst      , "", 700, 0, 7000 )


h_bkgdEst_tagMassSDTau32_dRapHi_inclusive = ROOT.TH1D("h_bkgdEst_tagMassSDTau32_dRapHi_inclusive_" + syst   , "", 700, 0, 7000 )
h_bkgdEst_tagMassSDTau32_dRapHi_0btag     = ROOT.TH1D("h_bkgdEst_tagMassSDTau32_dRapHi_0btag_" + syst       , "", 700, 0, 7000 )
h_bkgdEst_tagMassSDTau32_dRapHi_1btag     = ROOT.TH1D("h_bkgdEst_tagMassSDTau32_dRapHi_1btag_" + syst       , "", 700, 0, 7000 )
h_bkgdEst_tagMassSDTau32_dRapHi_2btag     = ROOT.TH1D("h_bkgdEst_tagMassSDTau32_dRapHi_2btag_" + syst       , "", 700, 0, 7000 )
h_bkgdEst_tagMassSDTau32_dRapLo_inclusive = ROOT.TH1D("h_bkgdEst_tagMassSDTau32_dRapLo_inclusive_" + syst   , "", 700, 0, 7000 )
h_bkgdEst_tagMassSDTau32_dRapLo_0btag     = ROOT.TH1D("h_bkgdEst_tagMassSDTau32_dRapLo_0btag_" + syst       , "", 700, 0, 7000 )
h_bkgdEst_tagMassSDTau32_dRapLo_1btag     = ROOT.TH1D("h_bkgdEst_tagMassSDTau32_dRapLo_1btag_" + syst       , "", 700, 0, 7000 )
h_bkgdEst_tagMassSDTau32_dRapLo_2btag     = ROOT.TH1D("h_bkgdEst_tagMassSDTau32_dRapLo_2btag_" + syst       , "", 700, 0, 7000 )

h_bkgdEst_modMass_tagMassSDTau32_dRapHi_inclusive = ROOT.TH1D("h_bkgdEst_modMass_tagMassSDTau32_dRapHi_inclusive_" + syst   , "", 700, 0, 7000 )
h_bkgdEst_modMass_tagMassSDTau32_dRapHi_0btag     = ROOT.TH1D("h_bkgdEst_modMass_tagMassSDTau32_dRapHi_0btag_" + syst       , "", 700, 0, 7000 )
h_bkgdEst_modMass_tagMassSDTau32_dRapHi_1btag     = ROOT.TH1D("h_bkgdEst_modMass_tagMassSDTau32_dRapHi_1btag_" + syst       , "", 700, 0, 7000 )
h_bkgdEst_modMass_tagMassSDTau32_dRapHi_2btag     = ROOT.TH1D("h_bkgdEst_modMass_tagMassSDTau32_dRapHi_2btag_" + syst       , "", 700, 0, 7000 )
h_bkgdEst_modMass_tagMassSDTau32_dRapLo_inclusive = ROOT.TH1D("h_bkgdEst_modMass_tagMassSDTau32_dRapLo_inclusive_" + syst   , "", 700, 0, 7000 )
h_bkgdEst_modMass_tagMassSDTau32_dRapLo_0btag     = ROOT.TH1D("h_bkgdEst_modMass_tagMassSDTau32_dRapLo_0btag_" + syst       , "", 700, 0, 7000 )
h_bkgdEst_modMass_tagMassSDTau32_dRapLo_1btag     = ROOT.TH1D("h_bkgdEst_modMass_tagMassSDTau32_dRapLo_1btag_" + syst       , "", 700, 0, 7000 )
h_bkgdEst_modMass_tagMassSDTau32_dRapLo_2btag     = ROOT.TH1D("h_bkgdEst_modMass_tagMassSDTau32_dRapLo_2btag_" + syst       , "", 700, 0, 7000 )


#@ MODMASS
FmodMass = ROOT.TFile("ModMass_2015_09_22.root")

h_modMass_Fat            = FmodMass.Get( "h_mAK8_ModMass"           ).Clone()
h_modMass_SD             = FmodMass.Get( "h_mSDropAK8_ModMass"      ).Clone()
h_modMass_Fat_jet0       = FmodMass.Get( "h_mAK8_ModMass_jet0"      ).Clone()
h_modMass_SD_jet0        = FmodMass.Get( "h_mSDropAK8_ModMass_jet0" ).Clone()
h_modMass_Fat_jet1       = FmodMass.Get( "h_mAK8_ModMass_jet1"      ).Clone()
h_modMass_SD_jet1        = FmodMass.Get( "h_mSDropAK8_ModMass_jet1" ).Clone()

h_modMass_Fat      .SetName("h_modMass_Fat")  
h_modMass_SD       .SetName("h_modMass_SD")  
h_modMass_Fat_jet0 .SetName("h_modMass_Fat_jet0")  
h_modMass_SD_jet0  .SetName("h_modMass_SD_jet0")  
h_modMass_Fat_jet1 .SetName("h_modMass_Fat_jet1")  
h_modMass_SD_jet1  .SetName("h_modMass_SD_jet1")  

ROOT.SetOwnership( h_modMass_Fat       , False )
ROOT.SetOwnership( h_modMass_SD        , False )
ROOT.SetOwnership( h_modMass_Fat_jet0  , False )
ROOT.SetOwnership( h_modMass_SD_jet0   , False )
ROOT.SetOwnership( h_modMass_Fat_jet1  , False )
ROOT.SetOwnership( h_modMass_SD_jet1   , False )

print "h_modMass_Fat      integral  " + str( h_modMass_Fat     .Integral() )
print "h_modMass_SD       integral  " + str( h_modMass_SD      .Integral() )
print "h_modMass_Fat_jet0 integral  " + str( h_modMass_Fat_jet0.Integral() )
print "h_modMass_SD_jet0  integral  " + str( h_modMass_SD_jet0 .Integral() )
print "h_modMass_Fat_jet1 integral  " + str( h_modMass_Fat_jet1.Integral() )
print "h_modMass_SD_jet1  integral  " + str( h_modMass_SD_jet1 .Integral() )


h_mistag_vs_jetPt_TagMassSDTau32 = []
for i in xrange(len(post)):
    h_mistag_vs_jetPt_TagMassSDTau32.append( Fmistag.Get("h_mistag_AntiTagTau32_ReqTopMassSD_TagMassSDTau32"+ post[i]   ).Clone())
  
    h_mistag_vs_jetPt_TagMassSDTau32[i]      .SetName("h_mistag_AntiTagTau32_ReqTopMassSD_TagMassSDTau32"+ post[i]    )
    
    ROOT.SetOwnership( h_mistag_vs_jetPt_TagMassSDTau32[i]    , False )
    


count = 0


for event in Tree:
  count +=1
  if count%1000 ==0:
    print str(count)+" / "+str(entries)
  
  RawJet0Pt   = event.Jet0PtRaw
  RawJet0Eta  = event.Jet0EtaRaw
  RawJet0Phi  = event.Jet0PhiRaw
  RawJet0Mass = event.Jet0MassRaw

  jet0P4Raw = ROOT.TLorentzVector()
  jet0P4Raw.SetPtEtaPhiM( RawJet0Pt, RawJet0Eta, RawJet0Phi, RawJet0Mass)

  RawJet1Pt   = event.Jet1PtRaw
  RawJet1Eta  = event.Jet1EtaRaw
  RawJet1Phi  = event.Jet1PhiRaw
  RawJet1Mass = event.Jet1MassRaw

  jet1P4Raw = ROOT.TLorentzVector()
  jet1P4Raw.SetPtEtaPhiM( RawJet1Pt, RawJet1Eta, RawJet1Phi, RawJet1Mass)

  # Jec corrections
  Jet0CorrFactor   = event.Jet0CorrFactor
  Jet0CorrFactorUp = event.Jet0CorrFactorUp
  Jet0CorrFactorDn = event.Jet0CorrFactorDn

  Jet1CorrFactor   = event.Jet1CorrFactor
  Jet1CorrFactorUp = event.Jet1CorrFactorUp
  Jet1CorrFactorDn = event.Jet1CorrFactorDn

  if jecSys == 0:
      jet0P4 = jet0P4Raw * Jet0CorrFactor
      jet1P4 = jet1P4Raw * Jet1CorrFactor
      maxJetHt = event.HT
  elif jecSys == 1:
      jet0P4 = jet0P4Raw * Jet0CorrFactorUp
      jet1P4 = jet1P4Raw * Jet1CorrFactorUp
      maxJetHt = event.HT_CorrUp
  elif jecSys == -1:
      jet0P4 = jet0P4Raw * Jet0CorrFactorDn
      jet1P4 = jet1P4Raw * Jet1CorrFactorDn
      maxJetHt = event.HT_CorrDn
  
  DijetMass = (jet0P4 + jet1P4).M()


  if jet0P4.Perp() < 400 or jet1P4.Perp() < 400:
    continue

  if maxJetHt < 1000:
    continue

  maxBdisc_jet0_ = event.Jet0SDbdisc0
  maxBdisc_jet1_ = event.Jet0SDbdisc1
  # define tags - make sure they are the same as what was used to calculate the mistag
  topTag0MassFat                     = event.Jet0Mass > 140 and event.Jet1Mass< 250
  topTag1MassFat                     = event.Jet1Mass > 140 and event.Jet1Mass< 250
  topTag0MassSD                      = event.Jet0MassSoftDrop > 110 and event.Jet0MassSoftDrop < 210
  topTag1MassSD                      = event.Jet1MassSoftDrop > 110 and event.Jet1MassSoftDrop < 210
  topTag0Tau32                       = event.Jet0Tau32 < 0.69
  topTag1Tau32                       = event.Jet1Tau32 < 0.69
  topTag0MinMass                     = event.Jet0CMSminMass > 50 
  topTag1MinMass                     = event.Jet1CMSminMass > 50
  topTag0MaxBdiscM                   = maxBdisc_jet0_ > 0.890 # CSVv2 medium operating point 2015_06
  topTag1MaxBdiscM                   = maxBdisc_jet1_ > 0.890 # CSVv2 medium operating point 2015_06
  topTag0MassSDTau32                 = topTag0MassSD and topTag0Tau32
  topTag1MassSDTau32                 = topTag1MassSD and topTag1Tau32
  topTag0MassSDMinMass               = topTag0MassSD and topTag0MinMass
  topTag1MassSDMinMass               = topTag1MassSD and topTag1MinMass
  topTag0MassSDMinMassTau32          = topTag0MassSD and topTag0MinMass and topTag0Tau32
  topTag1MassSDMinMassTau32          = topTag1MassSD and topTag1MinMass and topTag1Tau32
  topTag0MassSDMaxBdisc              = topTag0MassSD and topTag0MaxBdiscM
  topTag1MassSDMaxBdisc              = topTag1MassSD and topTag1MaxBdiscM
  topTag0MassFatTau32                = topTag0MassFat and topTag0Tau32
  topTag1MassFatTau32                = topTag1MassFat and topTag1Tau32
  topTag0MassFatMinMass              = topTag0MassFat and topTag0MinMass
  topTag1MassFatMinMass              = topTag1MassFat and topTag1MinMass
  topTag0MassFatMinMassTau32         = topTag0MassFat and topTag0MinMass and topTag0Tau32
  topTag1MassFatMinMassTau32         = topTag1MassFat and topTag1MinMass and topTag1Tau32
  

  #setup the modMass procedure
  DijetMass_modMass_jet0 = DijetMass
  DijetMass_modMass_jet1 = DijetMass
  DijetMass_modMass_flat_jet0 = DijetMass
  DijetMass_modMass_flat_jet1 = DijetMass
  #-----
  # randomly sample from QCD mass distribution in [140,250] 
  # ROOT.gRandom.SetSeed(0) # make sure =0 -> TRandom3 - Set the random generator sequence if seed is 0 (default value) a TUUID is generated and used to fill the first 8 integers of the seed 
  ROOT.gRandom = ROOT.TRandom3(0)
  randMass_QCD_Fat_jet0 = h_modMass_SD_jet0.GetRandom()
  randMass_QCD_Fat_jet1 = h_modMass_SD_jet1.GetRandom()

  # when doing the tag+X bkgd estimate procedure, change the mass of the X jet 
  jet0P4_modMass = copy.copy ( jet0P4 )
  p_vec_jet0 = ROOT.TVector3( jet0P4_modMass.Px(), jet0P4_modMass.Py(), jet0P4_modMass.Pz())
  jet0P4_modMass.SetVectM( p_vec_jet0, randMass_QCD_Fat_jet0)

  jet1P4_modMass = copy.copy ( jet1P4 )
  p_vec_jet1 = ROOT.TVector3(jet1P4_modMass.Px(), jet1P4_modMass.Py(), jet1P4_modMass.Pz())
  jet1P4_modMass.SetVectM( p_vec_jet1, randMass_QCD_Fat_jet1)

  # #sample from a uniform distribution in [140,250]
  rand =  ROOT.TRandom3(0)
  rand_mass = rand.Uniform(110,210)

  # print 'randMass_QCD_Fat_jet0 '+str(randMass_QCD_Fat_jet0)
  # print 'randMass_QCD_Fat_jet1 '+str(randMass_QCD_Fat_jet1)
  # print 'rand_mass '+str(rand_mass)

  jet0P4_modMass_flat = copy.copy ( jet0P4 )
  p_vec_jet0 = ROOT.TVector3( jet0P4_modMass_flat.Px(), jet0P4_modMass_flat.Py(), jet0P4_modMass_flat.Pz())
  jet0P4_modMass_flat.SetVectM( p_vec_jet0, rand_mass )

  jet1P4_modMass_flat = copy.copy ( jet1P4 )
  p_vec_jet1 = ROOT.TVector3( jet1P4_modMass_flat.Px(), jet1P4_modMass_flat.Py(), jet1P4_modMass_flat.Pz())
  jet1P4_modMass_flat.SetVectM( p_vec_jet1, rand_mass )

  # if jet 0 is outside of the top mass window, force it to have mass in the window 
  if event.Jet0MassSoftDrop < 110 or event.Jet0MassSoftDrop > 210:
      DijetMass_modMass_jet0 = (jet1P4+ jet0P4_modMass ).M()
      DijetMass_modMass_flat_jet0 = (jet1P4+ jet0P4_modMass_flat ).M()

  # if jet 0 is outside of the top mass window, force it to have mass in the window (sample from QCD mass distribution in [140,250])
  if event.Jet1MassSoftDrop < 110 or event.Jet1MassSoftDrop > 210:
      DijetMass_modMass_jet1 = (jet0P4+ jet1P4_modMass ).M()
      DijetMass_modMass_flat_jet1 = (jet0P4+ jet1P4_modMass_flat ).M()



  #^ fill double tagged dijet distributions
  if topTag0MassSDTau32 and topTag1MassSDTau32:
      if event.DijetDeltaRap > 1 :
          #inclusive
          h_mttMass_tagMassSDTau32_dRapHi_inclusive.Fill( DijetMass   , evWeight )
          if topTag0MaxBdiscM and topTag1MaxBdiscM:
                #2btag
                h_mttMass_tagMassSDTau32_dRapHi_2btag.Fill( DijetMass   , evWeight )
          if (topTag0MaxBdiscM and not topTag1MaxBdiscM) or (topTag1MaxBdiscM and not topTag0MaxBdiscM):
                #1btag
                h_mttMass_tagMassSDTau32_dRapHi_1btag.Fill( DijetMass   , evWeight )
          if not topTag0MaxBdiscM and not topTag1MaxBdiscM:
                #0btag
                h_mttMass_tagMassSDTau32_dRapHi_0btag.Fill( DijetMass   , evWeight )
      if event.DijetDeltaRap < 1:
            #inclusive
            h_mttMass_tagMassSDTau32_dRapLo_inclusive.Fill( DijetMass   , evWeight )
            if topTag0MaxBdiscM and topTag1MaxBdiscM:
                #2btag
                h_mttMass_tagMassSDTau32_dRapLo_2btag.Fill( DijetMass   , evWeight )
            if (topTag0MaxBdiscM and not topTag1MaxBdiscM) or (topTag1MaxBdiscM and not topTag0MaxBdiscM):
                #1btag
                h_mttMass_tagMassSDTau32_dRapLo_1btag.Fill( DijetMass   , evWeight )
            if not topTag0MaxBdiscM and not topTag1MaxBdiscM:
                #0btag
                h_mttMass_tagMassSDTau32_dRapLo_0btag.Fill( DijetMass   , evWeight )
  


  evWeight = 1
  rand1 =  ROOT.TRandom3(0)
  rand_bkgdest  = rand1.Uniform(0,1.0)

  bin = []
  rate = []
 
  #^ Fill predicted distribution

  # randomly select jet 0 to be the tag then fill predDist based on probability that jet 1 is mis-tagged
  if rand_bkgdest < 0.5 :

      if topTag0MassSDTau32 :
          # mttPredDist_tagMassSDTau32        .Accumulate(              ttMass, jet1P4.Perp(), topTag1MassSDTau32, evWeight )
          # mttPredDist_modMass_tagMassSDTau32.Accumulate( ttMass_modMass_jet1, jet1P4.Perp(), topTag1MassSDTau32, evWeight )
          for i in xrange(len(post)):
              bin.append ( h_mistag_vs_jetPt_TagMassSDTau32[i].GetXaxis().FindBin( event.Jet1Pt ))
              rate.append( h_mistag_vs_jetPt_TagMassSDTau32[i].GetBinContent(bin[i]))
          if event.DijetDeltaRap > 1 :
              #inclusive
              h_bkgdEst_tagMassSDTau32_dRapHi_inclusive              .Fill( DijetMass       , evWeight*rate[0])
              h_bkgdEst_modMass_tagMassSDTau32_dRapHi_inclusive      .Fill( DijetMass_modMass_jet1, evWeight*rate[0])
              if topTag0MaxBdiscM and topTag1MaxBdiscM:
                  #2btag
                  h_bkgdEst_tagMassSDTau32_dRapHi_2btag              .Fill( DijetMass       , evWeight*rate[1])
                  h_bkgdEst_modMass_tagMassSDTau32_dRapHi_2btag      .Fill( DijetMass_modMass_jet1, evWeight*rate[1])
              if (topTag0MaxBdiscM and not topTag1MaxBdiscM) or (topTag1MaxBdiscM and not topTag0MaxBdiscM):
                  #1btag
                  h_bkgdEst_tagMassSDTau32_dRapHi_1btag              .Fill( DijetMass       , evWeight*rate[2])
                  h_bkgdEst_modMass_tagMassSDTau32_dRapHi_1btag      .Fill( DijetMass_modMass_jet1, evWeight*rate[2])   
              if not topTag0MaxBdiscM and not topTag1MaxBdiscM:
                  #0btag
                  h_bkgdEst_tagMassSDTau32_dRapHi_0btag              .Fill( DijetMass       , evWeight*rate[3])
                  h_bkgdEst_modMass_tagMassSDTau32_dRapHi_0btag      .Fill( DijetMass_modMass_jet1, evWeight*rate[3])
          if event.DijetDeltaRap < 1:
              #inclusive
              h_bkgdEst_tagMassSDTau32_dRapLo_inclusive              .Fill( DijetMass       , evWeight*rate[4])
              h_bkgdEst_modMass_tagMassSDTau32_dRapLo_inclusive      .Fill( DijetMass_modMass_jet1, evWeight*rate[4])
              if topTag0MaxBdiscM and topTag1MaxBdiscM:
                  #2btag
                  h_bkgdEst_tagMassSDTau32_dRapLo_2btag              .Fill( DijetMass       , evWeight*rate[5])
                  h_bkgdEst_modMass_tagMassSDTau32_dRapLo_2btag      .Fill( DijetMass_modMass_jet1, evWeight*rate[5])
              if (topTag0MaxBdiscM and not topTag1MaxBdiscM) or (topTag1MaxBdiscM and not topTag0MaxBdiscM):
                  #1btag
                  h_bkgdEst_tagMassSDTau32_dRapLo_1btag              .Fill( DijetMass       , evWeight*rate[6])
                  h_bkgdEst_modMass_tagMassSDTau32_dRapLo_1btag      .Fill( DijetMass_modMass_jet1, evWeight*rate[6])
              if not topTag0MaxBdiscM and not topTag1MaxBdiscM:
                  #0btag
                  h_bkgdEst_tagMassSDTau32_dRapLo_0btag              .Fill( DijetMass       , evWeight*rate[7])
                  h_bkgdEst_modMass_tagMassSDTau32_dRapLo_0btag      .Fill( DijetMass_modMass_jet1, evWeight*rate[7])


  # randomly select jet 1 to be the tag then fill predDist based on probability that jet 0 is mis-tagged
  if rand_bkgdest >= 0.5 :

      if topTag1MassSDTau32 :
          # mttPredDist_tagMassSDTau32        .Accumulate(              ttMass, jet0P4.Perp(), topTag0MassSDTau32, evWeight )
          # mttPredDist_modMass_tagMassSDTau32.Accumulate( ttMass_modMass_jet0, jet0P4.Perp(), topTag0MassSDTau32, evWeight )
          for i in xrange(len(post)):
              bin.append (h_mistag_vs_jetPt_TagMassSDTau32[i].GetXaxis().FindBin( event.Jet0Pt ))
              rate.append( h_mistag_vs_jetPt_TagMassSDTau32[i].GetBinContent(bin[i]))
          if event.DijetDeltaRap > 1 :
              #inclusive
              h_bkgdEst_tagMassSDTau32_dRapHi_inclusive              .Fill( DijetMass       , evWeight*rate[0])
              h_bkgdEst_modMass_tagMassSDTau32_dRapHi_inclusive      .Fill( DijetMass_modMass_jet0, evWeight*rate[0])
              if topTag0MaxBdiscM and topTag1MaxBdiscM:
                  #2btag
                  h_bkgdEst_tagMassSDTau32_dRapHi_2btag              .Fill( DijetMass       , evWeight*rate[1])
                  h_bkgdEst_modMass_tagMassSDTau32_dRapHi_2btag      .Fill( DijetMass_modMass_jet0, evWeight*rate[1])
              if (topTag0MaxBdiscM and not topTag1MaxBdiscM) or (topTag1MaxBdiscM and not topTag0MaxBdiscM):
                  #1btag
                  h_bkgdEst_tagMassSDTau32_dRapHi_1btag              .Fill( DijetMass       , evWeight*rate[2])
                  h_bkgdEst_modMass_tagMassSDTau32_dRapHi_1btag      .Fill( DijetMass_modMass_jet0, evWeight*rate[2])   
              if not topTag0MaxBdiscM and not topTag1MaxBdiscM:
                  #0btag
                  h_bkgdEst_tagMassSDTau32_dRapHi_0btag              .Fill( DijetMass       , evWeight*rate[3])
                  h_bkgdEst_modMass_tagMassSDTau32_dRapHi_0btag      .Fill( DijetMass_modMass_jet0, evWeight*rate[3])
          if event.DijetDeltaRap < 1:
              #inclusive
              h_bkgdEst_tagMassSDTau32_dRapLo_inclusive              .Fill( DijetMass       , evWeight*rate[4])
              h_bkgdEst_modMass_tagMassSDTau32_dRapLo_inclusive      .Fill( DijetMass_modMass_jet0, evWeight*rate[4])
              if topTag0MaxBdiscM and topTag1MaxBdiscM:
                  #2btag
                  h_bkgdEst_tagMassSDTau32_dRapLo_2btag              .Fill( DijetMass       , evWeight*rate[5])
                  h_bkgdEst_modMass_tagMassSDTau32_dRapLo_2btag      .Fill( DijetMass_modMass_jet0, evWeight*rate[5])
              if (topTag0MaxBdiscM and not topTag1MaxBdiscM) or (topTag1MaxBdiscM and not topTag0MaxBdiscM):
                  #1btag
                  h_bkgdEst_tagMassSDTau32_dRapLo_1btag              .Fill( DijetMass       , evWeight*rate[6])
                  h_bkgdEst_modMass_tagMassSDTau32_dRapLo_1btag      .Fill( DijetMass_modMass_jet0, evWeight*rate[6])
              if not topTag0MaxBdiscM and not topTag1MaxBdiscM:
                  #0btag
                  h_bkgdEst_tagMassSDTau32_dRapLo_0btag              .Fill( DijetMass       , evWeight*rate[7])
                  h_bkgdEst_modMass_tagMassSDTau32_dRapLo_0btag      .Fill( DijetMass_modMass_jet0, evWeight*rate[7])
          # h_bkgdEst_modMass_flat_tagMassSDTau32 .Fill(  ttMass_modMass_flat_jet0, evWeight*rate)


   

OUT.cd()

h_mttMass_tagMassSDTau32_dRapHi_inclusive        .Write()
h_mttMass_tagMassSDTau32_dRapHi_2btag            .Write()
h_mttMass_tagMassSDTau32_dRapHi_1btag            .Write()
h_mttMass_tagMassSDTau32_dRapHi_0btag            .Write()
h_mttMass_tagMassSDTau32_dRapLo_inclusive        .Write()
h_mttMass_tagMassSDTau32_dRapLo_2btag            .Write()
h_mttMass_tagMassSDTau32_dRapLo_1btag            .Write()
h_mttMass_tagMassSDTau32_dRapLo_0btag            .Write()
h_bkgdEst_tagMassSDTau32_dRapHi_inclusive        .Write()
h_bkgdEst_tagMassSDTau32_dRapHi_2btag            .Write()
h_bkgdEst_tagMassSDTau32_dRapHi_1btag            .Write()
h_bkgdEst_tagMassSDTau32_dRapHi_0btag            .Write()
h_bkgdEst_tagMassSDTau32_dRapLo_inclusive        .Write()
h_bkgdEst_tagMassSDTau32_dRapLo_2btag            .Write()
h_bkgdEst_tagMassSDTau32_dRapLo_1btag            .Write()
h_bkgdEst_tagMassSDTau32_dRapLo_0btag            .Write()
h_bkgdEst_modMass_tagMassSDTau32_dRapHi_inclusive.Write()
h_bkgdEst_modMass_tagMassSDTau32_dRapHi_2btag    .Write()
h_bkgdEst_modMass_tagMassSDTau32_dRapHi_1btag    .Write()
h_bkgdEst_modMass_tagMassSDTau32_dRapHi_0btag    .Write()
h_bkgdEst_modMass_tagMassSDTau32_dRapLo_inclusive.Write()
h_bkgdEst_modMass_tagMassSDTau32_dRapLo_2btag    .Write() 
h_bkgdEst_modMass_tagMassSDTau32_dRapLo_1btag    .Write()
h_bkgdEst_modMass_tagMassSDTau32_dRapLo_0btag    .Write()


OUT.Write()
OUT.Close()


print "Number of events in h_mttMass_tagMassSDTau32_dRapHi_inclusive: ", h_mttMass_tagMassSDTau32_dRapHi_inclusive.GetSum()
print "Number of events in h_mttMass_tagMassSDTau32_dRapHi_0btag: "    , h_mttMass_tagMassSDTau32_dRapHi_0btag    .GetSum()         
print "Number of events in h_mttMass_tagMassSDTau32_dRapHi_1btag: "    , h_mttMass_tagMassSDTau32_dRapHi_1btag    .GetSum()         
print "Number of events in h_mttMass_tagMassSDTau32_dRapHi_2btag: "    , h_mttMass_tagMassSDTau32_dRapHi_2btag    .GetSum()         
print "Summed number of events of dRapHi_0btag + dRapHi_1btag + dRapHi_2btag: "       , h_mttMass_tagMassSDTau32_dRapHi_0btag.GetSum() + h_mttMass_tagMassSDTau32_dRapHi_1btag.GetSum() + h_mttMass_tagMassSDTau32_dRapHi_2btag.GetSum()
print ""
print "Number of events in h_mttMass_tagMassSDTau32_dRapLo_inclusive: ", h_mttMass_tagMassSDTau32_dRapLo_inclusive.GetSum()         
print "Number of events in h_mttMass_tagMassSDTau32_dRapLo_0btag: "    , h_mttMass_tagMassSDTau32_dRapLo_0btag    .GetSum()         
print "Number of events in h_mttMass_tagMassSDTau32_dRapLo_1btag: "    , h_mttMass_tagMassSDTau32_dRapLo_1btag    .GetSum()         
print "Number of events in h_mttMass_tagMassSDTau32_dRapLo_2btag: "    , h_mttMass_tagMassSDTau32_dRapLo_2btag    .GetSum() 
print "Summed number of events of dRapLo_0btag + dRapLo_1btag + dRapLo_2btag: "       , h_mttMass_tagMassSDTau32_dRapLo_0btag.GetSum() + h_mttMass_tagMassSDTau32_dRapLo_1btag.GetSum() + h_mttMass_tagMassSDTau32_dRapLo_2btag.GetSum()        
print ""
print ""
print "Number of events in h_bkgdEst_tagMassSDTau32_dRapHi_inclusive: ", h_bkgdEst_tagMassSDTau32_dRapHi_inclusive.GetSum()
print "Number of events in h_bkgdEst_tagMassSDTau32_dRapHi_0btag: "    , h_bkgdEst_tagMassSDTau32_dRapHi_0btag    .GetSum()         
print "Number of events in h_bkgdEst_tagMassSDTau32_dRapHi_1btag: "    , h_bkgdEst_tagMassSDTau32_dRapHi_1btag    .GetSum()         
print "Number of events in h_bkgdEst_tagMassSDTau32_dRapHi_2btag: "    , h_bkgdEst_tagMassSDTau32_dRapHi_2btag    .GetSum()         
print "Summed number of events of dRapHi_0btag + dRapHi_1btag + dRapHi_2btag: "       , h_bkgdEst_tagMassSDTau32_dRapHi_0btag.GetSum() + h_bkgdEst_tagMassSDTau32_dRapHi_1btag.GetSum() + h_bkgdEst_tagMassSDTau32_dRapHi_2btag.GetSum()
print ""
print "Number of events in h_bkgdEst_tagMassSDTau32_dRapLo_inclusive: ", h_bkgdEst_tagMassSDTau32_dRapLo_inclusive.GetSum()         
print "Number of events in h_bkgdEst_tagMassSDTau32_dRapLo_0btag: "    , h_bkgdEst_tagMassSDTau32_dRapLo_0btag    .GetSum()         
print "Number of events in h_bkgdEst_tagMassSDTau32_dRapLo_1btag: "    , h_bkgdEst_tagMassSDTau32_dRapLo_1btag    .GetSum()         
print "Number of events in h_bkgdEst_tagMassSDTau32_dRapLo_2btag: "    , h_bkgdEst_tagMassSDTau32_dRapLo_2btag    .GetSum() 
print "Summed number of events of dRapLo_0btag + dRapLo_1btag + dRapLo_2btag: "       , h_bkgdEst_tagMassSDTau32_dRapLo_0btag.GetSum() + h_bkgdEst_tagMassSDTau32_dRapLo_1btag.GetSum() + h_bkgdEst_tagMassSDTau32_dRapLo_2btag.GetSum()        
print ""
print ""
print "Number of events in h_bkgdEst_modMass_tagMassSDTau32_dRapHi_inclusive: ", h_bkgdEst_modMass_tagMassSDTau32_dRapHi_inclusive.GetSum()
print "Number of events in h_bkgdEst_modMass_tagMassSDTau32_dRapHi_0btag: "    , h_bkgdEst_modMass_tagMassSDTau32_dRapHi_0btag    .GetSum()         
print "Number of events in h_bkgdEst_modMass_tagMassSDTau32_dRapHi_1btag: "    , h_bkgdEst_modMass_tagMassSDTau32_dRapHi_1btag    .GetSum()         
print "Number of events in h_bkgdEst_modMass_tagMassSDTau32_dRapHi_2btag: "    , h_bkgdEst_modMass_tagMassSDTau32_dRapHi_2btag    .GetSum()         
print "Summed number of events of dRapHi_0btag + dRapHi_1btag + dRapHi_2btag: "       , h_bkgdEst_modMass_tagMassSDTau32_dRapHi_0btag.GetSum() + h_bkgdEst_modMass_tagMassSDTau32_dRapHi_1btag.GetSum() + h_bkgdEst_modMass_tagMassSDTau32_dRapHi_2btag.GetSum()
print ""
print "Number of events in h_bkgdEst_modMass_tagMassSDTau32_dRapLo_inclusive: ", h_bkgdEst_modMass_tagMassSDTau32_dRapLo_inclusive.GetSum()         
print "Number of events in h_bkgdEst_modMass_tagMassSDTau32_dRapLo_0btag: "    , h_bkgdEst_modMass_tagMassSDTau32_dRapLo_0btag    .GetSum()         
print "Number of events in h_bkgdEst_modMass_tagMassSDTau32_dRapLo_1btag: "    , h_bkgdEst_modMass_tagMassSDTau32_dRapLo_1btag    .GetSum()         
print "Number of events in h_bkgdEst_modMass_tagMassSDTau32_dRapLo_2btag: "    , h_bkgdEst_modMass_tagMassSDTau32_dRapLo_2btag    .GetSum() 
print "Summed number of events of dRapLo_0btag + dRapLo_1btag + dRapLo_2btag: "       , h_bkgdEst_modMass_tagMassSDTau32_dRapLo_0btag.GetSum() + h_bkgdEst_modMass_tagMassSDTau32_dRapLo_1btag.GetSum() + h_bkgdEst_modMass_tagMassSDTau32_dRapLo_2btag.GetSum()        









