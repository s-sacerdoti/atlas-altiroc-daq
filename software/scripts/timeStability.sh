B=8


for i in $(seq 100 120); 
do
    #d=Data/B9-toa-clkV$i
    d=Data/B$B-toa-clkV$i
    
    mkdir $d
    python scripts/runTimeWalkScans.py  -b $B -o $d
    source runTW_B$B.sh
    echo $d
    sleep 600
done

