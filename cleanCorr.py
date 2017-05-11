#!/usr/bin/env python
import sys
import yaml
import ROOT
sys.dont_write_bytecode=True

import prettyplots
from collections import OrderedDict

ROOT.gStyle.SetOptStat(0)
ROOT.gStyle.SetPalette(1)
ROOT.gROOT.SetBatch(ROOT.kTRUE)

prettyplots.setPalette('negblue')

POIstrs = yaml.safe_load(open('replacements.yml'))

# ---------------------------------------------------------------------
def iterate( args ):
  iter = args.createIterator()
  var = iter.Next()
  while var :
    yield var
    var = iter.Next()


# ---------------------------------------------------------------------
# check for config file
if len(sys.argv) <= 1:
  print 'Usage: ./%s workspace' % sys.argv[0]
  sys.exit()

tf = ROOT.TFile(sys.argv[1])
ws = tf.Get('combWS')
mc = ws.obj('ModelConfig')

fr = tf.Get('fitResult')
pois = mc.GetParametersOfInterest()

corrHist = fr.correlationHist()

poiStr = 'mu_'
poiNames = [ poi.GetName() for poi in iterate(pois) ]
poiNames.reverse()

poiMap = OrderedDict()
for poiName in poiNames:
  xbin, ybin = -1, -1
  for ibin in xrange(1,corrHist.GetNbinsY()+1):
    if poiName == corrHist.GetXaxis().GetBinLabel(ibin): xbin = ibin
    if poiName == corrHist.GetYaxis().GetBinLabel(ibin): ybin = ibin
  poiMap[poiName] = (xbin, ybin)

# Reduce correlation matrix
nPOI = len(poiMap)
h2 = ROOT.TH2F( 'corrHist', '', nPOI, 0, nPOI, nPOI, 0, nPOI);
o1 = ROOT.TH2F( 'overlay1', '', nPOI, 0, nPOI, nPOI, 0, nPOI);
o2 = ROOT.TH2F( 'overlay2', '', nPOI, 0, nPOI, nPOI, 0, nPOI);
o3 = ROOT.TH2F( 'overlay3', '', nPOI, 0, nPOI, nPOI, 0, nPOI);
o4 = ROOT.TH2F( 'overlay4', '', nPOI, 0, nPOI, nPOI, 0, nPOI);
for i, poiName1 in enumerate(poiNames):
  for j, poiName2 in enumerate(poiNames):
    io = poiMap[poiName1][0]
    jo = poiMap[poiName2][1]
    #corr = round(corrHist.GetBinContent(io, jo),2)
    corr = corrHist.GetBinContent(io, jo)
    h2.SetBinContent(nPOI-i, j+1, corr)
    if abs(corr) < 0.005:
      o2.SetBinContent(nPOI-i, j+1, corr)
    elif abs(corr) <= 0.60:
      o1.SetBinContent(nPOI-i, j+1, corr)
    elif corr == 1:
      o3.SetBinContent(nPOI-i, j+1, corr)
    else:
      o4.SetBinContent(nPOI-i, j+1, corr)

for i, poiName in enumerate(poiNames):
  poiName = poiName.replace(poiStr,'')
  if poiName in POIstrs:
    poiName = POIstrs[poiName]
  h2.GetXaxis().SetBinLabel(nPOI-i, poiName)
  h2.GetYaxis().SetBinLabel(i+1, poiName)

for i in xrange(nPOI):
  for j in xrange(i+1,nPOI):
    h2.SetBinContent(nPOI-i, j+1, 0)
    o1.SetBinContent(nPOI-i, j+1, 0)
    o2.SetBinContent(nPOI-i, j+1, 0)
    o3.SetBinContent(nPOI-i, j+1, 0)
    o4.SetBinContent(nPOI-i, j+1, 0)

can = ROOT.TCanvas('can','',1200,1100)
can.cd()

can.SetMargin(0.24, 0.14, 0.26, 0.02) # left, right, down, up

#ROOT.gStyle.SetPaintTextFormat('.2f');

h2.GetXaxis().LabelsOption('v')
h2.GetZaxis().SetTitle('#rho(X,Y)')
h2.GetXaxis().SetTickSize(0)
h2.GetYaxis().SetTickSize(0)

h2.SetMarkerSize(0.8)
h2.SetLabelSize(0.025,'xyz')

h2.SetMaximum(+1.0)
h2.SetMinimum(-1.0)

ex0 = ROOT.TExec('ex0','gStyle->SetPaintTextFormat(\".2f\");')
ex0.Draw()
h2.Draw('COLZ')

ex1 = ROOT.TExec('ex1','gStyle->SetPaintTextFormat(\".2f\");')
ex1.Draw()
o1.SetMarkerSize(0.9)
o1.Draw('TEXT SAME')

ex2 = ROOT.TExec('ex2','gStyle->SetPaintTextFormat(\"d\");')
ex2.Draw()
o2.SetMarkerSize(0.7)
o2.Draw('TEXT SAME')

ex3 = ROOT.TExec('ex3','gStyle->SetPaintTextFormat(\"g\");')
ex3.Draw()
o3.SetMarkerSize(1.3)
o3.SetMarkerColor(ROOT.kWhite)
o3.Draw('TEXT SAME')

ex4 = ROOT.TExec('ex4','gStyle->SetPaintTextFormat(\".2f\");')
ex4.Draw()
o4.SetMarkerSize(0.9)
o4.SetMarkerColor(ROOT.kWhite)
o4.Draw('TEXT SAME')

tt = ROOT.TLatex()
tt.SetTextSize(0.055)
tt.DrawLatexNDC(0.48, 0.900, '#it{ATLAS} #bf{Internal}')
tt.SetTextSize(0.030)
tt.DrawLatexNDC(0.52, 0.835, '#bf{ #sqrt{s}=13 TeV, 36.1 fb^{-1} }')
tt.DrawLatexNDC(0.52, 0.795, '#bf{ H #rightarrow #gamma#gamma,  m_{H}=125.09 GeV }')

can.SaveAs('plots/correlation.pdf')

