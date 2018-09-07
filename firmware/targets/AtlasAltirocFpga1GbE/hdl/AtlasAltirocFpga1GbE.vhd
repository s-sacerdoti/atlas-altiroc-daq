-------------------------------------------------------------------------------
-- File       : AtlasAltirocFpga1GbE.vhd
-- Company    : SLAC National Accelerator Laboratory
-- Created    : 2018-09-06
-- Last update: 2018-09-07
-------------------------------------------------------------------------------
-- Description: Top-Level module using 1 GbE communication
-------------------------------------------------------------------------------
-- This file is part of 'ATLAS ALTIROC DEV'.
-- It is subject to the license terms in the LICENSE.txt file found in the 
-- top-level directory of this distribution and at: 
--    https://confluence.slac.stanford.edu/display/ppareg/LICENSE.html. 
-- No part of 'ATLAS ALTIROC DEV', including this file, 
-- may be copied, modified, propagated, or distributed except according to 
-- the terms contained in the LICENSE.txt file.
-------------------------------------------------------------------------------

library ieee;
use ieee.std_logic_1164.all;

use work.StdRtlPkg.all;

entity AtlasAltirocFpga1GbE is
   generic (
      TPD_G        : time := 1 ns;
      BUILD_INFO_G : BuildInfoType);
   port (
      -- ASIC Ports
      renable      : out   sl;               -- RENABLE
      srinSc       : out   sl;               -- SRIN_SC
      rstbSc       : out   sl;               -- RSTB_SC
      ckSc         : out   sl;               -- CK_SC
      srinProbe    : out   sl;               -- SRIN_PROBE
      rstbProbe    : out   sl;               -- RSTB_PROBE
      rstbRam      : out   sl;               -- RSTB_RAM
      rstbRead     : out   sl;               -- RSTB_READ
      rstbTdc      : out   sl;               -- RSTB_TDC
      rstbCounter  : out   sl;               -- RSTB_COUNTER
      ckProbeAsic  : out   sl;               -- CK_PROBE_ASIC
      ckWriteAsic  : out   sl;               -- CK_WRITE_ASIC
      extTrig      : out   sl;               -- EXT_TRIG
      sroutSc      : in    sl;               -- SROUT_SC
      digProbe     : in    slv(1 downto 0);  -- DIGITAL_PROBE[2:1]
      sroutProbe   : in    sl;               -- SROUT_PROBE
      totBusyb     : in    sl;               -- TOT_BUSYB
      toaBusyb     : in    sl;               -- TOA_BUSYB
      doutP        : in    sl;               -- DOUT_P
      doutN        : in    sl;               -- DOUT_N
      cmdPulseP    : out   sl;               -- CMD_PULSE_P
      cmdPulseN    : out   sl;               -- CMD_PULSE_N
      -- CMD Pulse Delay Ports
      dlyLen       : out   sl;
      dlyData      : out   slv(9 downto 0);
      dlyTempScl   : inout sl;
      dlyTempSda   : inout sl;
      -- Jitter Cleaner PLL Ports
      localRefClkP : in    sl;
      localRefClkN : in    sl;
      pllClkOutP   : out   sl;
      pllClkOutN   : out   sl;
      pllClkInP    : in    slv(3 downto 0);
      pllClkInN    : in    slv(3 downto 0);
      pllSpiCsL    : out   sl;
      pllSpiSclk   : out   sl;
      pllSpiSdi    : out   sl;
      pllSpiSdo    : in    sl;
      pllSpiRstL   : out   sl;
      pllSpiOeL    : out   sl;
      pllClkSel    : out   slv(1 downto 0);
      pllIntrL     : in    sl;
      pllLolL      : in    sl;
      -- DAC Ports
      dacCsL       : out   sl;
      dacSclk      : out   sl;
      dacSdi       : out   sl;
      -- TTL IN/OUT Ports
      trigL        : in    sl;
      busy         : out   sl;
      spareInL     : in    sl;
      spareOut     : out   sl;
      -- Serial Communication Ports
      gtClkP       : in    sl;
      gtClkN       : in    sl;
      gtRxP        : in    sl;
      gtRxN        : in    sl;
      gtTxP        : out   sl;
      gtTxN        : out   sl;
      -- Boot Memory Ports
      bootCsL      : out   sl;
      bootMosi     : out   sl;
      bootMiso     : in    sl;
      -- Misc Ports
      oscOe        : out   slv(3 downto 0);
      led          : out   slv(3 downto 0);
      pwrSyncSclk  : out   sl;
      pwrSyncFclk  : out   sl;
      pwrScl       : inout sl;
      pwrSda       : inout sl;
      tempAlertL   : in    sl;
      vPIn         : in    sl;
      vNIn         : in    sl);
