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
      READ_DLY_S,
      READOUT_S,
      OSCOPE_DEADTIME_S);

   type RegType is record
      cntRst              : sl;
      trigMaster          : sl;
      trigMode            : sl;
      readoutStartDly     : slv(15 downto 0);
      readoutStartDlyCnt  : slv(15 downto 0);
      readoutStart        : sl;
      dropTrigCnt         : Slv32Array(3 downto 0);
      trigCnt             : Slv32Array(3 downto 0);
      strobeAlign         : slv(1 downto 0);
      enTrigMask          : slv(3 downto 0);
      trigCounter         : slv(15 downto 0);
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
      readoutStartDly     => (others => '0'),
      readoutStartDlyCnt  => (others => '0'),
      readoutStart        => '0',
      dropTrigCnt         => (others => (others => '0')),
      trigCnt             => (others => (others => '0')),
      strobeAlign         => "11",
      enTrigMask          => (others => '0'),
      trigCounter         => (others => '0'),
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

   signal softTrig : sl;

   signal bncTrig           : sl;
   signal extTrig           : sl;
   signal extTrigRisingEdge : sl;

   signal localTrigIn         : sl;
   signal localTrig           : sl;
   signal localTrigRisingEdge : sl;

   signal remoteTrigIn         : sl;
   signal remoteTrig           : sl;
   signal remoteTrigRisingEdge : sl;

   signal orTrigIn         : sl;
   signal orTrig           : sl;
   signal orTrigRisingEdge : sl;

   signal andTrigIn         : sl;
   signal andTrig           : sl;
   signal andTrigRisingEdge : sl;

