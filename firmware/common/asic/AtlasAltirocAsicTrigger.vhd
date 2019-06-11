-------------------------------------------------------------------------------
-- File       : AtlasAltirocAsicTrigger.vhd
-- Company    : SLAC National Accelerator Laboratory
-------------------------------------------------------------------------------
-- Description: ASIC Deserializer 
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

entity AtlasAltirocAsicTrigger is
   generic (
      TPD_G : time := 1 ns);
   port (
      -- Trigger Ports
      totBusy         : in  sl;         -- TOT_BUSY
      toaBusyb        : in  sl;         -- TOA_BUSYB
      trigL           : in  sl;
      busy            : out sl;
      spareInL        : in  sl;
      spareOut        : out sl;
      -- Calibration and 40 Strobe phase alignment Interface
      calPulse        : in  sl;
      strobeAlign     : out slv(1 downto 0);
      -- Readout Interface
      readoutStart    : out sl;
      readoutBusy     : in  sl;
      -- Reference Clock/Reset Interface
      clk160MHz       : in  sl;
      rst160MHz       : in  sl;
      strobe40MHz     : in  sl;
      -- AXI-Lite Interface 
      axilReadMaster  : in  AxiLiteReadMasterType;
      axilReadSlave   : out AxiLiteReadSlaveType;
      axilWriteMaster : in  AxiLiteWriteMasterType;
      axilWriteSlave  : out AxiLiteWriteSlaveType);
end AtlasAltirocAsicTrigger;

architecture rtl of AtlasAltirocAsicTrigger is

   constant TIMER_1_SEC_C : natural := getTimeRatio(160.0E+6, 1.0);

   type StateType is (
      IDLE_S,
      READOUT_S,
      OSCOPE_DEADTIME_S);

   type RegType is record
      cntRst              : sl;
      trigMaster          : sl;
      trigMode            : sl;
      readoutStart        : sl;
      dropTrigCnt         : Slv32Array(3 downto 0);
      strobeAlign         : slv(1 downto 0);
      enTrigMask          : slv(3 downto 0);
      trigCnt             : slv(15 downto 0);
      trigSizeBeforePause : slv(15 downto 0);
      deadtimeCnt         : slv(7 downto 0);
      deadtimeDuration    : slv(7 downto 0);
      timeout             : sl;
      timer               : natural range 0 to (TIMER_1_SEC_C-1);
      axilReadSlave       : AxiLiteReadSlaveType;
      axilWriteSlave      : AxiLiteWriteSlaveType;
      stateEncode         : slv(7 downto 0);
      state               : StateType;
   end record RegType;
   constant REG_INIT_C : RegType := (
      cntRst              => '0',
      trigMaster          => '0',
      trigMode            => '0',
      readoutStart        => '0',
      dropTrigCnt         => (others => (others => '0')),
      strobeAlign         => (others => '0'),
      enTrigMask          => (others => '0'),
      trigCnt             => (others => '0'),
      trigSizeBeforePause => (others => '0'),
      deadtimeCnt         => (others => '0'),
      deadtimeDuration    => (others => '0'),
      timeout             => '0',
      timer               => 0,
      axilReadSlave       => AXI_LITE_READ_SLAVE_INIT_C,
      axilWriteSlave      => AXI_LITE_WRITE_SLAVE_INIT_C,
      stateEncode         => (others => '0'),
      state               => IDLE_S);

   signal r   : RegType := REG_INIT_C;
   signal rin : RegType;

   signal spareIn               : sl;
   signal remoteTrig            : sl;
   signal remoteTrigRisingEdge  : sl;
   signal remoteTrigFallingEdge : sl;

   signal toaBusy              : sl;
   signal localTrig            : sl;
   signal localTrigRisingEdge  : sl;
   signal localTrigFallingEdge : sl;

   signal bncTrig            : sl;
   signal extTrig            : sl;
   signal extTrigRisingEdge  : sl;
   signal extTrigFallingEdge : sl;

   signal softTrig : sl;

