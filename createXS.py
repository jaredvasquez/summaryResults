#!/usr/bin/env python
import sys
import yaml
import ROOT as R
from math import sqrt
RF = R.RooFit

R.gStyle.SetOptStat(0)
R.gROOT.SetBatch(R.kTRUE)

POIstrs = yaml.safe_load(open('replacements.yml'))
errors = yaml.safe_load(open('errorsXS.yml'))

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

  paves = []
  pois = mc.GetParametersOfInterest()

  xmin, xmax = -0.3, 2.8
  #xmin, xmax = -0.1, 2.1 # expected

  can = R.TCanvas('can','can',900,1000)
  can.cd()
  can.SetMargin(0.15,0.04,0.12,0.11)

  tg = R.TGraphAsymmErrors()

  color = R.kBlue
  #color = R.kBlack
  tg.SetLineWidth(2)
  tg.SetMarkerStyle(20)
  tg.SetMarkerSize(1.2)
  tg.SetMarkerColor(color)
  tg.SetLineColor(color)
  tg.SetLineWidth(2)

  npoi = 0
  for poi in iterate(pois):
    if poi.isConstant(): continue
    if 'minus' in poi.GetName(): continue
    npoi += 1

  h = R.TH2F('hist',';Measured #sigma #times BR normalized to SM \t', 100, xmin, xmax, npoi, -0.5, npoi-0.5)
  h.SetTitleSize(0.042, 'X')

  jpoi = -1
  for poi in iterate(pois):
    if poi.isConstant(): continue
    if 'minus' in poi.GetName(): continue
    jpoi += 1
    ipoi = npoi-jpoi-1

    POIName = poi.GetName().replace('mu_','')
    mean = poi.getVal()
    errHi = abs(poi.getErrorHi())
    errLo = abs(poi.getErrorLo())
    print '%45s :  %+4.2f  +/-  %+4.2f  %4.2f' % (POIName, mean, errHi, -errLo)

    if POIName in POIstrs: POIName = POIstrs[POIName]

    h.GetYaxis().SetBinLabel(ipoi+1, POIName)
    tg.SetPoint(ipoi, mean, ipoi)
    tg.SetPointError(ipoi, errLo, errHi, 0., 0.)

  h.GetYaxis().SetLabelSize(0.06)
  #h.GetYaxis().SetLabelOffset(1.05)
  h.Draw('HIST')

  jpoi = -1
  for poi in iterate(pois):
    if poi.isConstant(): continue
    if 'minus' in poi.GetName(): continue
    jpoi += 1
    ipoi = npoi-jpoi-1

    POIName = poi.GetName().replace('mu_','')
    if not POIName in errors:
      continue

    errHI, errLO = errors[POIName]
    # add in BR uncertainties
    errHI = sqrt( errHI**2 + 0.0173**2 )
    errLO = sqrt( errLO**2 + 0.0172**2 )

    ybot, ytop = ipoi-0.5, ipoi+0.5
    if (ytop == npoi-0.5):
      ytop = npoi-0.51
    pave = R.TPave(1.0-errLO, ybot, 1.0+errHI, ytop)
    pave.SetBorderSize(1)
    #pave.SetFillStyle(3018)
    pave.SetFillColor(18)
    pave.SetLineWidth(0)
    pave.Draw()
    paves.append(pave)

  tline = R.TLine()
  tline.SetLineWidth(2)
  tline.SetLineColor(R.kGray+2)
  tline.SetLineStyle(2)
  tline.DrawLine(1.0, -0.5, 1.0, npoi-0.5)

  h.Draw('AXIS SAME')
  h.Draw('HIST SAME')
  tg.Draw('PE SAME')

  text = R.TLatex()
  text.SetTextSize(0.055)
  text.DrawLatexNDC(0.15, 0.930, '#it{ATLAS} #bf{Internal}')
  text.SetTextSize(0.035)
  text.DrawLatexNDC(0.56, 0.955, '#bf{ #sqrt{s}=13 TeV, 36.1 fb^{-1} }')
  text.DrawLatexNDC(0.56, 0.920, '#bf{ H #rightarrow #gamma#gamma,  m_{H}=125.09 GeV }')

  xmod, ymod = 0.0, 0.01
  pave = R.TPave(0.06-xmod, 0.04-ymod, 0.095-xmod, 0.075-ymod, 0, "NDC")
  pave.SetBorderSize(1)
  #pave.SetFillStyle(3018)
  pave.SetFillColor(18)
  pave.SetLineWidth(0)
  pave.Draw()
  text.SetTextSize(0.025)
  text.DrawLatexNDC(0.11-xmod, 0.05-ymod, '#bf{SM prediction}')
  #text.DrawLatexNDC(0.10-xmod, 0.0975, 'SM prediction')

  can.SaveAs('plots/summary_prodXS.pdf')

