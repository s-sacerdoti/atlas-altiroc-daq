##############################################################################
## This file is part of 'ATLAS ALTIROC DEV'.
## It is subject to the license terms in the LICENSE.txt file found in the 
## top-level directory of this distribution and at: 
##    https://confluence.slac.stanford.edu/display/ppareg/LICENSE.html. 
## No part of 'ATLAS ALTIROC DEV', including this file, 
## may be copied, modified, propagated, or distributed except according to 
## the terms contained in the LICENSE.txt file.
##############################################################################

# ASIC Ports

set_property -dict { PACKAGE_PIN U4 IOSTANDARD LVCMOS12 DRIVE 8 SLEW FAST } [get_ports { renable      }]; #  RENABLE
set_property -dict { PACKAGE_PIN U6 IOSTANDARD LVCMOS12 DRIVE 8 SLEW FAST } [get_ports { srinSc       }]; #  SRIN_SC
set_property -dict { PACKAGE_PIN U5 IOSTANDARD LVCMOS12 DRIVE 8 SLEW FAST } [get_ports { rstbSc       }]; #  RSTB_SC
set_property -dict { PACKAGE_PIN U2 IOSTANDARD LVCMOS12 DRIVE 8 SLEW FAST } [get_ports { ckSc         }]; #  CK_SC
set_property -dict { PACKAGE_PIN U1 IOSTANDARD LVCMOS12 DRIVE 8 SLEW FAST } [get_ports { srinProbe    }]; #  SRIN_PROBE
set_property -dict { PACKAGE_PIN W6 IOSTANDARD LVCMOS12 DRIVE 8 SLEW FAST } [get_ports { rstbProbe    }]; #  RSTB_PROBE
set_property -dict { PACKAGE_PIN W5 IOSTANDARD LVCMOS12 DRIVE 8 SLEW FAST } [get_ports { rstbRam      }]; #  RSTB_RAM
set_property -dict { PACKAGE_PIN V3 IOSTANDARD LVCMOS12 DRIVE 8 SLEW FAST } [get_ports { rstbRead     }]; #  RSTB_READ
set_property -dict { PACKAGE_PIN W3 IOSTANDARD LVCMOS12 DRIVE 8 SLEW FAST } [get_ports { rstbTdc      }]; #  RSTB_TDC
set_property -dict { PACKAGE_PIN U7 IOSTANDARD LVCMOS12 DRIVE 8 SLEW FAST } [get_ports { rstbCounter  }]; #  RSTB_COUNTER
set_property -dict { PACKAGE_PIN V6 IOSTANDARD LVCMOS12 DRIVE 8 SLEW FAST } [get_ports { ckProbeAsic  }]; #  CK_PROBE_ASIC
set_property -dict { PACKAGE_PIN V4 IOSTANDARD LVCMOS12 DRIVE 8 SLEW FAST } [get_ports { ckWriteAsic  }]; #  CK_WRITE_ASIC

set_property -dict { PACKAGE_PIN AE2 IOSTANDARD LVCMOS12 } [get_ports { sroutSc      }]; #  SROUT_SC
set_property -dict { PACKAGE_PIN AE6 IOSTANDARD LVCMOS12 } [get_ports { digProbe[0]  }]; #  DIGITAL_PROBE[2:1]
set_property -dict { PACKAGE_PIN AE5 IOSTANDARD LVCMOS12 } [get_ports { digProbe[1]  }]; #  DIGITAL_PROBE[2:1]
set_property -dict { PACKAGE_PIN AF3 IOSTANDARD LVCMOS12 } [get_ports { sroutProbe   }]; #  SROUT_PROBE
set_property -dict { PACKAGE_PIN AF2 IOSTANDARD LVCMOS12 } [get_ports { totBusyb     }]; #  TOT_BUSYB
set_property -dict { PACKAGE_PIN T7  IOSTANDARD LVCMOS12 } [get_ports { toaBusyb     }]; #  TOA_BUSYB

set_property -dict { PACKAGE_PIN F14 IOSTANDARD LVCMOS25 SLEW FAST } [get_ports { extTrig }]; #  EXT_TRIG

set_property -dict { PACKAGE_PIN W10 IOSTANDARD LVDS DIFF_TERM true } [get_ports { doutP }]; #  DOUT_P
set_property -dict { PACKAGE_PIN W9  IOSTANDARD LVDS DIFF_TERM true } [get_ports { doutN }]; #  DOUT_N