begin

   U_busy : entity work.OutputBufferReg
      generic map (
         TPD_G => TPD_G)
      port map (
         C => clk160MHz,
         I => readoutBusy,
         O => busy);                    -- BNC TTL output connector

   spareOut <= readoutBusy when(r.trigMaster = '1') else not(toaBusyb);  -- LEMO TTL output connector

   spareIn <= not(spareInL);            -- LEMO TTL input connector
   U_remoteTrig : entity work.SynchronizerEdge
      generic map (
         TPD_G          => TPD_G,
         RST_POLARITY_G => '0')
      port map (
         clk         => clk160MHz,
         rst         => r.enTrigMask(3),
         dataIn      => spareIn,
         dataOut     => remoteTrig,
         risingEdge  => remoteTrigRisingEdge,
         fallingEdge => remoteTrigFallingEdge);

   toaBusy <= not(toaBusyb);            -- PCIe input connector
   U_localTrig : entity work.SynchronizerEdge
      generic map (
         TPD_G          => TPD_G,
         RST_POLARITY_G => '0')
      port map (
         clk         => clk160MHz,
         rst         => r.enTrigMask(2),
         dataIn      => toaBusy,
         dataOut     => localTrig,
         risingEdge  => localTrigRisingEdge,
         fallingEdge => localTrigFallingEdge);

   bncTrig <= not(trigL);               -- BNC TTL input connector
   U_extTrig : entity work.SynchronizerEdge
      generic map (
         TPD_G          => TPD_G,
         RST_POLARITY_G => '0')
      port map (
         clk         => clk160MHz,
         rst         => r.enTrigMask(1),
         dataIn      => bncTrig,
         dataOut     => extTrig,
         risingEdge  => extTrigRisingEdge,
         fallingEdge => extTrigFallingEdge);

   softTrig <= r.enTrigMask(0) and calPulse;

   comb : process (axilReadMaster, axilWriteMaster, extTrig, localTrig, r,
                   readoutBusy, remoteTrig, remoteTrigRisingEdge, rst160MHz,
                   softTrig) is
      variable v       : RegType;
      variable axilEp  : AxiLiteEndPointType;
      variable trigger : sl;
   begin
      -- Latch the current value
      v := r;

      -- Reset strobes
      trigger        := '0';
      v.cntRst       := '0';
      v.readoutStart := '0';
      v.timeout      := '0';

      -- 1HZ timer
      if r.timer = (TIMER_1_SEC_C-1) then
         v.timer   := 0;
         v.timeout := '1'; -- 1Hz strobe
      else
         v.timer := r.timer + 1;
      end if;

      -- Check for counter reset
      if r.cntRst = '1' then
         v.dropTrigCnt := (others => (others => '0'));
      end if;

      ----------------------------------------------------------------------   
      --                AXI-Lite Register Transactions
      ----------------------------------------------------------------------   

      -- Determine the transaction type
      axiSlaveWaitTxn(axilEp, axilWriteMaster, axilReadMaster, v.axilWriteSlave, v.axilReadSlave);

      axiSlaveRegisterR(axilEp, x"00", 0, r.dropTrigCnt(0));
      axiSlaveRegisterR(axilEp, x"04", 0, r.dropTrigCnt(1));
      axiSlaveRegisterR(axilEp, x"08", 0, r.dropTrigCnt(2));
      axiSlaveRegisterR(axilEp, x"0C", 0, r.dropTrigCnt(3));

      axiSlaveRegister (axilEp, x"40", 0, v.trigMaster);
      axiSlaveRegister (axilEp, x"44", 0, v.strobeAlign);
      axiSlaveRegister (axilEp, x"48", 0, v.enTrigMask);
      axiSlaveRegister (axilEp, x"4C", 0, v.trigMode);

      axiSlaveRegister (axilEp, x"50", 0, v.trigSizeBeforePause);
      axiSlaveRegister (axilEp, x"54", 0, v.deadtimeDuration);
      axiSlaveRegisterR(axilEp, x"58", 0, r.stateEncode);

      axiSlaveRegister (axilEp, x"FC", 0, v.cntRst);

      -- Closeout the transaction
      axiSlaveDefault(axilEp, v.axilWriteSlave, v.axilReadSlave, AXI_RESP_DECERR_C);

      ----------------------------------------------------------------------      
      --                      Trigger logic
      ----------------------------------------------------------------------      
      -- Check if master trigger unit
      if (r.trigMaster = '1') then

         -- Check for AND trigger mode
         if (r.trigMode = '0') then
            if (localTrig = '1') and (remoteTrigRisingEdge = '1') then
               trigger := '1';
            end if;

         -- Else in OR trigger mode
         else
            if (localTrig = '1') or (remoteTrigRisingEdge = '1') then
               trigger := '1';
            end if;

         end if;

      -- Else slave trigger unit
      else

         -- Check for trigger decision from trigger master
         if (remoteTrigRisingEdge = '1') then
            trigger := '1';
         end if;

      end if;

      -- Check for soft or ext triggers (independent of trigMaster mode)
      if (softTrig = '1') or (extTrig = '1') then
         trigger := '1';
      end if;

      -- Check for dropping trigger w.r.t. trigger type
      if (r.state /= IDLE_S) then

         -- Check for cal pulse trig
         if (softTrig = '1') then
            v.dropTrigCnt(0) := r.dropTrigCnt(0) + 1;
         end if;

         -- Check for BNC trig
         if (extTrig = '1') then
            v.dropTrigCnt(1) := r.dropTrigCnt(1) + 1;
         end if;

         -- Check for PCIe trig
         if (localTrig = '1') then
            v.dropTrigCnt(2) := r.dropTrigCnt(2) + 1;
         end if;

         -- Check for LEMO trig
         if (remoteTrig = '1') then
            v.dropTrigCnt(3) := r.dropTrigCnt(3) + 1;
         end if;

      end if;

      ----------------------------------------------------------------------      
      --                         State Machine      
      ----------------------------------------------------------------------      
      case (r.state) is
         ----------------------------------------------------------------------      
         when IDLE_S =>
            v.stateEncode := x"00";
            -- Check for trigger
            if (trigger = '1') then
               -- Start the readout
               v.readoutStart := '1';
               -- Increment the counter
               v.trigCnt      := r.trigCnt + 1;
               -- Next state
               v.state        := READOUT_S;
            end if;
         ----------------------------------------------------------------------      
         when READOUT_S =>
            v.stateEncode := x"01";
            -- Wait for the readout to finish
            if (r.readoutStart = '0') and (readoutBusy = '0') then

               -- Check for no oscilloscope dead time
               if (r.trigSizeBeforePause = 0) then
                  -- Next state
                  v.state := IDLE_S;
               else

                  -- Check for number of trigger before pause
                  if (r.trigCnt = r.trigSizeBeforePause) then

                     -- Reset the counters
                     v.trigCnt     := (others => '0');
                     v.deadtimeCnt := (others => '0');
                     v.timer       := 0;

                     -- Check if deadtimeDuration is non-zero
                     if (r.deadtimeDuration /= 0) then
                        -- Next state
                        v.state := OSCOPE_DEADTIME_S;
                     else
                        -- Next state
                        v.state := IDLE_S;
                     end if;

                  else
                     -- Next state
                     v.state := IDLE_S;
                  end if;

               end if;

            end if;
         ----------------------------------------------------------------------      
         when OSCOPE_DEADTIME_S =>
            v.stateEncode := x"02";
            if (r.timeout = '1') then

               -- Increment the counter
               v.deadtimeCnt := r.deadtimeCnt + 1;

               -- Check if deadtimeDuration is non-zero
               if (v.deadtimeCnt /= r.deadtimeDuration) then
                  -- Next state
                  v.state := IDLE_S;
               end if;

            end if;
      ----------------------------------------------------------------------      
      end case;

      -- Check for trigger count reset conditions
      if (r.trigSizeBeforePause = 0) or (r.trigSizeBeforePause /= v.trigSizeBeforePause) then
         v.trigCnt := (others => '0');
      end if;

      -- Check for change in deadtimeDuration
      if (r.state = OSCOPE_DEADTIME_S) and (r.deadtimeDuration /= v.deadtimeDuration) then
         -- Next state
         v.state := IDLE_S;
      end if;

      -- Outputs
      axilWriteSlave <= r.axilWriteSlave;
      axilReadSlave  <= r.axilReadSlave;
      readoutStart   <= r.readoutStart;
      strobeAlign    <= r.strobeAlign;

      -- Reset
      if (rst160MHz = '1') then
         v                     := REG_INIT_C;
         -- Don't touch register configurations
         v.trigMaster          := r.trigMaster;
         v.strobeAlign         := r.strobeAlign;
         v.enTrigMask          := r.enTrigMask;
         v.trigMode            := r.trigMode;
         v.trigSizeBeforePause := r.trigSizeBeforePause;
         v.deadtimeDuration    := r.deadtimeDuration;
      end if;

      -- Register the variable for next clock cycle
      rin <= v;

   end process comb;

   seq : process (clk160MHz) is
   begin
      if rising_edge(clk160MHz) then
         r <= rin after TPD_G;
      end if;
   end process seq;

end rtl;
