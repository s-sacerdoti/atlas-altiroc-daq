-------------------------------------------------------------------------------
-- File       : AtlasAltirocAsicCalPulse.vhd
-- Company    : SLAC National Accelerator Laboratory
-------------------------------------------------------------------------------
-- Description: ALTIROC Cal Pulse module
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

entity AtlasAltirocAsicCalPulse is
   generic (
      TPD_G : time := 1 ns);
   port (
      -- Calibration Pulse Interface
      calPulse        : out sl;
      calPulseP       : out sl;         -- CAL_PULSE_P
      calPulseN       : out sl;         -- CAL_PULSE_N   
      -- Reference Clock/Reset Interface
      clk160MHz       : in  sl;
      rst160MHz       : in  sl;
      strobe40MHz     : in  sl;
      -- AXI-Lite Interface 
      axilReadMaster  : in  AxiLiteReadMasterType;
      axilReadSlave   : out AxiLiteReadSlaveType;
      axilWriteMaster : in  AxiLiteWriteMasterType;
      axilWriteSlave  : out AxiLiteWriteSlaveType);
end AtlasAltirocAsicCalPulse;

architecture rtl of AtlasAltirocAsicCalPulse is

   type StateType is (
      IDLE_S,
      RUN_S);

   type RegType is record
      pulse          : sl;
      start          : sl;
      continuous     : sl;
      pulseDelay     : slv(15 downto 0);
      pulseCount     : slv(15 downto 0);
      delaycnt       : slv(15 downto 0);
      pulseCnt       : slv(15 downto 0);
      axilReadSlave  : AxiLiteReadSlaveType;
      axilWriteSlave : AxiLiteWriteSlaveType;
      state          : StateType;
   end record;

   constant REG_INIT_C : RegType := (
      pulse          => '1',
      start          => '0',
      continuous     => '0',
      pulseDelay     => (others => '0'),
      pulseCount     => (others => '0'),
      delaycnt       => (others => '0'),
      pulseCnt       => (others => '0'),
      axilReadSlave  => AXI_LITE_READ_SLAVE_INIT_C,
      axilWriteSlave => AXI_LITE_WRITE_SLAVE_INIT_C,
      state          => IDLE_S);

   signal r   : RegType := REG_INIT_C;
   signal rin : RegType;

   signal pulse : sl;

   -- attribute dont_touch      : string;
   -- attribute dont_touch of r : signal is "TRUE";

begin

   comb : process (axilReadMaster, axilWriteMaster, r, rst160MHz, strobe40MHz) is
      variable v      : RegType;
      variable axilEp : AxiLiteEndPointType;
   begin
      -- Latch the current value
      v := r;

      -- Reset strobes
      v.pulse := '0';
      v.start := '0';

      ----------------------------------------------------------------------      
      -- Determine the transaction type continuous
      axiSlaveWaitTxn(axilEp, axilWriteMaster, axilReadMaster, v.axilWriteSlave, v.axilReadSlave);

      axiSlaveRegister (axilEp, x"0", 0, v.pulseDelay);
      axiSlaveRegister (axilEp, x"4", 0, v.pulseCount);
      axiSlaveRegister (axilEp, x"8", 0, v.start);
      axiSlaveRegister (axilEp, x"C", 0, v.continuous);

      -- Closeout the transaction
      axiSlaveDefault(axilEp, v.axilWriteSlave, v.axilReadSlave, AXI_RESP_DECERR_C);
      ---------------------------------------------------------------------- 

      -- State Machine
      case r.state is
         ----------------------------------------------------------------------
         when IDLE_S =>
            -- Reset the counter
            v.pulseCnt := (others => '0');
            v.delaycnt := (others => '0');

            -- Check for a non-zero pulse period
            if (r.start = '1') or (r.continuous = '1') then
               -- Next state
               v.state := RUN_S;
            end if;
         ----------------------------------------------------------------------
         when RUN_S =>
            -- Check for 40 MHz clock enable strobe
            if (strobe40MHz = '1') then

               -- Check if we need to drive the pulse
               if (r.delaycnt = 0) then
                  -- Set the flag
                  v.pulse := '1';
               end if;

               -- Increment the counter
               v.delaycnt := r.delaycnt + 1;

               -- Check if need to pulse output
               if (r.delaycnt = r.pulseDelay) then

                  -- Reset the counters
                  v.delaycnt := (others => '0');

                  -- Increment the counter
                  v.pulseCnt := r.pulseCnt + 1;

                  -- Check if need to pulse output
                  if (r.pulseCnt = r.pulseCount) and (r.continuous = '0') then

                     -- Next state
                     v.state := IDLE_S;

                  end if;

               end if;

            end if;
      ----------------------------------------------------------------------      
      end case;

      -- Check for change in configuration
      if (v.pulseDelay /= r.pulseDelay) or (v.pulseCount /= r.pulseCount) then
         -- Next state
         v.state := IDLE_S;
      end if;

      -- Check for stop condition
      if (r.continuous = '1') and (v.continuous = '0') then
         -- Next state
         v.state := IDLE_S;
      end if;

      -- Outputs
      axilWriteSlave <= r.axilWriteSlave;
      axilReadSlave  <= r.axilReadSlave;
      calPulse       <= r.pulse;

      -- Reset
      if (rst160MHz = '1') then
         v            := REG_INIT_C;
         -- Don't touch register configurations
         v.pulseDelay := r.pulseDelay;
         v.pulseCount := r.pulseCount;
         v.continuous := r.continuous;
      end if;

      -- Register the variable for next clock cycle
      rin <= v;

   end process comb;

   seq : process (clk160MHz) is
   begin
      if (rising_edge(clk160MHz)) then
         r <= rin after TPD_G;
      end if;
   end process seq;

   U_cmdPulse : entity work.OutputBufferReg
      generic map (
         TPD_G       => TPD_G,
         DIFF_PAIR_G => true)
      port map (
         C  => clk160MHz,
         I  => r.pulse,
         O  => calPulseP,
         OB => calPulseN);

end rtl;
