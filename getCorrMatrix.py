#!/usr/bin/env python
import sys
import ROOT as R
sys.dont_write_bytecode=True
import prettyplots


R.gStyle.SetOptStat(0)
R.gStyle.SetPalette(1)
R.gROOT.SetBatch(R.kTRUE)

prettyplots.setPalette("negblue")

# check for config file
if len(sys.argv) <= 1:
  print 'Usage: ./%s workspace' % sys.argv[0]
  sys.exit()

tf = R.TFile(sys.argv[1])
fr = tf.Get("fitResult")

poiBins1, poiNames1 = [], []
poiBins2, poiNames2 = [], []
corrHist = fr.correlationHist()

poiStr = "mu_"

for ibin in xrange(1,corrHist.GetNbinsX()+1):
  varName = corrHist.GetXaxis().GetBinLabel(ibin)
  if not poiStr in varName: continue
  poiBins1.append(ibin)
  poiNames1.append(varName.replace(poiStr,''))

for ibin in xrange(1,corrHist.GetNbinsY()+1):
  varName = corrHist.GetYaxis().GetBinLabel(ibin)
  if not poiStr in varName: continue
  poiBins2.append(ibin)
  poiNames2.append(varName.replace(poiStr,''))

# Reduce correlation matrix
nPOI = len(poiBins1)
h2 = R.TH2F( "corrHist", "", nPOI, 0, nPOI, nPOI, 0, nPOI);
for i, io in enumerate(poiBins1):
  for j, jo in enumerate(poiBins2):
    #if (nPOI-i > j+1): continue
    #if (nPOI-i < j+1): continue
    h2.SetBinContent( i+1, j+1, corrHist.GetBinContent( io, jo ) )
    #print i, j, "-->", io, jo, ":", corrHist.GetBinContent( io, jo )

#print corrHist.GetBinContent(1,2)
#corrHist.Draw("colz")

#h2.GetZaxis().SetTitle("Correlation")
for ibin, poiName in enumerate(poiNames1):
  h2.GetXaxis().SetBinLabel( ibin+1, poiName )
for ibin, poiName in enumerate(poiNames2):
  h2.GetYaxis().SetBinLabel( ibin+1, poiName )


can = R.TCanvas("can","",1000,1000)
can.cd()

can.SetMargin(0.20,0.12,0.23,0.09)
#can.SetTopMargin(0.09)
#can.SetRightMargin(0.12)
#can.SetLeftMargin(0.18)
#can.SetBottomMargin(0.23)

R.gStyle.SetPaintTextFormat("3.2f");

#print poiBins1, poiBins2
h2.GetXaxis().LabelsOption("v")
h2.SetTitle("\t\t\t\t Correlations Between Measured Cross-Sections")

h2.SetMarkerSize(0.8)
h2.SetLabelSize(0.025,"xyz")
#h2.SetLabelSize(0.03,"z")

h2.SetMaximum(+1.0)
h2.SetMinimum(-1.0)
h2.Draw("colz text")

can.SaveAs("plots/correlation.pdf")

