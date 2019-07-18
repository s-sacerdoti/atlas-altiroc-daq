-------------------------------------------------------------------------------
-- File       : AtlasAltirocAsic.vhd
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
use work.AxiStreamPkg.all;

library unisim;
use unisim.vcomponents.all;

entity AtlasAltirocAsic is
   generic (
      TPD_G           : time             := 1 ns;
      SIMULATION_G    : boolean          := false;
      AXI_BASE_ADDR_G : slv(31 downto 0) := (others => '0'));
   port (
      -- Reference Clock/Reset Interface
      clk160MHz       : in  sl;
      rst160MHz       : in  sl;
      strb40MHz       : in  sl;
      -- GPIO Ports
      rstbRam         : out sl;               -- RSTB_RAM
      rstCounter      : out sl;               -- RST_COUNTER
      rstbTdc         : out sl;               -- RSTB_TDC
      rstbDll         : out sl;               -- RSTB_DLL
      digProbe        : in  slv(1 downto 0);  -- DIGITAL_PROBE[2:1]
      dlyCal          : out Slv12Array(1 downto 0);
      pllClkSel       : out slv(1 downto 0);
      tdcClkSel       : out sl;               -- MUX_CLK_SEL 
      fpgaTdcClkP     : out sl;               -- FPGA_CK_40_P
      fpgaTdcClkN     : out sl;               -- FPGA_CK_40_M         
      -- Trigger Ports
      totBusy         : in  sl;               -- TOT_BUSY
      toaBusyb        : in  sl;               -- TOA_BUSYB
      trigL           : in  sl;
      busy            : out sl;
      spareInL        : in  sl;
      spareOut        : out sl;
      calPulseP       : out sl;               -- CAL_PULSE_P
      calPulseN       : out sl;               -- CAL_PULSE_N
      -- Slow Control Ports
      srinSc          : out sl;               -- SRIN_SC
      rstbSc          : out sl;               -- RSTB_SC
      ckSc            : out sl;               -- CK_SC
      sroutSc         : in  sl;               -- SROUT_SC
      -- Probe Ports
      srinProbe       : out sl;               -- SRIN_PROBE
      rstbProbe       : out sl;               -- RSTB_PROBE
      ckProbeAsic     : out sl;               -- CK_PROBE_ASIC
      sroutProbe      : in  sl;               -- SROUT_PROBE
      -- Readout Ports
      renable         : out sl;               -- RENABLE
      rstbRead        : out sl;               -- RSTB_READ
      doutP           : in  sl;               -- DOUT_P
      doutN           : in  sl;               -- DOUT_N
      rdClkP          : out sl;               -- CK_320_P
      rdClkN          : out sl;               -- CK_320_M     
      -- AXI-Lite Interface (axilClk domain)
      axilClk         : in  sl;
      axilRst         : in  sl;
      axilReadMaster  : in  AxiLiteReadMasterType;
      axilReadSlave   : out AxiLiteReadSlaveType;
      axilWriteMaster : in  AxiLiteWriteMasterType;
      axilWriteSlave  : out AxiLiteWriteSlaveType;
      -- Streaming ASIC Data Interface (axilClk domain)
      mDataMaster     : out AxiStreamMasterType;
      mDataSlave      : in  AxiStreamSlaveType);
end AtlasAltirocAsic;

