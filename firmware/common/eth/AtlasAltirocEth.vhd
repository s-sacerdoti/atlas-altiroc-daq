-------------------------------------------------------------------------------
-- File       : AtlasAltirocEth.vhd
-- Company    : SLAC National Accelerator Laboratory
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
use work.EthMacPkg.all;

library unisim;
use unisim.vcomponents.all;

entity AtlasAltirocEth is
   generic (
      TPD_G        : time             := 1 ns;
      SIMULATION_G : boolean          := false;
      SYNTH_MODE_G : string           := "inferred";
      ETH_10G_G    : boolean          := false;
      DHCP_G       : boolean          := true;
      IP_ADDR_G    : slv(31 downto 0) := x"0A01A8C0");  -- 192.168.1.10 (before DHCP)
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
      -- ETH Ports
      localMac        : in  slv(47 downto 0);
      ethClkP         : in  sl;
      ethClkN         : in  sl;
      ethRxP          : in  sl;
      ethRxN          : in  sl;
      ethTxP          : out sl;
      ethTxN          : out sl);
end AtlasAltirocEth;

architecture mapping of AtlasAltirocEth is

   constant CLK_FREQUENCY_C : real := ite(ETH_10G_G, 156.25E+6, 125.0E+6);

   constant SERVER_SIZE_C  : positive                                := 1;
   constant SERVER_PORTS_C : PositiveArray(SERVER_SIZE_C-1 downto 0) := (0 => 8192);

   signal ibMacMaster : AxiStreamMasterType;
   signal ibMacSlave  : AxiStreamSlaveType;
   signal obMacMaster : AxiStreamMasterType;
   signal obMacSlave  : AxiStreamSlaveType;

   signal obServerMasters : AxiStreamMasterArray(SERVER_SIZE_C-1 downto 0);
   signal obServerSlaves  : AxiStreamSlaveArray(SERVER_SIZE_C-1 downto 0);
   signal ibServerMasters : AxiStreamMasterArray(SERVER_SIZE_C-1 downto 0);
   signal ibServerSlaves  : AxiStreamSlaveArray(SERVER_SIZE_C-1 downto 0);

   constant APP_STREAMS_C     : positive                                       := 2;
   constant APP_AXIS_CONFIG_C : AxiStreamConfigArray(APP_STREAMS_C-1 downto 0) := (others => PGP3_AXIS_CONFIG_C);

   signal ethTxMasters : AxiStreamMasterArray(APP_STREAMS_C-1 downto 0) := (others => AXI_STREAM_MASTER_INIT_C);
   signal ethTxSlaves  : AxiStreamSlaveArray(APP_STREAMS_C-1 downto 0)  := (others => AXI_STREAM_SLAVE_FORCE_C);
   signal ethRxMasters : AxiStreamMasterArray(APP_STREAMS_C-1 downto 0) := (others => AXI_STREAM_MASTER_INIT_C);
   signal ethRxSlaves  : AxiStreamSlaveArray(APP_STREAMS_C-1 downto 0)  := (others => AXI_STREAM_SLAVE_FORCE_C);

   signal ethClk   : sl;
   signal ethRst   : sl;
   signal phyReady : sl;

   signal sysClk        : sl;
   signal sysRst        : sl;
   signal rssiConnected : sl;

