#!/usr/bin/env python
from optparse import OptionParser

parser = OptionParser()
parser.add_option('--cut', type='string', action='store',
                  dest='cut',
                  default = "FatJetTau2/FatJetTau1 < 0.6 && LeptonPt > 50. && LeptonPt + SemiLepMETpt > 250. && FatJetMassSoftDrop > 0 && AK4bDisc > 0.6",
                  help='Cut for')
parser.add_option('--filestr', type='string', action='store',
                  dest='filestr',
                  default = "nom",
                  help='Label for plots')
parser.add_option('--variable', type='string', action='store',
                  dest='variable',
                  default = 'FatJetMassSoftDrop',
                  help='Variable to plot')
parser.add_option('--lep', type='string', action='store',
                  dest='lep',
                  default = 'all',
                  help='Lepton to plot')
parser.add_option('--minval', type='float', action='store',
                  dest='minval',
                  default = 0.,
                  help='Minval for the plot')
parser.add_option('--maxval', type='float', action='store',
                  dest='maxval',
                  default = 250.,
                  help='Maxval for the plot')
parser.add_option('--nbins', type='int', action='store',
                  dest='nbins',
                  default = 25,
                  help='Nbins for the plot')
parser.add_option('--legleft',  action='store_true',
                  dest='legleft',
                  default = False,
                  help='Plot legend on the left')

parser.add_option('--trig', type = 'string', action='store',
                  dest='trig',
                  default = None,
                  help="Triggers to plot")
(options, args) = parser.parse_args()
argv = []

import ROOT
import array


ROOT.gStyle.SetOptStat(000000)
#ROOT.gROOT.Macro("rootlogon.C")
ROOT.gStyle.SetTitleOffset(1.0, "Y")
## ttbarIn = ROOT.TFile( 'NTUPLES/ttjets_b2ganafw_v6_jecv5_updatedsel_ntuple.root' )
## wjetsIn = ROOT.TFile( 'NTUPLES/wjets_b2ganafw_v5_sel1_extracats_jecv5_updatedsel_ntuple.root' )
## zjetsIn = ROOT.TFile( 'NTUPLES/zjets_b2ganafw_v4_sel1_extracats_jecv5_updatedsel_ntuple.root' )
## singletopIn = ROOT.TFile( 'NTUPLES/singletop_v74x_v4.3_tchan_local_sel1_extracats_jecv5_updatedsel_ntuple.root' )
## singlemuIn = ROOT.TFile( 'NTUPLES/singlemu_v74x_v6_dataset5_jecv5_updatedsel_ntuple.root' )
## singleelIn = ROOT.TFile( 'NTUPLES/singleel_v74x_v6_dataset5_jecv5_updatedsel_ntuple.root' )

ttbarIn = ROOT.TFile( 'NTUPLES/ttjets_b2ganafw_v6_jecv5_updatedmcrw_ntuple.root' )
wjetsIn = ROOT.TFile( 'NTUPLES/wjets_b2ganafw_v5_sel1_extracats_jecv5_updatedmcrw_ntuple.root' )
zjetsIn = ROOT.TFile( 'NTUPLES/zjets_b2ganafw_v4_sel1_extracats_jecv5_updatedmcrw_ntuple.root' )
singletopIn = ROOT.TFile( 'NTUPLES/singletop_v74x_v4.3_tchan_local_sel1_extracats_jecv5_updatedmcrw_ntuple.root' )
singlemuIn = ROOT.TFile( 'NTUPLES/singlemu_v74x_v6_dataset6_jecv5_updateddphi_ntuple.root' )
singleelIn = ROOT.TFile( 'NTUPLES/singleel_v74x_v6_dataset5_jecv5_updateddphi_ntuple.root' )

lumi = 1263.88

ttbar = ttbarIn.Get("TreeSemiLept")
wjets = wjetsIn.Get("TreeSemiLept")
zjets = zjetsIn.Get("TreeSemiLept")
singletop = singletopIn.Get("TreeSemiLept")
singlemu = singlemuIn.Get("TreeSemiLept")
singleel = singleelIn.Get("TreeSemiLept")

