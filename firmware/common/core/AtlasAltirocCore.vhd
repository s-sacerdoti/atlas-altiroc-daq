-------------------------------------------------------------------------------
-- File       : AtlasAltirocCore.vhd
-- Company    : SLAC National Accelerator Laboratory
-- Created    : 2018-09-07
-- Last update: 2018-10-09
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

use work.StdRtlPkg.all;
use work.AxiLitePkg.all;
use work.AxiStreamPkg.all;
use work.AtlasAltirocPkg.all;

library unisim;
use unisim.vcomponents.all;

entity AtlasAltirocCore is
   generic (
      TPD_G        : time             := 1 ns;
      BUILD_INFO_G : BuildInfoType;
      SIMULATION_G : boolean          := false;
      SYNTH_MODE_G : string           := "inferred";
      COM_TYPE_G   : string           := "PGPv3";
      ETH_10G_G    : boolean          := false;
      DHCP_G       : boolean          := true;
      IP_ADDR_G    : slv(31 downto 0) := x"0A01A8C0";  -- 192.168.1.10 (before DHCP)      
      PGP3_RATE_G  : string           := "6.25Gbps");  -- or "10.3125Gbps"      
   port (
      -- ASIC Ports
      renable      : out   sl;          -- RENABLE
      srinSc       : out   sl;          -- SRIN_SC
      rstbSc       : out   sl;          -- RSTB_SC
      ckSc         : out   sl;          -- CK_SC
      srinProbe    : out   sl;          -- SRIN_PROBE
      rstbProbe    : out   sl;          -- RSTB_PROBE
      rstbRam      : out   sl;          -- RSTB_RAM
      rstbRead     : out   sl;          -- RSTB_READ
      rstbTdc      : out   sl;          -- RSTB_TDC
      rstbCounter  : out   sl;          -- RSTB_COUNTER
      ckProbeAsic  : out   sl;          -- CK_PROBE_ASIC
      ckWriteAsic  : out   sl;          -- CK_WRITE_ASIC
      extTrig      : out   sl;          -- EXT_TRIG
      sroutSc      : in    sl;          -- SROUT_SC
      digProbe     : in    slv(1 downto 0);            -- DIGITAL_PROBE[2:1]
      sroutProbe   : in    sl;          -- SROUT_PROBE
      totBusyb     : in    sl;          -- TOT_BUSYB
      toaBusyb     : in    sl;          -- TOA_BUSYB
      doutP        : in    sl;          -- DOUT_P
      doutN        : in    sl;          -- DOUT_N
      cmdPulseP    : out   sl;          -- CMD_PULSE_P
      cmdPulseN    : out   sl;          -- CMD_PULSE_N
      -- CMD Pulse Delay Ports
      dlyLen       : out   sl;
      dlyData      : out   slv(9 downto 0);
      dlyTempScl   : inout sl;
      dlyTempSda   : inout sl;
      -- Jitter Cleaner PLL Ports
      localRefClkP : in    sl;
      localRefClkN : in    sl;
      pllClkOutP   : out   sl;
      pllClkOutN   : out   sl;
      pllClkInP    : in    slv(3 downto 0);
      pllClkInN    : in    slv(3 downto 0);
      pllSpiCsL    : out   sl;
      pllSpiSclk   : out   sl;
      pllSpiSdi    : out   sl;
      pllSpiSdo    : in    sl;
      pllSpiRstL   : out   sl;
      pllSpiOeL    : out   sl;
      pllClkSel    : out   slv(1 downto 0);
      pllIntrL     : in    sl;
      pllLolL      : in    sl;
      -- DAC Ports
      dacCsL       : out   sl;
      dacSclk      : out   sl;
      dacSdi       : out   sl;
      -- TTL IN/OUT Ports
      trigL        : in    sl;
      busy         : out   sl;
      spareInL     : in    sl;
      spareOut     : out   sl;
      -- Serial Communication Ports
      gtClkP       : in    sl;
      gtClkN       : in    sl;
      gtRxP        : in    sl;
      gtRxN        : in    sl;
      gtTxP        : out   sl;
      gtTxN        : out   sl;
      -- Boot Memory Ports
      bootCsL      : out   sl;
      bootMosi     : out   sl;
      bootMiso     : in    sl;
      -- Misc Ports
      oscOe        : out   slv(3 downto 0);
      led          : out   slv(3 downto 0);
      pwrSyncSclk  : out   sl;
      pwrSyncFclk  : out   sl;
      pwrScl       : inout sl;
      pwrSda       : inout sl;
      tempAlertL   : in    sl;
      vPIn         : in    sl;
      vNIn         : in    sl);
end AtlasAltirocCore;