set_property -dict { PACKAGE_PIN AC8 IOSTANDARD LVDS } [get_ports { cmdPulseP }]; #  CMD_PULSE_P
set_property -dict { PACKAGE_PIN AD8 IOSTANDARD LVDS } [get_ports { cmdPulseN }]; #  CMD_PULSE_N

# CMD Pulse Delay Ports

set_property -dict { PACKAGE_PIN L23 IOSTANDARD LVCMOS33 } [get_ports { dlyLen }];

set_property -dict { PACKAGE_PIN H23 IOSTANDARD LVCMOS33 } [get_ports { dlyData[0] }];
set_property -dict { PACKAGE_PIN H24 IOSTANDARD LVCMOS33 } [get_ports { dlyData[1] }];
set_property -dict { PACKAGE_PIN J21 IOSTANDARD LVCMOS33 } [get_ports { dlyData[2] }];
set_property -dict { PACKAGE_PIN H22 IOSTANDARD LVCMOS33 } [get_ports { dlyData[3] }];
set_property -dict { PACKAGE_PIN J24 IOSTANDARD LVCMOS33 } [get_ports { dlyData[4] }];
set_property -dict { PACKAGE_PIN J25 IOSTANDARD LVCMOS33 } [get_ports { dlyData[5] }];
set_property -dict { PACKAGE_PIN L22 IOSTANDARD LVCMOS33 } [get_ports { dlyData[6] }];
set_property -dict { PACKAGE_PIN K22 IOSTANDARD LVCMOS33 } [get_ports { dlyData[7] }];
set_property -dict { PACKAGE_PIN K23 IOSTANDARD LVCMOS33 } [get_ports { dlyData[8] }];
set_property -dict { PACKAGE_PIN J23 IOSTANDARD LVCMOS33 } [get_ports { dlyData[9] }];

set_property -dict { PACKAGE_PIN H21 IOSTANDARD LVCMOS33 } [get_ports { dlyTempScl }];
set_property -dict { PACKAGE_PIN G21 IOSTANDARD LVCMOS33 } [get_ports { dlyTempSda }];

# Jitter Cleaner PLL Ports

set_property -dict { PACKAGE_PIN K6 } [get_ports { localRefClkP }];
set_property -dict { PACKAGE_PIN K5 } [get_ports { localRefClkN }];

set_property -dict { PACKAGE_PIN AB12 IOSTANDARD LVDS } [get_ports { pllClkOutP }];
set_property -dict { PACKAGE_PIN AC12 IOSTANDARD LVDS } [get_ports { pllClkOutN }];

set_property -dict { PACKAGE_PIN AC9 IOSTANDARD LVDS DIFF_TERM true } [get_ports { pllClkInP[0] }];
set_property -dict { PACKAGE_PIN AD9 IOSTANDARD LVDS DIFF_TERM true } [get_ports { pllClkInN[0] }];

set_property -dict { PACKAGE_PIN AB11 IOSTANDARD LVDS DIFF_TERM true } [get_ports { pllClkInP[1] }];
set_property -dict { PACKAGE_PIN AC11 IOSTANDARD LVDS DIFF_TERM true } [get_ports { pllClkInN[1] }];

set_property -dict { PACKAGE_PIN E10 IOSTANDARD LVDS_25 DIFF_TERM true } [get_ports { pllClkInP[2] }];
set_property -dict { PACKAGE_PIN D10 IOSTANDARD LVDS_25 DIFF_TERM true } [get_ports { pllClkInN[2] }];

set_property -dict { PACKAGE_PIN C12 IOSTANDARD LVDS_25 DIFF_TERM true } [get_ports { pllClkInP[3] }];
set_property -dict { PACKAGE_PIN C11 IOSTANDARD LVDS_25 DIFF_TERM true } [get_ports { pllClkInN[3] }];

set_property -dict { PACKAGE_PIN AD10 IOSTANDARD LVCMOS18 SLEW FAST } [get_ports { pllClkSel[0]}];
set_property -dict { PACKAGE_PIN AE10 IOSTANDARD LVCMOS18 SLEW FAST } [get_ports { pllClkSel[1]}];
set_property -dict { PACKAGE_PIN AE12 IOSTANDARD LVCMOS18           } [get_ports { pllIntrL    }];
set_property -dict { PACKAGE_PIN AF12 IOSTANDARD LVCMOS18           } [get_ports { pllLolL     }];
set_property -dict { PACKAGE_PIN AE8  IOSTANDARD LVCMOS18 SLEW FAST } [get_ports { pllSpiSclk  }];
set_property -dict { PACKAGE_PIN AF8  IOSTANDARD LVCMOS18 SLEW FAST } [get_ports { pllSpiSdi   }];
set_property -dict { PACKAGE_PIN AE13 IOSTANDARD LVCMOS18 SLEW FAST } [get_ports { pllSpiCsL   }];
set_property -dict { PACKAGE_PIN AF13 IOSTANDARD LVCMOS18           } [get_ports { pllSpiSdo   }];
set_property -dict { PACKAGE_PIN AF10 IOSTANDARD LVCMOS18 SLEW FAST } [get_ports { pllSpiRstL  }];
set_property -dict { PACKAGE_PIN AF9  IOSTANDARD LVCMOS18 SLEW FAST } [get_ports { pllSpiOeL   }];