architecture mapping of AtlasAltirocAsic is

   constant SIM_SCLK_PERIOD_C : real := (4*6.4E-9);

   constant NUM_AXIL_MASTERS_C : natural := 7;

   constant GPIO_INDEX_C    : natural := 0;
   constant TDC_CLK_INDEX_C : natural := 1;
   constant CAL_INDEX_C     : natural := 2;
   constant TRIG_INDEX_C    : natural := 3;
   constant SC_INDEX_C      : natural := 4;
   constant PROBE_INDEX_C   : natural := 5;
   constant READ_INDEX_C    : natural := 6;

   constant XBAR_CONFIG_C : AxiLiteCrossbarMasterConfigArray(NUM_AXIL_MASTERS_C-1 downto 0) := genAxiLiteConfig(NUM_AXIL_MASTERS_C, AXI_BASE_ADDR_G, 20, 16);

   signal axilWriteMasters : AxiLiteWriteMasterArray(NUM_AXIL_MASTERS_C-1 downto 0);
   signal axilWriteSlaves  : AxiLiteWriteSlaveArray(NUM_AXIL_MASTERS_C-1 downto 0);
   signal axilReadMasters  : AxiLiteReadMasterArray(NUM_AXIL_MASTERS_C-1 downto 0);
   signal axilReadSlaves   : AxiLiteReadSlaveArray(NUM_AXIL_MASTERS_C-1 downto 0);

   signal tdcClkReadMaster  : AxiLiteReadMasterType;
   signal tdcClkReadSlave   : AxiLiteReadSlaveType;
   signal tdcClkWriteMaster : AxiLiteWriteMasterType;
   signal tdcClkWriteSlave  : AxiLiteWriteSlaveType;

   signal calReadMaster  : AxiLiteReadMasterType;
   signal calReadSlave   : AxiLiteReadSlaveType;
   signal calWriteMaster : AxiLiteWriteMasterType;
   signal calWriteSlave  : AxiLiteWriteSlaveType;

   signal trigReadMaster  : AxiLiteReadMasterType;
   signal trigReadSlave   : AxiLiteReadSlaveType;
   signal trigWriteMaster : AxiLiteWriteMasterType;
   signal trigWriteSlave  : AxiLiteWriteSlaveType;

   signal probeReadMaster  : AxiLiteReadMasterType;
   signal probeReadSlave   : AxiLiteReadSlaveType;
   signal probeWriteMaster : AxiLiteWriteMasterType;
   signal probeWriteSlave  : AxiLiteWriteSlaveType;

   signal readoutReadMaster  : AxiLiteReadMasterType;
   signal readoutReadSlave   : AxiLiteReadSlaveType;
   signal readoutWriteMaster : AxiLiteWriteMasterType;
   signal readoutWriteSlave  : AxiLiteWriteSlaveType;

   signal readoutStart : sl;
   signal readoutBusy  : sl;
   signal startReadout : sl;
   signal probeValid   : sl;
   signal probeIbData  : slv(739 downto 0);
   signal probeObData  : slv(739 downto 0);
   signal probeBusy    : sl;

   signal calPulse    : sl;
   signal strobe40MHz : sl;
   signal strobeAlign : slv(1 downto 0);

