#!/usr/bin/env python
import sys
import yaml
import ROOT as R
sys.dont_write_bytecode=True

import prettyplots
from collections import OrderedDict

R.gStyle.SetOptStat(0)
R.gStyle.SetPalette(1)
R.gROOT.SetBatch(R.kTRUE)

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

tf = R.TFile(sys.argv[1])
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
h2 = R.TH2F( 'corrHist', '', nPOI, 0, nPOI, nPOI, 0, nPOI);
OL = R.TH2F( 'corrHistOL', '', nPOI, 0, nPOI, nPOI, 0, nPOI);
for i, poiName1 in enumerate(poiNames):
  for j, poiName2 in enumerate(poiNames):
    io = poiMap[poiName1][0]
    jo = poiMap[poiName2][1]
    h2.SetBinContent(nPOI-i, j+1, round(corrHist.GetBinContent(io, jo),2))

for i, poiName in enumerate(poiNames):
  poiName = poiName.replace(poiStr,'')
  if poiName in POIstrs:
    poiName = POIstrs[poiName]
  h2.GetXaxis().SetBinLabel(nPOI-i, poiName)
  h2.GetYaxis().SetBinLabel(i+1, poiName)
  OL.SetBinContent(nPOI-i, i+1, 1)

can = R.TCanvas('can','',1200,1200)
can.cd()

can.SetMargin(0.26,0.14,0.26,0.09) # left, right, down, up

#R.gStyle.SetPaintTextFormat('.2g');
R.gStyle.SetPaintTextFormat('.2f');

h2.GetXaxis().LabelsOption('v')
h2.GetZaxis().SetTitle('#rho(X,Y)')
h2.GetXaxis().SetTickSize(0)
h2.GetYaxis().SetTickSize(0)

h2.SetMarkerSize(0.8)
h2.SetLabelSize(0.025,'xyz')

h2.SetMaximum(+1.0)
h2.SetMinimum(-1.0)
h2.Draw('COLZ TEXT SAME')

#R.gStyle.SetPaintTextFormat('0.1f')
#OL.SetMarkerColor(R.kWhite)
#OL.Draw('COL TEXT SAME')

tt = R.TLatex()
tt.SetTextSize(0.055)
tt.DrawLatexNDC(0.20, 0.940, '#it{ATLAS} #bf{Internal}')
tt.SetTextSize(0.025)
tt.DrawLatexNDC(0.60, 0.965, '#bf{ #sqrt{s}=13 TeV, 36.1 fb^{-1} }')
tt.DrawLatexNDC(0.60, 0.935, '#bf{ H #rightarrow #gamma#gamma,  m_{H}=125.09 GeV }')

can.SaveAs('plots/correlation.pdf')