architecture mapping of AtlasAltirocCore is

   constant NUM_AXIL_MASTERS_C : natural := 2;

   constant SYS_INDEX_C  : natural := 0;
   constant ASIC_INDEX_C : natural := 1;

   constant XBAR_CONFIG_C : AxiLiteCrossbarMasterConfigArray(NUM_AXIL_MASTERS_C-1 downto 0) := (
      SYS_INDEX_C     => (
         baseAddr     => x"0000_0000",
         addrBits     => 24,
         connectivity => x"FFFF"),
      ASIC_INDEX_C    => (
         baseAddr     => x"0100_0000",
         addrBits     => 24,
         connectivity => x"FFFF"));

   signal axilWriteMaster : AxiLiteWriteMasterType;
   signal axilWriteSlave  : AxiLiteWriteSlaveType;
   signal axilReadMaster  : AxiLiteReadMasterType;
   signal axilReadSlave   : AxiLiteReadSlaveType;

   signal axilWriteMasters : AxiLiteWriteMasterArray(NUM_AXIL_MASTERS_C-1 downto 0);
   signal axilWriteSlaves  : AxiLiteWriteSlaveArray(NUM_AXIL_MASTERS_C-1 downto 0);
   signal axilReadMasters  : AxiLiteReadMasterArray(NUM_AXIL_MASTERS_C-1 downto 0);
   signal axilReadSlaves   : AxiLiteReadSlaveArray(NUM_AXIL_MASTERS_C-1 downto 0);

   signal txDataMaster : AxiStreamMasterType;
   signal txDataSlave  : AxiStreamSlaveType;

   signal rxLinkUp : sl;
   signal txLinkUp : sl;

   signal axilClk : sl;
   signal axilRst : sl;

   signal clk160MHz : sl;
   signal rst160MHz : sl;

   signal deserClk : sl;
   signal deserRst : sl;

   signal status : AtlasAltirocStatusType := ALTIROC_STATUS_INIT_C;
   signal config : AtlasAltirocConfigType := ALTIROC_CONFIG_INIT_C;