begin

   -----------------------------------------------
   -- Phase alignment correction for 40 MHz strobe
   -----------------------------------------------
   U_SlvDelay : entity work.SlvDelay
      generic map (
         TPD_G        => TPD_G,
         DELAY_G      => 4,
         WIDTH_G      => 1,
         REG_OUTPUT_G => true)
      port map (
         clk     => clk160MHz,
         delay   => strobeAlign,
         din(0)  => strb40MHz,
         dout(0) => strobe40MHz);

   --------------------------
   -- AXI-Lite: Crossbar Core
   --------------------------  
   U_XBAR : entity work.AxiLiteCrossbar
      generic map (
         TPD_G              => TPD_G,
         NUM_SLAVE_SLOTS_G  => 1,
         NUM_MASTER_SLOTS_G => NUM_AXIL_MASTERS_C,
         MASTERS_CONFIG_G   => XBAR_CONFIG_C)
      port map (
         axiClk              => axilClk,
         axiClkRst           => axilRst,
         sAxiWriteMasters(0) => axilWriteMaster,
         sAxiWriteSlaves(0)  => axilWriteSlave,
         sAxiReadMasters(0)  => axilReadMaster,
         sAxiReadSlaves(0)   => axilReadSlave,
         mAxiWriteMasters    => axilWriteMasters,
         mAxiWriteSlaves     => axilWriteSlaves,
         mAxiReadMasters     => axilReadMasters,
         mAxiReadSlaves      => axilReadSlaves);

   ---------------------------
   -- AXI-Lite: GPIO Registers
   ---------------------------
   U_GPIO : entity work.AtlasAltirocAsicGpio
      generic map (
         TPD_G => TPD_G)
      port map (
         -- ASIC Interface
         rstbRam         => rstbRam,
         rstCounter      => rstCounter,
         rstbTdc         => rstbTdc,
         rstbDll         => rstbDll,
         digProbe        => digProbe,
         dlyCal          => dlyCal,
         pllClkSel       => pllClkSel,
         -- AXI-Lite Interface
         axilClk         => axilClk,
         axilRst         => axilRst,
         axilReadMaster  => axilReadMasters(GPIO_INDEX_C),
         axilReadSlave   => axilReadSlaves(GPIO_INDEX_C),
         axilWriteMaster => axilWriteMasters(GPIO_INDEX_C),
         axilWriteSlave  => axilWriteSlaves(GPIO_INDEX_C));

   --------------------------------
   -- AXI-Lite: TDC Clock Registers
   --------------------------------
   U_TdcClk : entity work.AtlasAltirocAsicTdcClk
      generic map (
         TPD_G => TPD_G)
      port map (
         -- ASIC Interface
         tdcClkSel       => tdcClkSel,
         fpgaTdcClkP     => fpgaTdcClkP,
         fpgaTdcClkN     => fpgaTdcClkN,
         -- AXI-Lite Interface
         clk160MHz       => clk160MHz,
         rst160MHz       => rst160MHz,
         axilReadMaster  => tdcClkReadMaster,
         axilReadSlave   => tdcClkReadSlave,
         axilWriteMaster => tdcClkWriteMaster,
         axilWriteSlave  => tdcClkWriteSlave);

   U_TdcClkAsync : entity work.AxiLiteAsync
      generic map (
         TPD_G           => TPD_G,
         NUM_ADDR_BITS_G => 16)
      port map (
         -- Slave Interface
         sAxiClk         => axilClk,
         sAxiClkRst      => axilRst,
         sAxiReadMaster  => axilReadMasters(TDC_CLK_INDEX_C),
         sAxiReadSlave   => axilReadSlaves(TDC_CLK_INDEX_C),
         sAxiWriteMaster => axilWriteMasters(TDC_CLK_INDEX_C),
         sAxiWriteSlave  => axilWriteSlaves(TDC_CLK_INDEX_C),
         -- Master Interface
         mAxiClk         => clk160MHz,
         mAxiClkRst      => rst160MHz,
         mAxiReadMaster  => tdcClkReadMaster,
         mAxiReadSlave   => tdcClkReadSlave,
         mAxiWriteMaster => tdcClkWriteMaster,
         mAxiWriteSlave  => tdcClkWriteSlave);

   -------------------------------------         
   -- AXI-Lite: Calibration Pulse Module
   -------------------------------------         
   U_CalPulse : entity work.AtlasAltirocAsicCalPulse
      generic map (
         TPD_G => TPD_G)
      port map (
         -- Calibration Pulse Interface
         calPulse        => calPulse,
         calPulseP       => calPulseP,
         calPulseN       => calPulseN,
         -- AXI-Lite Interface
         clk160MHz       => clk160MHz,
         rst160MHz       => rst160MHz,
         strobe40MHz     => strobe40MHz,
         axilReadMaster  => calReadMaster,
         axilReadSlave   => calReadSlave,
         axilWriteMaster => calWriteMaster,
         axilWriteSlave  => calWriteSlave);

   U_CalAsync : entity work.AxiLiteAsync
      generic map (
         TPD_G           => TPD_G,
         NUM_ADDR_BITS_G => 16)
      port map (
         -- Slave Interface
         sAxiClk         => axilClk,
         sAxiClkRst      => axilRst,
         sAxiReadMaster  => axilReadMasters(CAL_INDEX_C),
         sAxiReadSlave   => axilReadSlaves(CAL_INDEX_C),
         sAxiWriteMaster => axilWriteMasters(CAL_INDEX_C),
         sAxiWriteSlave  => axilWriteSlaves(CAL_INDEX_C),
         -- Master Interface
         mAxiClk         => clk160MHz,
         mAxiClkRst      => rst160MHz,
         mAxiReadMaster  => calReadMaster,
         mAxiReadSlave   => calReadSlave,
         mAxiWriteMaster => calWriteMaster,
         mAxiWriteSlave  => calWriteSlave);

   ---------------------------
   -- AXI-Lite: Trigger Module
   ---------------------------
   U_Trigger : entity work.AtlasAltirocAsicTrigger
      generic map (
         TPD_G => TPD_G)
      port map (
         totBusy         => totBusy,
         toaBusyb        => toaBusyb,
         trigL           => trigL,
         busy            => busy,
         spareInL        => spareInL,
         spareOut        => spareOut,
         -- Calibration and 40 Strobe phase alignment Interface
         calPulse        => calPulse,
         strobeAlign     => strobeAlign,
         -- Readout Interface
         readoutStart    => readoutStart,
         readoutBusy     => readoutBusy,
         -- Reference Clock/Reset Interface
         clk160MHz       => clk160MHz,
         rst160MHz       => rst160MHz,
         strobe40MHz     => strobe40MHz,
         -- AXI-Lite Interface 
         axilReadMaster  => trigReadMaster,
         axilReadSlave   => trigReadSlave,
         axilWriteMaster => trigWriteMaster,
         axilWriteSlave  => trigWriteSlave);

   U_TrigAsync : entity work.AxiLiteAsync
      generic map (
         TPD_G           => TPD_G,
         NUM_ADDR_BITS_G => 16)
      port map (
         -- Slave Interface
         sAxiClk         => axilClk,
         sAxiClkRst      => axilRst,
         sAxiReadMaster  => axilReadMasters(TRIG_INDEX_C),
         sAxiReadSlave   => axilReadSlaves(TRIG_INDEX_C),
         sAxiWriteMaster => axilWriteMasters(TRIG_INDEX_C),
         sAxiWriteSlave  => axilWriteSlaves(TRIG_INDEX_C),
         -- Master Interface
         mAxiClk         => clk160MHz,
         mAxiClkRst      => rst160MHz,
         mAxiReadMaster  => trigReadMaster,
         mAxiReadSlave   => trigReadSlave,
         mAxiWriteMaster => trigWriteMaster,
         mAxiWriteSlave  => trigWriteSlave);

   ---------------------------------------- 
   -- AXI-Lite: Slow Control Shift Register
   ---------------------------------------- 
   U_SlowControlShiftReg : entity work.AtlasAltirocAsicShiftReg
      generic map (
         TPD_G            => TPD_G,
         SHIFT_REG_SIZE_G => 965,
         CLK_PERIOD_G     => 6.4E-9,
         SCLK_PERIOD_G    => ite(SIMULATION_G, SIM_SCLK_PERIOD_C, 1.0E-6))
      port map (
         -- ASIC Ports
         srin            => srinSc,     -- SRIN_SC
         rstb            => rstbSc,     -- RSTB_SC
         ck              => ckSc,       -- CK_SC
         srout           => sroutSc,    -- SROUT_SC
         -- AXI-Lite Interface (axilClk domain)
         axilClk         => axilClk,
         axilRst         => axilRst,
         axilReadMaster  => axilReadMasters(SC_INDEX_C),
         axilReadSlave   => axilReadSlaves(SC_INDEX_C),
         axilWriteMaster => axilWriteMasters(SC_INDEX_C),
         axilWriteSlave  => axilWriteSlaves(SC_INDEX_C));

   ---------------------------------
   -- AXI-Lite: Probe Shift Register
   ---------------------------------
   U_ProbeShiftReg : entity work.AtlasAltirocAsicShiftReg
      generic map (
         TPD_G            => TPD_G,
         SHIFT_REG_SIZE_G => 740,
         CLK_PERIOD_G     => 6.25E-9,
         -- SCLK_PERIOD_G    => ite(SIMULATION_G, SIM_SCLK_PERIOD_C, 1.0E-6)) -- 1MHz
         SCLK_PERIOD_G    => ite(SIMULATION_G, SIM_SCLK_PERIOD_C, 1.0E-7)) -- 10MHz
      port map (
         -- ASIC Ports
         srin            => srinProbe,    -- SRIN_PROBE
         rstb            => rstbProbe,    -- RSTB_PROBE
         ck              => ckProbeAsic,  -- CK_PROBE_ASIC
         srout           => sroutProbe,   -- SROUT_PROBE
         -- External Interface
         extLock         => readoutBusy,
         extValid        => probeValid,
         extIbData       => probeIbData,
         extObData       => probeObData,
         busy            => probeBusy,
         -- AXI-Lite Interface (axilClk domain)
         axilClk         => clk160MHz,
         axilRst         => rst160MHz,
         axilReadMaster  => probeReadMaster,
         axilReadSlave   => probeReadSlave,
         axilWriteMaster => probeWriteMaster,
         axilWriteSlave  => probeWriteSlave);

   U_ProbeAsync : entity work.AxiLiteAsync
      generic map (
         TPD_G           => TPD_G,
         NUM_ADDR_BITS_G => 16)
      port map (
         -- Slave Interface
         sAxiClk         => axilClk,
         sAxiClkRst      => axilRst,
         sAxiReadMaster  => axilReadMasters(PROBE_INDEX_C),
         sAxiReadSlave   => axilReadSlaves(PROBE_INDEX_C),
         sAxiWriteMaster => axilWriteMasters(PROBE_INDEX_C),
         sAxiWriteSlave  => axilWriteSlaves(PROBE_INDEX_C),
         -- Master Interface
         mAxiClk         => clk160MHz,
         mAxiClkRst      => rst160MHz,
         mAxiReadMaster  => probeReadMaster,
         mAxiReadSlave   => probeReadSlave,
         mAxiWriteMaster => probeWriteMaster,
         mAxiWriteSlave  => probeWriteSlave);

   ---------------------------
   -- AXI-Lite: Readout Module
   ---------------------------
   U_Readout : entity work.AtlasAltirocAsicReadout
      generic map (
         TPD_G => TPD_G)
      port map (
         -- Readout Ports
         renable         => renable,
         rstbRead        => rstbRead,
         doutP           => doutP,
         doutN           => doutN,
         rdClkP          => rdClkP,
         rdClkN          => rdClkN,
         -- Trigger Interface (clk160MHz domain)
         readoutStart    => readoutStart,
         readoutBusy     => readoutBusy,
         -- Probe Interface (clk160MHz domain)
         probeValid      => probeValid,
         probeIbData     => probeIbData,
         probeObData     => probeObData,
         probeBusy       => probeBusy,
         -- Streaming ASIC Data Interface (axilClk domain)
         axilClk         => axilClk,
         axilRst         => axilRst,
         mDataMaster     => mDataMaster,
         mDataSlave      => mDataSlave,
         -- AXI-Lite Interface (clk160MHz domain)
         clk160MHz       => clk160MHz,
         rst160MHz       => rst160MHz,
         axilReadMaster  => readoutReadMaster,
         axilReadSlave   => readoutReadSlave,
         axilWriteMaster => readoutWriteMaster,
         axilWriteSlave  => readoutWriteSlave);

   U_ReadoutAsync : entity work.AxiLiteAsync
      generic map (
         TPD_G           => TPD_G,
         NUM_ADDR_BITS_G => 16)
      port map (
         -- Slave Interface
         sAxiClk         => axilClk,
         sAxiClkRst      => axilRst,
         sAxiReadMaster  => axilReadMasters(READ_INDEX_C),
         sAxiReadSlave   => axilReadSlaves(READ_INDEX_C),
         sAxiWriteMaster => axilWriteMasters(READ_INDEX_C),
         sAxiWriteSlave  => axilWriteSlaves(READ_INDEX_C),
         -- Master Interface
         mAxiClk         => clk160MHz,
         mAxiClkRst      => rst160MHz,
         mAxiReadMaster  => readoutReadMaster,
         mAxiReadSlave   => readoutReadSlave,
         mAxiWriteMaster => readoutWriteMaster,
         mAxiWriteSlave  => readoutWriteSlave);

end mapping;
