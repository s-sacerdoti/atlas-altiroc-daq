-------------------------------------------------------------------------------
-- File       : AtlasAltirocAsicPulseOneShot.vhd
-- Company    : SLAC National Accelerator Laboratory
-------------------------------------------------------------------------------
-- Description: One-Shot Pulser that has to cross clock domains
-------------------------------------------------------------------------------
-- This file is part of 'SLAC Firmware Standard Library'.
-- It is subject to the license terms in the LICENSE.txt file found in the 
-- top-level directory of this distribution and at: 
--    https://confluence.slac.stanford.edu/display/ppareg/LICENSE.html. 
-- No part of 'SLAC Firmware Standard Library', including this file, 
-- may be copied, modified, propagated, or distributed except according to 
-- the terms contained in the LICENSE.txt file.
-------------------------------------------------------------------------------

library ieee;
use ieee.std_logic_1164.all;
use ieee.std_logic_unsigned.all;
use ieee.std_logic_arith.all;

use work.StdRtlPkg.all;

entity AtlasAltirocAsicPulseOneShot is
   generic (
      TPD_G : time := 1 ns);
   port (
      clk        : in  sl;
      rst        : in  sl;
      pulseWidth : in  slv(15 downto 0);
      pulseIn    : in  sl;
      pulseOut   : out sl);
end AtlasAltirocAsicPulseOneShot;

architecture rtl of AtlasAltirocAsicPulseOneShot is

   type StateType is (
      IDLE_S,
      CNT_S);

   type RegType is record
      cnt     : slv(15 downto 0);
      pulseIn : sl;
      pulse   : sl;
      state   : StateType;
   end record RegType;

   constant REG_INIT_C : RegType := (
      cnt     => (others => '0'),
      pulseIn => '0',
      pulse   => '0',
      state   => IDLE_S);

   signal r   : RegType := REG_INIT_C;
   signal rin : RegType;

begin


   comb : process (pulseIn, pulseWidth, r, rst) is
      variable v : RegType;
   begin
      -- Latch the current value
      v := r;

      -- Make a delayed copy
      v.pulseIn := pulseIn;

      -- State Machine
      case r.state is
         ----------------------------------------------------------------------   
         when IDLE_S =>
            -- Check for non-zero pulse width
            if (pulseWidth /= 0) then
               -- Check for rising edge of input pulse
               if (r.pulseIn = '0') and (pulseIn = '1') then
                  -- Set the output
                  v.pulse := '1';
                  -- Next state
                  v.state := CNT_S;
               end if;
            end if;
         ----------------------------------------------------------------------   
         when CNT_S =>
            -- Check the counter
            if r.cnt = (pulseWidth-1) then
               -- Reset the counter
               v.cnt   := (others => '0');
               -- Reset the output
               v.pulse := '0';
               -- Next state
               v.state := IDLE_S;
            else
               -- Increment the counter
               v.cnt := r.cnt + 1;
            end if;
      ----------------------------------------------------------------------   
      end case;

      -- Outputs 
      pulseOut <= r.pulse;

      -- Reset
      if (rst = '1') then
         v := REG_INIT_C;
      end if;

      -- Register the variable for next clock cycle
      rin <= v;

   end process;

   seq : process (clk) is
   begin
      if rising_edge(clk) then
         r <= rin after TPD_G;
      end if;
   end process seq;

end rtl;
