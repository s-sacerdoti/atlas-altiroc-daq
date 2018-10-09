-------------------------------------------------------------------------------
-- File       : AtlasAltirocPgp3.vhd
-- Company    : SLAC National Accelerator Laboratory
-- Created    : 2018-09-07
-- Last update: 2018-09-07
-------------------------------------------------------------------------------
-- Description: Wrapper for PGPv3 communication
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
use work.AxiLitePkg.all;
use work.AxiStreamPkg.all;
use work.SsiPkg.all;
use work.Pgp3Pkg.all;
use work.AtlasAltirocPkg.all;

entity AtlasAltirocPgp3 is
   generic (
      TPD_G        : time    := 1 ns;
      SIMULATION_G : boolean := false;
      PGP3_RATE_G  : string  := "6.25Gbps");  -- or "10.3125Gbps"  
   port (
      -- AXI-Lite Interface (axilClk domain)
      axilClk         : out sl;
      axilRst         : out sl;
      axilReadMaster  : out AxiLiteReadMasterType;
      axilReadSlave   : in  AxiLiteReadSlaveType;
      axilWriteMaster : out AxiLiteWriteMasterType;
      axilWriteSlave  : in  AxiLiteWriteSlaveType;
      -- Streaming ASIC Data Interface (axilClk domain)
      sDataMaster     : in  AxiStreamMasterType;
      sDataSlave      : out AxiStreamSlaveType;
      -- Stable Reference IDELAY Clock and Reset
      refClk300MHz    : out sl;
      refRst300MHz    : out sl;
      -- Link Status
      rxLinkUp        : out sl;
      txLinkUp        : out sl;
      -- PGP Ports
      pgpClkP         : in  sl;
      pgpClkN         : in  sl;
      pgpRxP          : in  sl;
      pgpRxN          : in  sl;
      pgpTxP          : out sl;
      pgpTxN          : out sl);
end AtlasAltirocPgp3;

architecture mapping of AtlasAltirocPgp3 is

   signal pgpRxIn  : Pgp3RxInType  := PGP3_RX_IN_INIT_C;
   signal pgpRxOut : Pgp3RxOutType := PGP3_RX_OUT_INIT_C;

   signal pgpTxIn  : Pgp3TxInType  := PGP3_TX_IN_INIT_C;
   signal pgpTxOut : Pgp3TxOutType := PGP3_TX_OUT_INIT_C;

   signal pgpTxMasters : AxiStreamMasterArray(1 downto 0) := (others => AXI_STREAM_MASTER_INIT_C);
   signal pgpTxSlaves  : AxiStreamSlaveArray(1 downto 0)  := (others => AXI_STREAM_SLAVE_FORCE_C);
   signal pgpRxMasters : AxiStreamMasterArray(1 downto 0) := (others => AXI_STREAM_MASTER_INIT_C);
   signal pgpRxSlaves  : AxiStreamSlaveArray(1 downto 0)  := (others => AXI_STREAM_SLAVE_FORCE_C);
   signal pgpRxCtrl    : AxiStreamCtrlArray(1 downto 0)   := (others => AXI_STREAM_CTRL_UNUSED_C);

   signal pgpClk : sl;
   signal pgpRst : sl;

   signal pgpRefClkDiv2    : sl;
   signal pgpRefClkDiv2Rst : sl;

   signal sysClk : sl;
   signal sysRst : sl;

   -- attribute dont_touch             : string;
   -- attribute dont_touch of pgpRxOut : signal is "TRUE";
   -- attribute dont_touch of pgpTxOut : signal is "TRUE";

