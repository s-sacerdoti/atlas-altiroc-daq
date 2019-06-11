-------------------------------------------------------------------------------
-- File       : AtlasAltirocCore.vhd
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

use work.StdRtlPkg.all;
use work.AxiLitePkg.all;
use work.AxiStreamPkg.all;

library unisim;
use unisim.vcomponents.all;

entity AtlasAltirocCore is
   generic (
      TPD_G        : time             := 1 ns;
      BUILD_INFO_G : BuildInfoType;
      SIMULATION_G : boolean          := false;
      SYNTH_MODE_G : string           := "inferred";
      COM_TYPE_G   : string           := "ETH";
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
      rstCounter   : out   sl;          -- RST_COUNTER
      ckProbeAsic  : out   sl;          -- CK_PROBE_ASIC
      rstbDll      : out   sl;          -- RSTB_DLL
      sroutSc      : in    sl;          -- SROUT_SC
      digProbe     : in    slv(1 downto 0);            -- DIGITAL_PROBE[2:1]
      sroutProbe   : in    sl;          -- SROUT_PROBE
      totBusy      : in    sl;          -- TOT_BUSY
      toaBusyb     : in    sl;          -- TOA_BUSYB
      doutP        : in    sl;          -- DOUT_P
      doutN        : in    sl;          -- DOUT_N
      calPulseP    : out   sl;          -- PULSE_P
      calPulseN    : out   sl;          -- PULSE_N
      rdClkP       : out   sl;          -- CK_320_P
      rdClkN       : out   sl;          -- CK_320_M     
      tdcClkSel    : out   sl;          -- MUX_CLK_SEL 
      fpgaTdcClkP  : out   sl;          -- FPGA_CK_40_P
      fpgaTdcClkN  : out   sl;          -- FPGA_CK_40_M           
      -- CAL Pulse Delay Ports
      dlyCal       : out   Slv12Array(1 downto 0);
      dlyTempScl   : inout sl;
      dlyTempSda   : inout sl;
      -- Jitter Cleaner PLL Ports
      localRefClkP : in    sl;
      localRefClkN : in    sl;
      pllClkOutP   : out   sl;
      pllClkOutN   : out   sl;
      pllClkInP    : in    slv(1 downto 0);
      pllClkInN    : in    slv(1 downto 0);
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
   signal strb40MHz : sl;
   
   signal efuse      : slv(31 downto 0);
   signal localMac   : slv(47 downto 0);   

begin

   led(0) <= txLinkUp;
   led(1) <= not(axilRst);
   led(2) <= rxLinkUp;
   led(3) <= not(rst160MHz);
   
   U_EFuse : EFUSE_USR
      port map (
         EFUSEUSR => efuse);

   localMac(23 downto 0)  <= x"56_00_08";  -- 08:00:56:XX:XX:XX (big endian SLV)   
   localMac(47 downto 24) <= efuse(31 downto 8);   

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
         pllIntrL     => pllIntrL,
         pllLolL      => pllLolL,
         -- Status/Config Interface
         axilClk      => axilClk,
         axilRst      => axilRst,
         oscOe        => oscOe,
         pwrSyncSclk  => pwrSyncSclk,
         pwrSyncFclk  => pwrSyncFclk,
         -- Reference Clock/Reset Interface
         clk160MHz    => clk160MHz,
         rst160MHz    => rst160MHz,
         strb40MHz    => strb40MHz);

   ---------------
   -- PGPv3 Module
   ---------------         
   GEN_PGP : if (COM_TYPE_G = "PGPv3") or (SIMULATION_G = true) generate
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
   GEN_ETH : if (COM_TYPE_G = "ETH") and (SIMULATION_G = false) generate
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
            localMac        => localMac,
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
         localMac        => localMac,
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
         strb40MHz       => strb40MHz,
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
         rstCounter      => rstCounter,
         ckProbeAsic     => ckProbeAsic,
         rstbDll         => rstbDll,
         sroutSc         => sroutSc,
         digProbe        => digProbe,
         sroutProbe      => sroutProbe,
         totBusy         => totBusy,
         toaBusyb        => toaBusyb,
         doutP           => doutP,
         doutN           => doutN,
         calPulseP       => calPulseP,
         calPulseN       => calPulseN,
         rdClkP          => rdClkP,
         rdClkN          => rdClkN,
         tdcClkSel       => tdcClkSel,
         fpgaTdcClkP     => fpgaTdcClkP,
         fpgaTdcClkN     => fpgaTdcClkN,
         dlyCal          => dlyCal,
         pllClkSel       => pllClkSel,
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