# DAC Ports

set_property -dict { PACKAGE_PIN E26 IOSTANDARD LVCMOS33 SLEW FAST } [get_ports { dacCsL }];
set_property -dict { PACKAGE_PIN J26 IOSTANDARD LVCMOS33 SLEW FAST } [get_ports { dacSclk }];
set_property -dict { PACKAGE_PIN H26 IOSTANDARD LVCMOS33 SLEW FAST } [get_ports { dacSdi }];

# TTL IN/OUT Ports

set_property -dict { PACKAGE_PIN G22 IOSTANDARD LVCMOS33 } [get_ports { trigL }];
set_property -dict { PACKAGE_PIN G26 IOSTANDARD LVCMOS33 } [get_ports { busy }];
set_property -dict { PACKAGE_PIN F22 IOSTANDARD LVCMOS33 } [get_ports { spareInL }];
set_property -dict { PACKAGE_PIN D23 IOSTANDARD LVCMOS33 } [get_ports { spareOut }];

# Serial Communication Ports

set_property -dict { PACKAGE_PIN F2 } [get_ports { gtTxP }];
set_property -dict { PACKAGE_PIN F1 } [get_ports { gtTxN }];
set_property -dict { PACKAGE_PIN G4 } [get_ports { gtRxP }];
set_property -dict { PACKAGE_PIN G3 } [get_ports { gtRxN }];
set_property -dict { PACKAGE_PIN D6 } [get_ports { gtClkP }];
set_property -dict { PACKAGE_PIN D5 } [get_ports { gtClkN }];

# Boot Memory Ports

set_property -dict { PACKAGE_PIN C23 IOSTANDARD LVCMOS33 } [get_ports { bootCsL }];
set_property -dict { PACKAGE_PIN B24 IOSTANDARD LVCMOS33 } [get_ports { bootMosi }];
set_property -dict { PACKAGE_PIN A25 IOSTANDARD LVCMOS33 } [get_ports { bootMiso }];

# Misc Ports

set_property -dict { PACKAGE_PIN A13 IOSTANDARD LVCMOS25 } [get_ports { oscOe[0] }];
set_property -dict { PACKAGE_PIN A12 IOSTANDARD LVCMOS25 } [get_ports { oscOe[1] }];
set_property -dict { PACKAGE_PIN J14 IOSTANDARD LVCMOS25 } [get_ports { oscOe[2] }];
set_property -dict { PACKAGE_PIN F25 IOSTANDARD LVCMOS33 } [get_ports { oscOe[3] }];

set_property -dict { PACKAGE_PIN J8  IOSTANDARD LVCMOS25 } [get_ports { led[0] }];
set_property -dict { PACKAGE_PIN H9  IOSTANDARD LVCMOS25 } [get_ports { led[1] }];
set_property -dict { PACKAGE_PIN H8  IOSTANDARD LVCMOS25 } [get_ports { led[2] }];
set_property -dict { PACKAGE_PIN G10 IOSTANDARD LVCMOS25 } [get_ports { led[3] }];

set_property -dict { PACKAGE_PIN C24 IOSTANDARD LVCMOS33 } [get_ports { pwrSyncSclk }];
set_property -dict { PACKAGE_PIN D21 IOSTANDARD LVCMOS33 } [get_ports { pwrSyncFclk }];

set_property -dict { PACKAGE_PIN C22 IOSTANDARD LVCMOS33 } [get_ports { pwrScl }];
set_property -dict { PACKAGE_PIN B20 IOSTANDARD LVCMOS33 } [get_ports { pwrSda }];

set_property -dict { PACKAGE_PIN K21 IOSTANDARD LVCMOS33 } [get_ports { tempAlertL }];

##############################################################################

set_property CFGBVS VCCO         [current_design]
set_property CONFIG_VOLTAGE 3.3  [current_design]

set_property BITSTREAM.CONFIG.CONFIGRATE 50 [current_design] 

##############################################################################