begin

   led(0) <= rxLinkUp;
   led(1) <= txLinkUp;
   led(2) <= not(axilRst);
   led(3) <= not(rst160MHz);

   dlyLen  <= '0';
   dlyData <= config.dlyData;

   ----------------------
   -- Timing Clock Module
   ----------------------
   U_Clk : entity work.AtlasAltirocClk
      generic map(
         TPD_G        => TPD_G,
         SIMULATION_G => SIMULATION_G)
      port map(
         -- Jitter Cleaner PLL Ports
         localRefClkP => localRefClkP,
         localRefClkN => localRefClkN,
         pllClkOutP   => pllClkOutP,
         pllClkOutN   => pllClkOutN,
         pllClkInP    => pllClkInP,
         pllClkInN    => pllClkInN,
         pllSpiRstL   => pllSpiRstL,
         pllSpiOeL    => pllSpiOeL,
         pllClkSel    => pllClkSel,
         pllIntrL     => pllIntrL,
         pllLolL      => pllLolL,
         -- Status/Config Interface
         axilClk      => axilClk,
         axilRst      => axilRst,
         clkSel       => config.clkSel,
         oscOe        => oscOe,
         pwrSyncSclk  => pwrSyncSclk,
         pwrSyncFclk  => pwrSyncFclk,
         pllLocked    => status.pllLocked,
         -- Reference Clock/Reset Interface
         deserClk     => deserClk,
         deserRst     => deserRst,
         clk160MHz    => clk160MHz,
         rst160MHz    => rst160MHz);

   ---------------
   -- PGPv3 Module
   ---------------         
   GEN_PGP : if (COM_TYPE_G = "PGPv3") generate
      U_Pgp : entity work.AtlasAltirocPgp3
         generic map (
            TPD_G        => TPD_G,
            SIMULATION_G => SIMULATION_G,
            PGP3_RATE_G  => PGP3_RATE_G)
         port map (
            -- AXI-Lite Interfaces (axilClk domain)
            axilClk         => axilClk,
            axilRst         => axilRst,
            axilReadMaster  => axilReadMaster,
            axilReadSlave   => axilReadSlave,
            axilWriteMaster => axilWriteMaster,
            axilWriteSlave  => axilWriteSlave,
            -- Streaming ASIC Data Interface (axilClk domain)
            sDataMaster     => txDataMaster,
            sDataSlave      => txDataSlave,
            -- Link Status
            rxLinkUp        => rxLinkUp,
            txLinkUp        => txLinkUp,
            -- PGP Ports
            pgpClkP         => gtClkP,
            pgpClkN         => gtClkN,
            pgpRxP          => gtRxP,
            pgpRxN          => gtRxN,
            pgpTxP          => gtTxP,
            pgpTxN          => gtTxN);
   end generate;

   ---------------
   -- PGPv3 Module
   ---------------         
   GEN_ETH : if (COM_TYPE_G = "ETH") generate
      U_ETH : entity work.AtlasAltirocEth
         generic map (
            TPD_G        => TPD_G,
            SIMULATION_G => SIMULATION_G,
            ETH_10G_G    => ETH_10G_G,
            DHCP_G       => DHCP_G,
            IP_ADDR_G    => IP_ADDR_G)
         port map (
            -- AXI-Lite Interfaces (axilClk domain)
            axilClk         => axilClk,
            axilRst         => axilRst,
            axilReadMaster  => axilReadMaster,
            axilReadSlave   => axilReadSlave,
            axilWriteMaster => axilWriteMaster,
            axilWriteSlave  => axilWriteSlave,
            -- Streaming ASIC Data Interface (axilClk domain)
            sDataMaster     => txDataMaster,
            sDataSlave      => txDataSlave,
            -- Link Status
            rxLinkUp        => rxLinkUp,
            txLinkUp        => txLinkUp,
            -- PGP Ports
            ethClkP         => gtClkP,
            ethClkN         => gtClkN,
            ethRxP          => gtRxP,
            ethRxN          => gtRxN,
            ethTxP          => gtTxP,
            ethTxN          => gtTxN);
   end generate;

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

   -------------------       
   -- System Registers
   -------------------       
   U_System : entity work.AtlasAltirocSys
      generic map (
         TPD_G           => TPD_G,
         SIMULATION_G    => SIMULATION_G,
         AXI_BASE_ADDR_G => XBAR_CONFIG_C(SYS_INDEX_C).baseAddr,
         BUILD_INFO_G    => BUILD_INFO_G)
      port map (
         -- Configuration/Status interface
         status          => status,
         config          => config,
         -- AXI-Lite Interface (axilClk domain)
         axilClk         => axilClk,
         axilRst         => axilRst,
         axilReadMaster  => axilReadMasters(SYS_INDEX_C),
         axilReadSlave   => axilReadSlaves(SYS_INDEX_C),
         axilWriteMaster => axilWriteMasters(SYS_INDEX_C),
         axilWriteSlave  => axilWriteSlaves(SYS_INDEX_C),
         -- CMD Pulse Delay Ports
         dlyTempScl      => dlyTempScl,
         dlyTempSda      => dlyTempSda,
         -- Jitter Cleaner PLL Ports
         pllSpiCsL       => pllSpiCsL,
         pllSpiSclk      => pllSpiSclk,
         pllSpiSdi       => pllSpiSdi,
         pllSpiSdo       => pllSpiSdo,
         -- DAC Ports
         dacCsL          => dacCsL,
         dacSclk         => dacSclk,
         dacSdi          => dacSdi,
         -- Boot Memory Ports
         bootCsL         => bootCsL,
         bootMosi        => bootMosi,
         bootMiso        => bootMiso,
         -- Misc Ports
         pwrScl          => pwrScl,
         pwrSda          => pwrSda,
         tempAlertL      => tempAlertL,
         vPIn            => vPIn,
         vNIn            => vNIn);

   ----------------------------------
   -- ASIC Control and Readout Module
   ----------------------------------
   U_Asic : entity work.AtlasAltirocAsic
      generic map (
         TPD_G           => TPD_G,
         SIMULATION_G    => SIMULATION_G,
         AXI_BASE_ADDR_G => XBAR_CONFIG_C(ASIC_INDEX_C).baseAddr)
      port map (
         -- Reference Clock/Reset Interface
         clk160MHz       => clk160MHz,
         rst160MHz       => rst160MHz,
         deserClk        => deserClk,
         deserRst        => deserRst,
         -- ASIC Ports
         renable         => renable,
         srinSc          => srinSc,
         rstbSc          => rstbSc,
         ckSc            => ckSc,
         srinProbe       => srinProbe,
         rstbProbe       => rstbProbe,
         rstbRam         => rstbRam,
         rstbRead        => rstbRead,
         rstbTdc         => rstbTdc,
         rstbCounter     => rstbCounter,
         ckProbeAsic     => ckProbeAsic,
         ckWriteAsic     => ckWriteAsic,
         extTrig         => extTrig,
         sroutSc         => sroutSc,
         digProbe        => digProbe,
         sroutProbe      => sroutProbe,
         totBusyb        => totBusyb,
         toaBusyb        => toaBusyb,
         doutP           => doutP,
         doutN           => doutN,
         cmdPulseP       => cmdPulseP,
         cmdPulseN       => cmdPulseN,
         -- TTL IN/OUT Ports
         trigL           => trigL,
         busy            => busy,
         spareInL        => spareInL,
         spareOut        => spareOut,
         -- AXI-Lite Interface (axilClk domain)
         axilClk         => axilClk,
         axilRst         => axilRst,
         axilReadMaster  => axilReadMasters(ASIC_INDEX_C),
         axilReadSlave   => axilReadSlaves(ASIC_INDEX_C),
         axilWriteMaster => axilWriteMasters(ASIC_INDEX_C),
         axilWriteSlave  => axilWriteSlaves(ASIC_INDEX_C),
         -- Streaming ASIC Data Interface (axilClk domain)
         mDataMaster     => txDataMaster,
         mDataSlave      => txDataSlave);

end mapping;