titles = {
    'FatJetMassSoftDrop':['m_softdrop',';Soft Drop (#beta=0) Jet Mass (GeV);Number'],
    'FatJetMassPruned':['m_pruned',';Pruned Jet Mass (GeV);Number'],
    'LeptonPt':['leppt',';Lepton p_{T} (GeV);Number'],
    'LeptonPt + SemiLepMETpt':['htlep',';H_{T}^{LEP} (GeV);Number'],
    'FatJetTau2/FatJetTau1':['tau21',';#tau_{2}/#tau_{1};Number'],
    'FatJetTau3/FatJetTau2':['tau32',';#tau_{3}/#tau_{2};Number'],
    'NearestAK4JetPt':['ak4pt',';Lepton-side AK4 Jet p_{T} (GeV);Number'],
    'DeltaPhiLepFat':['deltaPhiLepFat',';#Delta #phi (lep, AK8);Number'],
    'NearestAK4JetEta':['ak4eta', ';Jet Rapidity;Number'],
    'FatJetRhoRatio':['ak8rho', ';Jet #rho = (m/p_{T}R)^{2};Number'],
    'AK4bDisc':['ak4bdisc',';Jet B Discriminator;Number'],
    'LeptonPtRel':['LeptonPtRel',';p_{T}^{REL} (lep,jet);Number'],
    'LeptonDRMin':['LeptonDRMin',';#Delta R (lep,jet);Number'],
    }

variable = options.variable
cut = options.cut
name = titles[variable][0]
title = titles[variable][1]
minval = options.minval
maxval = options.maxval
nbins = options.nbins
histbins = "(" + str(nbins) + ',' + str(minval) + ',' + str(maxval) + ")"


lepstrMC  = 'LeptonType >= 1'
lepstrELE = 'LeptonType == 1'
lepstrMUO = 'LeptonType == 2'
if options.lep == 'mu' :
    lepstrMC = lepstrMUO
elif options.lep == 'el' :
    lepstrMC = lepstrELE

#weightstr = "SemiLeptWeight * "
weightstr = ""

ttbar.Draw(variable     + " >> httbar"     + histbins, weightstr + "(" + cut + " && " + lepstrMC + ")", "goff")
wjets.Draw(variable     + " >> hwjets"     + histbins, weightstr + "(" + cut + " && " + lepstrMC + ")", "goff")
zjets.Draw(variable     + " >> hzjets"     + histbins, weightstr + "(" + cut + " && " + lepstrMC + ")", "goff")
singletop.Draw(variable + " >> hsingletop" + histbins, weightstr + "(" + cut + " && " + lepstrMC + ")", "goff")
singlemu.Draw(variable  + " >> hsinglemu"  + histbins, cut + " && " + lepstrMUO + " && " + options.trig, "goff")
singleel.Draw(variable  + " >> hsingleel"  + histbins, cut + " && " + lepstrELE + " && " + options.trig, "goff")

httbar = ROOT.gDirectory.Get('httbar')
hwjets = ROOT.gDirectory.Get('hwjets')
hzjets = ROOT.gDirectory.Get('hzjets')
hsingletop = ROOT.gDirectory.Get('hsingletop')

if options.lep == 'mu' : 
    hdata = ROOT.gDirectory.Get('hsinglemu').Clone()
    hdata.SetName("hdata")
elif options.lep == 'el' : 
    hdata = ROOT.gDirectory.Get('hsingleel').Clone()
    hdata.SetName("hdata")
else :
    hdata = ROOT.gDirectory.Get('hsinglemu').Clone()
    hdata.SetName("hdata")
    hsingleel = ROOT.gDirectory.Get('hsingleel')
    hdata.Add( hsingleel)



if httbar.Integral() > 0 : 
    httbar.Scale( 831.76 * lumi / 19665194. * httbar.GetEntries()/httbar.Integral())
else :
    httbar.Scale( 0.)
httbar.SetFillColor(ROOT.kGreen + 2)

