#! /usr/bin/env python


## _________                _____.__                            __  .__               
## \_   ___ \  ____   _____/ ____\__| ____  __ ______________ _/  |_|__| ____   ____  
## /    \  \/ /  _ \ /    \   __\|  |/ ___\|  |  \_  __ \__  \\   __\  |/  _ \ /    \ 
## \     \___(  <_> )   |  \  |  |  / /_/  >  |  /|  | \// __ \|  | |  (  <_> )   |  \
##  \______  /\____/|___|  /__|  |__\___  /|____/ |__|  (____  /__| |__|\____/|___|  /
##         \/            \/        /_____/                   \/                    \/ 
import sys
import math
import array as array
from optparse import OptionParser

from B2GTTreeSemiLepOut import B2GTTreeSemiLep
import B2GSelectSemiLepTTbar_Type1, B2GSelectSemiLepTTbar_Iso2D


import ROOT


class PlotSemiLepTTbar_HighMass() :
    '''
    Simple Plotter class for Semileptonic TTbar analyses.
    This will use "Selection" classes (the first below is B2GSelectSemiLepTTbar_Iso2D)


    '''
    

    def __init__(self, argv ) : 

        ###
        ### Get the command line options
        ###
        parser = OptionParser()

        parser.add_option('--infile', type='string', action='store',
                          dest='infile',
                          default = 'ttbarTuneCUETP8M2T4_highmass_METmu40el80ptRel10dRlep0p1.root',
                          help='Input file string')


        parser.add_option('--outfile', type='string', action='store',
                          dest='outfile',
                          default = 'outfile_PlotSemiLepTTbar_HighMass.root',
                          help='Output file string')

        parser.add_option('--ptrel', type='float', action='store',
                          dest='ptrel',
                          default = 30. ,
                          help='cut on relative pt btw ak4 and lepton')

        parser.add_option('--dRlep', type='float', action='store',
                          dest='dRlep',
                          default = 0.4,
                          help='cut on dR(AK4, lepton)')

        parser.add_option('--tau21Cut', type='float', action='store',
                          dest='tau21Cut',
                          default = 0.35,
                          help='Tau 21 cut')

        parser.add_option('--tau32Cut', type='float', action='store',
                          dest='tau32Cut',
                          default = 0.8,
                          help='Tau 32 cut')
        
        parser.add_option('--bdiscmin', type='float', action='store',
                          dest='bdiscmin',
                          default = 0.8484,
                          help='B discriminator cut')

        #parser.add_option('--wcand', type='int', action='store', #### !!!! Instead showing all 3 options on 1 plot
        #                  dest='wcand',                          #### most massive subjet is W candidate
        #                  default = 1,
        #                  help='Pick the W candidate subjet: 1 -most massive, 2 - lowest b disc, 3 - highest pt')

        parser.add_option('--binmin',dest="ptbinmin", 
                          default=200, 
                          type=int,
                          help="Minimum subjet 0 pt")

        parser.add_option('--binmax',dest="ptbinmax",
                          default=1000, 
                          type=int,
                          help="Maximum subjet 0 pt")
        (options, args) = parser.parse_args(argv)
        argv = []
     
        self.tau21Cut = options.tau21Cut
        self.tau32Cut = options.tau32Cut
        self.ptbinmin = options.ptbinmin
        self.ptbinmax = options.ptbinmax
        self.dRlep    = options.dRlep
        self.ptrel    = options.ptrel
   
        ### Counts of the W candidate subjet: 1 -most massive, 2 - lowest b disc, 3 - highest pt
        ### SJ0 is the leading pt subjet so countW3isSJ1 will always be 0
        self.countW1isSJ0 = 0
        self.countW1isSJ1 = 0
        self.countW2isSJ0 = 0
        self.countW2isSJ1 = 0
        self.countW3isSJ0 = 0
        self.countW3isSJ1 = 0

        self.countW1highMassandBdisc = 0 
        self.countW1highMassLowBdisc = 0
        self.countW2highMassandBdisc = 0 
        self.countW2highMassLowBdisc = 0
        self.countW3highMassandBdisc = 0 
        self.countW3highMassLowBdisc = 0

        ### Define counts of Gen Matched Ws in each category  passing and failing the options.tau21cut            
        self.countRealW1sInFail = 0
        self.countRealW1sInPass = 0
        self.countFakeW1sInFail = 0
        self.countFakeW1sInPass = 0
        self.countRealW2sInFail = 0
        self.countRealW2sInPass = 0
        self.countFakeW2sInFail = 0
        self.countFakeW2sInPass = 0
        self.countRealW3sInFail = 0
        self.countRealW3sInPass = 0
        self.countFakeW3sInFail = 0
        self.countFakeW3sInPass = 0        

        self.hists1D = {}
        self.hists2D = {}

        self.outfile = ROOT.TFile(options.outfile, "RECREATE")

        ### Create the tree class. This will make simple class members for each
        ### of the branches that we want to read from the Tree to save time.
        ### Also saved are some nontrivial variables that involve combinations
        ### of things from the tree
        self.treeobj = B2GTTreeSemiLep( options )
        
        print 'Getting entries'
        entries = self.treeobj.tree.GetEntries()
        self.eventsToRun = entries

        self.nlep = 2 # Electron and Muon are the 2 leptons considered

        ### Book histograms
        self.book()

    '''
    Coarse flow control. Loops over events, reads, and fills histograms. 
    Try not to modify anything here if you add something.
    Add whatever you can in "book" and "fill". If you need to add something
    complicated, cache it as a member variable in the Selector class you're interested
    in, and just make simple plots here. 
    '''
    def run(self):
        
        print 'processing ', self.eventsToRun, ' events'

        for jentry in xrange( self.eventsToRun ):
            if jentry % 100000 == 0 :
                print 'processing ' + str(jentry)
            ### get the next event            
            ientry = self.treeobj.tree.GetEntry( jentry ) 
       
            ### Get lepton and AK4 for 2D isolation plot
            self.leptonP4 = ROOT.TLorentzVector()
            self.leptonP4.SetPtEtaPhiM(
                                       self.treeobj.tree.LeptonPt,
                                       self.treeobj.tree.LeptonEta,
                                       self.treeobj.tree.LeptonPhi,
                                                           0. ) 

            self.ak4Jet = ROOT.TLorentzVector( )
            self.ak4Jet.SetPtEtaPhiM( self.treeobj.tree.AK4_dRminLep_Pt,
                                      self.treeobj.tree.AK4_dRminLep_Eta,
                                      self.treeobj.tree.AK4_dRminLep_Phi,
                                      self.treeobj.tree.AK4_dRminLep_Mass )             
            ### Get AK8 stuff -correct the subjets and sum to find SD+PUPPI AK8 mass
            PuppiJetCorr = self.treeobj.tree.JetPuppiCorrFactor
            
            self.ak8PuppiSDJetP4_Subjet0 = ROOT.TLorentzVector()
            self.ak8PuppiSDJetP4_Subjet0.SetPtEtaPhiM( self.treeobj.tree.JetPuppiSDsubjet0pt ,
                                                       self.treeobj.tree.JetPuppiSDsubjet0eta , 
                                                       self.treeobj.tree.JetPuppiSDsubjet0phi , 
                                                       self.treeobj.tree.JetPuppiSDsubjet0mass   )
            
            self.ak8PuppiSDJetP4_Subjet0Raw =   self.ak8PuppiSDJetP4_Subjet0 
            self.ak8PuppiSDJetP4_Subjet0 =   self.ak8PuppiSDJetP4_Subjet0  * PuppiJetCorr
            self.ak8subjet0PuppiSD_m = self.ak8PuppiSDJetP4_Subjet0.M()


            self.ak8PuppiSDJetP4_Subjet1 = ROOT.TLorentzVector()
            self.ak8PuppiSDJetP4_Subjet1.SetPtEtaPhiM( self.treeobj.tree.JetPuppiSDsubjet1pt ,
                                                       self.treeobj.tree.JetPuppiSDsubjet1eta , 
                                                       self.treeobj.tree.JetPuppiSDsubjet1phi , 
                                                       self.treeobj.tree.JetPuppiSDsubjet1mass   )
            self.ak8PuppiSDJetP4_Subjet1Raw =   self.ak8PuppiSDJetP4_Subjet1 
            self.ak8PuppiSDJetP4_Subjet1 =   self.ak8PuppiSDJetP4_Subjet1 * PuppiJetCorr
            self.ak8subjet1PuppiSD_m = self.ak8PuppiSDJetP4_Subjet1.M()

            self.ak8PuppiSDJetP4Raw =  self.ak8PuppiSDJetP4_Subjet0Raw +  self.ak8PuppiSDJetP4_Subjet1Raw
            #self.ak8PuppiSDJetP4Raw =   self.ak8PuppiSDJetP4
            self.ak8PuppiSDJetP4 = None
            self.ak8PuppiSD_m = 0.

            ### Only keep jets where both subjets have mass > 1 GeV
            if (self.ak8subjet1PuppiSD_m and self.ak8subjet0PuppiSD_m) > 1. :
                self.ak8PuppiSDJetP4 = self.ak8PuppiSDJetP4Raw * PuppiJetCorr            
                self.ak8PuppiSD_m = float(self.ak8PuppiSDJetP4.M()) 
            fatjetTau32 = self.treeobj.tree.JetPuppiTau32 

            ### Top mass window cut
            
            if  not ( 110. <= self.ak8PuppiSD_m <= 250.) : continue  

            ### Top tag loose n-subjettiness cut

            if  not ( fatjetTau32 <  self.tau32Cut) : continue

            ### Wtag mass window cut
            #if  not ( 10. <=  self.ak8subjet0PuppiSD_m <= 140.) : continue

            ### 2-D isolation cut (in the looser tree I applied [ ptRel > 10 OR dR > 0.1 ])
            if not (self.leptonP4.Perp(self.ak4Jet.Vect()) > self.ptrel or self.leptonP4.DeltaR(self.ak4Jet) > self.dRlep  ) : continue
           
            # fill histograms
            self.selectCountFill( )

        # Wrap it up. 
        print 'Finished looping'
        #self.close()
        #print 'Closed'



        
    def book( self ) :
        '''
        Book histograms, one for each stage of the selection. 
        '''
        self.outfile.cd()
    
        #self.hists1D = {}
        #self.hists2D = {}


        self.lepNames = ['Electron', 'Muon']

        self.titles1D = {
       # 'mostMassive':[';Most Massive Subjet Mass (GeV);Number', 130, 10, 140],
       # 'lowestBdisc':[';Lowest Bdisc Subjet Mass (GeV);Number', 130, 10, 140],
       # 'highestPt'  :[';Highest Pt   Subjet Mass (GeV);Number', 130, 10, 140],
        'dR_W_dfar_less0p8'  :[';Subjet Mass (GeV) ;Number', 65 , 10, 140],
        'AND_b_W_less0p5'    :[';Subjet Mass (GeV) ;Number', 65 , 10, 140],
        'AND_b_W_more0p5'    :[';Subjet Mass (GeV) ;Number', 65 , 10, 140],

        }
        
        ### TO-DO: Also make opposites leastMassive, highestBdisc, lowestpt
        
        for var in self.titles1D:
          title =  self.titles1D[var][0]   
          nbins =  self.titles1D[var][1]
          minval = self.titles1D[var][2]
          maxval = self.titles1D[var][3]
          th1name =   self.titles1D[var]  
          #print "var {} th1name {} title {}".format(var, th1name, title )
          self.hists1D[str(var)] = [      ROOT.TH1F(str(var)+'_'+self.lepNames[0]   , title , nbins , minval, maxval) ,
                                             ROOT.TH1F(str(var)+'_'+self.lepNames[1]  , title , nbins , minval, maxval) ,
                                             ROOT.TH1F(str(var)+'_ElandMu', title , nbins , minval, maxval) ]

        #print"Just created self.hists1D {}".format(self.hists1D)
        xhigh = 1.5
        xbins = 10
        self.titles2D = {
        'Iso2DHist':["Lepton 2D isolation (#Delta R vs p_{T}^{REL} );  dR(AK4, Lepton); p_{T}^{REL}(AK4, Lepton)", xbins, 0, 15, 20, 0, 2],

        'dRWcandWdfar_dRWcandb':[";dR(W cand jet, Wdfar); dR(W cand jet,b quark)", xbins, 0, xhigh, xbins, 0, xhigh],
        'dRWcandWdfar_dRWcandWdclose':[";dR(W cand jet, Wdfar ; dR(W cand jet, Wdclose) ", xbins, 0, xhigh, xbins, 0, xhigh],
        'dRWcandWdfar_dRbcandWdfar':[";dR(W cand jet, Wdfar ; dR(b cand jet, Wdfar) ", xbins, 0, xhigh, xbins, 0, xhigh],
        'dRWcandWdfar_dRbcandb':[";dR(W cand jet, Wdfar) ; dR(b cand jet, b quark) ", xbins, 0, xhigh, xbins, 0, xhigh],
        'dRWcandWdclose_dRbcandb':[";dR(W cand jet, Wdclose ); dR(b cand jet, b quark) ", xbins, 0, xhigh, xbins, 0, xhigh],
        'dRWcandb_dRbcandb':[";dR(W cand jet,b quark) ; dR(b cand jet, b quark) ", xbins, 0, xhigh, xbins, 0, xhigh],

        'ak8PuppiSDJetPt_dRWcandWdclose':[";AK8 PUPPI SD jet Pt (GeV) ; dR(W cand jet, Wdclose) ", 50, 400, 1000, xbins, 0, xhigh],
        'ak8PuppiSDJetPt_dRWcandWdfar':[";AK8 PUPPI SD jet Pt (GeV) ; dR(W cand jet,  Wdfar) ", 50, 400, 1000, xbins, 0, xhigh],
        'ak8PuppiSDJetPt_dRbcandb':[";AK8 PUPPI SD jet Pt (GeV) ; dR(b cand jet, b quark ) ", 50, 400, 1000, xbins, 0, xhigh],

        'ak8PuppiSDWSubJetPt_dRWcandWdclose':[";Most massive SD subjet Pt (GeV) ; dR(b cand jet, Wdclose ) ", 50, 200, 1000, xbins, 0, xhigh],
        'ak8PuppiSDWSubJetPt_dRWcandWdfar':[";Most massive SD subjet Pt (GeV) ; dR(b cand jet,  Wdfar) ", 50, 200, 1000, xbins, 0, xhigh],
        'ak8PuppiSDWSubJetPt_dRbcandb':[";Most massive SD subjet Pt (GeV) ; dR(b cand jet, b quark ) ", 50, 200, 1000, xbins, 0, xhigh],

        }

        for var in self.titles2D:
          title =  self.titles2D[var][0]   
          nbinsx =  self.titles2D[var][1]
          minx = self.titles2D[var][2]
          maxx = self.titles2D[var][3]
          nbinsy =  self.titles2D[var][4]
          miny = self.titles2D[var][5]
          maxy = self.titles2D[var][6]        
          th2name =   self.titles2D[var]       
          self.hists2D["%s"%var] =  [ ROOT.TH2F( var+ '_' + self.lepNames[0] , title , nbinsx , minx , maxx, nbinsy , miny , maxy) ,
                                           ROOT.TH2F( var+ '_' + self.lepNames[1], title , nbinsx , minx , maxx, nbinsy , miny , maxy) ,
                                           ROOT.TH2F( var+ '_ElandMu' , title , nbinsx , minx , maxx, nbinsy , miny , maxy) ]

    def selectCountFill( self) :
        '''
        Fill the histograms with gen matching criteria and variant W candidate subjets.
        '''
        
        ### Get neccessary info from the tree

        ilep = self.treeobj.tree.LeptonIsMu         



        ### Throw away events where subjets are too light
        #if (self.ak8PuppiSDJetP4_Subjet0.M() and self.ak8PuppiSDJetP4_Subjet1.M()) < 10. : continue

        SJ0tau1 = self.treeobj.tree.JetPuppiSDsubjet0tau1   
        SJ0tau2 = self.treeobj.tree.JetPuppiSDsubjet0tau2 
        SJ1tau1 = self.treeobj.tree.JetPuppiSDsubjet1tau1  
        SJ1tau2 = self.treeobj.tree.JetPuppiSDsubjet1tau2 

        SJ0tau21 = 10.
        SJ1tau21 = 10.
        if SJ0tau1 >= 0.1 :
          SJ0tau21 = SJ0tau2/ SJ0tau1
        if SJ1tau1 >= 0.1 :
          SJ1tau21 = SJ1tau2/ SJ1tau1

        SJ0Bdisc = self.treeobj.tree.JetPuppiSDsubjet0bdisc 
        SJ1Bdisc = self.treeobj.tree.JetPuppiSDsubjet1bdisc 

        ### Define the 3 W candidate categories
        self.SJ1 = None # Most massive
        self.SJ2 = None  # Lowest Bdisc
        self.SJ3 = None  # Highest Pt
        self.SJdR_W_dfar_less0p8 =  ROOT.TLorentzVector( )
        self.SJdR_W_dfar_less0p8_b_W_less0p5 =  ROOT.TLorentzVector( ) #None # Isolating different populations to see masses
        self.SJdR_W_dfar_less0p8_b_W_more0p5 =  ROOT.TLorentzVector( ) # None



        ### Tau21 in each of 3 cases
        tau21w1 = 10.
        tau21w2 = 10.
        tau21w3 = 10.

        ### Flag to know which subjet (0 or 1)is W candidate in each of 3 cases above (e.g case 3 is always True)
        self.subjet0isW1   =  False
        self.subjet0isW2   =  False
        self.subjet0isW3   =  False
        self.subjet1isW1   =  False
        self.subjet1isW2   =  False
        self.subjet1isW3   =  False

        ### Pick our W candidate from the 2 subjets. Currently definition 1, higher mass than the b candidate
        self.subjet0isW = self.subjet0isW1
        self.subjet1isW = self.subjet1isW1

        ### Pick the most massive as the W candidate
        #if self.whighMass == 1 :
        if (self.ak8PuppiSDJetP4_Subjet0.M() > self.ak8PuppiSDJetP4_Subjet1.M()) :
          self.subjet0isW1   = True
          self.countW1isSJ0 += 1
          tau21w1 = SJ0tau21
          self.SJ1 = self.ak8PuppiSDJetP4_Subjet0
        else:  
          self.subjet1isW1   = True
          self.countW1isSJ1 += 1
          tau21w1 = SJ1tau21
          self.SJ1 = self.ak8PuppiSDJetP4_Subjet1
    
        ### Pick the lowest Bdisc as the W candidate
        #if self.wlowBdisc == 1 :                                                                                                                                                          
        if SJ0Bdisc < SJ1Bdisc :                                                                                                                           
          self.subjet0isW2   = True                                                                                                                                                                          
          self.countW2isSJ0 += 1  
          tau21w2 = SJ0tau21  
          self.SJ2 = self.ak8PuppiSDJetP4_Subjet0                                                                                                                                                                        
        else:   
          self.subjet1isW2   = True
          self.countW2isSJ1 += 1  
          tau21w2 = SJ1tau21 
          self.SJ2 = self.ak8PuppiSDJetP4_Subjet1

        ### Pick the highest Pt as the W candidate
        #if self.whighPt == 1 :                                                                                                                                                                                                                                                                                   
        self.subjet0isW3   = True                                                                                                                                                                          
        self.countW3isSJ0 += 1        
        tau21w3 = SJ0tau21                                                                                                                                                                      
        self.SJ3 = self.ak8PuppiSDJetP4_Subjet0

        ### Decide on how W candidate subjet is picked ( options.wcand 1 for most massive, 2 for lowest b disc, 3 for highest pt)
        #self.whighMass = options.wcand      
        #self.wlowBdisc = options.wcand - 1  
        #self.whighPt   = options.wcand - 2   

        ### Count instances where W candidate has higher mass and higher bdisc 
        if self.subjet0isW1 :
          if SJ0Bdisc > SJ1Bdisc :
            self.countW1highMassandBdisc +=1
          else:
            self.countW1highMassLowBdisc +=1
        if self.subjet1isW1 :
          if SJ0Bdisc < SJ1Bdisc :
            self.countW1highMassandBdisc +=1
          else:
            self.countW1highMassLowBdisc +=1

        if self.subjet0isW2 :
          if self.ak8PuppiSDJetP4_Subjet0.M() > self.ak8PuppiSDJetP4_Subjet1.M() :
            self.countW2highMassLowBdisc +=1
        if self.subjet1isW2 :
          if self.ak8PuppiSDJetP4_Subjet0.M() < self.ak8PuppiSDJetP4_Subjet1.M() :
            self.countW2highMassLowBdisc +=1

        if self.subjet0isW3 :
          if (self.ak8PuppiSDJetP4_Subjet0.M() >self.ak8PuppiSDJetP4_Subjet1.M() ) and (SJ0Bdisc < SJ1Bdisc ) :
            self.countW3highMassLowBdisc +=1
          if (self.ak8PuppiSDJetP4_Subjet0.M() >self.ak8PuppiSDJetP4_Subjet1.M() ) and (SJ0Bdisc > SJ1Bdisc ) :
            self.countW3highMassandBdisc +=1

        #print"W candidate(higher mass subjet) has higher Bdisc than b candidate"

        isRealW1 = None
        isFakeW1 = None
        isRealW2 = None
        isFakeW2 = None
        isRealW3 = None
        isFakeW3 = None


                   #'dRWcandWdfar_dRWcandb':["dR(W candidate,[farthest daughter quark, b quark]), ", 25, 0, 1, 25, 0, 1]}
        ### Define dRs btw W candidate and W daughter quarks as well as b quark
        ### Note: These are set the Case 1 definition of W candidate (highest mass subjet)
        ### dR(W candidate subjet, daughter quark which is farthest from this subjet)
        self.dRWcandWdfar = None
        ### dR(W candidate subjet, daughter quark which is closest to this subjet)
        self.dRWcandWdclose = None
        ### dR(W candidate subjet, b quark )
        self.dRWcandb = None      
        ### dR(b candidate subjet, daughter quark which is farthest from W candidate subjet)
        self.dRbcandWdfar = None
        ### dR(b candidate subjet, daughter quark which is closest to W candidate subjet)
        self.dRbcandWdclose = None
        ### dR(b candidate subjet, b quark )
        self.dRbcandb = None

        ### If highest Pt subjet is also most massive
        if self.subjet0isW1 :
          self.dRWcandb = self.treeobj.tree.JetGenMatched_DeltaR_pup0_b
          self.dRbcandb = self.treeobj.tree.JetGenMatched_DeltaR_pup1_b
          if (self.treeobj.tree.JetGenMatched_DeltaR_pup0_Wd1  < self.treeobj.tree.JetGenMatched_DeltaR_pup0_Wd2):
              self.dRWcandWdclose =  self.treeobj.tree.JetGenMatched_DeltaR_pup0_Wd1
              self.dRWcandWdfar =  self.treeobj.tree.JetGenMatched_DeltaR_pup0_Wd2
              self.dRbcandWdclose =  self.treeobj.tree.JetGenMatched_DeltaR_pup1_Wd1
              self.dRbcandWdfar =  self.treeobj.tree.JetGenMatched_DeltaR_pup1_Wd2
          if (self.treeobj.tree.JetGenMatched_DeltaR_pup0_Wd1  > self.treeobj.tree.JetGenMatched_DeltaR_pup0_Wd2):
              self.dRWcandWdclose =  self.treeobj.tree.JetGenMatched_DeltaR_pup0_Wd2
              self.dRWcandWdfar =  self.treeobj.tree.JetGenMatched_DeltaR_pup0_Wd1
              self.dRbcandWdclose =  self.treeobj.tree.JetGenMatched_DeltaR_pup1_Wd2
              self.dRbcandWdfar =  self.treeobj.tree.JetGenMatched_DeltaR_pup1_Wd1

          if (self.treeobj.tree.JetGenMatched_DeltaR_pup0_Wd1  < self.treeobj.tree.JetGenMatched_DeltaR_pup0_b )  and  (self.treeobj.tree.JetGenMatched_DeltaR_pup0_Wd2  < self.treeobj.tree.JetGenMatched_DeltaR_pup0_b ) :
            isRealW1 = 1
            isFakeW1 = 0
          else:
            isRealW1 = 0
            isFakeW1 = 1
        ### If Lower Pt subjet is most massive
        if self.subjet1isW1 :
          self.dRWcandb = self.treeobj.tree.JetGenMatched_DeltaR_pup1_b
          self.dRbcandb = self.treeobj.tree.JetGenMatched_DeltaR_pup0_b
          if (self.treeobj.tree.JetGenMatched_DeltaR_pup1_Wd1  < self.treeobj.tree.JetGenMatched_DeltaR_pup1_Wd2):
              self.dRWcandWdclose =  self.treeobj.tree.JetGenMatched_DeltaR_pup1_Wd1
              self.dRWcandWdfar =  self.treeobj.tree.JetGenMatched_DeltaR_pup1_Wd2
              self.dRbcandWdclose =  self.treeobj.tree.JetGenMatched_DeltaR_pup0_Wd1
              self.dRbcandWdfar =  self.treeobj.tree.JetGenMatched_DeltaR_pup0_Wd2
          if (self.treeobj.tree.JetGenMatched_DeltaR_pup1_Wd1  > self.treeobj.tree.JetGenMatched_DeltaR_pup1_Wd2):
              self.dRWcandWdclose =  self.treeobj.tree.JetGenMatched_DeltaR_pup1_Wd2
              self.dRWcandWdfar =  self.treeobj.tree.JetGenMatched_DeltaR_pup1_Wd1
              self.dRbcandWdclose =  self.treeobj.tree.JetGenMatched_DeltaR_pup0_Wd2
              self.dRbcandWdfar =  self.treeobj.tree.JetGenMatched_DeltaR_pup0_Wd1         

        ### Isolating different populations from 2D plots to see mass distribution differences                                         
        if self.dRWcandWdfar < 0.8 :
          self.SJdR_W_dfar_less0p8 = self.SJ1
        if (self.dRWcandWdfar < 0.8) and (self.dRbcandWdfar < 0.5):
           self.SJdR_W_dfar_less0p8_b_W_less0p5 =  self.SJ1
        if (self.dRWcandWdfar < 0.8) and (self.dRbcandWdfar > 0.5):
          self.SJdR_W_dfar_less0p8_b_W_more0p5 =  self.SJ1

        ### Loose Gen matching requirement
        ### Real means both W daughter quarks are closer to the W than the b with no additional dR cut
        if self.subjet0isW1 :
          if (self.treeobj.tree.JetGenMatched_DeltaR_pup0_Wd1  < self.treeobj.tree.JetGenMatched_DeltaR_pup0_b )  and  (self.treeobj.tree.JetGenMatched_DeltaR_pup0_Wd2  < self.treeobj.tree.JetGenMatched_DeltaR_pup0_b ) :
            isRealW1 = 1
            isFakeW1 = 0
          else:
            isRealW1 = 0
            isFakeW1 = 1
        if self.subjet1isW1 :
          if (self.treeobj.tree.JetGenMatched_DeltaR_pup1_Wd1  < self.treeobj.tree.JetGenMatched_DeltaR_pup1_b )  and  (self.treeobj.tree.JetGenMatched_DeltaR_pup1_Wd2  < self.treeobj.tree.JetGenMatched_DeltaR_pup1_b ) :  
            isRealW1 = 1
            isFakeW1 = 0
          else:
            isRealW1 = 0
            isFakeW1 = 1
        if self.subjet0isW2 :
          if (self.treeobj.tree.JetGenMatched_DeltaR_pup0_Wd1  < self.treeobj.tree.JetGenMatched_DeltaR_pup0_b )  and  (self.treeobj.tree.JetGenMatched_DeltaR_pup0_Wd2  < self.treeobj.tree.JetGenMatched_DeltaR_pup0_b ) :
            isRealW2 = 1
            isFakeW2 = 0
          else:
            isRealW2 = 0
            isFakeW2 = 1
        if self.subjet1isW2 :
          if (self.treeobj.tree.JetGenMatched_DeltaR_pup1_Wd1  < self.treeobj.tree.JetGenMatched_DeltaR_pup1_b )  and  (self.treeobj.tree.JetGenMatched_DeltaR_pup1_Wd2  < self.treeobj.tree.JetGenMatched_DeltaR_pup1_b ) :  
            isRealW2 = 1
            isFakeW2 = 0
          else:
            isRealW2 = 0
            isFakeW2 = 1        ### See how many gen matched Ws pass and fail the tau21 cut
        if self.subjet0isW3 :
          if (self.treeobj.tree.JetGenMatched_DeltaR_pup0_Wd1  < self.treeobj.tree.JetGenMatched_DeltaR_pup0_b )  and  (self.treeobj.tree.JetGenMatched_DeltaR_pup0_Wd2  < self.treeobj.tree.JetGenMatched_DeltaR_pup0_b ) :
            isRealW3 = 1
            isFakeW3 = 0
          else:
            isRealW3 = 0
            isFakeW3 = 1
        if self.subjet1isW3 :
          if (self.treeobj.tree.JetGenMatched_DeltaR_pup1_Wd1  < self.treeobj.tree.JetGenMatched_DeltaR_pup1_b )  and  (self.treeobj.tree.JetGenMatched_DeltaR_pup1_Wd2  < self.treeobj.tree.JetGenMatched_DeltaR_pup1_b ) :  
            isRealW3 = 1
            isFakeW3 = 0
          else:
            isRealW3 = 0
            isFakeW3 = 1
        
        ### Count numbers of real and fake Ws in pass and fail for this tau21 cut
        if  isRealW1 == 1 :
          if tau21w1 >= self.tau21Cut :
            self.countRealW1sInFail += 1
          else :                                                             
            self.countRealW1sInPass += 1
        if  isFakeW1 == 1 :
          if tau21w1 >= self.tau21Cut : 
            self.countFakeW1sInFail += 1
          else :                                                            
            self.countFakeW1sInPass += 1

        if  isRealW2 == 1 :
          if tau21w2 >= self.tau21Cut :
            self.countRealW2sInFail += 1
          else :                                                             
            self.countRealW2sInPass += 1
        if  isFakeW2 == 1 :
          if tau21w2 >= self.tau21Cut : 
            self.countFakeW2sInFail += 1
          else :                                                            
            self.countFakeW2sInPass += 1

        if  isRealW3 == 1 :
          if tau21w3 >= self.tau21Cut :
            self.countRealW3sInFail += 1
          else :                                                             
            self.countRealW3sInPass += 1
        if  isFakeW3 == 1 :
          if tau21w3 >= self.tau21Cut : 
            self.countFakeW3sInFail += 1
          else :                                                            
            self.countFakeW3sInPass += 1

        ### Fill the histograms
        if self.ak8PuppiSDJetP4 != None:
            ### Choose which pt bin to plot  
            ### NOTE: counts are for all Pt bins
            SJpts = [self.SJ1.Pt() ]#, self.SJ2.Pt()  , self.SJ3.Pt() ]
            SJws =  [self.subjet0isW1 or self.subjet1isW1, self.subjet0isW2 or self.subjet1isW2, self.subjet0isW3 or self.subjet1isW3 ]

            for isj, sjpt in enumerate(SJpts):
                if (SJws[isj] ):
                    if not ( self.ptbinmin <= sjpt <= self.ptbinmax ): continue
            ### Store the values to fill into the TH1Fs        
            SJmasses = [
                         #self.SJ1.M()  , 
                         #self.SJ2.M()  , 
                         #self.SJ3.M()  ,
                         self.SJdR_W_dfar_less0p8.M()  ,
                         self.SJdR_W_dfar_less0p8_b_W_less0p5.M(),
                         self.SJdR_W_dfar_less0p8_b_W_more0p5.M(),

  ]
            ### Fill all TH1Fs  
            for ival, val in enumerate(self.hists1D.itervalues()):
                #print"Filling TH1Fs : val {} val[ilep] {}".format(val, val[ilep])
                val[ilep].Fill(SJmasses[ival])                         # Fill either Electron or Muon histo
                if ilep == (0 or 1): val[2].Fill(SJmasses[ival])       # Always Fill Electron + Muon histo
            
            ### 2D histogram filling
            if self.ak4Jet != None : 
                self.WcandP4 = self.SJ1 # <-- Most massive subjet    ROOT.TLorentzVector()
                '''
                if self.subjet0isW :
                    self.WcandP4 = self.SJ1 self.ak8PuppiSDJetP4_Subjet0
                if self.subjet1isW :
                    self.WcandP4 = self.ak8PuppiSDJetP4_Subjet1
                '''
                ### Fix this : surely theres a better way to fill the 2d histos
                ### Store values to fill 2D hists [x,y]
                fill2d = [ 
                          #[self.treeobj.tree.PtRel, self.treeobj.tree.AK4_dRminLep_dRlep],
                          [self.leptonP4.Perp(self.ak4Jet.Vect()), self.leptonP4.DeltaR( self.ak4Jet ) ],
                          #[self.ak4Jet.DeltaR( self.leptonP4 ) , self.ak4Jet.Perp(self.leptonP4.Vect()) ],

                          [self.dRWcandWdfar , self.dRWcandb ],
                          [self.dRWcandWdfar , self.dRWcandWdclose ],
                          [self.dRWcandWdfar , self.dRbcandWdfar ],
                          [self.dRWcandWdfar , self.dRbcandb ],
                          [self.dRWcandWdclose , self.dRbcandb ],
                          [self.dRWcandb , self.dRbcandb ],

                          [self.ak8PuppiSDJetP4.Pt() , self.dRWcandWdclose ],
                          [self.ak8PuppiSDJetP4.Pt() , self.dRWcandWdfar ],
                          [self.ak8PuppiSDJetP4.Pt() , self.dRbcandb ],

                          [self.WcandP4.Pt() , self.dRWcandWdclose ],
                          [self.WcandP4.Pt() , self.dRWcandWdfar ],
                          [self.WcandP4.Pt() , self.dRbcandb ]

                         ]
                ### Fill the TH2Fs          
                for ival, val in enumerate(self.hists2D.itervalues()):
                    val[ilep].Fill(fill2d[ival][0], fill2d[ival][1])
                    if ilep == (0 or 1): val[2].Fill(fill2d[ival][0], fill2d[ival][1]) # Always Fill Electron + Muon histo

    def close( self ) :
        '''
        Wrap it up. 
        '''
        self.outfile.cd() 
        self.outfile.Write()
        self.outfile.Close()

        '''

        print"              W candidate event counts                    "
        print"    WARNING: Counts are for all pt bins but plots are not "
        print".........................................................."
        print"Case 1:          W is most massive"
        print".........................................................."
        print"W is leading pt subjet     {0} of {1} total".format(self.countW1isSJ0 , self.countW1isSJ0+self.countW1isSJ1)
        print"W has high mass and low B disc {0} of {1} total".format(self.countW1highMassLowBdisc  , self.countW1highMassandBdisc + self.countW1highMassLowBdisc)
        print""
        print"Gen Matching:"
        print"Loose - Both W daughter quarks closer to W than b "
        print"W is real    {0} ".format( self.countRealW1sInFail + self.countRealW1sInPass )
        print"W is fake    {0} ".format( self.countFakeW1sInFail + self.countFakeW1sInPass )
        print""
        print"W tag:"
        print"WP - tau21 < {}".format(self.tau21Cut)
        print"real Ws Passed {}".format(self.countRealW1sInPass)
        print"fake Ws Passed {}".format(self.countFakeW1sInPass)
        print""
        print"real Ws Failed {}".format(self.countRealW1sInFail)
        print"fake Ws Failed {}".format(self.countFakeW1sInFail)
        print".........................................................."
        print"Case 2:          W is lowest Bdisc"
        print".........................................................."
        print"W is leading pt subjet     {0} of {1} total".format(self.countW2isSJ0 , self.countW2isSJ0+self.countW2isSJ1)
        print"W has high mass and low B disc {0} of {1} total".format(self.countW2highMassLowBdisc  , self.countW2isSJ0+self.countW2isSJ1 )
        print""
        print"Gen Matching:"
        print"Loose - Both W daughter quarks closer to W than b "
        print"W is real    {0} ".format( self.countRealW2sInFail + self.countRealW2sInPass )
        print"W is fake    {0} ".format( self.countFakeW2sInFail + self.countFakeW2sInPass )
        print""
        print"W tag:"
        print"WP - tau21 < {}".format(self.tau21Cut)
        print"real Ws Passed {}".format(self.countRealW2sInPass)
        print"fake Ws Passed {}".format(self.countFakeW2sInPass)
        print""
        print"real Ws Failed {}".format(self.countRealW2sInFail)
        print"fake Ws Failed {}".format(self.countFakeW2sInFail)
        print".........................................................."
        print"Case 3:          W is highest Pt"
        print".........................................................."
        print"W is leading pt subjet     {0} of {1} total".format(self.countW3isSJ0 , self.countW3isSJ0+self.countW3isSJ1)
        print"W has high mass and low B disc {0} of {1} total".format(self.countW3highMassLowBdisc  , self.countW3highMassandBdisc + self.countW3highMassLowBdisc)
        print""
        print"Gen Matching:"
        print"Loose - Both W daughter quarks closer to W than b "
        print"W is real    {0} ".format( self.countRealW3sInFail + self.countRealW3sInPass )
        print"W is fake    {0} ".format( self.countFakeW3sInFail + self.countFakeW3sInPass )
        print""
        print"W tag:"
        print"WP - tau21 < {}".format(self.tau21Cut)
        print"real Ws Passed {}".format(self.countRealW3sInPass)
        print"fake Ws Passed {}".format(self.countFakeW3sInPass)
        print""
        print"real Ws Failed {}".format(self.countRealW3sInFail)
        print"fake Ws Failed {}".format(self.countFakeW3sInFail)
        '''


    def plot1D( self ) :
        '''
        Plot all histos you just created
        '''

        ROOT.gStyle.SetOptStat(000000)
        self.c1 = ROOT.TCanvas("c1" , "c1" ,1,1,745,701)
        self.c1.SetHighLightColor(2)
        self.c1.Range(0,0,1,1)
        self.c1.SetFillColor(0)
        self.c1.SetBorderMode(0)
        self.c1.SetBorderSize(2)
        self.c1.SetTickx(1)
        self.c1.SetTicky(1)
        self.c1.SetLeftMargin(0.14)
        self.c1.SetRightMargin(0.04)
        self.c1.SetTopMargin(0.08)
        self.c1.SetBottomMargin(0.15)
        self.c1.SetFrameFillStyle(0)
        self.c1.SetFrameBorderMode(0)

        ### Set x axis range for W candidate Mass plot
        rangeMin = 50
        rangeMax = 140

        ### Set colors for the W candidates
        colorslist = [ROOT.kViolet+8 ,ROOT.kAzure+8, ROOT.kPink+8]
            
        ### Create the legend
        self.leg = ROOT.TLegend(0.58,0.7,0.65,0.84)
        self.leg.SetFillColor(0)
        self.leg.SetBorderSize(0)
        self.leg.SetTextSize(0.025)
        ### FIX THIS: Eventually plot merged and unmerged for each category
        ### self.leg.AddEntry( self.ttbarUnmerged, 'Unmatched   t#bar{t} ', 'f')
        ### self.leg.AddEntry( self.ttbarMerged,   'Gen-Matched t#bar{t} ', 'f')
        ###  For now only plot the histograms with both Electrons and Muons val[2] (val  is electrons and val[1] is muons )      
        
        self.y_max = 1.6
        ith1 = 0
        for nameof , th1 in self.hists1D.iteritems() :      
            #print"th1 is {} and th1[2] is {}".format(th1, th1[2] )
            #th1[2].GetXaxis().SetRangeUser( rangeMin, rangeMax )
            th1[2].GetXaxis().SetNdivisions(506)
            th1[2].GetXaxis().SetLabelFont(42)
            th1[2].GetXaxis().SetLabelSize(0.05)
            th1[2].GetXaxis().SetTitleSize(0.0475)
            th1[2].GetXaxis().SetTickLength(0.045)
            th1[2].GetXaxis().SetTitleOffset(1.15)
            th1[2].GetXaxis().SetTitleFont(42)
            th1[2].GetXaxis().SetTitle("[Most Massive] PUPPI softdrop subjet mass (GeV)")

            th1[2].SetMaximum(self.y_max * th1[2].GetMaximum() )
            th1[2].SetMinimum(0.0001 )
            th1[2].GetYaxis().SetTitle("Events")
            th1[2].GetYaxis().SetNdivisions(506)
            th1[2].GetYaxis().SetLabelFont(42)
            th1[2].GetYaxis().SetLabelSize(0.035)
            th1[2].GetYaxis().SetTitleSize(0.04)
            th1[2].GetYaxis().SetTitleOffset(0.9)
            th1[2].GetYaxis().SetTitleFont(42)   

            th1[2].SetLineColor(colorslist[ith1])
            ith1+=1
            th1[2].SetLineStyle(0)
            if ith1 > 0 : th1[2].Draw("hist same")
            else : th1[2].Draw("hist")

            self.leg.AddEntry( th1[2] , nameof , 'l')

        self.leg.Draw()
        '''
        self.words = ROOT.TLatex(0.14,0.916,"#font[62]{CMS} #font[52]{Preliminary}")
        self.words.SetNDC()
        self.words.SetTextFont(42)
        self.words.SetTextSize(0.0725)
        self.words.SetLineWidth(2)
        self.words.Draw()
        
        ttTune = None
        self.otherttbar = False
        if self.otherttbar == True :
            ttTune = '#scale[0.6]{(80X Powheg + Pythia 8) Tune CUETP8M2T4}'
        else: ttTune = '#scale[0.6]{(80X Powheg + Pythia 8) Tune CUETP8M1} '

        self.words1 = ROOT.TLatex(0.7,0.916, ttTune)
        self.words1.SetNDC()
        self.words1.SetTextAlign(31)
        self.words1.SetTextFont(42)
        self.words1.SetTextSize(0.0725)
        self.words1.SetLineWidth(2)
        self.words1.Draw()
        '''
        self.c1.Modified()
        self.c1.Print("./ttbarStudies/SDsubjet3WcandPopulations.png", "png")
        ### End plotting of TH1Fs
    def plot2D( self ) :
        ### Begin plotting of TH2Fs
        ROOT.gStyle.SetOptStat(000000)
        ith2 = 0
        for nameof , th2 in self.hists2D.iteritems() :      
            #print"th2 is {} and th2[2] is {}".format(th2, th2[2] )      
            self.c2 = ROOT.TCanvas("c2"+ nameof , "c2" + nameof ,1,1,745,701)
            self.c2.SetHighLightColor(2)
            self.c2.Range(0,0,1,1)
            self.c2.SetFillColor(0)
            self.c2.SetBorderMode(0)
            self.c2.SetBorderSize(2)
            self.c2.SetTickx(1)
            self.c2.SetTicky(1)
            self.c2.SetLeftMargin(0.14)
            self.c2.SetRightMargin(0.04)
            self.c2.SetTopMargin(0.08)
            self.c2.SetBottomMargin(0.15)
            self.c2.SetFrameFillStyle(0)
            self.c2.SetFrameBorderMode(0)     

            th2[2].GetXaxis().SetNdivisions(506)
            th2[2].GetXaxis().SetLabelFont(42)
            th2[2].GetXaxis().SetLabelSize(0.05)
            th2[2].GetXaxis().SetTitleSize(0.0475)
            th2[2].GetXaxis().SetTickLength(0.045)
            th2[2].GetXaxis().SetTitleOffset(1.15)
            th2[2].GetXaxis().SetTitleFont(42)
            #th2[2].GetXaxis().SetTitle("")

            #th2[2].SetMaximum(self.y_max * th2[2].GetMaximum() )
            th2[2].SetMinimum(0.0001 )
            #th2[2].GetYaxis().SetTitle("")
            th2[2].GetYaxis().SetNdivisions(506)
            th2[2].GetYaxis().SetLabelFont(42)
            th2[2].GetYaxis().SetLabelSize(0.04375)
            th2[2].GetYaxis().SetTitleSize(0.04225)
            th2[2].GetYaxis().SetTitleOffset(1.1)
            th2[2].GetYaxis().SetTitleFont(42)   

            #th2[2].SetLineColor(colorslist[ith1])
            ith2+=1
            #th2[2].SetLineStyle(0)
            th2[2].Draw("colz")
            self.c2.Modified()
            self.c2.Print("./ttbarStudies/2Dplotof_{}.png".format(nameof), "png")

        ### Write the output tree and close the outfile
        self.close()
        print 'Closed'
'''
        Executable
'''
if __name__ == "__main__" :
    r = PlotSemiLepTTbar_HighMass(sys.argv)
    r.run()
    r.plot1D()
    r.plot2D()