begin

   axilClk <= sysClk;
   axilRst <= sysRst;

   txLinkUp <= phyReady;
   rxLinkUp <= rssiConnected;

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
         CLKIN_PERIOD_G     => ite(ETH_10G_G, 6.4, 8.0),
         DIVCLK_DIVIDE_G    => 1,
         CLKFBOUT_MULT_F_G  => ite(ETH_10G_G, 6.0, 7.5),
         CLKOUT0_DIVIDE_F_G => 3.125,   -- 300 MHz = 937.5 MHz/3.125
         CLKOUT1_DIVIDE_G   => 6)       -- 156.25 MHz = 937.5 MHz/6       
      port map(
         clkIn     => ethClk,
         rstIn     => ethRst,
         clkOut(0) => refClk300MHz,
         clkOut(1) => sysClk,
         rstOut(0) => refRst300MHz,
         rstOut(1) => sysRst);

   GEN_1G : if (ETH_10G_G = false) generate
      U_Eth : entity work.GigEthGtx7Wrapper
         generic map (
            TPD_G              => TPD_G,
            -- DMA/MAC Configurations
            NUM_LANE_G         => 1,
            -- QUAD PLL Configurations
            USE_GTREFCLK_G     => false,
            CLKIN_PERIOD_G     => 3.2,   -- 312.5 MHz
            DIVCLK_DIVIDE_G    => 10,    -- 31.25 MHz = (312.5 MHz/10)
            CLKFBOUT_MULT_F_G  => 32.0,  -- 1 GHz = (32 x 31.25 MHz)
            CLKOUT0_DIVIDE_F_G => 8.0,   -- 125 MHz = (1.0 GHz/8)         
            -- AXI Streaming Configurations
            AXIS_CONFIG_G      => (others => EMAC_AXIS_CONFIG_C))
         port map (
            -- Local Configurations
            localMac(0)     => localMac,
            -- Streaming DMA Interface 
            dmaClk(0)       => ethClk,
            dmaRst(0)       => ethRst,
            dmaIbMasters(0) => obMacMaster,
            dmaIbSlaves(0)  => obMacSlave,
            dmaObMasters(0) => ibMacMaster,
            dmaObSlaves(0)  => ibMacSlave,
            -- Misc. Signals
            extRst          => '0',
            phyClk          => ethClk,
            phyRst          => ethRst,
            phyReady(0)     => phyReady,
            -- MGT Clock Port
            gtClkP          => ethClkP,
            gtClkN          => ethClkN,
            -- MGT Ports
            gtTxP(0)        => ethTxP,
            gtTxN(0)        => ethTxN,
            gtRxP(0)        => ethRxP,
            gtRxN(0)        => ethRxN);
   end generate;

   GEN_10G : if (ETH_10G_G = true) generate
      U_Eth : entity work.TenGigEthGtx7Wrapper
         generic map (
            TPD_G         => TPD_G,
            REFCLK_DIV2_G => true,      -- TRUE: gtClkP/N = 312.5 MHz
            AXIS_CONFIG_G => (others => EMAC_AXIS_CONFIG_C))
         port map (
            -- Local Configurations
            localMac(0)     => localMac,
            -- Streaming DMA Interface 
            dmaClk(0)       => ethClk,
            dmaRst(0)       => ethRst,
            dmaIbMasters(0) => obMacMaster,
            dmaIbSlaves(0)  => obMacSlave,
            dmaObMasters(0) => ibMacMaster,
            dmaObSlaves(0)  => ibMacSlave,
            -- Misc. Signals
            extRst          => '0',
            phyClk          => ethClk,
            phyRst          => ethRst,
            phyReady(0)     => phyReady,
            -- MGT Clock Port (156.25 MHz)
            gtClkP          => ethClkP,
            gtClkN          => ethClkN,
            -- MGT Ports
            gtTxP(0)        => ethTxP,
            gtTxN(0)        => ethTxN,
            gtRxP(0)        => ethRxP,
            gtRxN(0)        => ethRxN);
   end generate;

   ----------------------
   -- IPv4/ARP/UDP Engine
   ----------------------
   U_UDP : entity work.UdpEngineWrapper
      generic map (
         -- Simulation Generics
         TPD_G          => TPD_G,
         -- UDP Server Generics
         SERVER_EN_G    => true,
         SERVER_SIZE_G  => SERVER_SIZE_C,
         SERVER_PORTS_G => SERVER_PORTS_C,
         -- UDP Client Generics
         CLIENT_EN_G    => false,
         -- General IPv4/ARP/DHCP Generics
         DHCP_G         => DHCP_G,
         CLK_FREQ_G     => CLK_FREQUENCY_C,
         COMM_TIMEOUT_G => 10)
      port map (
         -- Local Configurations
         localMac        => localMac,
         localIp         => IP_ADDR_G,
         -- Interface to Ethernet Media Access Controller (MAC)
         obMacMaster     => obMacMaster,
         obMacSlave      => obMacSlave,
         ibMacMaster     => ibMacMaster,
         ibMacSlave      => ibMacSlave,
         -- Interface to UDP Server engine(s)
         obServerMasters => obServerMasters,
         obServerSlaves  => obServerSlaves,
         ibServerMasters => ibServerMasters,
         ibServerSlaves  => ibServerSlaves,
         -- Clock and Reset
         clk             => ethClk,
         rst             => ethRst);

   ------------------------------------------
   -- Software's RSSI Server Interface @ 8192
   ------------------------------------------
   U_RssiServer : entity work.RssiCoreWrapper
      generic map (
         TPD_G               => TPD_G,
         SERVER_G            => true,
         APP_ILEAVE_EN_G     => true,    -- Interleaved RSSI (PackVer = 2)
         MAX_SEG_SIZE_G      => 1024,
         WINDOW_ADDR_SIZE_G  => 4,
         PIPE_STAGES_G       => 1,
         TIMEOUT_UNIT_G      => 1.0E-3,  -- In units of seconds
         CLK_FREQUENCY_G     => CLK_FREQUENCY_C,
         APP_STREAMS_G       => APP_STREAMS_C,
         APP_STREAM_ROUTES_G => (
            0                => X"00",   -- SRPv3
            1                => X"01"),  -- Data[0]          
         APP_AXIS_CONFIG_G   => APP_AXIS_CONFIG_C,
         TSP_AXIS_CONFIG_G   => EMAC_AXIS_CONFIG_C)
      port map (
         clk_i             => ethClk,
         rst_i             => ethRst,
         openRq_i          => '1',
         rssiConnected_o   => rssiConnected,
         -- Application Layer Interface
         sAppAxisMasters_i => ethTxMasters,
         sAppAxisSlaves_o  => ethTxSlaves,
         mAppAxisMasters_o => ethRxMasters,
         mAppAxisSlaves_i  => ethRxSlaves,
         -- Transport Layer Interface
         sTspAxisMaster_i  => obServerMasters(0),
         sTspAxisSlave_o   => obServerSlaves(0),
         mTspAxisMaster_o  => ibServerMasters(0),
         mTspAxisSlave_i   => ibServerSlaves(0));

   U_Vc0 : entity work.SrpV3AxiLite
      generic map (
         TPD_G               => TPD_G,
         SLAVE_READY_EN_G    => true,
         GEN_SYNC_FIFO_G     => false,
         AXI_STREAM_CONFIG_G => PGP3_AXIS_CONFIG_C)
      port map (
         -- Streaming Slave (Rx) Interface (sAxisClk domain) 
         sAxisClk         => ethClk,
         sAxisRst         => ethRst,
         sAxisMaster      => ethRxMasters(0),
         sAxisSlave       => ethRxSlaves(0),
         -- Streaming Master (Tx) Data Interface (mAxisClk domain)
         mAxisClk         => ethClk,
         mAxisRst         => ethRst,
         mAxisMaster      => ethTxMasters(0),
         mAxisSlave       => ethTxSlaves(0),
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
         SYNTH_MODE_G => SYNTH_MODE_G,
         SIMULATION_G => true,          -- Using AXIS Slave
         RX_G         => false)
      port map (
         -- System Interface (axilClk domain)
         sysClk      => sysClk,
         sysRst      => sysRst,
         sAxisMaster => sDataMaster,
         sAxisSlave  => sDataSlave,
         -- PGP Interface (pgpClk domain)
         pgpClk      => ethClk,
         pgpRst      => ethRst,
         pgpTxMaster => ethTxMasters(1),
         pgpTxSlave  => ethTxSlaves(1));

end mapping;
