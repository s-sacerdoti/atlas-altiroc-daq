-------------------------------------------------------------------------------
-- File       : AtlasAltirocAsicPulseTrain.vhd
-- Company    : SLAC National Accelerator Laboratory
-------------------------------------------------------------------------------
-- Description: ALTIROC readout core module
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

entity AtlasAltirocAsicPulseTrain is
   generic (
      TPD_G : time := 1 ns);
   port (
      -- Clock and Reset
      clk40MHz    : in  sl;
      rst40MHz    : in  sl;
      -- Configuration Interface
      continuous  : in  sl;
      oneShot     : in  sl;
      pulseCount  : in  slv(15 downto 0);
      pulseWidth  : in  slv(15 downto 0);
      pulsePeriod : in  slv(15 downto 0);
      -- ASIC Ports
      emuTrig     : out sl;
      cmdPulseP   : out sl;             -- CMD_PULSE_P
      cmdPulseN   : out sl;             -- CMD_PULSE_N
      extTrig     : out sl);            -- EXT_TRIG      
end AtlasAltirocAsicPulseTrain;

architecture rtl of AtlasAltirocAsicPulseTrain is

   type StateType is (
      IDLE_S,
      RUN_S);

   type RegType is record
      pulse      : sl;
      continuous : sl;
      start      : sl;
      stop       : sl;
      cnt        : slv(15 downto 0);
      pulseCnt   : slv(15 downto 0);
      state      : StateType;
   end record;

   constant REG_INIT_C : RegType := (
      pulse      => '0',
      continuous => '0',
      start      => '0',
      stop       => '0',
      cnt        => (others => '0'),
      pulseCnt   => (others => '0'),
      state      => IDLE_S);

   signal r   : RegType := REG_INIT_C;
   signal rin : RegType;

   -- attribute dont_touch      : string;
   -- attribute dont_touch of r : signal is "TRUE";

begin

   comb : process (continuous, oneShot, pulseCount, pulsePeriod, pulseWidth, r,
                   rst40MHz) is
      variable v      : RegType;
      variable axilEp : AxiLiteEndPointType;
   begin
      -- Latch the current value
      v := r;

      -- Reset strobes
      v.pulse := '0';
      v.start := '0';
      v.stop  := '0';

      -- Keep a delay copy
      v.continuous := continuous;

      -- Check for start conditions
      if (r.continuous = '0') and (continuous = '1') then
         v.start := '1';
      end if;

      -- Check for stop conditions
      if (r.continuous = '1') and (continuous = '0') then
         v.stop := '1';
      end if;

      -- State Machine
      case r.state is
         ----------------------------------------------------------------------
         when IDLE_S =>
            -- Reset the counter
            v.cnt      := (others => '0');
            v.pulseCnt := (others => '0');
            -- Check for a non-zero pulse period
            if (pulsePeriod /= 0) then
               -- Check for start and a one-shot trigger with a non-zero pulse count
               if (r.start = '1') or ((oneShot = '1') and (pulseCount /= 0)) then
                  -- Next state
                  v.state := RUN_S;
               end if;
            end if;
         ----------------------------------------------------------------------
         when RUN_S =>
            -- Increment the counter
            v.cnt := r.cnt + 1;
            -- Check the pulse width
            if (r.cnt < pulseWidth) then
               v.pulse := '1';
            end if;
            -- Check for last count value
            if (r.cnt >= (pulsePeriod-1)) then
               -- Reset the counter
               v.cnt := (others => '0');
               -- Check if not continuous mode
               if (r.continuous = '0') then
                  -- Increment the counter
                  v.pulseCnt := r.pulseCnt + 1;
                  -- Check for last one-shot pulse
                  if (r.pulseCnt >= (pulseCount-1)) then
                     -- Reset the counter
                     v.pulseCnt := (others => '0');
                     -- Next state
                     v.state    := IDLE_S;
                  end if;
               end if;
            end if;
            -- Check for stop
            if r.stop = '1' then
               -- Next state
               v.state := IDLE_S;
            end if;
      ----------------------------------------------------------------------
      end case;

      -- Outputs
      emuTrig <= r.pulse;

      -- Reset
      if (rst40MHz = '1') then
         v := REG_INIT_C;
      end if;

      -- Register the variable for next clock cycle
      rin <= v;

   end process comb;

   seq : process (clk40MHz) is
   begin
      if (rising_edge(clk40MHz)) then
         r <= rin after TPD_G;
      end if;
   end process seq;

   -------------------------------------------------
   -- TDC START generated from EXT_TRIG or CMD_PULSE
   -- TDC STOP  generated from clock's rising_edge
   -------------------------------------------------
   U_extTrig : entity work.OutputBufferReg
      generic map (
         TPD_G => TPD_G)
      port map (
         C => clk40MHz,
         I => r.pulse,
         O => extTrig);

   U_cmdPulse : entity work.OutputBufferReg
      generic map (
         TPD_G       => TPD_G,
         DIFF_PAIR_G => true)
      port map (
         C  => clk40MHz,
         I  => r.pulse,
         O  => cmdPulseP,
         OB => cmdPulseN);

end rtl;
