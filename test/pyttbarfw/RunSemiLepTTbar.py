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

from B2GTTreeSemiLep import B2GTTreeSemiLep
import B2GSelectSemiLepTTbar_Type2, B2GSelectSemiLepTTbar_IsoStd , B2GSelectSemiLepTTbar_Type1, B2GSelectSemiLepTTbar_Iso2D

import time as time
import ROOT


class RunSemiLepTTbar(OptionParser) :
    '''
    Driver class for Semileptonic TTbar analyses.
    This will use "Selection" classes (the first below is B2GSelectSemiLepTTbar)
    that return a bitset of cuts at different phases. This class can then
    make plots at those stages of selection.

    The factorization allows different drivers to use the same selection classes
    with the same bitsets, or to use different selections to use the same histogramming
    functionality.


    '''
    

    def __init__(self, argv ) : 

        ###
        ### Get the command line options
        ###
        parser = OptionParser()

        parser.add_option('--infile', type='string', action='store',
                          dest='infile',
                          default = '',
                          help='Input file string')


        parser.add_option('--outfile', type='string', action='store',
                          dest='outfile',
                          default = '',
                          help='Output file string')

        parser.add_option('--tau21Cut', type='float', action='store',
                          dest='tau21Cut',
                          default = 0.4,
                          help='Tau 21 cut')

        parser.add_option('--tau32Cut', type='float', action='store',
                          dest='tau32Cut',
                          default = 0.69,
                          help='Tau 32 cut')
        
        parser.add_option('--bdiscmin', type='float', action='store',
                          dest='bdiscmin',
                          default = 0.8,
                          help='B discriminator cut')

        parser.add_option('--ignoreTrig', action='store_true',
                          dest='ignoreTrig',
                          default = False,
                          help='Ignore the trigger?')
        
        parser.add_option('--Type2', action='store_true',
                          default=False,
                          dest='Type2',
                          help='Do you want to apply selection for type 2 tops as described in AN-16-215 ?')

        parser.add_option('--verbose', action='store_true',
                          default=False,
                          dest='verbose',
                          help='Do you want to print values of key variables?')

        (options, args) = parser.parse_args(argv)
        argv = []

        self.startTime = time.time()


        self.outfile = ROOT.TFile(options.outfile, "RECREATE")

        ### Create the tree class. This will make simple class members for each
        ### of the branches that we want to read from the Tree to save time.
        ### Also saved are some nontrivial variables that involve combinations
        ### of things from the tree
        self.treeobj = B2GTTreeSemiLep( options )

        self.options = options

        print 'Getting entries'
        entries = self.treeobj.tree.GetEntries()
        self.eventsToRun = entries
        ### Save event weights for negative weight rescaling of MC
        self.theWeightList = []

        ###  Count number of events with negative weights
        self.NegWeightsnum = 0.

        ###  Sum all weights in event
        self.Weightssum = 0.

        ### Here is the semileptonic ttbar selection for W jets
        if options.Type2 :
            self.lepSelection = B2GSelectSemiLepTTbar_IsoStd.B2GSelectSemiLepTTbar_IsoStd( options, self.treeobj )
            self.hadSelection = B2GSelectSemiLepTTbar_Type2.B2GSelectSemiLepTTbar_Type2( options, self.treeobj, self.lepSelection )
        else :
            self.lepSelection = B2GSelectSemiLepTTbar_Iso2D.B2GSelectSemiLepTTbar_Iso2D( options, self.treeobj )
            self.hadSelection = B2GSelectSemiLepTTbar_Type1.B2GSelectSemiLepTTbar_Type1( options, self.treeobj, self.lepSelection )
        self.nstages = self.lepSelection.nstages + self.hadSelection.nstages

        ### Array to count events passing each stage Fix this: auto set to correct nstages total

        self.passedCutCount = [] 
        for count in xrange(0, self.lepSelection.nstages):
            self.passedCutCount.append(    self.lepSelection.passedCount[count]            )
        for count in xrange(0, self.hadSelection.nstages):
            self.passedCutCount.append(    self.hadSelection.passedCount[count]            )


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
            # get the next tree in the chain and verify            
            ientry = self.treeobj.tree.GetEntry( jentry )        
            # Select events, get the bitset corresponding to the cut flow
            passbitsLep = self.lepSelection.select()
            passbitsHad = self.hadSelection.select()
            passbits = passbitsLep + passbitsHad
            # For each stage in the cut flow, make plots
            for ipassbit in xrange( len(passbits) ) :
                if passbits[ipassbit] :
                    self.fill( ipassbit )

        # Wrap it up. 
        print 'Finished looping'
        self.close()
        print 'Closed'



        
    def book( self ) :
        '''
        Book histograms, one for each stage of the selection. 
        '''
        self.outfile.cd()

        self.LeptonPtHist = []
        self.LeptonEtaHist = []
        self.METPtHist = []
        self.HTLepHist = []
        self.Iso2DHist = []
        self.AK4BdiscHist = []        

        self.AK8PtHist = []
        self.AK8SDPtHist = [] 
        self.AK8PuppiSDPtHist = [] 
        self.AK8PuppiPtHist = [] 

        self.AK8PuppiSDPtoverPuppiPtvsPuppiPttHist = []
        self.AK8SDPtovergenPtvsGenPttHist = []

        self.AK8EtaHist = []
        self.AK8puppitau21Hist = []
        self.AK8puppitau32Hist = []
        self.AK8MHist = []
        self.AK8MSDHist = []
        self.AK8MSDSJ0Hist = []
        self.AK8SDSJ0PtHist = []          

        self.AK8MPt200To300Hist = []
        self.AK8MSDPt200To300Hist = []
        self.AK8MSDSJ0Pt200To300Hist = []

        self.AK8MPt300To400Hist = []
        self.AK8MSDPt300To400Hist = []
        self.AK8MSDSJ0Pt300To400Hist = []

        self.AK8MPt400To500Hist = []
        self.AK8MSDPt400To500Hist = []
        self.AK8MSDSJ0Pt400To500Hist = []

        self.AK8MPt500To800Hist = []
        self.AK8MSDPt500To800Hist = []
        self.AK8MSDSJ0Pt500To800Hist = []

        ### Cut-Flow Histogram with number of events passing each cut
        self.hCutFlow = []

        self.hists = []

        for ival in xrange(self.nstages):
            self.AK8PtHist.append( ROOT.TH1F("AK8PtHist" +  str(ival), "Jet p_{T}, Stage " + str(ival), 1000, 0, 1000) )
            self.AK8SDPtHist.append( ROOT.TH1F("AK8SDPtHist" +  str(ival), "Jet SD p_{T}, Stage " + str(ival), 1000, 0, 1000) )
            self.AK8PuppiSDPtHist.append( ROOT.TH1F("AK8PuppiSDPtHist" +  str(ival), "Jet Puppi SD p_{T}, Stage " + str(ival), 1000, 0, 1000) )
            self.AK8PuppiPtHist.append( ROOT.TH1F("AK8PuppiPtHist" +  str(ival), "Jet p_{T}, Stage " + str(ival), 1000, 0, 1000) )

            self.AK8PuppiSDPtoverPuppiPtvsPuppiPttHist.append( ROOT.TH1F("AK8PuppiSDPtoverPuppiPtvsPuppiPttHist" +  str(ival), "Jet p_{T}, Stage " + str(ival), 1000, 0, 1000) )
            self.AK8SDPtovergenPtvsGenPttHist.append( ROOT.TH1F("AK8SDPtovergenPtvsGenPttHist" +  str(ival), "Jet p_{T}, Stage " + str(ival), 1000, 0, 1000) )

            self.AK8SDSJ0PtHist.append( ROOT.TH1F("AK8SDSJ0PtHist" +  str(ival), "SD subjet 0 P_{T}, Stage " + str(ival), 1000, 0, 1000) )
            self.AK8EtaHist.append( ROOT.TH1F("AK8EtaHist" +  str(ival), "Jet #eta, Stage " + str(ival), 1000, -2.5, 2.5) )
            self.AK8puppitau21Hist.append( ROOT.TH1F("AK8puppitau21Hist" +  str(ival), "Jet #tau_{21}, Stage " + str(ival), 1000, 0., 1.) )
            self.AK8puppitau32Hist.append( ROOT.TH1F("AK8puppitau32Hist" +  str(ival), "Jet #tau_{32}, Stage " + str(ival), 1000, 0., 1.) )

            self.AK8MHist.append( ROOT.TH1F("AK8MHist" +  str(ival), "Jet Mass, Stage " + str(ival), 1000, 0, 500) )
            self.AK8MSDHist.append( ROOT.TH1F("AK8MSDHist" +  str(ival), "Jet Soft Dropped Mass, Stage " + str(ival), 1000, 0, 500) )
            self.AK8MSDSJ0Hist.append( ROOT.TH1F("AK8MSDSJ0Hist" +  str(ival), "Leading Subjet Soft Dropped Mass, Stage " + str(ival), 1000, 0, 500) )

            self.LeptonPtHist.append( ROOT.TH1F("LeptonPtHist" +  str(ival), "Lepton p_{T}, Stage " + str(ival), 1000, 0, 1000) )
            self.LeptonEtaHist.append( ROOT.TH1F("LeptonEtaHist" +  str(ival), "Lepton #eta, Stage " + str(ival), 1000, -2.5, 2.5) )

            self.METPtHist.append( ROOT.TH1F("METPtHist" +  str(ival), "Missing p_{T}, Stage " + str(ival), 1000, 0, 1000) )
            self.HTLepHist.append( ROOT.TH1F("HTLepHist" +  str(ival), "Lepton p_{T} + Missing p_{T}, Stage " + str(ival), 1000, 0, 1000) )
            self.Iso2DHist.append ( ROOT.TH2F("Iso2DHist" +  str(ival), "Lepton 2D isolation (#Delta R vs p_{T}^{REL} ), Stage " + str(ival), 25, 0, 500, 25, 0, 1) )
            self.AK4BdiscHist.append( ROOT.TH1F("AK4BdiscHist" +  str(ival), "CSVv2 B disc , Stage " + str(ival), 1000, 0., 1.) )

            # Create histos for type 1 selection binned by pt of leading SD subjet 
            self.AK8MPt200To300Hist.append( ROOT.TH1F("AK8MPt200To300Hist" +  str(ival), "Jet Mass, Stage " + str(ival), 1000, 0, 500) )
            self.AK8MSDPt200To300Hist.append( ROOT.TH1F("AK8MSDPt200To300Hist" +  str(ival), "Jet Soft Dropped Mass, Stage " + str(ival), 1000, 0, 500) )
            self.AK8MSDSJ0Pt200To300Hist.append( ROOT.TH1F("AK8MSDSJ0Pt200To300Hist" +  str(ival), "Leading Subjet Soft Dropped Mass, Stage " + str(ival), 1000, 0, 500) )

            self.AK8MPt300To400Hist.append( ROOT.TH1F("AK8MPt300To400Hist" +  str(ival), "Jet Mass, Stage " + str(ival), 1000, 0, 500) )
            self.AK8MSDPt300To400Hist.append( ROOT.TH1F("AK8MSDPt300To400Hist" +  str(ival), "Jet Soft Dropped Mass, Stage " + str(ival), 1000, 0, 500) )
            self.AK8MSDSJ0Pt300To400Hist.append( ROOT.TH1F("AK8MSDSJ0Pt300To400Hist" +  str(ival), "Leading Subjet Soft Dropped Mass, Stage " + str(ival), 1000, 0, 500) )

            self.AK8MPt400To500Hist.append( ROOT.TH1F("AK8MPt400To500Hist" +  str(ival), "Jet Mass, Stage " + str(ival), 1000, 0, 500) )
            self.AK8MSDPt400To500Hist.append( ROOT.TH1F("AK8MSDPt400To500Hist" +  str(ival), "Jet Soft Dropped Mass, Stage " + str(ival), 1000, 0, 500) )
            self.AK8MSDSJ0Pt400To500Hist.append( ROOT.TH1F("AK8MSDSJ0Pt400To500Hist" +  str(ival), "Leading Subjet Soft Dropped Mass, Stage " + str(ival), 1000, 0, 500) )

            self.AK8MPt500To800Hist.append( ROOT.TH1F("AK8MPt500To800Hist" +  str(ival), "Jet Mass, Stage " + str(ival), 1000, 0, 500) )
            self.AK8MSDPt500To800Hist.append( ROOT.TH1F("AK8MSDPt500To800Hist" +  str(ival), "Jet Soft Dropped Mass, Stage " + str(ival), 1000, 0, 500) )
            self.AK8MSDSJ0Pt500To800Hist.append( ROOT.TH1F("AK8MSDSJ0Pt500To800Hist" +  str(ival), "Leading Subjet Soft Dropped Mass, Stage " + str(ival), 1000, 0, 500) )

            
            #Cut-Flow Histogram with number of events passing each cut
            self.hCutFlow.append(ROOT.TH1F("hCutFlow" +  str(ival), " ;Stage " +  str(ival)+" of Selection; Events passing cuts ", 1, 0, 2 ) )


    def fill( self, index ) :
        '''
        Fill the histograms we're interested in. If you're doing something complicated, make a
        member variable in the Selector class to cache the variable and just fill here. 
        '''
        a = self.lepSelection
        b = self.hadSelection 

        theWeight =  b.EventWeight * b.PUWeight
        self.theWeightList.append(theWeight)
        self.Weightssum += theWeight
        #print "Event weight * PU weight is {} ".format(theWeight)

        if 0. < theWeight < 0.000158828959689 : 
            theWeight =1. #setting data weight to 1  fix this : make options available within this function- if options.infile == 'data.root' :
            #print "set weight to 1"

        # Deal with negative weights 
        if theWeight < 0. :
           theWeight *= -1.
           self.NegWeightsnum += 1

        self.hCutFlow[index].Fill(self.passedCutCount[index])


        self.ak8Jet = None
        self.ak8JetRaw = None

        self.ak8SDJet = None
        self.ak8SDJetRaw = None

        self.ak8PuppiJet = None
        self.ak8PuppiJetRaw = None

        self.ak8PuppiSDJet = None
        self.ak8PuppiSDJetRaw = None

        self.AK8PuppiSDPtoverPuppiPtvsPuppiPttHist = None
        self.AK8SDPtovergenPtvsGenPttHist = None

        self.SDptPuppipt = None
        self.SDptGenpt = None

        if b.ak8Jet != None :
            self.AK8PtHist[index].Fill( b.ak8Jet.Perp()  , theWeight )
            if b.ak8SDJet != None :
                # Pt Response Plot 1
                self.SDptGenpt = float(b.ak8SDJet.Perp())  / float(b.ak8Jet.Perp() ) 
                #self.AK8SDPtovergenPtvsGenPttHist[index].Fill( b.ak8SDJet.Perp() , b.ak8Jet.Perp() )    # /b.ak8Jet.Perp() 
                # Fix this : fill response histos

        if b.ak8SDJet != None :
            self.AK8SDPtHist[index].Fill( b.ak8SDJet.Perp()  , theWeight )

        if b.ak8PuppiJet != None :
            self.AK8PtHist[index].Fill( b.ak8PuppiJet.Perp()  , theWeight )

        if b.ak8PuppiJet != None :
            self.AK8PuppiPtHist[index].Fill( b.ak8PuppiJet.Perp()  , theWeight )
            self.AK8SDSJ0PtHist[index].Fill( b.ak8PuppiSDJet_Subjet0.Perp()  , theWeight )
            self.AK8EtaHist[index].Fill( b.ak8PuppiJet.Eta()  , theWeight )
            self.AK8puppitau21Hist[index].Fill( b.puppitau21  , theWeight )
            self.AK8puppitau32Hist[index].Fill( b.puppitau32  , theWeight )

            self.AK8MHist[index].Fill( b.ak8_Puppim  , theWeight )
            if b.ak8PuppiSDJet != None :
                # Pt Response Plot 2
                self.SDptPuppipt = float(b.ak8PuppiSDJet.Perp())  / float(b.ak8PuppiJet.Perp() ) 
                #self.AK8PuppiSDPtoverPuppiPtvsPuppiPttHist[index].Fill( self.SDptPuppipt  , b.ak8PuppiJet.Perp() )  
                # Fix this : fill response histos

        if b.ak8PuppiSDJet != None :
            self.AK8MSDHist[index].Fill( b.ak8PuppiSD_m  , theWeight )
            self.AK8MSDSJ0Hist[index].Fill( b.ak8SDsj0_m  , theWeight )


            # Filling jet mass histos binned by pt of the leading SD subjet

            self.AK8MPt200To300Hist[index].Fill( b.ak8PuppiJet200.M()  , theWeight )
            self.AK8MSDPt200To300Hist[index].Fill( b.ak8PuppiSDJet200.M()  , theWeight )
            if  b.ak8SDsj0_m200 > 0.0001:
                self.AK8MSDSJ0Pt200To300Hist[index].Fill(  b.ak8SDsj0_m200 , theWeight )

            self.AK8MPt300To400Hist[index].Fill( b.ak8PuppiJet300.M()  , theWeight )
            self.AK8MSDPt300To400Hist[index].Fill( b.ak8PuppiSDJet300.M()  , theWeight )
            if  b.ak8SDsj0_m300 > 0.0001:
                self.AK8MSDSJ0Pt300To400Hist[index].Fill(  b.ak8SDsj0_m300 , theWeight )


            self.AK8MPt400To500Hist[index].Fill(  b.ak8PuppiJet400.M()  , theWeight )
            self.AK8MSDPt400To500Hist[index].Fill( b.ak8PuppiSDJet400.M()  , theWeight )
            if  b.ak8SDsj0_m400 > 0.0001:
                self.AK8MSDSJ0Pt400To500Hist[index].Fill(  b.ak8SDsj0_m400 , theWeight )


            self.AK8MPt500To800Hist[index].Fill( b.ak8PuppiJet500.M()  , theWeight )
            self.AK8MSDPt500To800Hist[index].Fill( b.ak8PuppiSDJet500.M()  , theWeight )
            if  b.ak8SDsj0_m500 > 0.0001:
                self.AK8MSDSJ0Pt500To800Hist[index].Fill(  b.ak8SDsj0_m500 , theWeight )


        if a.leptonP4 != None : 
            self.LeptonPtHist[index].Fill( a.leptonP4.Perp()  , theWeight )
            self.LeptonEtaHist[index].Fill( a.leptonP4.Eta()  , theWeight )
            self.METPtHist[index].Fill( a.nuP4.Perp() , theWeight  )
            self.HTLepHist[index].Fill( a.leptonP4.Perp() + a.nuP4.Perp()  , theWeight )
            if a.ak4Jet != None : 
                self.Iso2DHist[index].Fill( a.leptonP4.Perp( a.ak4Jet.Vect() ), a.leptonP4.DeltaR( a.ak4Jet )  , theWeight  )
                self.AK4BdiscHist[index].Fill(b.ak4JetBdisc , theWeight)





    def close( self ) :
        '''
        Wrap it up. 
        '''
        self.negfrac = float(self.NegWeightsnum) / float(self.eventsToRun)
        print "{0:1.0f} Negative weights/ {1:10.0f} total events: fraction {2:3.4f}".format(self.NegWeightsnum, self.eventsToRun, self.negfrac)
        

        self.ts = (time.time() - self.startTime)

        self.unitIs = 'Seconds'
        if self.ts > 60. :
            self.ts /= 60.
            self.unitIs = 'Minutes'
        if self.ts > 60. :
            self.ts /= 60.
            self.unitIs = 'Hours' 

        print ('The script took {0}  {1}!'.format(   self.ts  , self.unitIs    ) )


        self.outfile.cd() 
        self.outfile.Write()
        self.outfile.Close()


'''
        Executable
'''
if __name__ == "__main__" :
    r = RunSemiLepTTbar(sys.argv)
    r.run()
