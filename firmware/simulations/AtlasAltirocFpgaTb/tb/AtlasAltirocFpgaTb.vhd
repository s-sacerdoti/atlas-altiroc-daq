-------------------------------------------------------------------------------
-- File       : AtlasAltirocFpgaTb.vhd
-- Company    : SLAC National Accelerator Laboratory
-- Created    : 2018-06-18
-- Last update: 2018-11-20
-------------------------------------------------------------------------------
-- Description: Simulation Testbed for testing the AtlasAltirocFpga module
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
use ieee.std_logic_unsigned.all;
use ieee.std_logic_arith.all;

use work.StdRtlPkg.all;
use work.AxiLitePkg.all;
use work.AxiStreamPkg.all;
use work.Pgp3Pkg.all;
use work.BuildInfoPkg.all;

entity AtlasAltirocFpgaTb is end AtlasAltirocFpgaTb;

architecture testbed of AtlasAltirocFpgaTb is

   constant TPD_G : time := 1 ns;

   signal clk160MHzP : sl := '0';
   signal clk160MHzN : sl := '1';

   signal pgpClkP : sl := '0';
   signal pgpClkN : sl := '1';

   signal shiftSc    : sl := '0';
   signal shiftProbe : sl := '0';

   signal pllClkInP : slv(3 downto 0);
   signal pllClkInN : slv(3 downto 0);

begin

   U_Clk160 : entity work.ClkRst
      generic map (
         CLK_PERIOD_G      => 6.256 ns,  -- 159.8 MHz
         RST_START_DELAY_G => 0 ns,  -- Wait this long into simulation before asserting reset
         RST_HOLD_TIME_G   => 1000 ns)  -- Hold reset for this long)
      port map (
         clkP => clk160MHzP,
         clkN => clk160MHzN);

   U_ClkPgp : entity work.ClkRst
      generic map (
         CLK_PERIOD_G      => 3.2 ns,   -- 312.5 MHz
         RST_START_DELAY_G => 0 ns,  -- Wait this long into simulation before asserting reset
         RST_HOLD_TIME_G   => 1000 ns)  -- Hold reset for this long)
      port map (
         clkP => pgpClkP,
         clkN => pgpClkN);

   pllClkInP <= (others => clk160MHzP);
   pllClkInN <= (others => clk160MHzN);

   U_Fpga : entity work.AtlasAltirocCore
      generic map (
         TPD_G        => TPD_G,
         SIMULATION_G => true,
         BUILD_INFO_G => BUILD_INFO_C)
      port map (
         -- ASIC Ports
         renable      => open,          -- RENABLE
         srinSc       => shiftSc,       -- SRIN_SC
         rstbSc       => open,          -- RSTB_SC
         ckSc         => open,          -- CK_SC
         srinProbe    => shiftProbe,    -- SRIN_PROBE
         rstbProbe    => open,          -- RSTB_PROBE
         rstbRam      => open,          -- RSTB_RAM
         rstbRead     => open,          -- RSTB_READ
         rstbTdc      => open,          -- RSTB_TDC
         rstbCounter  => open,          -- RSTB_COUNTER
         ckProbeAsic  => open,          -- CK_PROBE_ASIC
         ckWriteAsic  => open,          -- CK_WRITE_ASIC
         extTrig      => open,          -- EXT_TRIG
         sroutSc      => shiftSc,       -- SROUT_SC
         digProbe     => "00",          -- DIGITAL_PROBE[2:1]
         sroutProbe   => shiftProbe,    -- SROUT_PROBE
         totBusyb     => '1',           -- TOT_BUSYB
         toaBusyb     => '1',           -- TOA_BUSYB
         doutP        => '0',           -- DOUT_P
         doutN        => '1',           -- DOUT_N
         cmdPulseP    => open,          -- CMD_PULSE_P
         cmdPulseN    => open,          -- CMD_PULSE_N
         -- CMD Pulse Delay Ports
         dlyLen       => open,
         dlyData      => open,
         dlyTempScl   => open,
         dlyTempSda   => open,
         -- Jitter Cleaner PLL Ports
         localRefClkP => clk160MHzP,
         localRefClkN => clk160MHzN,
         pllClkOutP   => open,
         pllClkOutN   => open,
         pllClkInP    => pllClkInP,
         pllClkInN    => pllClkInN,
         pllSpiCsL    => open,
         pllSpiSclk   => open,
         pllSpiSdi    => open,
         pllSpiSdo    => '1',
         pllSpiRstL   => open,
         pllSpiOeL    => open,
         pllClkSel    => open,
         pllIntrL     => '1',
         pllLolL      => '1',
         -- DAC Ports
         dacCsL       => open,
         dacSclk      => open,
         dacSdi       => open,
         -- TTL IN/OUT Ports
         trigL        => '1',
         busy         => open,
         spareInL     => '1',
         spareOut     => open,
         -- Serial Communication Ports
         gtClkP       => pgpClkP,
         gtClkN       => pgpClkN,
         gtRxP        => '0',
         gtRxN        => '1',
         gtTxP        => open,
         gtTxN        => open,
         -- Boot Memory Ports
         bootCsL      => open,
         bootMosi     => open,
         bootMiso     => '1',
         -- Misc Ports
         oscOe        => open,
         led          => open,
         pwrSyncSclk  => open,
         pwrSyncFclk  => open,
         pwrScl       => open,
         pwrSda       => open,
         tempAlertL   => '1',
         vPIn         => 'Z',
         vNIn         => 'Z');

end testbed;
