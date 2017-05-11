#!/usr/bin/env python
import sys
import yaml
import ROOT as R
RF = R.RooFit

R.gStyle.SetOptStat(0)
R.gROOT.SetBatch(R.kTRUE)

POIstrs = yaml.safe_load(open('replacements.yml'))

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

  xmin, xmax = -10.0, 11.0
  #xmin, xmax = -4, 6
  xmin, xmax = -5.5, 7.2

  can = R.TCanvas('can','can',900,1000)
  can.cd()
  can.SetMargin(0.35,0.04,0.12,0.11)

  tg = R.TGraphAsymmErrors()

  color = R.kBlue
  tg.SetLineWidth(2)
  tg.SetMarkerStyle(20)
  tg.SetMarkerSize(1.2)
  tg.SetMarkerColor(color)
  tg.SetLineColor(color)
  tg.SetLineWidth(2)

  npoi = 0
  for poi in iterate(pois):
    if poi.isConstant(): continue
    npoi += 1

  h = R.TH2F('hist',';Measured XS w.r.t. SM \t', 100, xmin, xmax, npoi, -0.5, npoi-0.5)
  h.SetTitleSize(0.042, 'X')

  for ipoi, poi in enumerate(iterate(pois)):
    if poi.isConstant(): continue
    ipoi = npoi-ipoi-1

    POIName = poi.GetName().replace('mu_','')
    mean = poi.getVal()
    errHi = abs(poi.getErrorHi())
    errLo = abs(poi.getErrorLo())
    print '%-25s :  %+4.2f  %4.2f' % (POIName, errHi, -errLo)

    if POIName in POIstrs: POIName = POIstrs[POIName]

    h.GetYaxis().SetBinLabel(ipoi+1, POIName)
    tg.SetPoint(ipoi, mean, ipoi)
    tg.SetPointError(ipoi, errLo, errHi, 0., 0.)

  tline = R.TLine()
  tline.SetLineWidth(2)
  tline.SetLineColor(R.kGray)
  tline.SetLineStyle(2)

  h.Draw('HIST')
  tline.DrawLine(1.0, -0.5, 1.0, npoi-0.5)
  tg.Draw('PE SAME')

  text = R.TLatex()
  text.SetTextSize(0.055)
  text.DrawLatexNDC(0.15, 0.930, '#it{ATLAS} #bf{Internal}')
  text.SetTextSize(0.035)
  text.DrawLatexNDC(0.56, 0.955, '#bf{ #sqrt{s}=13 TeV, 36.1 fb^{-1} }')
  text.DrawLatexNDC(0.56, 0.920, '#bf{ H #rightarrow #gamma#gamma,  m_{H}=125.09 GeV }')

  can.SaveAs('plots/summary_STXS.pdf')

