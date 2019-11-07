-------------------------------------------------------------------------------
-- File       : AtlasAltirocAsicTrigger.vhd
-- Company    : SLAC National Accelerator Laboratory
-------------------------------------------------------------------------------
-- Description: ASIC Trigger 
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
      bncInL          : in  sl;
      bncOut          : out sl;
      lemoInL         : in  sl;
      lemoOut         : out sl;
      -- Calibration and 40 Strobe phase alignment Interface
      calPulse        : in  sl;
      calStrb40MHz    : out sl;
      -- Readout Interface
      readoutStart    : out sl;
      readoutCnt      : out slv(31 downto 0);
      dropCnt         : out slv(31 downto 0);
      timeStamp       : out slv(63 downto 0);
      readoutBusy     : in  sl;
      probeBusy       : in  sl;
      -- Reference Clock/Reset Interface
      clk160MHz       : in  sl;
      rst160MHz       : in  sl;
      strb40MHz       : in  sl;
      -- AXI-Lite Interface 
      axilReadMaster  : in  AxiLiteReadMasterType;
      axilReadSlave   : out AxiLiteReadSlaveType;
      axilWriteMaster : in  AxiLiteWriteMasterType;
      axilWriteSlave  : out AxiLiteWriteSlaveType);
end AtlasAltirocAsicTrigger;

architecture rtl of AtlasAltirocAsicTrigger is

   constant TIMER_1_SEC_C : slv(31 downto 0) := toSlv(160000000-1, 32);

   type StateType is (
      IDLE_S,
      READ_DLY_S,
      READOUT_S,
      OSCOPE_DEADTIME_S);

   type RegType is record
      timeCnt             : slv(63 downto 0);
      timeStamp           : slv(63 downto 0);
      cntRst              : sl;
      enableReadout       : sl;
      -- Oscilloscope Deadtime
      busyPulseWidth      : slv(7 downto 0);
      trigPauseCnt        : slv(15 downto 0);
      trigSizeBeforePause : slv(15 downto 0);
      deadtimeCnt         : slv(7 downto 0);
      deadtimeDuration    : slv(7 downto 0);
      timeout             : sl;
      timer               : slv(31 downto 0);
      -- Trigger Control
      trigMaster          : sl;
      trigMode            : sl;
      calStrobeAlign      : slv(1 downto 0);
      trigStrobeAlign     : slv(1 downto 0);
      enSoftTrig          : sl;
      enBncTrig           : sl;
      enLocalTrig         : sl;
      enRemoteTrig        : sl;
      remoteTrigDly       : sl;
      orTrigDly           : sl;
      andTrigDly          : sl;
      -- Trigger Monitoring
      readoutCnt          : slv(31 downto 0);
      triggerCnt          : slv(31 downto 0);
      dropCnt             : slv(31 downto 0);
      dropTrigCnt         : Slv32Array(3 downto 0);
      trigCnt             : Slv32Array(3 downto 0);
      -- AXI Lite
      axilReadSlave       : AxiLiteReadSlaveType;
      axilWriteSlave      : AxiLiteWriteSlaveType;
      -- FSM
      busy                : sl;
      readoutStart        : sl;
      readoutStartDly     : slv(15 downto 0);
      readoutStartDlyCnt  : slv(15 downto 0);
      stateEncode         : slv(7 downto 0);
      state               : StateType;
   end record RegType;
   constant REG_INIT_C : RegType := (
      timeCnt             => (others => '0'),
      timeStamp           => (others => '0'),
      cntRst              => '0',
      enableReadout       => '0',
      -- Oscilloscope Deadtime
      busyPulseWidth      => (others => '1'),
      trigPauseCnt        => (others => '0'),
      trigSizeBeforePause => (others => '0'),
      deadtimeCnt         => (others => '0'),
      deadtimeDuration    => (others => '0'),
      timeout             => '0',
      timer               => (others => '0'),
      -- Trigger Control
      trigMaster          => '0',
      trigMode            => '0',
      calStrobeAlign      => "11",
      trigStrobeAlign     => "11",
      enSoftTrig          => '0',
      enBncTrig           => '0',
      enLocalTrig         => '0',
      enRemoteTrig        => '0',
      remoteTrigDly       => '0',
      orTrigDly           => '0',
      andTrigDly          => '0',
      -- Trigger Monitoring
      readoutCnt          => (others => '0'),
      triggerCnt          => (others => '0'),
      dropCnt             => (others => '0'),
      dropTrigCnt         => (others => (others => '0')),
      trigCnt             => (others => (others => '0')),
      -- AXI Lite
      axilReadSlave       => AXI_LITE_READ_SLAVE_INIT_C,
      axilWriteSlave      => AXI_LITE_WRITE_SLAVE_INIT_C,
      -- FSM
      busy                => '0',
      readoutStart        => '0',
      readoutStartDly     => (others => '0'),
      readoutStartDlyCnt  => (others => '0'),
      stateEncode         => (others => '0'),
      state               => IDLE_S);

   signal r   : RegType := REG_INIT_C;
   signal rin : RegType;

   signal softTrig   : sl;
   signal bncIn      : sl;
   signal bncTrig    : sl;
   signal localTrig  : sl;
   signal remoteTrig : sl;
   signal orTrig     : sl;
   signal andTrig    : sl;
   signal trigWindow : sl;
   signal busyPulse  : sl;

   signal toaBusy    : sl;
   signal lemoIn     : sl;
   signal lemoOutInt : sl;

