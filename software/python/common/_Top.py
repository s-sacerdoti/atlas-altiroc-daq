#!/usr/bin/env python3
##############################################################################
## This file is part of 'ATLAS ALTIROC DEV'.
## It is subject to the license terms in the LICENSE.txt file found in the 
## top-level directory of this distribution and at: 
##    https://confluence.slac.stanford.edu/display/ppareg/LICENSE.html. 
## No part of 'ATLAS ALTIROC DEV', including this file, 
## may be copied, modified, propagated, or distributed except according to 
## the terms contained in the LICENSE.txt file.
##############################################################################

import rogue
import rogue.hardware.axi
import rogue.utilities.fileio

import pyrogue
import pyrogue as pr
import pyrogue.protocols
import pyrogue.utilities.fileio
import pyrogue.interfaces.simulation

import common
import time
import click

rogue.Version.minVersion('3.7.0') 

class Top(pr.Root):
    def __init__(   self,       
            name        = 'Top',
            description = 'Container for FEB FPGA',
            ip          = ['10.0.0.1'],
            pollEn      = True,
            initRead    = True,
            configProm  = False,
            advanceUser = False,
            refClkSel   = 'IntClk',
            pllConfig   = 'config/pll-config/Si5345-RevD-Registers.csv',
            loadYaml    = True,
            userYaml    = [''],
            defaultFile = 'config/defaults.yml',
            **kwargs):
        super().__init__(name=name, description=description, **kwargs)
        
        # Set the min. firmware Version support by the software
        self.minFpgaVersion = 0x20000045
        
        # Enable Init after config
        self.InitAfterConfig._default = True        
        
        # Cache the parameters
        self.refClkSel   = refClkSel
        self.pllConfig   = pllConfig
        self.advanceUser = advanceUser
        self.configProm  = configProm
        self.ip          = ip
        self.numEthDev   = len(ip)  if (ip[0] != 'simulation') else 1
        self._timeout    = 1.0      if (ip[0] != 'simulation') else 100.0 
        self._pollEn     = pollEn   if (ip[0] != 'simulation') else False
        self._initRead   = initRead if (ip[0] != 'simulation') else False      
        self.loadYaml    = loadYaml
        self.userYaml    = userYaml
        self.defaultFile = defaultFile
        
        # File writer
        self.dataWriter = pr.utilities.fileio.StreamWriter()
        self.add(self.dataWriter)
                
        # Create arrays to be filled
        self.rudp       = [None for i in range(self.numEthDev)]
        self.srpStream  = [None for i in range(self.numEthDev)]
        self.dataStream = [None for i in range(self.numEthDev)]
        self.memMap     = [None for i in range(self.numEthDev)]
        
        # Loop through the devices
        for i in range(self.numEthDev):
        
            ######################################################################
            if (self.ip[0] == 'simulation'):
                self.srpStream[i]  = rogue.interfaces.stream.TcpClient('localhost',9000)
                self.dataStream[i] = rogue.interfaces.stream.TcpClient('localhost',9002)  
            else:
                self.rudp[i]       = pr.protocols.UdpRssiPack(host=ip[i],port=8192,packVer=2,jumbo=False)        
                self.srpStream[i]  = self.rudp[i].application(0)
                self.dataStream[i] = self.rudp[i].application(1) 
                
            ######################################################################
            
            # Connect the SRPv3 to PGPv3.VC[0]
            self.memMap[i] = rogue.protocols.srp.SrpV3()                
            pr.streamConnectBiDir( self.memMap[i], self.srpStream[i] )             
            
            # Connect data stream to file as channel to dataStream
            pr.streamConnect(self.dataStream[i],self.dataWriter.getChannel(i))
                
            ######################################################################
            
            # Add devices
            self.add(common.Fpga( 
                name        = f'Fpga[{i}]', 
                memBase     = self.memMap[i], 
                offset      = 0x00000000, 
                configProm  = self.configProm, 
                advanceUser = self.advanceUser, 
                expand      = True, 
            ))
        
        ######################################################################
        
        # Start the system
        self.start(
            pollEn   = self._pollEn,
            initRead = self._initRead,
            timeout  = self._timeout,
        )        
        
    def start(self,**kwargs):
        super(Top, self).start(**kwargs) 

        # Check if not PROM loading 
        if not self.configProm and (self.ip[0] != 'simulation'):
        
            # Hide all the "enable" variables
            for enableList in self.find(typ=pr.EnableVariable):
                # Hide by default
                enableList.hidden = True  
            
            # Loop through FPGA devices
            for i in range(self.numEthDev):
            
                # Check for min. FW version
                fwVersion = self.Fpga[i].AxiVersion.FpgaVersion.get()
                if (fwVersion < self.minFpgaVersion):
                    errMsg = f"""
                        Fpga[{i}].AxiVersion.FpgaVersion = {fwVersion:#04x} < {self.minFpgaVersion:#04x}
                        Please update Fpga[{i}] at IP={self.ip[i]} firmware using software/scripts/ReprogramFpga.py
                        """
                    click.secho(errMsg, bg='red')
                    raise ValueError(errMsg)
                
                # Check for an incompatible V1 FPGA eFUSE value
                if (self.Fpga[i].AxiVersion.Efuse.get() < 0x00004EA9):
                    errMsg = 'incompatible Version1 FPGA board Detected'
                    click.secho(errMsg, bg='red')
                    raise ValueError(errMsg)
                    
                # Check if the list of user YAML file les than number of FPGAs
                if (len(self.userYaml) < self.numEthDev):
                    errMsg = 'There are less User YAML files than the number of FPGAs to load'
                    click.secho(errMsg, bg='red')
                    raise ValueError(errMsg)                    
                
                if (self.advanceUser):
                    # Prevent FEB from thermal shutdown until FPGA Tj = 100 degC (max. operating temp)  
                    self.Fpga[i].BoardTemp.RemoteTcritSetpoint.set(95)    
         
                # Set the PLL reference
                self.Fpga[i].Asic.Gpio.RefClkSel.setDisp(self.refClkSel)
                     
                # Load the PLL configurations
                self.Fpga[i].Pll.CsvFilePath.set(self.pllConfig)
                
                # Check if not locked
                if (not self.Fpga[i].Pll.Locked.get()):
                    self.Fpga[i].Pll.LoadCsvFile()
                                        
            # Wait for the SiLab PLL to lock
            print ('Waiting for SiLab PLLs to lock')
            time.sleep(1.0)
            
            # Loop through the devices
            for i in range(self.numEthDev):             
                retry = 0
                while (retry<2):
                    if (self.Fpga[i].Pll.Locked.get()):
                        break
                    else:
                        retry = retry + 1
                        self.Fpga[i].Pll.LoadCsvFile() 
                        time.sleep(5.0)          
                        
                # Print the results
                if (retry<2):
                    print (f'PLL[{i}] locks established')
                else:
                    click.secho(
                        "\n\n\
                        ***************************************************\n\
                        ***************************************************\n\
                        Failed to establish PLL[%i] locking after 10 seconds\n\
                        ***************************************************\n\
                        ***************************************************\n\n"\
                        % i, bg='red',
                    )    
        
            # Loop through FPGA devices
            for i in range(self.numEthDev):
                
                # Hide unused variables (clean up GUI display)
                self.Fpga[i].AxiVersion.UserReset.hidden = True
                self.Fpga[i].AxiVersion.DeviceId.hidden  = True
                
                # Unhide the ASIC's enable that are dependent on Pll.Locked
                self.Fpga[i].Asic.TdcClk.enable.hidden   = False
                self.Fpga[i].Asic.CalPulse.enable.hidden = False
                self.Fpga[i].Asic.Trig.enable.hidden     = False
                self.Fpga[i].Asic.Probe.enable.hidden    = False
                self.Fpga[i].Asic.Readout.enable.hidden  = False
                
                # Check if we are loading YAML files
                if self.loadYaml:
                    # Load the Default YAML file
                    print(f'Loading Fpga[{i}]:path={self.defaultFile} Default Configuration File...')
                    self.LoadConfig(self.defaultFile)                
                    # Load the board specific YAML file
                    if (self.userYaml[i] != ''):
                        print(f'Loading Fpga[{i}]:path={self.userYaml[i]} User Configuration File...')
                        self.LoadConfig(self.userYaml[i])

                
                    
                
        else:
            # Hide all the "enable" variables
            for enableList in self.find(typ=pr.EnableVariable):
                # Hide by default
                enableList.hidden = True  
                
        if (self._initRead):               
            self.ReadAll()
            self.ReadAll()
     
    # Function calls after loading YAML configuration
    def initialize(self):
        super().initialize()
        for i in range(self.numEthDev):
            # Reset the RAM, TDC and DLL resets
            self.Fpga[i].Asic.Gpio.RSTB_RAM.set(0x0)
            self.Fpga[i].Asic.Gpio.RSTB_TDC.set(0x0)
            self.Fpga[i].Asic.Gpio.RSTB_DLL.set(0x0)
            time.sleep(0.001)
            self.Fpga[i].Asic.Gpio.RSTB_RAM.set(0x1)                
            self.Fpga[i].Asic.Gpio.RSTB_TDC.set(0x1)
            self.Fpga[i].Asic.Gpio.RSTB_DLL.set(0x1)
            
            # Reset the sequence and trigger counters
            self.Fpga[i].Asic.Trig.CountReset()
            self.Fpga[i].Asic.Readout.SeqCntRst()
            
