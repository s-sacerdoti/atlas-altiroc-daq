-------------------------------------------------------------------------------
-- File       : AtlasAltirocAsic.vhd
-- Company    : SLAC National Accelerator Laboratory
-- Created    : 2018-09-07
-- Last update: 2018-09-07
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

   signal dout     : sl;
   signal trig     : sl;
   signal cmdPulse : sl;

   signal trigDdr     : sl;
   signal cmdPulseDdr : sl;

begin

   U_dout : IBUFDS
      port map (
         I  => doutP,
         IB => doutN,
         O  => dout);

   trig     <= '0';
   cmdPulse <= '0';

   renable     <= '0';
   srinSc      <= '0';
   rstbSc      <= '0';
   ckSc        <= '0';
   srinProbe   <= '0';
   rstbProbe   <= '0';
   rstbRam     <= '0';
   rstbRead    <= '0';
   rstbTdc     <= '0';
   rstbCounter <= '0';
   ckProbeAsic <= '0';
   ckWriteAsic <= '0';

   busy     <= '0';
   spareOut <= '0';

   axilReadSlave  <= AXI_LITE_READ_SLAVE_EMPTY_DECERR_C;
   axilWriteSlave <= AXI_LITE_WRITE_SLAVE_EMPTY_DECERR_C;

   mDataMaster <= AXI_STREAM_MASTER_INIT_C;

   ----------------------------------------------------
   -- Use the SELECTIO register for outputting EXT_TRIG
   ----------------------------------------------------

   U_trigDdr : ODDR
      port map (
         C  => clk160MHz,
         Q  => trigDdr,
         CE => '1',
         D1 => trig,
         D2 => trig,
         R  => '0',
         S  => '0');

   U_extTrig : OBUF
      port map (
         I => trigDdr,
         O => extTrig);

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