begin

   -----------------------------------------------
   -- Phase alignment correction for 40 MHz strobe
   -----------------------------------------------

   U_calStrb40MHz : entity work.SlvDelay
      generic map (
         TPD_G        => TPD_G,
         DELAY_G      => 4,
         WIDTH_G      => 1,
         REG_OUTPUT_G => true)
      port map (
         clk     => clk160MHz,
         delay   => r.calStrobeAlign,
         din(0)  => strb40MHz,
         dout(0) => calStrb40MHz);

   U_trigWindow : entity work.SlvDelay
      generic map (
         TPD_G        => TPD_G,
         DELAY_G      => 4,
         WIDTH_G      => 1,
         REG_OUTPUT_G => true)
      port map (
         clk     => clk160MHz,
         delay   => r.trigStrobeAlign,
         din(0)  => strb40MHz,
         dout(0) => trigWindow);

   -----------------------
   -- PCIe input connector
   -----------------------
   U_toaBusy : entity work.Synchronizer
      generic map (
         TPD_G          => TPD_G,
         OUT_POLARITY_G => '0')         -- Invert the signal
      port map (
         clk     => clk160MHz,
         dataIn  => toaBusyb,
         dataOut => toaBusy);
   localTrig <= toaBusy and r.enLocalTrig;

   ---------------------------
   -- LEMO TTL input connector
   ---------------------------
   U_lemoIn : entity work.Synchronizer
      generic map (
         TPD_G          => TPD_G,
         OUT_POLARITY_G => '0')         -- Invert the signal
      port map (
         clk     => clk160MHz,
         dataIn  => lemoInL,
         dataOut => lemoIn);
   remoteTrig <= lemoIn and r.enRemoteTrig;

   ----------------------------------------
   -- OR Logic for Remote and Local Trigger
   ----------------------------------------
   orTrig <= (localTrig or remoteTrig) and not(r.busy) and not(probeBusy) and trigWindow and r.trigMode;  -- r.trigMode='1' = OR mode

   -----------------------------------------
   -- AND Logic for Remote and Local Trigger
   -----------------------------------------   
   andTrig <= (localTrig and remoteTrig) and not(r.busy) and not(probeBusy) and trigWindow and not(r.trigMode);  -- r.trigMode='0' = AND mode   

   ------------------------------------------------------------------
   -- LEMO TTL output connector:
   --    if trigger master then send copy of master trigger
   --    if trigger slave  then send copy of ASIC's TOA_BUSY_L signal
   ------------------------------------------------------------------
   lemoOutInt <= r.busy when(r.trigMaster = '1') else toaBusy;
   U_lemoOut : entity work.OutputBufferReg
      generic map (
         TPD_G => TPD_G)
      port map (
         C => clk160MHz,
         I => lemoOutInt,
         O => lemoOut);

   ---------------------------
   -- BNC TTL output connector
   ---------------------------
   U_oneShot : entity work.AtlasAltirocBusyOneShot
      generic map (
         TPD_G             => TPD_G,
         PULSE_BIT_WIDTH_G => 8)
      port map (
         clk        => clk160MHz,
         rst        => rst160MHz,
         pulseWidth => r.busyPulseWidth,
         trigIn     => r.busy,
         pulseOut   => busyPulse);

   U_BNC_BUSY_OUTPUT : entity work.OutputBufferReg
      generic map (
         TPD_G => TPD_G)
      port map (
         C => clk160MHz,
         I => busyPulse,
         O => bncOut);

   --------------------------
   -- CMD_PULSE Trigger input
   --------------------------
   softTrig <= r.enSoftTrig and calPulse;

   --------------------------
   -- BNC TTL input connector
   --------------------------
   U_extTrig : entity work.RstSync
      generic map (
         TPD_G           => TPD_G,
         IN_POLARITY_G   => '0',        -- Active LOW logic
         OUT_POLARITY_G  => '1',        -- Active HIGH logic
         RELEASE_DELAY_G => 3,
         OUT_REG_RST_G   => false)
      port map (
         clk      => clk160MHz,
         asyncRst => bncInL,            -- Active LOW
         syncRst  => bncIn);            -- Active HIGH
   U_extTrigSync : entity work.SynchronizerEdge
      generic map (
         TPD_G          => TPD_G,
         RST_POLARITY_G => '0')         -- Active LOW
      port map (
         clk        => clk160MHz,
         rst        => r.enBncTrig,     -- Active LOW
         dataIn     => bncIn,
         risingEdge => bncTrig);

   ------------------------
   -- Combinatorial Process
   ------------------------
   comb : process (andTrig, axilReadMaster, axilWriteMaster, bncIn, bncTrig,
                   localTrig, orTrig, r, readoutBusy, remoteTrig, rst160MHz,
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
      if r.timer = 0 then
         v.timer   := TIMER_1_SEC_C;
         v.timeout := '1';              -- 1Hz strobe
      else
         v.timer := r.timer - 1;
      end if;

      -- Check for counter reset
      if r.cntRst = '1' then
         v.dropTrigCnt  := (others => (others => '0'));
         v.trigCnt      := (others => (others => '0'));
         v.trigPauseCnt := (others => '0');
         v.triggerCnt   := (others => '0');
         v.dropCnt      := (others => '0');
      end if;

      -- Update the trigger/readout busy
      if (r.state /= IDLE_S) then
         v.busy := '1';
      else
         v.busy := '0';
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

      axiSlaveRegisterR(axilEp, x"10", 0, r.trigCnt(0));
      axiSlaveRegisterR(axilEp, x"14", 0, r.trigCnt(1));
      axiSlaveRegisterR(axilEp, x"18", 0, r.trigCnt(2));
      axiSlaveRegisterR(axilEp, x"1C", 0, r.trigCnt(3));
      axiSlaveRegisterR(axilEp, x"20", 0, r.triggerCnt);
      axiSlaveRegisterR(axilEp, x"24", 0, r.dropCnt);
      axiSlaveRegisterR(axilEp, x"28", 0, r.timeCnt);  -- 0x28:0x2F

      axiSlaveRegister (axilEp, x"40", 0, v.trigMaster);

      axiSlaveRegister (axilEp, x"44", 0, v.calStrobeAlign);
      axiSlaveRegister (axilEp, x"44", 8, v.trigStrobeAlign);

      axiSlaveRegister (axilEp, x"48", 0, v.enSoftTrig);
      axiSlaveRegister (axilEp, x"48", 1, v.enBncTrig);
      axiSlaveRegister (axilEp, x"48", 2, v.enLocalTrig);
      axiSlaveRegister (axilEp, x"48", 3, v.enRemoteTrig);

      axiSlaveRegister (axilEp, x"4C", 0, v.trigMode);

      axiSlaveRegister (axilEp, x"50", 0, v.readoutStartDly);
      axiSlaveRegister (axilEp, x"50", 16, v.trigSizeBeforePause);

      axiSlaveRegister (axilEp, x"54", 0, v.deadtimeDuration);
      axiSlaveRegister (axilEp, x"54", 8, v.busyPulseWidth);

      axiSlaveRegisterR(axilEp, x"58", 0, r.stateEncode);
      axiSlaveRegisterR(axilEp, x"58", 8, r.deadtimeCnt);
      axiSlaveRegisterR(axilEp, x"5C", 0, r.trigPauseCnt);

      axiSlaveRegisterR(axilEp, x"60", 0, bncIn);
      axiSlaveRegisterR(axilEp, x"60", 1, localTrig);
      axiSlaveRegisterR(axilEp, x"60", 2, remoteTrig);
      axiSlaveRegisterR(axilEp, x"60", 3, orTrig);
      axiSlaveRegisterR(axilEp, x"60", 4, andTrig);

      axiSlaveRegister (axilEp, x"80", 0, v.enableReadout);

      axiSlaveRegister (axilEp, x"FC", 0, v.cntRst);

      -- Closeout the transaction
      axiSlaveDefault(axilEp, v.axilWriteSlave, v.axilReadSlave, AXI_RESP_DECERR_C);

      ----------------------------------------------------------------------      
      --                      Trigger logic
      ---------------------------------------------------------------------- 

      -- Check if readout enabled
      if (r.enableReadout = '1') then

         -- Check for CMD_PULSE trigger
         if (softTrig = '1') then
            -- Check if dropping trigger
            if (r.state /= IDLE_S) then
               -- Increment the counter
               v.dropTrigCnt(0) := r.dropTrigCnt(0) + 1;
               v.dropCnt        := r.dropCnt + 1;
            else
               -- Set the flag
               trigger      := '1';
               -- Increment the counter
               v.trigCnt(0) := r.trigCnt(0) + 1;
            end if;
         end if;

         -- Check for BNC rising edge trigger
         if (bncTrig = '1') then
            -- Check if dropping trigger
            if (r.state /= IDLE_S) then
               -- Increment the counter
               v.dropTrigCnt(1) := r.dropTrigCnt(1) + 1;
               v.dropCnt        := r.dropCnt + 1;
            else
               -- Set the flag
               trigger      := '1';
               -- Increment the counter
               v.trigCnt(1) := r.trigCnt(1) + 1;
            end if;
         end if;

         -- Check for trigger master trigger
         v.orTrigDly  := orTrig;
         v.andTrigDly := andTrig;
         if (r.trigMaster = '1') then
            if (orTrig = '1' and r.orTrigDly = '0') or (andTrig = '1' and r.andTrigDly = '0') then
               -- Check if dropping trigger
               if (r.state /= IDLE_S) then
                  -- Increment the counter
                  v.dropTrigCnt(2) := r.dropTrigCnt(2) + 1;
                  v.dropCnt        := r.dropCnt + 1;
               else
                  -- Set the flag
                  trigger      := '1';
                  -- Increment the counter
                  v.trigCnt(2) := r.trigCnt(2) + 1;
               end if;
            end if;
         end if;

         -- Check for trigger slave trigger
         v.remoteTrigDly := remoteTrig;
         if (r.trigMaster = '0') then
            if (remoteTrig = '1') and (r.remoteTrigDly = '0') then
               -- Check if dropping trigger
               if (r.state /= IDLE_S) then
                  -- Increment the counter
                  v.dropTrigCnt(3) := r.dropTrigCnt(3) + 1;
                  v.dropCnt        := r.dropCnt + 1;
               else
                  -- Set the flag
                  trigger      := '1';
                  -- Increment the counter
                  v.trigCnt(3) := r.trigCnt(3) + 1;
               end if;
            end if;
         end if;

         -- Check for trigger
         if (trigger = '1') then
            -- Increment the counter
            v.triggerCnt := r.triggerCnt + 1;
         end if;

      end if;

      -- Increment the counter
      v.timeCnt := r.timeCnt + 1;

      ----------------------------------------------------------------------      
      --                         State Machine      
      ----------------------------------------------------------------------      
      case (r.state) is
         ----------------------------------------------------------------------      
         when IDLE_S =>
            v.stateEncode := x"00";
            -- Reset the counters
            v.deadtimeCnt := (others => '0');
            -- Check for trigger
            if (trigger = '1') and (r.enableReadout = '1') then
               -- Increment the counter
               v.trigPauseCnt := r.trigPauseCnt + 1;
               -- Latch the values
               v.readoutCnt   := r.triggerCnt;
               v.timeStamp    := r.timeCnt;
               -- Next state
               v.state        := READ_DLY_S;
            end if;
         ----------------------------------------------------------------------      
         when READ_DLY_S =>
            v.stateEncode        := x"01";
            -- Increment the counter
            v.readoutStartDlyCnt := r.readoutStartDlyCnt + 1;
            -- Check the counter
            if (r.readoutStartDlyCnt = r.readoutStartDly) then
               -- Reset the counter
               v.readoutStartDlyCnt := (others => '0');
               -- Start the readout
               v.readoutStart       := '1';
               -- Next state
               v.state              := READOUT_S;
            end if;
         ----------------------------------------------------------------------      
         when READOUT_S =>
            v.stateEncode := x"02";
            -- Wait for the readout to finish
            if (r.readoutStart = '0') and (readoutBusy = '0') then

               -- Check for no oscilloscope dead time
               if (r.trigSizeBeforePause = 0) then
                  -- Next state
                  v.state := IDLE_S;
               else

                  -- Check for number of trigger before pause
                  if (r.trigPauseCnt = r.trigSizeBeforePause) then

                     -- Reset the counters
                     v.trigPauseCnt := (others => '0');
                     v.deadtimeCnt  := (others => '0');
                     v.timer        := TIMER_1_SEC_C;

                     -- Check if deadtimeDuration is non-zero and trigger master
                     if (r.deadtimeDuration /= 0) and (r.trigMaster = '1') then
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
            v.stateEncode := x"03";
            if (r.timeout = '1') then

               -- Increment the counter
               v.deadtimeCnt := r.deadtimeCnt + 1;

               -- Check if dead time duration reached or max timeout
               if (v.deadtimeCnt = r.deadtimeDuration) or (v.deadtimeCnt = x"FF") then

                  -- Reset the counters
                  v.deadtimeCnt := (others => '0');

                  -- Next state
                  v.state := IDLE_S;

               end if;

            end if;
      ----------------------------------------------------------------------      
      end case;

      -- Check for trigger count reset conditions
      if (r.trigSizeBeforePause = 0) or (r.trigSizeBeforePause /= v.trigSizeBeforePause) then
         v.trigPauseCnt := (others => '0');
      end if;

      -- Check for change in deadtimeDuration
      if (v.state = OSCOPE_DEADTIME_S) and (r.deadtimeDuration /= v.deadtimeDuration) then
         -- Next state
         v.state := IDLE_S;
      end if;

      -- Outputs
      axilWriteSlave <= r.axilWriteSlave;
      axilReadSlave  <= r.axilReadSlave;
      readoutStart   <= r.readoutStart;
      readoutCnt     <= r.readoutCnt;
      dropCnt        <= r.dropCnt;
      timeStamp      <= r.timeStamp;

      -- Reset
      if (rst160MHz = '1') then
         v                     := REG_INIT_C;
         -- Don't touch register configurations
         v.enableReadout       := r.enableReadout;
         v.trigMaster          := r.trigMaster;
         v.calStrobeAlign      := r.calStrobeAlign;
         v.trigStrobeAlign     := r.trigStrobeAlign;
         v.enSoftTrig          := r.enSoftTrig;
         v.enBncTrig           := r.enBncTrig;
         v.enLocalTrig         := r.enLocalTrig;
         v.enRemoteTrig        := r.enRemoteTrig;
         v.trigMode            := r.trigMode;
         v.readoutStartDly     := r.readoutStartDly;
         v.trigSizeBeforePause := r.trigSizeBeforePause;
         v.deadtimeDuration    := r.deadtimeDuration;
         v.busyPulseWidth      := r.busyPulseWidth;
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