begin

   ------------------------------------------------------------------
   -- LEMO TTL output connector:
   --    if trigger master then send copy of master trigger
   --    if trigger slave  then send copy of ASIC's TOA_BUSY_L signal
   ------------------------------------------------------------------
   spareOut <= (orTrigIn or AndTrigIn) and not(readoutBusy) when(r.trigMaster = '1') else not(toaBusyb);

   ---------------------------
   -- BNC TTL output connector
   ---------------------------
   U_BNC_BUSY_OUTPUT : entity work.OutputBufferReg
      generic map (
         TPD_G => TPD_G)
      port map (
         C => clk160MHz,
         I => readoutBusy,
         O => busy);

   --------------------------
   -- CMD_PULSE Trigger input
   --------------------------
   softTrig <= r.enTrigMask(0) and calPulse;

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
         asyncRst => trigL,
         syncRst  => bncTrig);
   U_extTrigSync : entity work.SynchronizerEdge
      generic map (
         TPD_G          => TPD_G,
         RST_POLARITY_G => '0')
      port map (
         clk        => clk160MHz,
         rst        => r.enTrigMask(1),
         dataIn     => bncTrig,
         dataOut    => extTrig,
         risingEdge => extTrigRisingEdge);

   -----------------------
   -- PCIe input connector
   -----------------------
   U_localTrig : entity work.RstSync
      generic map (
         TPD_G           => TPD_G,
         IN_POLARITY_G   => '0',        -- Active LOW logic
         OUT_POLARITY_G  => '1',        -- Active HIGH logic
         RELEASE_DELAY_G => 3,
         OUT_REG_RST_G   => false)
      port map (
         clk      => clk160MHz,
         asyncRst => toaBusyb,
         syncRst  => localTrigIn);
   U_localTrigSync : entity work.SynchronizerEdge
      generic map (
         TPD_G          => TPD_G,
         RST_POLARITY_G => '0')
      port map (
         clk        => clk160MHz,
         rst        => r.enTrigMask(2),
         dataIn     => localTrigIn,
         dataOut    => localTrig,
         risingEdge => localTrigRisingEdge);

   ---------------------------
   -- LEMO TTL input connector
   ---------------------------
   U_remoteTrig : entity work.RstSync
      generic map (
         TPD_G           => TPD_G,
         IN_POLARITY_G   => '0',        -- Active LOW logic
         OUT_POLARITY_G  => '1',        -- Active HIGH logic
         RELEASE_DELAY_G => 3,
         OUT_REG_RST_G   => false)
      port map (
         clk      => clk160MHz,
         asyncRst => spareInL,
         syncRst  => remoteTrigIn);     -- >= 3 cycle pulse output width    
   U_remoteTrigSync : entity work.SynchronizerEdge
      generic map (
         TPD_G          => TPD_G,
         RST_POLARITY_G => '0')
      port map (
         clk        => clk160MHz,
         rst        => r.enTrigMask(3),
         dataIn     => remoteTrigIn,
         dataOut    => remoteTrig,
         risingEdge => remoteTrigRisingEdge);

   ----------------------------------------
   -- OR Logic for Remote and Local Trigger
   ----------------------------------------
   orTrigIn <= (r.enTrigMask(3) and remoteTrigIn) or (r.enTrigMask(2) and localTrigIn);
   U_orTrigSync : entity work.SynchronizerEdge
      generic map (
         TPD_G          => TPD_G,
         RST_POLARITY_G => '0')         -- r.trigMode='1' = OR mode
      port map (
         clk        => clk160MHz,
         rst        => r.trigMode,
         dataIn     => orTrigIn,
         dataOut    => orTrig,
         risingEdge => orTrigRisingEdge);

   -----------------------------------------
   -- AND Logic for Remote and Local Trigger
   -----------------------------------------
   andTrigIn <= (r.enTrigMask(3) and remoteTrigIn) and (r.enTrigMask(2) and localTrigIn);
   U_andTrigSync : entity work.SynchronizerEdge
      generic map (
         TPD_G          => TPD_G,
         RST_POLARITY_G => '1')         -- r.trigMode='0' = AND mode
      port map (
         clk        => clk160MHz,
         rst        => r.trigMode,
         dataIn     => andTrigIn,
         dataOut    => andTrig,
         risingEdge => andTrigRisingEdge);

   ------------------------
   -- Combinatorial Process
   ------------------------
   comb : process (andTrig, andTrigRisingEdge, axilReadMaster, axilWriteMaster,
                   extTrig, extTrigRisingEdge, localTrig, orTrig,
                   orTrigRisingEdge, r, readoutBusy, remoteTrig,
                   remoteTrigRisingEdge, rst160MHz, softTrig) is
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
         v.timeout := '1';              -- 1Hz strobe
      else
         v.timer := r.timer + 1;
      end if;

      -- Check for counter reset
      if r.cntRst = '1' then
         v.dropTrigCnt := (others => (others => '0'));
         v.trigCnt     := (others => (others => '0'));
         v.trigCounter := (others => '0');
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

      axiSlaveRegister (axilEp, x"40", 0, v.trigMaster);
      axiSlaveRegister (axilEp, x"44", 0, v.strobeAlign);
      axiSlaveRegister (axilEp, x"48", 0, v.enTrigMask);
      axiSlaveRegister (axilEp, x"4C", 0, v.trigMode);

      axiSlaveRegister (axilEp, x"50", 0, v.readoutStartDly);
      axiSlaveRegister (axilEp, x"50", 16, v.trigSizeBeforePause);
      axiSlaveRegister (axilEp, x"54", 0, v.deadtimeDuration);
      axiSlaveRegisterR(axilEp, x"58", 0, r.stateEncode);
      axiSlaveRegisterR(axilEp, x"5C", 0, r.trigCounter);

      axiSlaveRegisterR(axilEp, x"60", 0, extTrig);
      axiSlaveRegisterR(axilEp, x"60", 1, localTrig);
      axiSlaveRegisterR(axilEp, x"60", 2, remoteTrig);
      axiSlaveRegisterR(axilEp, x"60", 3, orTrig);
      axiSlaveRegisterR(axilEp, x"60", 4, andTrig);

      axiSlaveRegister (axilEp, x"FC", 0, v.cntRst);

      -- Closeout the transaction
      axiSlaveDefault(axilEp, v.axilWriteSlave, v.axilReadSlave, AXI_RESP_DECERR_C);

      ----------------------------------------------------------------------      
      --                      Trigger logic
      ---------------------------------------------------------------------- 

      -- Check for CMD_PULSE trigger
      if (softTrig = '1') then
         -- Check if dropping trigger
         if (r.state /= IDLE_S) then
            -- Increment the counter
            v.dropTrigCnt(0) := r.dropTrigCnt(0) + 1;
         else
            -- Set the flag
            trigger      := '1';
            -- Increment the counter
            v.trigCnt(0) := r.trigCnt(0) + 1;
         end if;
      end if;

      -- Check for BNC trigger
      if (extTrigRisingEdge = '1') then
         -- Check if dropping trigger
         if (r.state /= IDLE_S) then
            -- Increment the counter
            v.dropTrigCnt(1) := r.dropTrigCnt(1) + 1;
         else
            -- Set the flag
            trigger      := '1';
            -- Increment the counter
            v.trigCnt(1) := r.trigCnt(1) + 1;
         end if;
      end if;

      -- Check for trigger master trigger (Note: trigMode gated on the SynchronizerEdge modules)
      if (r.trigMaster = '1') and (orTrigRisingEdge = '1' or andTrigRisingEdge = '1') then
         -- Check if dropping trigger
         if (r.state /= IDLE_S) then
            -- Increment the counter
            v.dropTrigCnt(2) := r.dropTrigCnt(2) + 1;
         else
            -- Set the flag
            trigger      := '1';
            -- Increment the counter
            v.trigCnt(2) := r.trigCnt(2) + 1;
         end if;
      end if;

      -- Check for trigger slave trigger
      if (r.trigMaster = '0') and (remoteTrigRisingEdge = '1') then
         -- Check if dropping trigger
         if (r.state /= IDLE_S) then
            -- Increment the counter
            v.dropTrigCnt(3) := r.dropTrigCnt(3) + 1;
         else
            -- Set the flag
            trigger      := '1';
            -- Increment the counter
            v.trigCnt(3) := r.trigCnt(3) + 1;
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
               -- Increment the counter
               v.trigCounter := r.trigCounter + 1;
               -- Next state
               v.state       := READ_DLY_S;
            end if;
         ----------------------------------------------------------------------      
         when READ_DLY_S =>
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
            v.stateEncode := x"01";
            -- Wait for the readout to finish
            if (r.readoutStart = '0') and (readoutBusy = '0') then

               -- Check for no oscilloscope dead time
               if (r.trigSizeBeforePause = 0) then
                  -- Next state
                  v.state := IDLE_S;
               else

                  -- Check for number of trigger before pause
                  if (r.trigCounter = r.trigSizeBeforePause) then

                     -- Reset the counters
                     v.trigCounter := (others => '0');
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
         v.trigCounter := (others => '0');
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
         v.readoutStartDly     := r.readoutStartDly;
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
