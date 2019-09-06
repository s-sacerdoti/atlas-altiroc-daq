#Probe ON. For probe OFF change RestoreProbeConfig=0x0 in config yml - will be off during measurement, but on before and after.

#scan TOT vs Qinj - 
python scripts/measureTOT.py  --board 8 --useExt False --ch 0 --DAC 500 --pulserMin 0 --pulserMax 20 --pulserStep 1
#scan TOT vs extTrig width ... is discri probe a copy of ext trig? Can't turn discri off!!
python scripts/measureTOT.py  --board 8 --useExt True --ch 0  --pulserMin 2000 --pulserMax 2700 --pulserStep 10
## obs: result changes when using LegacyV1AsicCalPulseStart or CalPulse.Start()??

#measure TOA vs cmd_pulser delay 
python scripts/measureTOA.py --board 8 --useExt False --ch 0 --DAC 500 --delayMin 2300 --delayMax 2700 --delayStep 20
#TOA vs extTrig pulse (constant width, changing delay)
python scripts/measureTOA.py --board 8 --useExt True --ch 0 --delayMin 1850 --delayMax 2300 --delayStep 10

#sort of working TOA vs TOT vs Qinj
python scripts/measureTW.py --ip 192.168.1.10 --board 8 --useExt False --ch 0 --DAC 500 --pulserMin 0 --pulserMax 20 --pulserStep 1
