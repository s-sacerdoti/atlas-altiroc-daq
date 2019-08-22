-------------------------------------------------------------------------------
-- File       : AtlasAltirocFpga1GbETb.vhd
-- Company    : SLAC National Accelerator Laboratory
-------------------------------------------------------------------------------
-- Description: Simulation Testbed for testing the FPGA module
-------------------------------------------------------------------------------
-- This file is part of 'ATLAS RD53 FMC DEV'.
-- It is subject to the license terms in the LICENSE.txt file found in the 
-- top-level directory of this distribution and at: 
--    https://confluence.slac.stanford.edu/display/ppareg/LICENSE.html. 
-- No part of 'ATLAS RD53 FMC DEV', including this file, 
-- may be copied, modified, propagated, or distributed except according to 
-- the terms contained in the LICENSE.txt file.
-------------------------------------------------------------------------------

library ieee;
use ieee.std_logic_1164.all;
use ieee.std_logic_unsigned.all;
use ieee.std_logic_arith.all;

use work.StdRtlPkg.all;
use work.BuildInfoPkg.all;

entity AtlasAltirocFpga1GbETb is end AtlasAltirocFpga1GbETb;

architecture testbed of AtlasAltirocFpga1GbETb is

   constant TPD_G : time := 1 ns;


   type RegType is record
      data  : slv(20 downto 0);
      index : natural range 0 to 21;
      dout  : sl;
   end record RegType;
   constant REG_INIT_C : RegType := (
      data  => toSlv(1, 21),
      index => 0,
      dout  => '0');

   signal r   : RegType := REG_INIT_C;
   signal rin : RegType;


   signal renable     : sl              := '0';
   signal srinSc      : sl              := '0';
   signal rstbSc      : sl              := '1';
   signal ckSc        : sl              := '0';
   signal srinProbe   : sl              := '0';
   signal rstbProbe   : sl              := '1';
   signal rstbRam     : sl              := '1';
   signal rstbRead    : sl              := '1';
   signal rstbTdc     : sl              := '1';
   signal rstCounter  : sl              := '0';
   signal ckProbeAsic : sl              := '0';
   signal rstbDll     : sl              := '1';
   signal sroutSc     : sl              := '0';
   signal digProbe    : slv(1 downto 0) := "00";
   signal sroutProbe  : sl              := '0';
   signal totBusy     : sl              := '0';
   signal toaBusyb    : sl              := '1';
   signal doutP       : sl              := '0';
   signal doutN       : sl              := '1';
   signal calPulseP   : sl              := '0';
   signal calPulseN   : sl              := '1';
   signal rdClkP      : sl              := '0';
   signal rdClkN      : sl              := '1';
   signal tdcClkSel   : sl              := '0';
   signal fpgaTdcClkP : sl              := '0';
   signal fpgaTdcClkN : sl              := '1';

   signal trigL    : sl := '1';
   signal busy     : sl := '0';
   signal spareInL : sl := '1';
   signal spareOut : sl := '0';

   signal clk312P : sl := '0';
   signal clk312N : sl := '1';

   signal clk160P : sl := '0';
   signal clk160N : sl := '1';
   signal pllLolL : sl := '0';

   signal clk40P : sl := '0';
   signal clk40N : sl := '1';

