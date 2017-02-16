#! /usr/bin/env python

import ROOT

import TrigMap

class B2GSelectSemiLepTTbar_IsoStd( ) :
    """
    Selects boosted semileptonic ttbar events with standard isolation.
    """
    def __init__(self, options, tree ):
        self.ignoreTrig = options.ignoreTrig
        self.nstages = 10
        self.tree = tree        
        self.trigMap = TrigMap.TrigMap()
        self.verbose = options.verbose
        self.infile = options.infile

        ### Cached class member variables for plotting
        self.runNum = 0.
        self.theWeight = 0.

        self.leptonP4 = None
        self.nuP4 = None
        self.ak4Jet = None
        self.ak8Jet = None
        self.ak8SDJet = None
        self.trigIndex = [ self.trigMap.HLT_Mu50_v,
            #elf.trigMap.HLT_TkMu50_v
            self.trigMap.HLT_Ele45_CaloIdVT_GsfTrkIdT_PFJet200_PFJet50_v,
            #self.trigMap.HLT_Ele105_CaloIdVT_GsfTrkIdT_v          ] ### To-Do: Add other trigger as suggested here https://twiki.cern.ch/twiki/bin/viewauth/CMS/SWGuideMuonIdRun2
        ### Cached class member variables for plotting
        self.RunNumber = None
        self.theWeight = None
        self.leptonP4 = None
        self.nuP4 = None
        self.ak4Jet = None
        self.ak8Jet = None
        self.ak8SDJetP4 = None
        self.ak8PuppiSDJetP4_Subjet1 = None
        
        
        if self.verbose: print "self.trigIndex[0] {}".format(self.trigIndex[0])
        #self.printAK4Warning = True

        self.passed = [False] * self.nstages
        self.passedCount = [0] * self.nstages

        ### Create empty weights used for histo filling
        self.theWeight = 1.
        self.EventWeight = 1.
        self.PUWeight = 1.
        self.TriggEffIs  = 1.
        self.CutIDScaleFIs = 1.
        self.CutIDScaleFLooseIs =1.
        #self.MuonHIPScaleFIs =1.
        self.recoSFIs = 1.
        self.HEEPSFIs = 1.
        self.MuHighPtScaleFIs = 1.

        ### Muon Scale factors and efficiencies
        ### See https://twiki.cern.ch/twiki/bin/view/CMS/MuonWorkInProgressAndPagResults#Results_on_the_full_2016_data


        ### Muon trigger efficiency corrections
        self.printtriggerWarning = True
        self.TriggEffIs = 1.0

        self.finCor1 = ROOT.TFile.Open( "./muon_trg_summer16.root","READ")

        ### SFs to apply to data and/or MC after requiring event passes mu50 or trkmu50

        if self.printtriggerWarning :
            print '----------------------------------- WARNING --------------------------------------'
            print  ' The MC samples used here are old, must update to Moriond2017 samples to be accurate.'
            print  ' Trigger SFs and efficiencies are not accurate for this data/MC as it was processed requiring trigger:'
            print  ' Muons: HLT_Mu50 .'
            print  ' Electrons: Ele45_CaloIdVT_GsfTrkIdT_PFJet200_PFJet50 OR Ele50_CaloIdVT_GsfTrkIdT_PFJet140 OR Ele50_CaloIdVT_GsfTrkIdT_PFJet165'
            print  ' Update of triggers will occur after V5 ttrees have been produced'
            print '-----------------------------------------------------------------------------------'

        ### Not applying trigger SFs for the data

        ### SFs for the ttbar mc since the trigger was applied to it
        self.PtetaTriggSFmc_Period1      = self.finCor1.Get("h_eff_trg_mu50tkmu50_sf_1")
        self.PtetaTriggSFmc_Period2      = self.finCor1.Get("h_eff_trg_mu50tkmu50_sf_2")
        self.PtetaTriggSFmc_Period3      = self.finCor1.Get("h_eff_trg_mu50tkmu50_sf_3")
        self.PtetaTriggSFmc_Period4      = self.finCor1.Get("h_eff_trg_mu50tkmu50_sf_4")

        ### efficiencies for the rest of the MC since the trigger was not applied  (Also need SFs)
        self.PtetaTriggEffmc_Period1      = self.finCor1.Get("h_eff_trg_mu50tkmu50_mc_1")
        self.PtetaTriggEffmc_Period2      = self.finCor1.Get("h_eff_trg_mu50tkmu50_mc_2")
        self.PtetaTriggEffmc_Period3      = self.finCor1.Get("h_eff_trg_mu50tkmu50_mc_3")
        self.PtetaTriggEffmc_Period4      = self.finCor1.Get("h_eff_trg_mu50tkmu50_mc_4")

        ### HighPt Muon


        ### This is the official recommandation plus temp SFs for muons pt > 120 GeV (See Hengne's email for further information)
        self.finCor2 = ROOT.TFile.Open( "./muon_idiso_summer16.root","READ")

        self.HighPteffIs = 1.0

        ### Muon cut based ID corrections

        self.CutIDScaleFTightIs = 1.0
        self.CutIDScaleFLooseIs = 1.0
        self.finCor3 = ROOT.TFile.Open( "./EfficienciesAndSF_BCDEF.root","READ")
        self.finCor4 = ROOT.TFile.Open( "./EfficienciesAndSF_GH.root","READ")

        self.PtetaCutIDMuScaleFTightBtoF      = self.finCor3.Get("MC_NUM_TightID_DEN_genTracks_PAR_pt_eta/abseta_pt_ratio")
        self.PtetaCutIDMuScaleFTightGH      = self.finCor4.Get("MC_NUM_TightID_DEN_genTracks_PAR_pt_eta/abseta_pt_ratio")

        self.PtetaCutIDMuScaleFLooseBtoF      = self.finCor3.Get("MC_NUM_LooseID_DEN_genTracks_PAR_pt_eta/abseta_pt_ratio")
        self.PtetaCutIDMuScaleFLooseGH      = self.finCor4.Get("MC_NUM_LooseID_DEN_genTracks_PAR_pt_eta/abseta_pt_ratio")

        ### Only valid for pt < 120 Gev
        self.PtetaCutIDMuScaleFHighPtBtoF      = self.finCor3.Get("MC_NUM_HighPtID_DEN_genTracks_PAR_newpt_eta/abseta_pair_ne_ratio")
        self.PtetaCutIDMuScaleFHighPtGH      = self.finCor4.Get("MC_NUM_HighPtID_DEN_genTracks_PAR_newpt_eta/abseta_pair_ne_ratio")

        ### These should be the same as those above but with coverage for pt >120 Gev
        self.PtetaCutIDMuScaleFdataHighPtBtoF = self.finCor2.Get("h_mu_hpt_data_1")
        self.PtetaCutIDMuScaleFdataHighPtGH = self.finCor2.Get("h_mu_hpt_data_2")
        self.PtetaCutIDMuScaleFmcHighPtBtoF = self.finCor2.Get("h_mu_hpt_mc_1")
        self.PtetaCutIDMuScaleFmcHighPtGH = self.finCor2.Get("h_mu_hpt_mc_2")

        '''
        ### Muon HIP SF   I THINK THIS IS NOT NEEDED AFTER REReco CHECK THIS

        self.MuonHIPScaleFIs = 1.0
        self.finCor3 = ROOT.TFile.Open( "./ratios.root","READ")
        self.ratio_eta   =   self.finCor3.Get("ratio_eta")
        '''

        ### Electron reconstruction SF
        ###  Info here https://twiki.cern.ch/twiki/bin/viewauth/CMS/EgammaIDRecipesRun2#Electron_efficiencies_and_scale
        self.recoSFIs = 1.
        self.finCor5 = ROOT.TFile.Open( "./egammaEff_reconstructionSF.root","READ")

        #effdatareco = self.finCor5.Get("Gamma_EffData2D")
        #effmcreco =   self.finCor5.Get("EGamma_EffMC2D")

        self.hSFreco =      self.finCor5.Get("EGamma_SF2D")

        ### Electron cut based ID corrections

        self.CutIDScaleFMediumIs = 1.0
        self.CutIDScaleFLooseIs = 1.0
        self.finCor6 = ROOT.TFile.Open( "./egammaEffi_MedCutBasedID.root","READ")
        self.finCor7 = ROOT.TFile.Open( "./egammaEffi_LooseCutBasedID.root","READ")

        self.PtetaCutIDElScaleFMedium     = self.finCor6.Get("EGamma_SF2D")
        self.PtetaCutIDEldataEffMedium     = self.finCor6.Get("EGamma_EffData2D")
        self.PtetaCutIDElmcEffMedium     = self.finCor6.Get("EGamma_EffMC2D")

        self.PtetaCutIDElScaleFLoose      = self.finCor7.Get("EGamma_SF2D")
        self.PtetaCutIDEldataEffLoose     = self.finCor7.Get("EGamma_EffData2D")
        self.PtetaCutIDElmcEffLoose     = self.finCor7.Get("EGamma_EffMC2D")

        ### B tag weights
        ### Adapted from example https://twiki.cern.ch/twiki/bin/view/CMS/BTagCalibration#Code_example_in_Python
        ### Applied work around 2. listed here  https://twiki.cern.ch/twiki/bin/view/CMS/BTagCalibration#Additional_scripts

        # from within CMSSW:
        ROOT.gSystem.Load('libCondFormatsBTauObjects')
        ROOT.gSystem.Load('libCondToolsBTau')

        # OR using standalone code:
        #ROOT.gROOT.ProcessLine('.L BTagCalibrationStandalone.cpp+')

        # get the sf data loaded
        self.calib = ROOT.BTagCalibration('CSVv2_Moriond17_B_H','CSVv2_Moriond17_B_H.csv')#('csvv2_ichep', 'CSVv2_ichep.csv')

        # making a std::vector<std::string>> in python is a bit awkward,
        # but works with root (needed to load other sys types):
        self.v_sys = getattr(ROOT, 'vector<string>')()
        self.v_sys.push_back('up')
        self.v_sys.push_back('down')

        # make a reader instance and load the sf data
        self.reader = ROOT.BTagCalibrationReader(
            1,              # 0 is for loose op, 1: medium, 2: tight, 3: discr. reshaping
            "central",      # central systematic type
            self.v_sys,          # vector of other sys. types
        )
        self.reader.load(
            self.calib,
            0,          # 0 is for b flavour, 1: FLAV_C, 2: FLAV_UDSG
            "comb"      # measurement type
        )
        self.BtagWeight = 1.0
        self.BtagWeightsubjet = 1.
        ### Flags to distinguish different input files
        self.itIsData = None
        self.itIsTTbar = None

        theFileIs = self.infile
        if theFileIs.find("un2016")== -1 :
            self.itIsData = False
            if self.verbose :
                print "MC : Event and PU weights != 1"

        else :
            self.itIsData = True
            if self.verbose : print "DATA : weights = 1"

        if (theFileIs.find("ttbar")== -1 and theFileIs.find("un2016")== -1 ):
            if self.verbose :print "other MC : Event triggers were NOT applied so trigger efficiency will be !"

        else :
            self.itIsTTbar = True
            if self.verbose : print "ttbar MC : Event triggers were applied so trigger efficiency will NOT be !"


    """
        This is the "select" function that does the work for the event selection. If you have any complicated
        stuff to do, do it here and create a class member variable to cache the results. 
    """
    def select( self ):
        
        self.leptonP4 = None
        self.nuP4 = None
        self.ak4Jet = None
        
        ### Get Run Number of data event
        self.runNum = self.tree.SemiLeptRunNum[0]
        if self.verbose: print"RunNumber is {}...tree value is {}".format(self.runNum,  self.tree.SemiLeptRunNum[0] )
        ### Define the 4 vectors of the leptonic top system


        self.leptonP4 = ROOT.TLorentzVector()
        self.leptonP4.SetPtEtaPhiM( 
                                   self.tree.LeptonPt[0],
                                   self.tree.LeptonEta[0],
                                   self.tree.LeptonPhi[0], 
                                                       0. )

        self.nuP4 = ROOT.TLorentzVector()
        self.nuP4 = ROOT.TLorentzVector( 
                                        self.tree.SemiLeptMETpt[0],
                                        self.tree.SemiLeptMETpx[0], 
                                        self.tree.SemiLeptMETpy[0], 
                                                                0. )

        
        ### B tag SF (To be applied after b-tag is required at stage 12 in type1 and type2)
        self.ak4Jet = ROOT.TLorentzVector( )        
        self.ak4Jet.SetPtEtaPhiM( self.tree.AK4_dRminLep_Pt[0],
                                  self.tree.AK4_dRminLep_Eta[0],
                                  self.tree.AK4_dRminLep_Phi[0],
                                  self.tree.AK4_dRminLep_Mass[0] )

        ### MC generator weights and PU  weights
        if self.itIsData :
            self.EventWeight = 1.0
            self.PUWeight = 1.0
        else:
            self.EventWeight = self.tree.SemiLeptEventWeight[0]
            self.PUWeight = self.tree.SemiLeptPUweight[0]  
            

        ### B tag SF (To be applied after b-tag is required)

        if  self.itIsData :        self.BtagWeight = 1.0
        else: 
            self.BtagWeight = self.reader.eval_auto_bounds(
                                                        'central',      # systematic (here also 'up'/'down' possible)
                                                        0,              # jet flavor (0 for b jets)
                                                        self.ak4Jet.Eta() ,            # eta
                                                        self.ak4Jet.Perp()            # pt
                                                    )
        if self.verbose: print"BtagWeight is {0:2.2f}".format(self.BtagWeight)                                        

        # Work the cut flow
        # Stage 0 : None.
        # Stage 1 : Trigger
        # Stage 2 : Lepton selection
        # Stage 3 : MET selection
        # Stage 4 : Leptonic-side AK4 jet selection
        # Stage 5 : Wlep pt selection
        self.passed = [False] * self.nstages
        self.passedCount = [0] * self.nstages

        self.passed[0] = True
        self.passedCount[0] += 1
        if self.verbose: print"Stage 0: Preliminary cuts from B2GTreeMaker V4"

        self.CutIDScaleFLooseIs =  1.0

        if self.leptonP4 != None  and not self.itIsData: # self.RunNumber
            if self.tree.LeptonIsMu[0] == 1:
                self.CutIDScaleFLooseIs = self.MuonCutIDScaleFLoose( self.leptonP4.Perp() , abs(self.leptonP4.Eta()) , self.tree.SemiLeptRunNum[0] )
                if self.verbose : "MuonCutIDScaleFLoose: {0:2.4f} for pt {1:2.2f} and abs(eta) {2:2.2f}".format(self.CutIDScaleFLooseIs ,self.leptonP4.Perp() , abs(self.leptonP4.Eta())  )
            elif self.tree.LeptonIsMu[0] == 0  :
                #print"WARNING: ElectronCutIDScaleFLoose not yet applied"
                self.CutIDScaleFLooseIs = self.ElectronCutIDScaleFLoose( self.leptonP4.Perp() , abs(self.leptonP4.Eta()) , self.tree.SemiLeptRunNum[0] )
                if self.verbose : "ElectronCutIDScaleFLoose: {0:2.4f} for pt {1:2.2f} and abs(eta) {2:2.2f}".format(self.CutIDScaleFLooseIs ,self.leptonP4.Perp() , abs(self.leptonP4.Eta())  )
                self.recoSFIs = self.ElectronRecoSF( self.leptonP4.Eta(), self.leptonP4.Perp( ))


        if self.tree.LeptonIsMu[0] == 1 and self.leptonP4 != None  : # self.RunNumber
            self.TriggEffIs = 1.
            if not self.itIsData :
                self.TriggEffIs = self.MuonTriggEff( self.leptonP4.Perp() , abs(self.leptonP4.Eta())   , self.tree.SemiLeptRunNum[0] )

        if self.tree.LeptonIsMu[0] == 0 and not self.itIsData and self.leptonP4 != None  :
            print"WARNING: Electron trigger SF and eff not yet applied" 
              
        ### Trigger efficiency for morind MC + ReReco data Mu50 PR TRKMu50                                               
        ### we are using Mu50, switching with v5 ttrees                                                                  
                                                                                                                     
        self.theWeight =  self.EventWeight * self.PUWeight * self.CutIDScaleFLooseIs *  self.TriggEffIs * self.recoSFIs 
        if self.verbose : print "theWeight for stage {0:} is : {1:2.2f} = eventWeight {2:2.2f} * self.PUWeight{3:2.2f} * self.CutIDScaleFLooseIs {4:2.2f} *nTriggEffIs {5:2.2f} * self.recoSFIs  {6:2.2f}".format( 0, self.theWeight,  self.EventWeight , self.PUWeight , self.CutIDScaleFLooseIs * self.CutIDScaleFLooseIs, self.TriggEffIs, self.recoSFIs )


        if not self.ignoreTrig :
            self.trigIs = "" 
            for itrig in self.trigIndex :
                if bool ( self.tree.SemiLeptTrigPass[itrig] ) == True :
                    if self.verbose: print"trigIs {}".format( self.trigMap.names[itrig] )
                    self.trigIs = self.trigMap.names[itrig]              
                    self.passed[1] = True
            if not self.passed[1] : return self.passed
        else :
            self.passed[1] = True
        self.passedCount[1] += 1
        if self.verbose: print"Stage 1: Passed trigger {}".format(self.trigIs)


        self.MuHigh = self.tree.LeptonIsMu[0] == 1  and self.tree.MuHighPt[0] >0.
        self.ElHEEP = self.tree.LeptonIsMu[0] == 0 #and  self.tree.Electron_iso_passHEEP[0] > 0.
        if self.verbose: print"Stage 2 CHECK: Muis HighPt {} or Electron passed HEEP {}".format(self.tree.MuHighPt[0], self.tree.Electron_iso_passHEEP[0] )

        if self.tree.LeptonIsMu[0] == 1 and self.leptonP4 != None and  not self.itIsData  :
            self.MuHighPtScaleFIs = self.MuonHighPtScaleF( self.leptonP4.Perp() , abs(self.leptonP4.Eta()) ,  self.RunNumber )
            if self.verbose : "MuonHighPtScaleF: {0:2.2f} for pt {1:2.2f} and abs(eta) {2:2.2f}".format(self.CutIDScaleFIs,self.leptonP4.Perp() , abs(self.leptonP4.Eta())  )

        if self.tree.LeptonIsMu[0] == 0 and not self.itIsData and self.leptonP4 != None  :
            self.HEEPSFIs = self.ElectronHEEPEff(self.leptonP4.Eta() )
            print"ElectronHEEPEff: {0:2.3f} for eta {1:2.3f}".format(self.HEEPSFIs,  self.leptonP4.Eta() )


        self.theWeight =  self.EventWeight * self.PUWeight * self.CutIDScaleFLooseIs * self.recoSFIs * self.TriggEffIs * self.MuHighPtScaleFIs * self.HEEPSFIs
        if self.verbose : print "theWeight for stage {0:} is : {1:2.4f} = eventWeight {2:2.2f} * self.PUWeight{3:2.2f} * self.CutIDScaleFLooseIs {4:2.2f} * self.recoSFIs  {5:2.2f} * self.TriggEffIs {6:2.3f} *  self.MuHighPtScaleFIs {7:2.3f} * self.HEEPSFIs {8:2.3f}".format( 0, self.theWeight, self.EventWeight , self.PUWeight , self.CutIDScaleFIs, self.recoSFIs , self.TriggEffIs ,  self.MuHighPtScaleFIs , self.HEEPSFIs)



        if not ( self.MuHigh or self.ElHEEP ): return self.passed
        self.passed[2] = True
        self.passedCount[2] += 1 
        if self.verbose: print"Stage 2: Muis HighPt {} or Electron passed HEEP {}".format(self.tree.MuHighPt[0], self.tree.Electron_iso_passHEEP[0] )

        if self.leptonP4 != None  and not self.itIsData: # self.RunNumber                                                                                                                                        
            if self.tree.LeptonIsMu[0] == 1:
                self.CutIDScaleFIs = self.MuonCutIDScaleFTight( self.leptonP4.Perp() , abs(self.leptonP4.Eta()) , self.tree.SemiLeptRunNum[0] )
                if self.verbose : "MuonCutIDScaleFTight: {0:2.4f} for pt {1:2.2f} and abs(eta) {2:2.2f}".format(self.CutIDScaleFIs ,self.leptonP4.Perp() , abs(self.leptonP4.Eta())  )
            elif self.tree.LeptonIsMu[0] == 0  :
                #print"WARNING: ElectronCutIDScaleFLoose not yet applied"                                                                                                                                        
                self.CutIDScaleFIs = self.ElectronCutIDScaleFMedium( self.leptonP4.Perp() , abs(self.leptonP4.Eta()) , self.tree.SemiLeptRunNum[0] )
                if self.verbose : "ElectronCutIDScaleFMedium: {0:2.4f} for pt {1:2.2f} and abs(eta) {2:2.2f}".format(self.CutIDScaleFIs ,self.leptonP4.Perp() , (self.leptonP4.Eta())  )

        self.theWeight =  self.EventWeight * self.PUWeight * self.CutIDScaleFIs * self.recoSFIs * self.TriggEffIs * self.MuHighPtScaleFIs * self.HEEPSFIs
        if self.verbose : print "theWeight for stage {0:} is : {1:2.4f} = eventWeight {2:2.2f} * self.PUWeight{3:2.2f} * self.CutIDScaleFIs {4:2.2f} * self.recoSFIs  {5:2.2f} * self.TriggEffIs {6:2.3f} self.MuHighPtScaleFIs{7:2.3f} * self.HEEPSFIs {8:2.3f}".format( 0, self.theWeight, self.EventWeight , self.PUWeight , self.CutIDScaleFIs, self.recoSFIs , self.TriggEffIs ,self.MuHighPtScaleFIs,  self.HEEPSFIs)



        self.MuTight = self.tree.LeptonIsMu[0] == 1 and  self.tree.MuTight[0] == 1  
        self.ElMedium = self.tree.LeptonIsMu[0] == 0 and self.tree.Electron_noiso_passMedium[0] == 1

        if not (self.MuTight or  self.ElMedium ): return self.passed 
        self.passed[3] = True
        self.passedCount[3] += 1         
        if self.verbose: print"Stage 3: Muon is tight {} or Electron passed tight cut based ID with no iso {}".format(self.tree.MuTight[0], self.tree.Electron_noiso_passTight[0] )


        if not (( self.tree.LeptonIsMu[0] == 1 and self.leptonP4.Perp() > 53. and abs(self.leptonP4.Eta()) < 2.1 ) or  (self.tree.LeptonIsMu[0] == 0 and self.leptonP4.Perp() > 120. and (0. < abs(self.leptonP4.Eta()) < 1.442 or 1.56  < abs(self.leptonP4.Eta()) < 2.5 )  )) : return self.passed
        self.passed[4] = True
        self.passedCount[4] += 1        
        if self.verbose: print"Stage 4: Lepton passed Pt and eta cuts"


        if not (( self.tree.LeptonIsMu[0] == 1 and self.tree.MuIso[0] < 0.1 ) or   (self.tree.LeptonIsMu[0] == 0 )):
            return self.passed
        self.passed[5] = True
        self.passedCount[5] += 1 
        if self.verbose: print"Stage 5: MuIso < 0.1 or Electron"
        
        
        if not (( self.tree.LeptonIsMu[0] == 1 and self.nuP4.Perp() > 40.) or ( self.tree.LeptonIsMu[0] == 0 and self.nuP4.Perp() > 80.)) : return self.passed
        self.passed[6] = True
        self.passedCount[6] += 1
        if self.verbose: print"Stage 6: MET Pt passed cuts"

        
        if not ( self.ak4Jet.Perp() > 30. and abs(self.ak4Jet.Eta()) < 2.4  ) : return self.passed
        self.passed[7] = True
        self.passedCount[7] += 1
        if self.verbose: print"Stage 7: AK4 passed Pt and eta cuts"

        
        if not (  self.tree.DeltaRJetLep[0] > .4 ) : return self.passed # To-do: Hemisphere cut btw lepton and W candidate ak8 , check this is actually dR(lep, AK8)
        self.passed[8] = True
        self.passedCount[8] += 1
        if self.verbose: print"Stage 8: Lepton outside cone of b-jet"


        if not (  (self.leptonP4 + self.nuP4).Perp() > 200. )    : return self.passed
        self.passed[9] = True
        self.passedCount[9] += 1
        if self.verbose: print"Stage 9: Leptonic W pt > 200 Gev"

        return self.passed
        
    def MuonTriggEff(self, muonpt, muoneta, runNum) : #{ROOT file from
        #https://twiki.cern.ch/twiki/bin/view/CMS/MuonWorkInProgressAndPagResults
        TriggEff = 1.
        TriggSF = 1.

        runNumIs = None
        binx = None
        biny = None
        binxsf = None
        binysf = None


        if self.itIsData :
            return float(TriggSF)
        if 0. < runNum <= 274094. : ### Run Period 1
            binxsf = self.PtetaTriggSFmc_Period1.GetXaxis().FindBin( muoneta )
            binysf = self.PtetaTriggSFmc_Period1.GetYaxis().FindBin( muonpt )
            TriggSF = self.PtetaTriggSFmc_Period1.GetBinContent(binxsf, binysf )

            binx = self.PtetaTriggEffmc_Period1.GetXaxis().FindBin( muoneta  )
            biny = self.PtetaTriggEffmc_Period1.GetYaxis().FindBin( muonpt )
            TriggEff = self.PtetaTriggEffmc_Period1.GetBinContent(binx, biny )
        if 274094. < runNum < 278167. : ### Run Period 2
            binxsf = self.PtetaTriggSFmc_Period2.GetXaxis().FindBin( muoneta )
            binysf = self.PtetaTriggSFmc_Period2.GetYaxis().FindBin( muonpt )
            TriggSF = self.PtetaTriggSFmc_Period2.GetBinContent(binxsf , binysf )

            binx = self.PtetaTriggEffmc_Period2.GetXaxis().FindBin( muoneta  )
            biny = self.PtetaTriggEffmc_Period2.GetYaxis().FindBin( muonpt )
            TriggEff = self.PtetaTriggEffmc_Period2.GetBinContent(binx, biny )
        if  278167. <= runNum < 278820.: ### Run Period 3
            binxsf = self.PtetaTriggSFmc_Period3.GetXaxis().FindBin( muoneta )
            binysf = self.PtetaTriggSFmc_Period3.GetYaxis().FindBin( muonpt )
            TriggSF = self.PtetaTriggSFmc_Period3.GetBinContent(binxsf, binysf )

            binx = self.PtetaTriggEffmc_Period3.GetXaxis().FindBin( muoneta  )
            biny = self.PtetaTriggEffmc_Period3.GetYaxis().FindBin( muonpt )
            TriggEff = self.PtetaTriggEffmc_Period3.GetBinContent(binx, biny )
        if  278820.<= runNum : ### Run Period 4
            binxsf = self.PtetaTriggSFmc_Period4.GetXaxis().FindBin( muoneta )
            binysf = self.PtetaTriggSFmc_Period4.GetYaxis().FindBin( muonpt )
            TriggSF = self.PtetaTriggSFmc_Period4.GetBinContent(binxsf, binysf )

            binx = self.PtetaTriggEffmc_Period4.GetXaxis().FindBin( muoneta  )
            biny = self.PtetaTriggEffmc_Period4.GetYaxis().FindBin( muonpt )
            TriggEff = self.PtetaTriggEffmc_Period4.GetBinContent(binx, biny )

        if TriggSF > 3. :
            TriggSF =float( TriggSF/100.)
            if self.verbose: print"MuonTriggEff WARNING: SF is > 3., dividing by 100."
        if TriggEff > 3.:
            TriggEff =float( TriggEff/100.)
            if self.verbose: print"MuonTriggEff WARNING: eff is > 3., dividing by 100."

        if self.itIsTTbar :
            TriggEff = TriggSF
            if self.verbose : print "MuonTriggEff ttbar : Muon trigger SF is {0:2.2f} : using pt {1:2.2f},  eta {2:2.2f}".format( TriggEff, muonpt, muoneta)
        else:
            TriggEff =  TriggEff * TriggSF
            if self.verbose : print "MuonTriggEff other MC : Muon trigger Eff*SF is {0:2.2f} : pt {1:2.2f}, and eta {2:2.2f}".format( TriggEff, muonpt, muoneta)
        return float(TriggEff)


    def MuonCutIDScaleFTight(self, muonpt, muoneta, runNum) :
        if muonpt > 120.:
            print "MuonCutIDScaleFTight is for pt 0-120 GeV, this pt is {0:2.2f}".format(muonpt)
            return 1.
        if runNum < 278808. : #run2106B-F
            PtetaCutIDMuScaleFTight = self.PtetaCutIDMuScaleFTightBtoF
        else : #run2106GH
            PtetaCutIDMuScaleFTight =    self.PtetaCutIDMuScaleFTightGH

        binx = PtetaCutIDMuScaleFTight.GetXaxis().FindBin( muoneta )
        biny = PtetaCutIDMuScaleFTight.GetYaxis().FindBin( muonpt )
        CutIDScaleFl = PtetaCutIDMuScaleFTight.GetBinContent(binx, biny )
        if self.verbose : print "MuonCutIDScaleFTight: eta {0:2.2f}, pt {1:2.2f}, SF is {2:2.2f}".format( muoneta , muonpt, CutIDScaleFl )

        #if self.verbose : print "MuonCutIDScaleFTight: get bin: x (using eta) {}, y (using pt) {}, SF is {}".format(binx, biny, CutIDScaleFl )
        return float(CutIDScaleFl)
    '''
    def MuonCutIDScaleFLoose(self, muonpt, muoneta, runNum) :
        if runNum < 278808. : #run2106B-F
            PtetaCutIDMuScaleFLoose = self.PtetaCutIDMuScaleFLooseBtoF
        else : #run2106GH
            PtetaCutIDMuScaleFLoose =    self.PtetaCutIDMuScaleFLooseGH

        binx = PtetaCutIDMuScaleFLoose.GetXaxis().FindBin( muoneta  )
        biny = PtetaCutIDMuScaleFLoose.GetYaxis().FindBin( muonpt )
        CutIDScaleFl = PtetaCutIDScaleFLoose.GetBinContent(binx, biny )
        if self.verbose : print "MuonCutIDScaleFLoose: get bin: x (using eta) {}, y (using pt) {}, SF is {}".format(binx, biny, CutIDScaleFl )
        return float(CutIDScaleFl)
    #PtetaCutIDMuScaleFLoose = 1.0
    '''
    def MuonCutIDScaleFLoose(self, muonpt, muoneta, runNum) :
        PtetaCutIDMuScaleFLoose = None
        if muonpt > 120.:
            print "MuonCutIDScaleFLoose is for pt 0-120 GeV, this pt is {}".format(muonpt) 
            return 1. 
        if runNum < 278808. : #run2106B-F
            PtetaCutIDMuScaleFLoose = self.PtetaCutIDMuScaleFLooseBtoF
        else : #run2106GH
            PtetaCutIDMuScaleFLoose =    self.PtetaCutIDMuScaleFLooseGH

        binx = PtetaCutIDMuScaleFLoose.GetXaxis().FindBin( muoneta  )
        biny = PtetaCutIDMuScaleFLoose.GetYaxis().FindBin( muonpt )
        CutIDScaleFl = PtetaCutIDMuScaleFLoose.GetBinContent(binx, biny )
        if self.verbose : print "MuonCutIDScaleFLoose: eta {0:2.2f}, pt {1:2.2f}, SF is {2:2.2f}".format( muoneta , muonpt, CutIDScaleFl )
        #print "MuonCutIDScaleFLoose hist is {0:} for pt {1:2.2f} bin {2:} and eta {3:2.2f} bin {4:} the SF is {5:2.2f} ".format( PtetaCutIDMuScaleFLoose, muonpt, binx, muoneta, biny, CutIDScaleFl)
        return CutIDScaleFl     

    def MuonHighPtScaleF(self, muonpt, muoneta, runNum) :
        highSF = 1.0
        if runNum < 278808. : #run2106B-F                                     
            if self.itIsData:
                HighPt = self.PtetaCutIDMuScaleFdataHightPtBtoF
            else:
                HighPt = self.PtetaCutIDMuScaleFmcHighPtBtoF

        else :
            if self.itIsData:
                HighPt = self.PtetaCutIDMuScaleFdataHighPtGH
            else:
                HighPt = self.PtetaCutIDMuScaleFmcHighPtGH

        binx = HighPt.GetXaxis().FindBin( muoneta  )
        biny = HighPt.GetYaxis().FindBin( muonpt )
        CutIDScaleFl = HighPt.GetBinContent(binx, biny )
        if self.verbose : print "MuonHighPtScaleF: eta {0:2.2f}, pt {1:2.2f}, SF is {2:2.2f}".format( muoneta , muonpt, CutIDScaleFl )
        return float(CutIDScaleFl)


    def ElectronCutIDScaleFLoose(self, elpt, eleta, runNum) :
        PtetaCutIDElScaleFLoose = self.PtetaCutIDElScaleFLoose
        binx = PtetaCutIDElScaleFLoose.GetXaxis().FindBin( eleta  )
        biny = PtetaCutIDElScaleFLoose.GetYaxis().FindBin( elpt )
        CutIDScaleFl = PtetaCutIDElScaleFLoose.GetBinContent(binx, biny )
        if self.verbose : print "ElectronCutIDScaleFLoose: eta {0:2.2f}, pt {1:2.2f}, SF is {2:2.2f}".format( eleta , elpt, CutIDScaleFl )

        #print "ElectronCutIDScaleFLoose hist is {0:} for pt {1:2.2f} bin {2:} and eta {3:2.2f} bin {4:} the SF is {5:2.2f} ".format( PtetaCutIDElScaleFLoose, muonpt, binx, muoneta, biny, CutIDScaleFl)
        return CutIDScaleFl
        
    def ElectronCutIDScaleFMedium(self, elpt, eleta, runNum) :
        PtetaCutIDElScaleFMedium = self.PtetaCutIDElScaleFMedium
        binx = PtetaCutIDElScaleFMedium.GetXaxis().FindBin( eleta  )
        biny = PtetaCutIDElScaleFMedium.GetYaxis().FindBin( elpt )
        CutIDScaleFl = PtetaCutIDElScaleFMedium.GetBinContent(binx, biny )
        if self.verbose : print "ElectronCutIDScaleFMedium: eta {0:2.2f}, pt {1:2.2f}, SF is {2:2.2f}".format( eleta , elpt, CutIDScaleFl )
        return CutIDScaleFl
    '''
       self.PtetaCutIDElScaleFMedium     = self.finCor6.Get("EGamma_SF2D")
        self.PtetaCutIDEldataEffMedium     = self.finCor6.Get("EGamma_EffData2D")
        self.PtetaCutIDElmcEffMedium     = self.finCor6.Get("EGamma_EffMC2D")

        self.PtetaCutIDElScaleFLoose      = self.finCor7.Get("EGamma_SF2D")
        self.PtetaCutIDEldataEffLoose     = self.finCor7.Get("EGamma_EffData2D")
        self.PtetaCutIDElmcEffLoose     = self.finCor7.Get("EGamma_EffMC2D")



        self.PtetaCutIDMuScaleFdataHighPtBtoF = self.finCor2.Get("h_mu_hpt_data\
_1")
        self.PtetaCutIDMuScaleFdataHighPtGH = self.finCor2.Get("h_mu_hpt_data_2\
")
        self.PtetaCutIDMuScaleFmcHighPtBtoF = self.finCor2.Get("h_mu_hpt_mc_1")
        self.PtetaCutIDMuScaleFmcHighPtGH = self.finCor2.Get("h_mu_hpt_mc_2")



    ### SF for High-pT ID and (detector based) Tracker Relative Isolation
    def MuonIsoScaleF(self, muonpt, muoneta) : #{ROOT file from
        #https://twiki.cern.ch/twiki/bin/view/CMS/MuonWorkInProgressAndPagResults            ### TO-DO: Implement this for type 2 selection
        MuonIsoScaleF = 1.
        binx = self.fff.GetXaxis().FindBin( muonpt  )
        biny = self.fff.GetYaxis().FindBin( muoneta )
        MuonIsoScaleF = self.fff.GetBinContent(binx, biny )
        if self.verbose : print "get bin: x (using pt) {}, y (using eta) {}, CUt ID Eff is {}".format(binx, biny, MuonIsoScaleF )
        return float(MuonIsoScaleF)

    ### Not needed after Re-Reco CHECK THIS, either way fixed in 2016GH

    ### HIP SF : muon tracking specific SFs covering HIP inefficiencies
    def MuonHIPScaleF(self,  muoneta) : #{ROOT file from
        #https://twiki.cern.ch/twiki/bin/view/CMS/MuonReferenceEffsRun2#Tracking_efficiency_provided_by
        ### TO-DO: Implement this for type 2 selection
        MuonHIPScaleF = 1.

        MuonHIPScaleF = self.ratio_eta.Eval(muoneta)
        if self.verbose : print "(using eta) {}, HIP SF is {}".format(muoneta,  MuonHIPScaleF )
        return float(MuonHIPScaleF)
    '''
    def ElectronHEEPEff(self, eleta) :
        ### UNAPPROVED
        ### we used HEEP 6    https://github.com/cmsb2g/B2GTTbar/blob/master/test/run_B2GTTbarTreeMaker_MC2_Toolbox.py#L70
        ### eff for HEEP 7
        ### https://indico.cern.ch/event/609862/contributions/2458684/attachments/1405493/2147118/HEEP7_Moriond_ScaleFactor_0130.pdf
        effHEEP = 1.
        etabinnedHEEPefficiency = [  [ 0.984, 0.971, 0.961, 0.973, 0.978 , 0.980], [0.002, 0.001, 0.001, 0.001, 0.001, 0.002] ]
        etabins = [-2.5, -1.566, -1.4442, -.5, 0., 0.5, 1.4442, 1.566, 2.5]
        for ibin, ebin in enumerate(etabins):
            if  ebin < eleta < etabins[ibin+1]:
                if self.verbose: print "Here elets {0:2.2f} is btw the values [{1:2.2f}, {2:2.2f}] which puts it is bin {3:} and eff {4:2.3f}".format(eleta, ebin, etabins[ibin+1], ibin-1 , effHEEP)
                effHEEP = etabinnedHEEPefficiency[0][ibin-2]
        #if self.verbose : print "ElectronHEEPEff: {0:2.2f}, eta {1:2.2f}".format( effHEEP, eleta)
        return float(effHEEP)

    def ElectronRecoSF(self, eleta, elpt)    :
        ### https://twiki.cern.ch/twiki/bin/viewauth/CMS/EgammaIDRecipesRun2#Electron_efficiencies_and_scale
        ### https://indico.cern.ch/event/604907/contributions/2452907/attachments/1401460/2139067/RecoSF_ApprovalMoriond17_25Jan2017.pdf
        ### 1D, not Pt dependant
        recoSF = 1.
        rbinx = self.hSFreco.GetXaxis().FindBin( eleta )
        rbiny = self.hSFreco.GetYaxis().FindBin( elpt )
        recoSF = self.hSFreco.GetBinContent(rbinx, rbiny )
        if self.verbose : print "ElectronRecoSF: {0:2.2f}, pt {1:2.2f}, eta {2:2.2f}".format( recoSF, elpt, eleta)
        return float(recoSF)

    ### TO-DO: Eventually apply Kalman corrections
    '''
    if options.isMC :
        c=ROOT.KalmanMuonCalibrator("MC_80X_13TeV")
    else :
        c=ROOT.KalmanMuonCalibrator("DATA_80X_13TeV")
    def getKalmanMuonCorr(pt, eta, phi, charge) : #{
        # apply muon corrections as described here https://twiki.cern.ch/twiki/bin/viewauth/CMS/MuonScaleResolKalman
        if pt > 200. : return pt # shoulld add inner tracker eta cut
        if options.verbose : print 'HIP Correcting Muon Pt = {0:4.3f} GeV'.format(pt)
        if charge < 0. :
            chargeSign = -1 
        if charge > 0. :
            chargeSign = 1    
        CorrMuPt =c.getCorrectedPt(pt, eta, phi, chargeSign)
        if options.verbose : print 'After HIP Correcting Muon Pt = {0:4.3f} GeV'.format(CorrMuPt)
        dpt = abs( pt- CorrMuPt )
        dptopt = dpt/ pt
        CorrMuPtError = c.getCorrectedError(CorrMuPt , eta, dptopt)#'Recall! This correction is only valid after smearing'
        CorrMuPt = c.smear(CorrMuPt , eta)
        
        #print 'propagate the statistical error of the calibration
        #print 'first get number of parameters'
        #N=c.getN()
        #print N,'parameters'
        #for i in range(0,N):
            #c.vary(i,+1)
            #print 'variation',i,'ptUp', c.getCorrectedPt(pt, eta phi, charge)
            #c.vary(i,-1)
            #print 'variation',i,'ptDwn', c.getCorrectedPt(pt, eta phi, charge)
        #c.reset()
        #print 'propagate the closure error 
        #c.varyClosure(+1)
        
        #newpt =  c.getCorrectedPt(pt, eta, phi, chargeSign)
        if options.verbose : print 'After HIP Correcting Muon Pt and vary closure and smear  = {0:4.3f}'.format(CorrMuPt)
        #newpt2 = c.smear(pt , eta)
        #if options.verbose : print 'After HIP Correcting Muon Pt and vary closure and smear  = {0:4.3f}'.format(newpt2)

        return CorrMuPt
    '''

    
