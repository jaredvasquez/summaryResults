#!/usr/bin/env python
import sys
import ROOT as R
RF = R.RooFit

R.gStyle.SetOptStat(0)
R.gROOT.SetBatch(R.kTRUE)

labels = {
  'GGH' : '#splitline{ggF}{Categories}',
  'VBF' : '#splitline{VBF}{Categories}',
  'VH'  : '#splitline{#it{VH}}{Categories}',
  'TTH' : '#splitline{t#bar{t}H}{Categories}',
  #'TTH' : '#splitline{t#bar{t}H}{Categories}',
}

# ---------------------------------------------------------------------
def iterate( args ):
  iter = args.createIterator()
  var = iter.Next()
  while var :
    yield var
    var = iter.Next()

# ---------------------------------------------------------------------
if __name__ == "__main__":
  # check for config file
  if len(sys.argv) <= 1:
    print 'Usage: ./%s workspace' % sys.argv[0]
    sys.exit()

  tf = R.TFile(sys.argv[1])
  ws = tf.Get('combWS')
  mc = ws.obj('ModelConfig')

  pois = mc.GetParametersOfInterest()

  xmin, xmax = 0, 2.0
  xmin, xmax = -0.3, 1.6
  xmin, xmax = 0.25, 1.6 # clipped errors
  comb = [ 0.94, 0.15, 0.14 ]

  can = R.TCanvas('can','can',800,600)
  can.cd()
  can.SetMargin(0.20,0.04,0.12,0.11)

  tg = R.TGraphAsymmErrors()
  te = R.TGraphAsymmErrors()

  color = R.kBlack
  tg.SetMarkerStyle(20)
  tg.SetMarkerSize(1.2)
  tg.SetMarkerColor(color)
  tg.SetLineColor(color)
  tg.SetLineWidth(2)

  npoi = 1
  for poi in iterate(pois):
    if poi.isConstant(): continue
    npoi += 1

  h = R.TH2F('hist',';Signal Strength \t', 100, xmin, xmax, npoi, -0.5, npoi-0.5)
  h.SetTitleSize(0.042, 'X')
  h.GetYaxis().SetLabelSize(0.062)

  for ipoi, poi in enumerate(iterate(pois)):
    if poi.isConstant(): continue
    ipoi = npoi-ipoi-1

    POIName = poi.GetName().replace('mu_','')
    mean = poi.getVal()
    errHi = abs(poi.getErrorHi())
    errLo = abs(poi.getErrorLo())
    print '%-25s :  %+4.2f  %4.2f' % (POIName, errHi, -errLo)

    h.GetYaxis().SetBinLabel(ipoi+1, labels[POIName] )
    tg.SetPoint(ipoi, mean, ipoi)
    tg.SetPointError(ipoi, errLo, errHi, 0., 0.)

  # Show Combined
  h.GetYaxis().SetBinLabel(1, "Combined")
  tg.SetPoint(0, comb[0], 0)
  tg.SetPointError(0, comb[2], comb[1], 0., 0.)

  #te.SetPoint(0, comb[0], 0)
  #te.SetLineColor(R.kRed)
  #te.SetPointError(0, comb[2], comb[1], -0.5, npoi)
  #te.SetFillColor(R.kBlue)
  #te.SetFillStyle(3002)

  tline = R.TLine()
  tline.SetLineWidth(1)
  tline.SetLineColor(R.kBlue)
  tline.SetLineStyle(2)

  h.Draw('HIST')

  pave = R.TPave( comb[0]-comb[2], -0.5, comb[0]+comb[1], npoi-0.5 )
  pave.SetBorderSize(1)
  pave.SetFillStyle(3018)
  pave.SetFillColor(R.kBlue)
  pave.SetLineWidth(0)
  pave.Draw()

  #te.Draw('C SAME')
  tline.DrawLine(1.0, -0.5, 1.0, npoi-0.5)
  tg.Draw('PE SAME')

  tline.SetLineWidth(1)
  tline.SetLineColor(R.kBlue)
  tline.DrawLine(xmin, 0.5, xmax, 0.5)

  text = R.TLatex()
  text.SetTextSize(0.055)
  text.DrawLatexNDC(0.22, 0.930, '#it{ATLAS} #bf{Internal}')
  text.SetTextSize(0.035)
  text.DrawLatexNDC(0.66, 0.955, '#bf{ #sqrt{s}=13 TeV, 36.1 fb^{-1} }')
  text.DrawLatexNDC(0.66, 0.920, '#bf{ H #rightarrow #gamma#gamma,  m_{H}=125.09 GeV }')

  can.SaveAs('plots/summary_prods.pdf')

