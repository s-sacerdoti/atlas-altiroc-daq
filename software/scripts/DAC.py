def getDACList(board):
    dacList={}
    if board==2:
        dacList[5]=350
        dacList[6]=360
        dacList[7]=350
        dacList[8]=330
        dacList[10]=380
        dacList[12]=320
        dacList[13]=340
        dacList[14]=330
    elif board==3:
        dacList[1]=408
        dacList[2]=310
        dacList[3]=348
        dacList[4]=334
        dacList[5]=374
        dacList[6]=362
        dacList[7]=344
        dacList[8]=356      
        dacList[10]=340
        dacList[11]=374
        dacList[12]=360
        dacList[13]=382
        dacList[14]=418        
    elif board==8:
        dacList[0]=440#B8,4,0 
        dacList[1]=435#B8,4,1 
        dacList[2]=360#B8,4,1 
        dacList[3]=440#B8,4,1 
        dacList[4]=360#B8,4,1 
        dacList[5]=440#B8,4,1 
        dacList[6]=410#B8,4,0 
        dacList[7]=375#B8,4,1 
        dacList[8]=430#B8,4,1 
        dacList[9]=305#B8,4,1
        dacList[10]=455#B8,4,0.960000 
        dacList[11]=445#B8,4,0.980000 
        dacList[12]=410#B8,4,1.000000 
        dacList[13]=465#B8,4,0.960000 
        dacList[14]=295#B8,4,1.000000 
        # dacList[0]=   345 
        # dacList[1]=   335  
        # dacList[2]=   290
        # dacList[3]=   340
        # dacList[4]=   345
        # dacList[5]=   340
        # dacList[6]=   335#TOAfrac=0.2
        # dacList[7]=   305#TOAfrac=0.2
        # dacList[8]=   330
        # dacList[9]=   295 
        # dacList[10]=  365
        # dacList[11]=  355
        # dacList[12]=  330 
        # dacList[13]=  360#large TOAfrac
        # dacList[14]=  310
    elif board==13:
        # dacList[0]=320
        # dacList[1]=305
        # dacList[2]=330
        # dacList[3]=315
        # dacList[4]=305
        # dacList[5]=385
        # dacList[7]=310
        # dacList[8]=335      
        # dacList[9]=325  
        # dacList[10]=320
        # dacList[11]=345
        # dacList[12]=365
        # dacList[13]=345
        # dacList[14]=350

        dacList[0]=330#B13,4,1.000000 
        dacList[1]=310#B13,4,0.970000 
        dacList[2]=330#B13,4,1.000000 
        dacList[3]=320#B13,4,0.980000 
        dacList[4]=300#B13,4,0.990000 
        dacList[5]=390#B13,4,1.000000
        #dacList[6]=TOO noisy?
        dacList[7]=310#B13,4,0.990000 
        dacList[8]=340#B13,4,1.000000 
        dacList[9]=320#B13,4,0.980000         
        dacList[10]=320#B13,4,1.000000 
        dacList[11]=345#B13,4,0.970000 
        dacList[12]=365#B13,4,0.990000 
        dacList[13]=350#B13,4,0.990000 
        dacList[14]=340#Q=5
    

        
    elif board==15:
        dacList[0]=330
        dacList[1]=310
        dacList[2]=340
        dacList[3]=330
        dacList[4]=320
        dacList[5]=400
        dacList[7]=320
        dacList[8]=350      
        dacList[9]=340  
        dacList[10]=330
        dacList[11]=350
        dacList[12]=370
        dacList[13]=360
        dacList[14]=360
        dacList[15]=300
        dacList[16]=380
        dacList[17]=330
        dacList[18]=390
        dacList[19]=370      
        dacList[20]=350
        dacList[21]=340
        dacList[22]=430
        dacList[23]=400
        dacList[24]=360        
    elif board==18:
        dacList[0]=360
        dacList[1]=390
        dacList[2]=406
        dacList[3]=340
        #dacList[4]=440
        dacList[5]=360
        #dacList[6]=
        #dacList[7]=
        #dacList[8]=      
        dacList[9]=356  
        dacList[10]=344
        dacList[11]=336
        dacList[12]=326
        dacList[13]=376
        dacList[14]=376
        
    return dacList
