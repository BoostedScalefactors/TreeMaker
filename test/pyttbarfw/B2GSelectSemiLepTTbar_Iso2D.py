#! /usr/bin/env python

import ROOT

import TrigMap

class B2GSelectSemiLepTTbar_Iso2D( ) :
    """
    Selects boosted semileptonic ttbar events with standard isolation.
    """
    def __init__(self, options, tree ):
        self.ignoreTrig = options.ignoreTrig
        self.nstages = 8
        self.tree = tree        
        self.trigMap = TrigMap.TrigMap()

        # Cached class member variables for plotting
        self.leptonP4 = None
        self.nuP4 = None

        self.trigIndex = [
            self.trigMap.HLT_Mu30_eta2p1_PFJet150_PFJet50_v,
            self.trigMap.HLT_Mu40_eta2p1_PFJet200_PFJet50_v,
            #self.trigMap.HLT_Ele45_CaloIdVT_GsfTrkIdT_PFJet200_PFJet50_v,
            #self.trigMap.HLT_Ele50_CaloIdVT_GsfTrkIdT_PFJet140_v,
            #self.trigMap.HLT_Ele50_CaloIdVT_GsfTrkIdT_PFJet165_v
            ]

        #self.printAK4Warning = True

        self.passed = [False] * self.nstages  
        self.passedCount = [0] * self.nstages

    """
        This is the "select" function that does the work for the event selection. If you have any complicated
        stuff to do, do it here and create a class member variable to cache the results. 
    """
    def select( self ) :

        self.leptonP4 = None
        self.nuP4 = None
        self.ak4Jet = None
        self.ak8Jet = None
        self.ak8SDJet = None
        

        self.leptonP4 = ROOT.TLorentzVector()
        self.leptonP4.SetPtEtaPhiM( self.tree.LeptonPt[0], self.tree.LeptonEta[0], self.tree.LeptonPhi[0], 0)
        self.nuP4 = ROOT.TLorentzVector( self.tree.SemiLeptMETpt[0], self.tree.SemiLeptMETpx[0], self.tree.SemiLeptMETpy[0], 0. )
        self.ak4Jet = ROOT.TLorentzVector()
        self.ak4Jet.SetPtEtaPhiM( self.tree.AK4_dRminLep_Pt[0], self.tree.AK4_dRminLep_Eta[0], self.tree.AK4_dRminLep_Phi[0], self.tree.AK4_dRminLep_Mass[0] )
        '''
        if self.printAK4Warning :
            print '----------------------------------- WARNING --------------------------------------'
            print '    AK4 jet mass is not set correctly. It is set to zero because it is not filled.'
            print '    To be fixed. Do NOT use the AK4 four vector, but you can use the three vector.'
            self.printAK4Warning = False
        '''
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

        if not self.ignoreTrig : 
            for itrig in self.trigIndex :
                if bool ( self.tree.SemiLeptTrigPass[itrig] ) == True :
                    self.passed[1] = True
            if not self.passed[1] : return self.passed
        else :
            self.passed[1] = True
        self.passedCount[1] += 1

        if not (( self.tree.LeptonIsMu[0] == 1 and self.leptonP4.Perp() > 50. and abs(self.leptonP4.Eta()) < 2.1  ) or (self.tree.LeptonIsMu[0] == 0 and  self.leptonP4.Perp() > 50. and abs(self.leptonP4.Eta()) < 2.5 )) : #and self.tree.MuTight[0]
            return self.passed
        self.passed[2] = True
        self.passedCount[2] += 1
        
        if not ( self.nuP4.Perp() > 50.) : return self.passed
        self.passed[3] = True
        self.passedCount[3] += 1

        # NOTE: This jet cut was found to be strongly suboptimal by the semileptonic team. They had better performance at pt > 15 GeV, with 
        # delta R < 0.4 and ptrel > 20. For now, we will raise the HTLep cut and ptrel cut but we need to fix this. 
        if not ( self.ak4Jet.Perp() > 15. and abs(self.ak4Jet.Eta()) < 3.0  ) : return self.passed    
        self.passed[4] = True
        self.passedCount[4] += 1
        
        # NOTE: I changed this from DeltRJetLep which is dR(lep, AK8) 
        # https://github.com/cmsb2g/B2GTTbar/blob/79ec8fcd1965adb4840b448bfaa4f9049df76f6d/plugins/B2GTTbarTreeMaker.cc#L4621
        if not  (self.tree.AK4_dRminLep_dRlep[0] > 0.4 or self.tree.PtRel[0] > 20 ) : return self.passed
        self.passed[5] = True
        self.passedCount[5] += 1

        if not ( self.tree.DeltaRJetLep[0] > 1. ) : return self.passed # Hemisphere cut btw lepton and the ak8
        self.passed[6] = True
        self.passedCount[6] += 1

        if not ( (self.leptonP4 + self.nuP4).Perp() > 150. ) : return self.passed
        self.passed[7] = True
        self.passedCount[7] += 1


        return self.passed#, self.passedCount

                    

    
