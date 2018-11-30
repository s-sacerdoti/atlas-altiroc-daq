-------------------------------------------------------------------------------
-- File       : AtlasAltirocAsicPulseTrain.vhd
-- Company    : SLAC National Accelerator Laboratory
-------------------------------------------------------------------------------
-- Description: ALTIROC Pulse Train module
--              TDC START generated from EXT_TRIG or CMD_PULSE
--              TDC STOP  generated from clock's rising_edge
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
      clk40MHz      : in  sl;
      rst40MHz      : in  sl;
      clk160MHz     : in  sl;
      rst160MHz     : in  sl;
      -- Configuration Interface
      continuous    : in  sl;
      oneShot       : in  sl;
      pulseDelay    : in  slv(15 downto 0);
      readDelay     : in  slv(15 downto 0);
      readDuration  : in  slv(15 downto 0);
      pulseCount    : in  slv(15 downto 0);
      pulseWidth    : in  slv(15 downto 0);
      pulsePeriod   : in  slv(15 downto 0);
      rstCntMask    : in  slv(1 downto 0);
      emuTrig       : out sl;
      readoutEnable : out sl;
      -- ASIC Ports
      rstbCounter   : out sl;           -- RSTB_COUNTER
      renable       : out sl;           -- RENABLE      
      cmdPulseP     : out sl;           -- CMD_PULSE_P
      cmdPulseN     : out sl;           -- CMD_PULSE_N
      extTrig       : out sl);          -- EXT_TRIG      
end AtlasAltirocAsicPulseTrain;

architecture rtl of AtlasAltirocAsicPulseTrain is

   type StateType is (
      IDLE_S,
      START_DLY_S,
      RUN_S,
      READ_DLY_S,
      READ_S);

   type RegType is record
      pulseDelay   : slv(15 downto 0);
      readDelay    : slv(15 downto 0);
      readDuration : slv(15 downto 0);
      pulseCount   : slv(15 downto 0);
      pulsePeriod  : slv(15 downto 0);
      rstbCounter  : sl;
      renable      : sl;
      pulse        : sl;
      cnt          : slv(15 downto 0);
      pulseCnt     : slv(15 downto 0);
      state        : StateType;
   end record;

   constant REG_INIT_C : RegType := (
      pulseDelay   => (others => '0'),
      readDelay    => (others => '0'),
      readDuration => (others => '0'),
      pulseCount   => (others => '0'),
      pulsePeriod  => (others => '0'),
      rstbCounter  => '1',
      renable      => '0',
      pulse        => '0',
      cnt          => (others => '0'),
      pulseCnt     => (others => '0'),
      state        => IDLE_S);

   signal r   : RegType := REG_INIT_C;
   signal rin : RegType;

   signal pulse : sl;

   -- attribute dont_touch      : string;
   -- attribute dont_touch of r : signal is "TRUE";

