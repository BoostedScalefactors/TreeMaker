#! /usr/bin/env python

import ROOT

import TrigMap

class B2GSelectSemiLepTTbar_Iso2D( ) :
    """
    Selects boosted semileptonic ttbar events with non-isolated leptons , as described in CMS AN-15-107
    """
    def __init__(self, options, tree ):
        self.ignoreTrig = options.ignoreTrig
        self.verbose = options.verbose
        self.infile = options.infile

        self.nstages = 10
        if self.verbose: print "Begin leptonic top selection with {} stages".format(self.nstages)
        self.tree = tree        
        self.trigMap = TrigMap.TrigMap()


       
        # Define Kinematic Cut Values
        
        # Work the cut flow
        # Stage 0 : None.
        # Stage 1 : Trigger
        
        self.trigIndex = [
            self.trigMap.HLT_Mu45_eta2p1_v,
            #elf.trigMap.HLT_Mu30_eta2p1_PFJet150_PFJet50_v,
            #self.trigMap.HLT_Mu40_eta2p1_PFJet200_PFJet50_v,
            self.trigMap.HLT_Ele45_CaloIdVT_GsfTrkIdT_PFJet200_PFJet50_v,
            self.trigMap.HLT_Ele50_CaloIdVT_GsfTrkIdT_PFJet140_v,
            self.trigMap.HLT_Ele50_CaloIdVT_GsfTrkIdT_PFJet165_v
            ]        
        
        # Stage 2 : Lepton kinematic selection
        
        self.muonPtCut = 53.
        self.muonEtaCut = 2.1

        self.electronPtCut = 53.
        self.electronEtaCut = 2.5
        
        #self.passMuon_Pt = self.tree.LeptonIsMu[0] == 1 and self.leptonP4.Perp() > self.muonPtCut         
        #self.passElectron_Pt = self.tree.LeptonIsMu[0] == 0 and self.leptonP4.Perp() > self.electronPtCut  
     
        #self.passMuon_Eta = self.tree.LeptonIsMu[0] == 1 and abs(self.leptonP4.Eta()) < self.muonEtaCut
        #self.passElectron_Eta = self.tree.LeptonIsMu[0] == 0  and abs(self.leptonP4.Eta()) < self.electronEtaCut

        ### There is a problem with cut based ID currently where nothing is passing Electron_noiso_*


        # Stage 3 : Lepton Cut based ID selection 
        # Tight (no iso for electrons).   ### Was Medium for muons in paper however Tight is suggested by semi-lept group for new 2016 data.

        # self.passMuon_Tight = self.tree.LeptonIsMu[0] > 0. and self.tree.MuTight[0] > 0.    
        #self.passElectron_Tight_noIso = self.tree.LeptonIsMu[0] < 1.  and self.tree.Electron_noiso_passTight[0] > 0.        

        # Stage 4 : Muon High Pt ID selection 
        
        # Stage 5 : MET selection
        self.muonMETPtCut = 50.
        self.electronMETPtCut = 120.


        # Stage 6 : Leptonic-side AK4 jet selection
        self.AK4jetPtCut = 50.
        self.AK4EtaCut = 2.4

        # Stage 7 : 2D cut (decrease QCD contamination)
        self.DrAK4Lep = 0.4
        self.PtRel = 40.


        # Stage 8 : Hemisphere cut (keep leptons far from AK8 Jet)
        #  DR(AK8, Lepton) > 1.

        # Stage 9 : Wlep pt selection
        self.MuonHtLepCut = 200.
        self.ElectronHtLepCut = 200.

        ### Cached class member variables for plotting
        self.runNum = None
        self.theWeight = None
        self.leptonP4 = None
        self.nuP4 = None
        self.ak4Jet = None
        self.ak8Jet = None
        self.ak8SDJet = None

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
        self.MuonHIPScaleFIs =1.


        ### Muon trigger efficiency corrections
  
        self.TriggEffIs = 1.0  
        self.finCor1 = ROOT.TFile.Open( "./SingleMuonTrigger_Z_RunBCD_prompt80X_7p65.root","READ")
        self.PtetaTriggEff_Run273158_to_274093      = self.finCor1.Get("Mu45_eta2p1_PtEtaBins_Run273158_to_274093/efficienciesDATA/pt_abseta_DATA")
        self.PtetaTriggEff_Run274094_to_276097      = self.finCor1.Get("Mu45_eta2p1_PtEtaBins_Run274094_to_276097/efficienciesDATA/pt_abseta_DATA")
        ### Muon cut based ID corrections
  
        self.CutIDScaleFIs = 1.0  
        self.CutIDScaleFLooseIs = 1.0  
        self.finCor2 = ROOT.TFile.Open( "./MuonID_Z_RunBCD_prompt80X_7p65.root","READ")
        self.PtetaCutIDScaleFTight      = self.finCor2.Get("MC_NUM_TightIDandIPCut_DEN_genTracks_PAR_pt_spliteta_bin1/pt_abseta_ratio")
        self.PtetaCutIDScaleFLoose      = self.finCor2.Get("MC_NUM_LooseID_DEN_genTracks_PAR_pt_spliteta_bin1/pt_abseta_ratio")
        ### Muon HIP SF
  
        self.MuonHIPScaleFIs = 1.0  
        self.finCor3 = ROOT.TFile.Open( "./ratios.root","READ")
        self.ratio_eta   =   self.finCor3.Get("ratio_eta")
        ### B tag weights       
        ### Adapted from example https://twiki.cern.ch/twiki/bin/view/CMS/BTagCalibration#Code_example_in_Python
        ### Applied work around 2. listed here  https://twiki.cern.ch/twiki/bin/view/CMS/BTagCalibration#Additional_scripts

        # from within CMSSW:
        ROOT.gSystem.Load('libCondFormatsBTauObjects') 
        ROOT.gSystem.Load('libCondToolsBTau') 

        # OR using standalone code:
        #ROOT.gROOT.ProcessLine('.L BTagCalibrationStandalone.cpp+') 

        # get the sf data loaded
        self.calib = ROOT.BTagCalibration('csvv2_ichep', 'CSVv2_ichep.csv')

        # making a std::vector<std::string>> in python is a bit awkward, 
        # but works with root (needed to load other sys types):
        self.v_sys = getattr(ROOT, 'vector<string>')()
        self.v_sys.push_back('up')
        self.v_sys.push_back('down')

        # make a reader instance and load the sf data
        self.reader = ROOT.BTagCalibrationReader(
            0,              # 0 is for loose op, 1: medium, 2: tight, 3: discr. reshaping
            "central",      # central systematic type
            self.v_sys,          # vector of other sys. types
        )    
        self.reader.load(
            self.calib, 
            0,          # 0 is for b flavour, 1: FLAV_C, 2: FLAV_UDSG 
            "comb"      # measurement type
        )        
        self.BtagWeight = 1.0

        ### Flag to distinguish data from MC
        self.itIsData = None
        theFileIs = self.infile
        if theFileIs.find("un2016")== -1 : 
            self.itIsData = False
            if self.verbose :  
                print "MC : Event and PU weights != 1"

        else : 
            self.itIsData = True                     
            if self.verbose : print "DATA : weights = 1" 

    """
        This is the "select" function that does the work for the event selection. If you have any complicated
        stuff to do, do it here and create a class member variable to cache the results. 
    """
    def select( self ) :
        self.runNum = None
        self.theWeight = None
        
        self.leptonP4 = None
        self.nuP4 = None
        self.ak4Jet = None
        

        ### Get Run Number of data event
        self.runNum = self.tree.SemiLeptRunNum[0]

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



                                                                
        self.EventWeight = 1.
        self.PUWeight = 1.
        self.TriggEffIs = 1.
        self.CutIDScaleFLooseIs = 1.
        self.CutIDScaleFIs = 1.
        self.MuonHIPScaleFIs = 1.
        self.BtagWeight = 1.
        
        ### MC generator weights and PU  weights
        if self.itIsData :
            self.EventWeight = 1.0
            self.PUWeight = 1.0
        else:
            self.EventWeight = self.tree.SemiLeptEventWeight[0]
            self.PUWeight = self.tree.SemiLeptPUweight[0]              
            
        if self.tree.LeptonIsMu[0] == 1 and not self.itIsData and self.leptonP4 != None  :
            self.TriggEffIs = self.MuonTriggEff( self.leptonP4.Perp() , abs(self.leptonP4.Eta())   , self.tree.SemiLeptRunNum[0] )
            if self.verbose : "Muon trigger eff is {0:2.2f} for pt {1:2.2f} and abs(eta) {2:2.2f}".format(self.TriggEffIs,self.leptonP4.Perp() , abs(self.leptonP4.Eta())  )

            self.CutIDScaleFLooseIs = self.MuonCutIDScaleFLoose( self.leptonP4.Perp() , abs(self.leptonP4.Eta())  )
            if self.verbose : "Muon Cut ID LOOSE  eff is {0:2.2f} for pt {1:2.2f} and abs(eta) {2:2.2f}".format(self.CutIDScaleFLooseIs ,self.leptonP4.Perp() , abs(self.leptonP4.Eta())  )

            self.CutIDScaleFIs = self.MuonCutIDScaleFTight( self.leptonP4.Perp() , abs(self.leptonP4.Eta())  )
            if self.verbose : "Muon Cut ID MEDIUM eff is {0:2.2f} for pt {1:2.2f} and abs(eta) {2:2.2f}".format(self.CutIDScaleFIs,self.leptonP4.Perp() , abs(self.leptonP4.Eta())  )

            self.MuonHIPScaleFIs = self.MuonHIPScaleF( self.leptonP4.Eta() )
            if self.verbose : "Muon HIP SF is {0:2.2f} for eta {1:2.2f}".format(self.MuonHIPScaleFIs, self.leptonP4.Eta()  )

        if self.tree.LeptonIsMu[0] == 0 and not self.itIsData and self.leptonP4 != None  :
            print"WARNING: Electron scale factors, trigger efficiencies and weights not yet applied"    
            '''
              self.TriggEffIs = self.MuonTriggEff( self.leptonP4.Perp() , abs(self.leptonP4.Eta())   , self.tree.SemiLeptRunNum[0] )
            if self.verbose : "Muon trigger eff is {0:2.2f} for pt {1:2.2f} and abs(eta) {2:2.2f}".format(self.TriggEffIs,self.leptonP4.Perp() , abs(self.leptonP4.Eta())  )

            self.CutIDScaleFLooseIs = self.MuonCutIDScaleFLoose( self.leptonP4.Perp() , abs(self.leptonP4.Eta())  )
            if self.verbose : "Muon Cut ID LOOSE  eff is {0:2.2f} for pt {1:2.2f} and abs(eta) {2:2.2f}".format(self.CutIDScaleFLooseIs ,self.leptonP4.Perp() , abs(self.leptonP4.Eta())  )

            self.CutIDScaleFIs = self.MuonCutIDScaleFTight( self.leptonP4.Perp() , abs(self.leptonP4.Eta())  )
            if self.verbose : "Muon Cut ID MEDIUM eff is {0:2.2f} for pt {1:2.2f} and abs(eta) {2:2.2f}".format(self.CutIDScaleFIs,self.leptonP4.Perp() , abs(self.leptonP4.Eta())  )

            self.MuonHIPScaleFIs = self.MuonHIPScaleF( self.leptonP4.Eta() )
            if self.verbose : "Muon HIP SF is {0:2.2f} for eta {1:2.2f}".format(self.MuonHIPScaleFIs, self.leptonP4.Eta()  )

            '''
        if  self.itIsData :        self.BtagWeight = 1.0
        else: self.BtagWeight = self.reader.eval_auto_bounds(
                                                        'central',      # systematic (here also 'up'/'down' possible)
                                                        0,              # jet flavor (0 for b jets)
                                                        self.ak4Jet.Eta() ,            # eta
                                                        self.ak4Jet.Perp()            # pt
                                                    )


        '''
        if self.printAK4Warning :
            print '----------------------------------- WARNING --------------------------------------'
            print  ' error resolved'
        '''
        self.passMuon_Pt = self.tree.LeptonIsMu[0] == 1 and self.leptonP4.Perp() > self.muonPtCut
        self.passElectron_Pt = self.tree.LeptonIsMu[0] == 0 and self.leptonP4.Perp() > self.electronPtCut
                                                                                                                                                                                                      
        self.passMuon_Eta = self.tree.LeptonIsMu[0] == 1 and abs(self.leptonP4.Eta()) < self.muonEtaCut
        self.passElectron_Eta = self.tree.LeptonIsMu[0] == 0  and abs(self.leptonP4.Eta()) < self.electronEtaCut

        self.passMuon_Tight = self.tree.LeptonIsMu[0] > 0. and self.tree.MuTight[0] > 0.
        self.passElectron_Tight_noIso = self.tree.LeptonIsMu[0] < 1.  and self.tree.Electron_noiso_passTight[0] > 0.        


        self.passed = [False] * self.nstages
        self.passedCount = [0] * self.nstages

        self.passed[0] = True
        self.passedCount[0] += 1
        if self.verbose: print"Stage 0: Preliminary cuts from B2GTreeMaker V4"

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


        if self.tree.LeptonIsMu[0] > 0. : ### Muon
            if not ( self.leptonP4.Perp() > self.muonPtCut and   abs(self.leptonP4.Eta()) < self.muonEtaCut ) : return self.passed
        if self.tree.LeptonIsMu[0] < 1. : ### Electron
            if not ( self.leptonP4.Perp() > self.electronPtCut and   abs(self.leptonP4.Eta()) < self.electronEtaCut ) : return self.passed
        self.passed[2] = True
        self.passedCount[2] += 1
        if self.verbose :
            if self.passMuon_Eta :print "Stage 2a: Exactly 1 muon candidate  eta {0:2.2f} < ( {1:2.2f} )".format(
                                                                        self.leptonP4.Eta(),
                                                                        self.muonEtaCut)
            else :print "Stage 2a: Exactly 1 electron candidate  eta {0:2.2f} < ( {1:2.2f} )".format(
                                                                        self.leptonP4.Eta(),
                                                                        self.electronEtaCut)

        if self.verbose : print "Stage 2b: lepton candidate pt {0:2.2f} GeV > ({1:2.2f} GeV)".format(
                                                                        self.leptonP4.Perp(),
                                                                        self.muonPtCut)
                                                                       
        if self.verbose  : print "Stage 3 CHECK: ELECTRON  passnoiso loose {} med {} tight {}- MUON is High Pt {} is tight {}".format(
                                 self.tree.Electron_noiso_passLoose[0] , 
                                 self.tree.Electron_noiso_passMedium[0],
                                 self.tree.Electron_noiso_passTight[0],
                                 self.tree.MuHighPt[0],
                                 self.tree.MuTight[0]  )                                                                       
                                                                       

        if self.tree.LeptonIsMu[0] > 0. : ### Muon
            if not self.tree.MuTight[0] > 0.  : return self.passed
        if self.tree.LeptonIsMu[0] < 1. : ### Electron
            if not self.tree.Electron_noiso_passMedium[0] > 0.  : return self.passed
        self.passed[3] = True
        self.passedCount[3] += 1
        if self.verbose  : print "Stage 3: Muon (Electron) passed Tight (Medium) Cut based ID (with no iso) passnoiso loose {} med {} tight {}".format(self.tree.Electron_noiso_passLoose[0] , self.tree.Electron_noiso_passMedium[0], self.tree.Electron_noiso_passTight[0] )

        ### NOTE : High Pt Muon ID is now required as suggested here https://twiki.cern.ch/twiki/bin/view/CMS/SWGuideMuonIdRun2#2016_Data
        if not (( self.tree.LeptonIsMu[0] == 1 and self.tree.MuHighPt[0] == 1 and self.tree.SemiLeptPassMETFilters[0] == 1) or  (self.tree.LeptonIsMu[0] == 0 and  self.tree.SemiLeptPassMETFilters[0] == 1 )) : 
            return self.passed
        self.passed[4] = True
        self.passedCount[4] += 1
        if self.verbose  : print "Stage 4: Muon is HighPt and lepton pass self.tree.SemiLeptPassMETFilters[0] == {} ".format(self.tree.SemiLeptPassMETFilters[0] )


        if self.verbose: print"Stage 5 CHECK: Lepton is a Muon bool {}, MET is {} GeV".format(self.tree.LeptonIsMu[0] , self.nuP4.Perp() )

        if self.tree.LeptonIsMu[0] > 0. :
            if not self.nuP4.Perp() > self.muonMETPtCut  : return self.passed
        if self.tree.LeptonIsMu[0] < 1. :
            if not self.nuP4.Perp() > self.electronMETPtCut  : return self.passed
        self.passed[5] = True
        self.passedCount[5] += 1
        if self.verbose : 
            if self.tree.LeptonIsMu[0] == 1 :


                print "Stage 5: Muon  MET pt {0:2.2f} GeV > ( {1:2.2f} GeV ) ".format(
                                                                        self.nuP4.Perp(),
                                                                        self.muonMETPtCut )
            else:
                print "Stage 5: Electron MET pt {0:2.2f} GeV > ( {1:2.2f} GeV ) ".format(
                                                                        self.nuP4.Perp(),
                                                                        self.electronMETPtCut )
 
        if not ( self.ak4Jet.Perp() > self.AK4jetPtCut and abs(self.ak4Jet.Eta()) < self.AK4EtaCut  ) : return self.passed    
        self.passed[6] = True
        self.passedCount[6] += 1
        if self.verbose : print "Stage 6: AK4 jet pt {0:2.2f} GeV > ( {1:2.2f} GeV ) and eta {2:2.2f} < ( {3:2.2f} )".format( 
                                                                                             self.ak4Jet.Perp(),
                                                                                             self.AK4jetPtCut, 
                                                                                             self.ak4Jet.Eta(),
                                                                                             self.AK4EtaCut)       

        # NOTE: This jet cut was found to be strongly suboptimal by the semileptonic team. They had better performance at pt > 15 GeV, with 
        # delta R < 0.4 and ptrel > 20. For now, we will raise the HTLep cut and ptrel cut but we need to fix this.
        if not  (self.tree.AK4_dRminLep_dRlep[0] > self.DrAK4Lep or self.tree.PtRel[0] > self.PtRel ) : return self.passed
        self.passed[7] = True
        self.passedCount[7] += 1
        if self.verbose : print "Stage 7: DR(AK4, lep) {0:2.2f}  > ( {1:2.2f} ) or PtRel(AK4, lep) {2:2.2f} > ( {3:2.2f} )".format( 
                                                                                                      self.tree.AK4_dRminLep_dRlep[0],
                                                                                                                        self.DrAK4Lep,
                                                                                                                   self.tree.PtRel[0],
                                                                                                                           self.PtRel)
        if not ( self.tree.DeltaRJetLep[0] > 1. ) : return self.passed # Hemisphere cut btw lepton and the ak8
        self.passed[8] = True
        self.passedCount[8] += 1
        if self.verbose : print "Stage 8: DR(AK8, lep) {0:2.2f}  > ( 1.0 )".format( self.tree.DeltaRJetLep[0] )

        if self.tree.LeptonIsMu[0] > 0. :
            if not (self.leptonP4 + self.nuP4 ).Perp() > self.MuonHtLepCut  : return self.passed
        if self.tree.LeptonIsMu[0] < 1. :
            if not (self.leptonP4 + self.nuP4 ).Perp() > self.ElectronHtLepCut  : return self.passed
        self.passed[9] = True
        self.passedCount[9] += 1
        if self.verbose : print "Stage 9: Leptonic W Pt  (Lepton Pt + MET Pt ) {0:2.2f} > ( {1:2.2f} GeV )".format( (self.leptonP4 + self.nuP4).Perp(), self.MuonHtLepCut )

        return self.passed

    def MuonTriggEff(self, muonpt, muoneta, runNum) : #{ROOT file from
        #https://twiki.cern.ch/twiki/bin/view/CMS/MuonWorkInProgressAndPagResults
        ### TO-DO: Implement this for type 2 selection
        TriggEff = 1.
        runNumIs = None
        if  muonpt >= 500. and abs(muoneta) > 1.2 :
            TriggEff = 0.0
        else :
            ### Note: This needs to be updated as SFs for new data become available...
            ### To-DO: decide which percentage to weight by each run histo
            binx = self.PtetaTriggEff_Run274094_to_276097.GetXaxis().FindBin( muonpt  )
            biny = self.PtetaTriggEff_Run274094_to_276097.GetYaxis().FindBin( muoneta )
            TriggEff = self.PtetaTriggEff_Run274094_to_276097.GetBinContent(binx, biny )
            if self.verbose : print "get bin: x (using pt) {}, y (using eta) {}, CUt ID Eff is {}".format(binx, biny, TriggEff )

        return float(TriggEff)      
  

    def MuonCutIDScaleFTight(self, muonpt, muoneta) : #{ROOT file from
        #https://twiki.cern.ch/twiki/bin/view/CMS/MuonWorkInProgressAndPagResults
        ### TO-DO: Implement this for type 2 selection
        if muonpt >= 500. and abs(muoneta) > 1.2 :
            CutIDScaleFt = 0.0
        else :
            binx = self.PtetaCutIDScaleFTight.GetXaxis().FindBin( muonpt  )
            biny = self.PtetaCutIDScaleFTight.GetYaxis().FindBin( muoneta )
            CutIDScaleFt = self.PtetaCutIDScaleFTight.GetBinContent(binx, biny )
            if self.verbose : print "get bin: x (using pt) {}, y (using eta) {}, CUt ID Eff is {}".format(binx, biny, CutIDScaleFt )
        return float(CutIDScaleFt) 
     
    def MuonCutIDScaleFLoose(self, muonpt, muoneta) : #{ROOT file from
        #https://twiki.cern.ch/twiki/bin/view/CMS/MuonWorkInProgressAndPagResults
        ### TO-DO: Implement this for type 2 selection
        if  muonpt >= 500. and abs(muoneta) > 1.2 :
            CutIDScaleFl = 0.0
        else :
            binx = self.PtetaCutIDScaleFLoose.GetXaxis().FindBin( muonpt  )
            biny = self.PtetaCutIDScaleFLoose.GetYaxis().FindBin( muoneta )
            CutIDScaleFl = self.PtetaCutIDScaleFLoose.GetBinContent(binx, biny )
            if self.verbose : print "get bin: x (using pt) {}, y (using eta) {}, CUt ID Eff is {}".format(binx, biny, CutIDScaleFl )
        return float(CutIDScaleFl)    

    ### SF for High-pT ID and (detector based) Tracker Relative Isolation
    def MuonIsoScaleF(self, muonpt, muoneta) : #{ROOT file from
        #https://twiki.cern.ch/twiki/bin/view/CMS/MuonWorkInProgressAndPagResults            ### TO-DO: Implement this for type 2 selection
        MuonIsoScaleF = 1.
        if muonpt >= 500. and abs(muoneta) > 1.2 :
            MuonIsoScaleF = 0.0
        else :
            binx = self.fff.GetXaxis().FindBin( muonpt  )
            biny = self.fff.GetYaxis().FindBin( muoneta )
            MuonIsoScaleF = self.fff.GetBinContent(binx, biny )
            if self.verbose : print "get bin: x (using pt) {}, y (using eta) {}, CUt ID Eff is {}".format(binx, biny, MuonIsoScaleF )
        return float(MuonIsoScaleF)    

    ### HIP SF : muon tracking specific SFs covering HIP inefficiencies
    def MuonHIPScaleF(self,  muoneta) : #{ROOT file from
        #https://twiki.cern.ch/twiki/bin/view/CMS/MuonReferenceEffsRun2#Tracking_efficiency_provided_by       
        ### TO-DO: Implement this for type 2 selection
        MuonHIPScaleF = 1.

        MuonHIPScaleF = self.ratio_eta.Eval(muoneta)
        if self.verbose : print "(using eta) {}, HIP SF is {}".format(muoneta,  MuonHIPScaleF )
        return float(MuonHIPScaleF)    


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
