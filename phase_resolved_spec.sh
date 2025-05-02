# 1- change the phase range xx:xx and the phase change for the naming xx-xx 
# 2- change the source name
# 3- change the initial values for the period, freq and it's derivatve in case of new source

cp PNclean_barry_source_filtered_0.3-10kev_0882184001.fits PNclean_barry_source_filtered_0.3-10kev_0882184001_phase.fits 

#build the phase column of the source file (must be in the barycentered event)
phasecalc tables=PNclean_barry_source_filtered_0.3-10kev_0882184001.fits:EVENTS frequency=0.3075268206574549 frequencydot=-5.248226316513e-12 epoch=2022-10-16T03:49:14.816


#select intervals in phase
tabgtigen table=PNclean_barry_source_filtered_0.3-10kev_0882184001_phase.fits:EVENTS expression='(PHASE in [0.5:0.8])' gtiset=PNgti_0882184001_src_0.5-0.8.fits timecolumn=TIME

evselect table=PNclean_barry_source_filtered_0.3-10kev_0882184001_phase.fits:EVENTS withfilteredset=yes filteredset=PNclean_barry_source_filtered_0.3-10kev_0882184001_phase_0.5-0.8.fits destruct=Y expression='#XMMEA_EP && gti(PNgti_0882184001_src_0.5-0.8.fits,TIME)' updateexposure=yes filterexposure=yes keepfilteroutput=yes

evselect table=PNclean_barry_source_filtered_0.3-10kev_0882184001_phase_0.5-0.8.fits withspectrumset=yes spectrumset=PNclean_barry_source_filtered_0.3-10kev_0882184001_phase_0.5-0.8_spectra.fits energycolumn=PI spectralbinsize=5 withspecranges=yes specchannelmin=0 specchannelmax=20479 expression='(FLAG==0) && (PATTERN <=4) && (PI>150)'


############## Same for the bkg ###########
phasecalc tables=PNclean_barry_bkg_filtered_0.3-10kev_0882184001.fits:EVENTS frequency=0.3075268206574549 frequencydot=-5.248226316513e-12 epoch=2022-10-16T03:49:14.816

cp PNclean_barry_bkg_filtered_0.3-10kev_0882184001.fits PNclean_barry_bkg_filtered_0.3-10kev_0882184001_phase.fits 

tabgtigen table=PNclean_barry_bkg_filtered_0.3-10kev_0882184001_phase.fits:EVENTS expression='(PHASE in [0.5:0.8])' gtiset=PNgti_0882184001_bkg_0.5-0.8.fits timecolumn=TIME

evselect table=PNclean_barry_bkg_filtered_0.3-10kev_0882184001_phase.fits:EVENTS withfilteredset=yes filteredset=PNclean_barry_bkg_filtered_0.3-10kev_0882184001_phase_0.5-0.8.fits destruct=Y expression='#XMMEA_EP && gti(PNgti_0882184001_bkg_0.5-0.8.fits,TIME)' updateexposure=yes filterexposure=yes keepfilteroutput=yes

evselect table=PNclean_barry_bkg_filtered_0.3-10kev_0882184001_phase_0.5-0.8.fits withspectrumset=yes spectrumset=PNclean_barry_bkg_filtered_0.3-10kev_0882184001_phase_0.5-0.8_spectra.fits energycolumn=PI spectralbinsize=5 withspecranges=yes specchannelmin=0 specchannelmax=20479 expression='(FLAG==0) && (PATTERN <=4) && (PI>150)'



backscale spectrumset=PNclean_barry_bkg_filtered_0.3-10kev_0882184001_phase_0.5-0.8_spectra.fits badpixlocation=PNclean_bary_0882184001.fits 
backscale spectrumset=PNclean_barry_source_filtered_0.3-10kev_0882184001_phase_0.5-0.8_spectra.fits badpixlocation=PNclean_bary_0882184001.fits 

rmfgen spectrumset=PNclean_barry_source_filtered_0.3-10kev_0882184001_phase_0.5-0.8_spectra.fits rmfset=PNsrc_0882184001_phase_0.5-0.8.rmf
arfgen spectrumset=PNclean_barry_source_filtered_0.3-10kev_0882184001_phase_0.5-0.8_spectra.fits arfset=PNsrc_0882184001_phase_0.5-0.8.arf withrmfset=yes rmfset=PNsrc_0882184001_phase_0.5-0.8.rmf detmaptype=psf badpixlocation=PNclean_bary_0882184001.fits


specgroup spectrumset=PNclean_barry_source_filtered_0.3-10kev_0882184001_phase_0.5-0.8_spectra.fits mincounts=50 oversample=3 setbad='0:0.3,10.0-100.0' units=KEV rmfset=PNsrc_0882184001_phase_0.5-0.8.rmf arfset=PNsrc_0882184001_phase_0.5-0.8.arf backgndset=PNclean_barry_bkg_filtered_0.3-10kev_0882184001_phase_0.5-0.8_spectra.fits groupedset=PNsrc_0882184001_phase_0.5-0.8_spectra_grp50.fits