begin

   axilClk <= sysClk;
   axilRst <= sysRst;

   rxLinkUp <= pgpRxOut.linkReady;
   txLinkUp <= pgpTxOut.linkReady;

   U_PwrUpRst : entity work.PwrUpRst
      generic map(
         TPD_G         => TPD_G,
         SIM_SPEEDUP_G => SIMULATION_G)
      port map (
         clk    => pgpRefClkDiv2,
         rstOut => pgpRefClkDiv2Rst);

   U_MMCM : entity work.ClockManager7
      generic map(
         TPD_G              => TPD_G,
         SIMULATION_G       => SIMULATION_G,
         TYPE_G             => "MMCM",
         INPUT_BUFG_G       => false,
         FB_BUFG_G          => false,
         RST_IN_POLARITY_G  => '1',
         NUM_CLOCKS_G       => 2,
         -- MMCM attributes
         BANDWIDTH_G        => "OPTIMIZED",
         CLKIN_PERIOD_G     => 6.4,     -- 156.25 MHz
         DIVCLK_DIVIDE_G    => 1,       -- 156.25 MHz = 156.25 MHz/1
         CLKFBOUT_MULT_F_G  => 6.0,     -- 937.5 MHz = 156.25 MHz x 6     
         CLKOUT0_DIVIDE_F_G => 3.125,   -- 300 MHz = 937.5 MHz/3.125
         CLKOUT1_DIVIDE_G   => 6)       -- 156.25 MHz = 937.5 MHz/6       
      port map(
         clkIn     => pgpRefClkDiv2,
         rstIn     => pgpRefClkDiv2Rst,
         clkOut(0) => refClk300MHz,
         clkOut(1) => sysClk,
         rstOut(0) => refRst300MHz,
         rstOut(1) => sysRst);

   U_PGPv3 : entity work.Pgp3Gtx7Wrapper
      generic map(
         TPD_G               => TPD_G,
         ROGUE_SIM_EN_G      => SIMULATION_G,
         ROGUE_SIM_USER_ID_G => 12,
         NUM_LANES_G         => 1,
         NUM_VC_G            => 2,
         RATE_G              => PGP3_RATE_G,
         REFCLK_TYPE_G       => PGP3_REFCLK_312_C,
         EN_PGP_MON_G        => false,
         EN_GTH_DRP_G        => false,
         EN_QPLL_DRP_G       => false)
      port map (
         -- Stable Clock and Reset
         stableClk         => sysClk,
         stableRst         => sysRst,
         -- Gt Serial IO
         pgpGtTxP(0)       => pgpTxP,
         pgpGtTxN(0)       => pgpTxN,
         pgpGtRxP(0)       => pgpRxP,
         pgpGtRxN(0)       => pgpRxN,
         -- GT Clocking
         pgpRefClkP        => pgpClkP,
         pgpRefClkN        => pgpClkN,
         pgpRefClkDiv2Bufg => pgpRefClkDiv2,
         -- Clocking
         pgpClk(0)         => pgpClk,
         pgpClkRst(0)      => pgpRst,
         -- Non VC Rx Signals
         pgpRxIn(0)        => pgpRxIn,
         pgpRxOut(0)       => pgpRxOut,
         -- Non VC Tx Signals
         pgpTxIn(0)        => pgpTxIn,
         pgpTxOut(0)       => pgpTxOut,
         -- Frame Transmit Interface
         pgpTxMasters      => pgpTxMasters,
         pgpTxSlaves       => pgpTxSlaves,
         -- Frame Receive Interface
         pgpRxMasters      => pgpRxMasters,
         pgpRxCtrl         => pgpRxCtrl,
         pgpRxSlaves       => pgpRxSlaves,
         -- AXI-Lite Register Interface (axilClk domain)
         axilClk           => sysClk,
         axilRst           => sysRst,
         axilReadMaster    => AXI_LITE_READ_MASTER_INIT_C,
         axilReadSlave     => open,
         axilWriteMaster   => AXI_LITE_WRITE_MASTER_INIT_C,
         axilWriteSlave    => open);

   U_Vc0 : entity work.SrpV3AxiLite
      generic map (
         TPD_G               => TPD_G,
         SLAVE_READY_EN_G    => SIMULATION_G,
         GEN_SYNC_FIFO_G     => false,
         AXI_STREAM_CONFIG_G => PGP3_AXIS_CONFIG_C)
      port map (
         -- Streaming Slave (Rx) Interface (sAxisClk domain) 
         sAxisClk         => pgpClk,
         sAxisRst         => pgpRst,
         sAxisMaster      => pgpRxMasters(0),
         sAxisSlave       => pgpRxSlaves(0),
         sAxisCtrl        => pgpRxCtrl(0),
         -- Streaming Master (Tx) Data Interface (mAxisClk domain)
         mAxisClk         => pgpClk,
         mAxisRst         => pgpRst,
         mAxisMaster      => pgpTxMasters(0),
         mAxisSlave       => pgpTxSlaves(0),
         -- Master AXI-Lite Interface (axilClk domain)
         axilClk          => sysClk,
         axilRst          => sysRst,
         mAxilReadMaster  => axilReadMaster,
         mAxilReadSlave   => axilReadSlave,
         mAxilWriteMaster => axilWriteMaster,
         mAxilWriteSlave  => axilWriteSlave);

   U_Vc1 : entity work.AtlasAltirocPgp3AxisFifo
      generic map (
         TPD_G        => TPD_G,
         SIMULATION_G => SIMULATION_G,
         RX_G         => false,
         SLAVE_AXI_CONFIG_G  => ssiAxiStreamConfig(4),
         MASTER_AXI_CONFIG_G => ssiAxiStreamConfig(4))
      port map (
         -- System Interface (axilClk domain)
         sysClk      => sysClk,
         sysRst      => sysRst,
         sAxisMaster => sDataMaster,
         sAxisSlave  => sDataSlave,
         -- PGP Interface (pgpClk domain)
         pgpClk      => pgpClk,
         pgpRst      => pgpRst,
         pgpTxMaster => pgpTxMasters(1),
         pgpTxSlave  => pgpTxSlaves(1));

end mapping;
