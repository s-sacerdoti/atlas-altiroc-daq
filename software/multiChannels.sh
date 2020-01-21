#NAME="MC-SRAMON-PAON-DISCRION-CTESTON"
#NAME="MC-15ch-PAOFF-DISCRIOFF-SRAMOFF-CTESTOFF-TrigExtOFF-V1"

#NAME="MC-15ch-PAOFF-DISCRIOFF-SRAMOFF-CTESTOFF-TrigExtON-V1"

NAME="testMC-12ch-PAON-DISCRION-SRAMOFF-CTESTOFF-TrigExtOFF-V2"
#NAME="MC-ch14-PAON-DISCRION-SRAMOFF-CTESTOFF-TrigExtOFF-V2"


#NO TRIG EXT
#NO TRIG EXT
#NO TRIG EXT
#NO TRIG EXT
#python scripts/measureTimeWalk.py --skipExistingFile True --morePointsAtLowQ False --debug False --display False --moreStatAtLowQ True -N 100 --useProbePA False --useProbeDiscri False  --checkOFtoa False --checkOFtot False --board 8  --delay 2500  --QMin 5 --QMax 63 --QStep 1 --out Data/$NAME  --ch 4  --Cd 4 --DAC 345 --Rin_Vpa 0
#sleep 5

#python scripts/measureTOA.py --skipExistingFile True -N 50 --debug False --display False --Cd 4 --checkOFtoa False --checkOFtot False --ch 4 --board 8 --DAC 345 --Q 13 --delayMin 2200 --delayMax 2700 --delayStep 1 --out Data/$NAME
#sleep 5

## ADD --Cd 0

N=50
ch=4
cd=0

#python scripts/measureTOA.py --skipExistingFile True -N $N --debug False --display False --checkOFtoa False --checkOFtot False  --board 8 --ch $ch --useExt True --delayMin 1800 --delayMax 2300 --delayStep 1  --out Data/$NAME --DAC 320 --Cd $cd
#sleep 5

#python scripts/measureTOA.py --skipExistingFile True -N $N --debug False --display False --checkOFtoa False --checkOFtot False  --board 8 --ch $ch --useExt True --delayMin 1800 --delayMax 2300 --delayStep 1  --out Data/$NAME --DAC 365 --Cd $cd
#sleep 5 

#python scripts/measureTOA.py --skipExistingFile True -N $N --debug False --display False --checkOFtoa False --checkOFtot False  --board 8 --ch $ch --useExt True --delayMin 1800 --delayMax 2300 --delayStep 1  --out Data/$NAME --DAC 400 --Cd $cd
#sleep 5


#for ch in 0 1 2 3 5 6 7;
for ch in 0; 	  
do 
python scripts/measureTOA.py --skipExistingFile True -N $N --debug False --display False --checkOFtoa False --checkOFtot False  --board 8 --ch $ch --useExt True --delayMin 1800 --delayMax 2300 --delayStep 5  --out Data/$NAME --DAC 400 --Cd $cd
sleep 3
done



#No Cd DAC 400
#python scripts/measureTOA.py --skipExistingFile True -N $N --debug False --display False --checkOFtoa False --checkOFtot False  --board 8 --ch $ch --useExt True --delayMin 1800 --delayMax 2300 --delayStep 1  --out Data/$NAME --DAC 400 