end AtlasAltirocFpga1GbE;

architecture top_level of AtlasAltirocFpga1GbE is

begin

   U_Core : entity work.AtlasAltirocCore
      generic map (
         TPD_G        => TPD_G,
         BUILD_INFO_G => BUILD_INFO_G,
         COM_TYPE_G   => "ETH",
         ETH_10G_G    => false,
         DHCP_G       => true,
         IP_ADDR_G    => x"0A01A8C0")  -- 192.168.1.10 (before DHCP)            
      port map (
         -- ASIC Ports
         renable      => renable,
         srinSc       => srinSc,
         rstbSc       => rstbSc,
         ckSc         => ckSc,
         srinProbe    => srinProbe,
         rstbProbe    => rstbProbe,
         rstbRam      => rstbRam,
         rstbRead     => rstbRead,
         rstbTdc      => rstbTdc,
         rstbCounter  => rstbCounter,
         ckProbeAsic  => ckProbeAsic,
         ckWriteAsic  => ckWriteAsic,
         extTrig      => extTrig,
         sroutSc      => sroutSc,
         digProbe     => digProbe,
         sroutProbe   => sroutProbe,
         totBusyb     => totBusyb,
         toaBusyb     => toaBusyb,
         doutP        => doutP,
         doutN        => doutN,
         cmdPulseP    => cmdPulseP,
         cmdPulseN    => cmdPulseN,
         -- CMD Pulse Delay Ports
         dlyLen       => dlyLen,
         dlyData      => dlyData,
         dlyTempScl   => dlyTempScl,
         dlyTempSda   => dlyTempSda,
         -- Jitter Cleaner PLL Ports
         localRefClkP => localRefClkP,
         localRefClkN => localRefClkN,
         pllClkOutP   => pllClkOutP,
         pllClkOutN   => pllClkOutN,
         pllClkInP    => pllClkInP,
         pllClkInN    => pllClkInN,
         pllSpiCsL    => pllSpiCsL,
         pllSpiSclk   => pllSpiSclk,
         pllSpiSdi    => pllSpiSdi,
         pllSpiSdo    => pllSpiSdo,
         pllSpiRstL   => pllSpiRstL,
         pllSpiOeL    => pllSpiOeL,
         pllClkSel    => pllClkSel,
         pllIntrL     => pllIntrL,
         pllLolL      => pllLolL,
         -- DAC Ports
         dacCsL       => dacCsL,
         dacSclk      => dacSclk,
         dacSdi       => dacSdi,
         -- TTL IN/OUT Ports
         trigL        => trigL,
         busy         => busy,
         spareInL     => spareInL,
         spareOut     => spareOut,
         -- Serial Communication Ports
         gtClkP       => gtClkP,
         gtClkN       => gtClkN,
         gtRxP        => gtRxP,
         gtRxN        => gtRxN,
         gtTxP        => gtTxP,
         gtTxN        => gtTxN,
         -- Boot Memory Ports
         bootCsL      => bootCsL,
         bootMosi     => bootMosi,
         bootMiso     => bootMiso,
         -- Misc Ports
         led          => led,
         oscOe        => oscOe,
         pwrSyncSclk  => pwrSyncSclk,
         pwrSyncFclk  => pwrSyncFclk,
         pwrScl       => pwrScl,
         pwrSda       => pwrSda,
         tempAlertL   => tempAlertL,
         vPIn         => vPIn,
         vNIn         => vNIn);

end top_level;
