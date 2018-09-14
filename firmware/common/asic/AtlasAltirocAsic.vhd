-------------------------------------------------------------------------------
-- File       : AtlasAltirocAsic.vhd
-- Company    : SLAC National Accelerator Laboratory
-- Created    : 2018-09-07
-- Last update: 2018-09-13
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
use work.AtlasAltirocPkg.all;

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
      -- ASIC Ports
      renable         : out sl;               -- RENABLE
      srinSc          : out sl;               -- SRIN_SC
      rstbSc          : out sl;               -- RSTB_SC
      ckSc            : out sl;               -- CK_SC
      srinProbe       : out sl;               -- SRIN_PROBE
      rstbProbe       : out sl;               -- RSTB_PROBE
      rstbRam         : out sl;               -- RSTB_RAM
      rstbRead        : out sl;               -- RSTB_READ
      rstbTdc         : out sl;               -- RSTB_TDC
      rstbCounter     : out sl;               -- RSTB_COUNTER
      ckProbeAsic     : out sl;               -- CK_PROBE_ASIC
      ckWriteAsic     : out sl;               -- CK_WRITE_ASIC
      extTrig         : out sl;               -- EXT_TRIG
      sroutSc         : in  sl;               -- SROUT_SC
      digProbe        : in  slv(1 downto 0);  -- DIGITAL_PROBE[2:1]
      sroutProbe      : in  sl;               -- SROUT_PROBE
      totBusyb        : in  sl;               -- TOT_BUSYB
      toaBusyb        : in  sl;               -- TOA_BUSYB
      doutP           : in  sl;               -- DOUT_P
      doutN           : in  sl;               -- DOUT_N
      cmdPulseP       : out sl;               -- CMD_PULSE_P
      cmdPulseN       : out sl;               -- CMD_PULSE_N
      -- TTL IN/OUT Ports
      trigL           : in  sl;
      busy            : out sl;
      spareInL        : in  sl;
      spareOut        : out sl;
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

   constant NUM_AXIL_MASTERS_C : natural := 2;

   constant SC_INDEX_C    : natural := 0;
   constant PROBE_INDEX_C : natural := 1;

   constant XBAR_CONFIG_C : AxiLiteCrossbarMasterConfigArray(NUM_AXIL_MASTERS_C-1 downto 0) := (
      SC_INDEX_C      => (
         baseAddr     => (x"0000_0000" + AXI_BASE_ADDR_G),
         addrBits     => 16,
         connectivity => x"FFFF"),
      PROBE_INDEX_C   => (
         baseAddr     => (x"0001_0000" + AXI_BASE_ADDR_G),
         addrBits     => 16,
         connectivity => x"FFFF"));

   signal axilWriteMasters : AxiLiteWriteMasterArray(NUM_AXIL_MASTERS_C-1 downto 0);
   signal axilWriteSlaves  : AxiLiteWriteSlaveArray(NUM_AXIL_MASTERS_C-1 downto 0);
   signal axilReadMasters  : AxiLiteReadMasterArray(NUM_AXIL_MASTERS_C-1 downto 0);
   signal axilReadSlaves   : AxiLiteReadSlaveArray(NUM_AXIL_MASTERS_C-1 downto 0);

   signal dout     : sl;
   signal trig     : sl;
   signal cmdPulse : sl;

   signal trigDdr     : sl;
   signal cmdPulseDdr : sl;

begin

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

   ---------------------------------------- 
   -- AXI-Lite: Slow Control Shift Register
   ---------------------------------------- 
   U_SlowControlShiftReg : entity work.AtlasAltirocAsicShiftReg
      generic map (
         TPD_G            => TPD_G,
         SHIFT_REG_SIZE_G => 965,
         SCLK_PERIOD_G    => 1.0E-6)    -- 1MHz = 1/1.0E-6    
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
         SCLK_PERIOD_G    => 1.0E-6)      -- 1MHz = 1/1.0E-6    
      port map (
         -- ASIC Ports
         srin            => srinProbe,    -- SRIN_PROBE
         rstb            => rstbProbe,    -- RSTB_PROBE
         ck              => ckProbeAsic,  -- CK_PROBE_ASIC
         srout           => sroutProbe,   -- SROUT_PROBE
         -- AXI-Lite Interface (axilClk domain)
         axilClk         => axilClk,
         axilRst         => axilRst,
         axilReadMaster  => axilReadMasters(PROBE_INDEX_C),
         axilReadSlave   => axilReadSlaves(PROBE_INDEX_C),
         axilWriteMaster => axilWriteMasters(PROBE_INDEX_C),
         axilWriteSlave  => axilWriteSlaves(PROBE_INDEX_C));

   U_dout : IBUFDS
      port map (
         I  => doutP,
         IB => doutN,
         O  => dout);

   trig        <= '0';
   cmdPulse    <= '0';
   renable     <= '0';
   rstbRam     <= '0';
   rstbRead    <= '0';
   rstbTdc     <= '0';
   rstbCounter <= '0';
   ckWriteAsic <= '0';

   busy     <= '0';
   spareOut <= '0';

   mDataMaster <= AXI_STREAM_MASTER_INIT_C;

   ----------------------------------------------------
   -- Use the SELECTIO register for outputting EXT_TRIG
   ----------------------------------------------------

   U_extTrig : entity work.AtlasAltirocOutputReg
      generic map (
         TPD_G => TPD_G)
      port map (
         clk => clk160MHz,
         I   => trig,
         O   => extTrig);

   -----------------------------------------------------
   -- Use the SELECTIO register for outputting CMD_PULSE
   -----------------------------------------------------

   U_cmdPulseDdr : ODDR
      port map (
         C  => clk160MHz,
         Q  => cmdPulseDdr,
         CE => '1',
         D1 => cmdPulse,
         D2 => cmdPulse,
         R  => '0',
         S  => '0');

   U_cmdPulse : OBUFDS
      port map (
         I  => cmdPulseDdr,
         O  => cmdPulseP,
         OB => cmdPulseN);

end mapping;