begin

   comb : process (continuous, oneShot, pulseCount, pulseDelay, pulsePeriod, r,
                   readDelay, readDuration, rst40MHz, rstCntMask) is
      variable v      : RegType;
      variable axilEp : AxiLiteEndPointType;
   begin
      -- Latch the current value
      v := r;

      -- Reset strobes
      v.pulse := '0';

      -- State Machine
      case r.state is
         ----------------------------------------------------------------------
         when IDLE_S =>
            -- Reset flags
            v.rstbCounter := '1';
            v.renable     := '0';

            -- Reset the counter
            v.cnt      := (others => '0');
            v.pulseCnt := (others => '0');

            -- Update local cache
            v.pulseDelay   := pulseDelay;
            v.readDelay    := readDelay;
            v.readDuration := readDuration;
            v.pulseCount   := pulseCount;
            v.pulsePeriod  := pulsePeriod;

            -- Check for a non-zero pulse period
            if (pulsePeriod /= 0) then

               -- Check for start and a one-shot trigger with a non-zero pulse count
               if (continuous = '1') or ((oneShot = '1') and (pulseCount /= 0)) then

                  -- Set the flag (active LOW)
                  v.rstbCounter := not(rstCntMask(0));

                  -- Check for zero pulse delay
                  if (pulseDelay = 0) then
                     -- Next state
                     v.state := RUN_S;
                  else
                     -- Next state
                     v.state := START_DLY_S;
                  end if;

               end if;

            end if;
         ----------------------------------------------------------------------
         when START_DLY_S =>
            -- Reset the flag (active LOW)
            v.rstbCounter := '1';

            -- Increment the counter
            v.cnt := r.cnt + 1;

            if (r.cnt = (r.pulseDelay-1)) then
               -- Reset the counter
               v.cnt   := (others => '0');
               -- Next state
               v.state := RUN_S;
            end if;
         ----------------------------------------------------------------------
         when RUN_S =>
            -- Reset the flag (active LOW)
            v.rstbCounter := '1';

            -- Increment the counter
            v.cnt := r.cnt + 1;

            -- Check if need to pulse output
            if (r.cnt = 0) then
               -- Set the flag
               v.pulse    := '1';
               -- Increment the counter
               v.pulseCnt := r.pulseCnt + 1;
            end if;

            -- Check for last count value or last one-shot pulse
            if (r.cnt = (r.pulsePeriod-1)) or (v.pulseCnt = r.pulseCount) then

               -- Reset the counters
               v.cnt := (others => '0');

               -- Check for last one-shot pulse
               if (v.pulseCnt = r.pulseCount) then

                  -- Reset the counter
                  v.pulseCnt := (others => '0');

                  -- Check for zero read delay
                  if (r.readDelay = 0) then
                     -- Set the flag (active LOW)
                     v.rstbCounter := not(rstCntMask(1));
                     -- Next state
                     v.state       := READ_S;
                  else
                     -- Next state
                     v.state := READ_DLY_S;
                  end if;

               end if;
            end if;
         ----------------------------------------------------------------------
         when READ_DLY_S =>
            -- Increment the counter
            v.cnt := r.cnt + 1;

            -- Check the end of the period
            if (r.cnt = (r.readDelay-1)) then

               -- Reset the counter
               v.cnt := (others => '0');

               -- Set the flag (active LOW)
               v.rstbCounter := not(rstCntMask(1));

               -- Next state
               v.state := READ_S;

            end if;
         ----------------------------------------------------------------------
         when READ_S =>
            -- Increment the counter
            v.cnt := r.cnt + 1;

            -- Check if need to set read enable signal
            if (r.cnt = 0) then
               -- Set the flag
               v.renable := '1';
            end if;

            -- Check if need to deassert the reset
            if (r.cnt = 1) then
               -- Set the flag (active LOW)
               v.rstbCounter := '1';
            end if;

            -- Check the end of the period
            if (r.cnt = (r.readDuration-1)) then

               -- Reset the counter
               v.cnt := (others => '0');

               -- Set the flag
               v.renable := '0';

               -- Set the flag (active LOW)
               v.rstbCounter := '1';

               -- Check if doing another iteration
               if (continuous = '1') and (pulsePeriod /= 0) and (pulseCount /= 0) then

                  -- Update local cache
                  v.pulseDelay   := pulseDelay;
                  v.readDelay    := readDelay;
                  v.readDuration := readDuration;
                  v.pulseCount   := pulseCount;
                  v.pulsePeriod  := pulsePeriod;

                  -- Set the flag (active LOW)
                  v.rstbCounter := not(rstCntMask(0));

                  -- Check for zero pulse delay
                  if (pulseDelay = 0) then
                     -- Next state
                     v.state := RUN_S;
                  else
                     -- Next state
                     v.state := START_DLY_S;
                  end if;

               else
                  -- Next state
                  v.state := IDLE_S;
               end if;

            end if;
      ----------------------------------------------------------------------      
      end case;

      -- Outputs
      emuTrig       <= r.pulse;
      readoutEnable <= r.renable;

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

   U_rstbCounter : entity work.OutputBufferReg
      generic map (
         TPD_G => TPD_G)
      port map (
         C => clk40MHz,
         I => r.rstbCounter,
         O => rstbCounter);

   U_renable : entity work.OutputBufferReg
      generic map (
         TPD_G => TPD_G)
      port map (
         C => clk40MHz,
         I => r.renable,
         O => renable);

   U_oneShot : entity work.AtlasAltirocAsicPulseOneShot
      generic map (
         TPD_G => TPD_G)
      port map (
         clk        => clk160MHz,
         rst        => rst160MHz,
         pulseWidth => pulseWidth,
         pulseIn    => r.pulse,
         pulseOut   => pulse);

   U_extTrig : entity work.OutputBufferReg
      generic map (
         TPD_G => TPD_G)
      port map (
         C => clk160MHz,
         I => pulse,
         O => extTrig);

   U_cmdPulse : entity work.OutputBufferReg
      generic map (
         TPD_G       => TPD_G,
         DIFF_PAIR_G => true)
      port map (
         C  => clk160MHz,
         I  => pulse,
         O  => cmdPulseP,
         OB => cmdPulseN);

end rtl;
