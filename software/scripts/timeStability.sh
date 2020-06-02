B=9


for i in $(seq 10 20); 
do
    #d=Data/B9-toa-clkV$i
    d=Data/B$B-toa-clkV$i
    
    mkdir $d
    python scripts/runTimeWalkScans.py  -b $B -o $d
    source runTW_B$B.sh
    echo $d
    sleep 600
done

