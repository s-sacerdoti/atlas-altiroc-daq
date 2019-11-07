-------------------------------------------------------------------------------
-- File       : AtlasAltirocClk.vhd
-- Company    : SLAC National Accelerator Laboratory
-------------------------------------------------------------------------------
-- Description: PLL Wrapper and external 160 MHz clock MUX
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
      pllClkInP    : in  slv(1 downto 0);
      pllClkInN    : in  slv(1 downto 0);
      pllSpiRstL   : out sl;
      pllSpiOeL    : out sl;
      pllIntrL     : in  sl;
      pllLolL      : in  sl;
      -- Status/Config Interface
      axilClk      : in  sl;
      axilRst      : in  sl;
      oscOe        : out slv(3 downto 0);
      pwrSyncSclk  : out sl;
      pwrSyncFclk  : out sl;
      pllLocked    : out sl;
      -- Reference Clock/Reset Interface
      clk160MHz    : out sl;
      rst160MHz    : out sl;
      strb40MHz    : out sl);
end AtlasAltirocClk;

architecture mapping of AtlasAltirocClk is

   type RegType is record
      fastCnt     : natural range 0 to 5;
      slowCnt     : natural range 0 to 23;
      fastSyncClk : sl;
      slowSyncClk : sl;
   end record;

   constant REG_INIT_C : RegType := (
      fastCnt     => 0,
      slowCnt     => 0,
      fastSyncClk => '0',
      slowSyncClk => '0');

   signal r   : RegType := REG_INIT_C;
   signal rin : RegType;

   signal localRefClock : sl;
   signal localRefClk   : sl;
   signal pllClkIn      : slv(1 downto 0);
   signal clock160MHz   : sl;
   signal sample40MHz   : sl;
   signal strobe40MHz   : sl;
   signal reset160MHz   : sl;

begin

   -------------------------------------------   
   -- On-board 40 MHz reference for SI5345 PLL
   -------------------------------------------      
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

   ---------------------------------
   -- FPGA_CLK_IN[1:0] Input buffers
   ---------------------------------
   GEN_VEC : for i in 1 downto 0 generate
      U_IBUFDS : IBUFDS
         port map (
            I  => pllClkInP(i),
            IB => pllClkInN(i),
            O  => pllClkIn(i));
   end generate GEN_VEC;

   ----------------------------------------
   -- 160 MHz clock/reset and 40 MHz strobe
   ----------------------------------------
   U_clk160MHz : BUFG
      port map (
         I => pllClkIn(0),
         O => clock160MHz);

   U_rst160MHz : entity work.PwrUpRst
      generic map(
         TPD_G          => TPD_G,
         IN_POLARITY_G  => '0',
         OUT_POLARITY_G => '1')
      port map (
         clk    => clock160MHz,
         arst   => pllLolL,
         rstOut => reset160MHz);

   clk160MHz <= clock160MHz;
   rst160MHz <= reset160MHz;

   U_strobe40MHz : entity work.InputBufferReg
      generic map (
         TPD_G => TPD_G)
      port map (
         C  => clock160MHz,
         I  => pllClkIn(1),
         Q2 => sample40MHz);

   U_strb40MHz : entity work.SynchronizerOneShot
      generic map (
         TPD_G         => TPD_G,
         BYPASS_SYNC_G => true)
      port map (
         clk     => clock160MHz,
         dataIn  => sample40MHz,
         dataOut => strobe40MHz);

   strb40MHz <= strobe40MHz;

   ------------------------------------------
   -- Synchronizing the DC/DC to 40 MHz clock
   ------------------------------------------
   comb : process (r) is
      variable v : RegType;
   begin
      -- Latch the current value
      v := r;

      -- Check for last count
      if r.fastCnt = 5 then
         -- Reset the counter
         v.fastCnt     := 0;
         -- Toggle the flag
         v.fastSyncClk := not (r.fastSyncClk);  -- 3.33 MHz = 40MHz/(2 x 6)
      else
         -- Increment the counter
         v.fastCnt := r.fastCnt + 1;
      end if;

      -- Check for last count
      if r.slowCnt = 23 then
         -- Reset the counter
         v.slowCnt     := 0;
         -- Reset the flag
         v.slowSyncClk := not (r.slowSyncClk);  -- 833 kHz = 40MHz/(2 x 24)
      else
         -- Increment the counter
         v.slowCnt := r.slowCnt + 1;
      end if;

      -- Register the variable for next clock cycle
      rin <= v;

      -- Outputs
      pwrSyncFclk <= r.fastSyncClk;
      pwrSyncSclk <= r.slowSyncClk;

   end process comb;

   seq : process (clock160MHz, reset160MHz) is
   begin
      -- Asynchronous reset
      if (reset160MHz = '1') then
         r <= REG_INIT_C after TPD_G;
      -- Clock 
      elsif rising_edge(clock160MHz) then
         -- Clock Enable
         if (strobe40MHz = '1') then
            r <= rin after TPD_G;
         end if;
      end if;
   end process seq;

   ---------------------
   -- OSC Always enabled
   ---------------------
   oscOe <= x"F";

   ------------------------
   -- PLL OE Always enabled
   ------------------------
   pllSpiOeL <= '0';

   -----------------------------------------------------
   -- Reset SPI interface with respect to AXI-Lite reset
   -----------------------------------------------------
   U_pllSpiRstL : entity work.PwrUpRst
      generic map(
         TPD_G          => TPD_G,
         IN_POLARITY_G  => '1',
         OUT_POLARITY_G => '0',
         SIM_SPEEDUP_G  => SIMULATION_G)
      port map (
         clk    => axilClk,
         arst   => axilRst,
         rstOut => pllSpiRstL);

end mapping;