if hwjets.Integral() > 0 : 
    hwjets.Scale(20508.9 * lumi / 24089991. * hwjets.GetEntries()/hwjets.Integral())
else :
    hwjets.Scale( 0.)
hwjets.SetFillColor(ROOT.kRed)

if hzjets.Integral() > 0 : 
    hzjets.Scale( 2008.4 * lumi / 19925500. * hzjets.GetEntries()/hzjets.Integral())
else :
    hzjets.Scale( 0. )
hzjets.SetFillColor(ROOT.kBlue - 4)

if hsingletop.Integral() > 0  : 
    hsingletop.Scale( 216.99 * lumi / 3999910. * hsingletop.GetEntries()/hsingletop.Integral())
else :
    hsingletop.Scale(0)
hsingletop.SetFillColor(ROOT.kCyan )


hdata.SetMarkerStyle(20)
hdata.SetTitle( title )

mc = ROOT.THStack(variable, title)
mc.Add( hzjets )
mc.Add( hwjets )
mc.Add( hsingletop )
mc.Add( httbar )


if not options.legleft : 
    leg = ROOT.TLegend( 0.7, 0.7, 0.89, 0.89)
else :
    leg = ROOT.TLegend( 0.3, 0.7, 0.59, 0.89)
leg.SetFillColor(0)
leg.SetBorderSize(0)

leg.AddEntry( hdata, 'Data', 'p')
leg.AddEntry( httbar, 't#bar{t}', 'f')
leg.AddEntry( hwjets, 'W+Jets', 'f')
leg.AddEntry( hzjets, 'Z+Jets', 'f')
leg.AddEntry( hsingletop, 'Single top quark', 'f')


c = ROOT.TCanvas(variable,variable)
hdata.Draw('e')
mc.Draw("hist same")
hdata.Draw('e same')
hdata.Draw("axis same")

max1 = hdata.GetMaximum()
max2 = mc.GetHistogram().GetMaximum()

hdata.SetMaximum( max (max1,max2) * 1.2 )


leg.Draw()

tlx = ROOT.TLatex()
tlx.SetNDC()
tlx.SetTextFont(42)
tlx.SetTextSize(0.057)
tlx.DrawLatex(0.131, 0.91, "CMS Preliminary #sqrt{s}=13 TeV, " + str(lumi) + " pb^{-1}")
# tlx.DrawLatex(0.77, 0.86, "#bf{CMS}")
# tlx.DrawLatex(0.72, 0.83, "#it{very preliminary}")
tlx.SetTextSize(0.025)
xInfo = 0.18
yInfoTop = 0.84
yInfo2 = yInfoTop-0.042
yInfo3 = yInfo2-0.042
yInfo4 = yInfo3-0.042
yInfo5 = yInfo4-0.042
yInfo6 = yInfo5-0.042
#tlx.DrawLatex(xInfo, yInfoTop, "#bf{CMS Top Tagger}") # same for AK4 and AK8
#tlx.DrawLatex(xInfo, yInfo2 , "#bf{Madgraph}") # same for AK4 and AK8                   
#tlx.DrawLatex(xInfo, yInfo2, "#bf{anti-k_{T} R= 0.8}") # 0.8 or 0.4 for AK8 and AK4              change with histo
#tlx.DrawLatex(xInfo, yInfo4, "#bf{|#eta| < 2.4 }")  # same for AK4 and AK8
#if options.plotW :
#    tlx.DrawLatex(xInfo, yInfo5, "#bf{p_{T} > 200 GeV}")# > 400 for AK8 and > 30 for AK4     change with histo
#else : 
#    tlx.DrawLatex(xInfo, yInfo5, "#bf{p_{T} > 400 GeV}")# > 400 for AK8 and > 30 for AK4     change with histo
#tlx.DrawLatex(xInfo, yInfo6, "#bf{25 ns}")  # change with 25 or 50 ns bunchcrossings     change with root files


c.Update()
c.Draw()

c.Print( name + '_' + options.filestr + '.png', 'png' )
c.Print( name + '_' + options.filestr + '.pdf', 'pdf' )
