-------------------------------------------------------------------------------
-- File       : AtlasAltirocClk.vhd
-- Company    : SLAC National Accelerator Laboratory
-- Created    : 2018-09-07
-- Last update: 2018-09-07
-------------------------------------------------------------------------------
-- Description: PLL Wrapper and 160 MHz clock MUX
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

library unisim;
use unisim.vcomponents.all;

entity AtlasAltirocClk is
   generic (
      TPD_G        : time    := 1 ns;
      SIMULATION_G : boolean := false);
   port (
      -- Jitter Cleaner PLL Ports
      localRefClkP : in  sl;
      localRefClkN : in  sl;
      pllClkOutP   : out sl;
      pllClkOutN   : out sl;
      pllClkInP    : in  slv(3 downto 0);
      pllClkInN    : in  slv(3 downto 0);
      pllSpiRstL   : out sl;
      pllSpiOeL    : out sl;
      pllClkSel    : out slv(1 downto 0);
      pllIntrL     : in  sl;
      pllLolL      : in  sl;
      -- Status/Config Interface
      axilClk      : in  sl;
      axilRst      : in  sl;
      clkSel       : in  slv(1 downto 0);
      oscOe        : out slv(3 downto 0);
      pwrSyncSclk  : out sl;
      pwrSyncFclk  : out sl;
      pllLocked    : out sl;
      -- Reference Clock/Reset Interface
      clk640MHz    : out sl;
      rst640MHz    : out sl;
      clk320MHz    : out sl;
      rst320MHz    : out sl;
      clk160MHz    : out sl;
      rst160MHz    : out sl);
end AtlasAltirocClk;

architecture mapping of AtlasAltirocClk is

   signal localRefClock : sl;
   signal localRefClk   : sl;

   signal pllClkIn : slv(3 downto 0);

   signal refClk : sl;
   signal refRst : sl;

begin

   pllClkSel <= clkSel;

   U_IBUFDS : IBUFDS_GTE2
      port map (
         I     => localRefClkP,
         IB    => localRefClkN,
         CEB   => '0',
         ODIV2 => open,
         O     => localRefClock);

   U_localRefClk : BUFG
      port map (
         I => localRefClock,
         O => localRefClk);

   U_ClkOutBufDiff : entity work.ClkOutBufDiff
      generic map (
         TPD_G => TPD_G)
      port map (
         clkIn   => localRefClk,
         clkOutP => pllClkOutP,
         clkOutN => pllClkOutN);

   GEN_VEC : for i in 3 downto 0 generate
      U_IBUFDS : IBUFDS
         port map (
            I  => pllClkInP(i),
            IB => pllClkInN(i),
            O  => pllClkIn(i));
   end generate GEN_VEC;

   U_refClk : BUFG
      port map (
         I => pllClkIn(0),
         O => refClk);

   U_PwrUpRst : entity work.PwrUpRst
      generic map(
         TPD_G         => TPD_G,
         SIM_SPEEDUP_G => SIMULATION_G)
      port map (
         arst   => pllLolL,
         clk    => refClk,
         rstOut => refRst);

   U_PLL : entity work.ClockManager7
      generic map(
         TPD_G            => TPD_G,
         SIMULATION_G     => SIMULATION_G,
         TYPE_G           => "PLL",
         BANDWIDTH_G      => "HIGH",
         INPUT_BUFG_G     => false,
         FB_BUFG_G        => true,
         NUM_CLOCKS_G     => 3,
         CLKIN_PERIOD_G   => 6.256,     -- 160 MHz
         DIVCLK_DIVIDE_G  => 1,         -- 160 MHz = 160 MHz/1
         CLKFBOUT_MULT_G  => 8,         -- 1.28 GHz = 160 MHz x 8
         CLKOUT0_DIVIDE_G => 2,         -- 640 MHz = 1.28 GHz/2
         CLKOUT1_DIVIDE_G => 4,         -- 320 MHz = 1.28 GHz/4
         CLKOUT2_DIVIDE_G => 8)         -- 160 MHz = 1.28 GHz/8
      port map(
         clkIn     => refClk,
         rstIn     => refRst,
         -- Clock Outputs
         clkOut(0) => clk640MHz,
         clkOut(1) => clk320MHz,
         clkOut(2) => clk160MHz,
         -- Reset Outputs
         rstOut(0) => rst640MHz,
         rstOut(1) => rst320MHz,
         rstOut(2) => rst160MHz,
         -- Status         
         locked    => pllLocked);

   -- Not synchronizing the DC/DC to system clock
   pwrSyncSclk <= '0';
   pwrSyncFclk <= '0';

   -- OSC Always enabled
   oscOe <= x"F";

   -- PLL OE Always enabled
   pllSpiOeL <= '0';

   -- Reset SPI interface with respect to AXI-Lite reset
   pllSpiRstL <= not(axilRst);

end mapping;