begin

   comb : process (r, renable, rstbRead) is
      variable v : RegType;
   begin
      -- Latch the current value
      v := r;

      -- Check for the readout enable
      if renable = '1' then
      
         -- Update the output
         v.dout := r.data(r.index);

         -- Increment the index
         v.index := r.index + 1;

         -- Check for last bit of the serialized word
         if (r.index = 20) then

            -- Reset the index
            v.index := 0;

            -- Increment the data pattern (don't touch "01" start pattern)
            v.data := r.data + 4;

         end if;

      end if;

      -- Outputs
      doutP <= r.dout;
      doutN <= not(r.dout);

      -- Reset
      if (rstbRead = '0') then
         v := REG_INIT_C;
      end if;

      -- Register the variable for next clock cycle
      rin <= v;

   end process comb;

   seq : process (rdClkP) is
   begin
      -- "The data are available on DataOut(0:20) around 3ns after the falling edge of Rck." page20 of datasheet
      if falling_edge(rdClkP) then  
         r <= rin after 3 ns;
      end if;
   end process seq;

   U_clk312P : entity work.ClkRst
      generic map (
         CLK_PERIOD_G      => 3.2 ns,
         RST_START_DELAY_G => 0 ns,
         RST_HOLD_TIME_G   => 1000 ns)
      port map (
         clkP => clk312P,
         clkN => clk312N);

   U_clk160P : entity work.ClkRst
      generic map (
         CLK_PERIOD_G      => 6.25 ns,
         RST_START_DELAY_G => 0 ns,
         RST_HOLD_TIME_G   => 1000 ns)
      port map (
         clkP => clk160P,
         clkN => clk160N,
         rstL => pllLolL);

   U_clk40P : entity work.ClkRst
      generic map (
         CLK_PERIOD_G      => 25.0 ns,
         RST_START_DELAY_G => 0 ns,
         RST_HOLD_TIME_G   => 1000 ns)
      port map (
         clkP => clk40P,
         clkN => clk40N);

   U_Fpga : entity work.AtlasAltirocFpga1GbE
      generic map (
         TPD_G        => TPD_G,
         SIMULATION_G => true,
         BUILD_INFO_G => BUILD_INFO_C)
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
         rstCounter   => rstCounter,
         ckProbeAsic  => ckProbeAsic,
         rstbDll      => rstbDll,
         sroutSc      => sroutSc,
         digProbe     => digProbe,
         sroutProbe   => sroutProbe,
         totBusy      => totBusy,
         toaBusyb     => toaBusyb,
         doutP        => doutP,
         doutN        => doutN,
         calPulseP    => calPulseP,
         calPulseN    => calPulseN,
         rdClkP       => rdClkP,
         rdClkN       => rdClkN,
         tdcClkSel    => tdcClkSel,
         fpgaTdcClkP  => fpgaTdcClkP,
         fpgaTdcClkN  => fpgaTdcClkN,
         -- CAL Pulse Delay Ports
         dlyCal       => open,
         dlyTempScl   => open,
         dlyTempSda   => open,
         -- Jitter Cleaner PLL Ports
         localRefClkP => clk160P,
         localRefClkN => clk160N,
         pllClkOutP   => open,
         pllClkOutN   => open,
         pllClkInP(0) => clk160P,
         pllClkInP(1) => clk40P,
         pllClkInN(0) => clk160N,
         pllClkInN(1) => clk40N,
         pllSpiCsL    => open,
         pllSpiSclk   => open,
         pllSpiSdi    => open,
         pllSpiSdo    => '0',
         pllSpiRstL   => open,
         pllSpiOeL    => open,
         pllClkSel    => open,
         pllIntrL     => '1',
         pllLolL      => pllLolL,
         -- DAC Ports
         dacCsL       => open,
         dacSclk      => open,
         dacSdi       => open,
         -- TTL IN/OUT Ports
         trigL        => trigL,
         busy         => busy,
         spareInL     => spareInL,
         spareOut     => spareOut,
         -- Serial Communication Ports
         gtClkP       => clk312P,
         gtClkN       => clk312N,
         gtRxP        => '0',
         gtRxN        => '1',
         gtTxP        => open,
         gtTxN        => open,
         -- Boot Memory Ports
         bootCsL      => open,
         bootMosi     => open,
         bootMiso     => '0',
         -- Misc Ports
         led          => open,
         oscOe        => open,
         pwrSyncSclk  => open,
         pwrSyncFclk  => open,
         pwrScl       => open,
         pwrSda       => open,
         tempAlertL   => '1',
         vPIn         => '0',
         vNIn         => '1');

end testbed;
