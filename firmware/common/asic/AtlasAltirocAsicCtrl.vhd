-------------------------------------------------------------------------------
-- File       : AtlasAltirocAsicCtrl.vhd
-- Company    : SLAC National Accelerator Laboratory
-- Created    : 2018-09-14
-- Last update: 2018-11-01
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

entity AtlasAltirocAsicCtrl is
   generic (
      TPD_G : time := 1 ns);
   port (
      -- ASIC Interface  (clk160MHz domain)
      clk160MHz       : in  sl;
      rst160MHz       : in  sl;
      renable         : out sl;         -- RENABLE
      rstbRam         : out sl;         -- RSTB_RAM
      rstbRead        : out sl;         -- RSTB_READ
      rstbTdc         : out sl;         -- RSTB_TDC
      rstbCounter     : out sl;         -- RSTB_COUNTER
      ckWriteAsic     : out sl;         -- CK_WRITE_ASIC
      deserSampleEdge : out sl;
      continuous      : out sl;
      oneShot         : out sl;
      pulseCount      : out slv(15 downto 0);
      pulseWidth      : out slv(15 downto 0);
      pulsePeriod     : out slv(15 downto 0);
      emuEnable       : out sl;
      dataEnable      : out sl;
      -- AXI-Lite Interface (axilClk domain)
      axilClk         : in  sl;
      axilRst         : in  sl;
      axilReadMaster  : in  AxiLiteReadMasterType;
      axilReadSlave   : out AxiLiteReadSlaveType;
      axilWriteMaster : in  AxiLiteWriteMasterType;
      axilWriteSlave  : out AxiLiteWriteSlaveType);
end AtlasAltirocAsicCtrl;

architecture mapping of AtlasAltirocAsicCtrl is

   constant CK_WR_CONFIG_SIZE_C : positive := 3;

   type RegType is record
      continuous      : sl;
      oneShot         : sl;
      pulseCount      : slv(15 downto 0);
      pulseWidth      : slv(15 downto 0);
      pulsePeriod     : slv(15 downto 0);
      deserSampleEdge : sl;
      renable         : sl;
      rstbRam         : sl;
      rstbRead        : sl;
      rstbTdc         : sl;
      rstbCounter     : sl;
      ckWrConfig      : slv(CK_WR_CONFIG_SIZE_C-1 downto 0);
      emuEnable       : sl;
      dataEnable      : sl;
      axilReadSlave   : AxiLiteReadSlaveType;
      axilWriteSlave  : AxiLiteWriteSlaveType;
   end record;

   constant REG_INIT_C : RegType := (
      continuous      => '0',
      oneShot         => '0',
      pulseCount      => toSlv(1, 16),
      pulseWidth      => toSlv(1, 16),
      pulsePeriod     => toSlv(2, 16),
      deserSampleEdge => '0',
      renable         => '0',
      rstbRam         => '1',
      rstbRead        => '1',
      rstbTdc         => '1',
      rstbCounter     => '1',
      ckWrConfig      => (others => '0'),
      emuEnable       => '0',
      dataEnable      => '0',
      axilReadSlave   => AXI_LITE_READ_SLAVE_INIT_C,
      axilWriteSlave  => AXI_LITE_WRITE_SLAVE_INIT_C);

   signal r   : RegType := REG_INIT_C;
   signal rin : RegType;

   signal ckWr       : sl                                       := '0';
   signal ckWrConfig : slv(CK_WR_CONFIG_SIZE_C-1 downto 0)      := (others => '0');
   signal ckWrCnt    : slv((2**CK_WR_CONFIG_SIZE_C)-1 downto 0) := (others => '0');

   -- attribute dont_touch         : string;
   -- attribute dont_touch of ckWr : signal is "TRUE";   

begin

   comb : process (axilReadMaster, axilRst, axilWriteMaster, r) is
      variable v      : RegType;
      variable axilEp : AxiLiteEndPointType;
   begin
      -- Latch the current value
      v := r;

      -- Reset strobes
      v.oneShot := '0';

      -- Determine the transaction type
      axiSlaveWaitTxn(axilEp, axilWriteMaster, axilReadMaster, v.axilWriteSlave, v.axilReadSlave);

      axiSlaveRegister(axilEp, x"800", 0, v.renable);
      axiSlaveRegister(axilEp, x"804", 0, v.rstbRam);
      axiSlaveRegister(axilEp, x"808", 0, v.rstbRead);
      axiSlaveRegister(axilEp, x"80C", 0, v.rstbTdc);
      axiSlaveRegister(axilEp, x"810", 0, v.rstbCounter);
      axiSlaveRegister(axilEp, x"814", 0, v.ckWrConfig);

      axiSlaveRegister(axilEp, x"900", 0, v.deserSampleEdge);
      axiSlaveRegister(axilEp, x"904", 0, v.emuEnable);
      axiSlaveRegister(axilEp, x"908", 0, v.dataEnable);

      axiSlaveRegister(axilEp, x"A00", 0, v.pulseCount);
      axiSlaveRegister(axilEp, x"A04", 0, v.pulseWidth);
      axiSlaveRegister(axilEp, x"A08", 0, v.pulsePeriod);
      axiSlaveRegister(axilEp, x"A0C", 0, v.continuous);
      axiSlaveRegister(axilEp, x"A10", 0, v.oneShot);

      -- Closeout the transaction
      axiSlaveDefault(axilEp, v.axilWriteSlave, v.axilReadSlave, AXI_RESP_DECERR_C);

      -- Reset
      if (axilRst = '1') then
         v := REG_INIT_C;
      end if;

      -- Register the variable for next clock cycle
      rin <= v;

      -- Outputs
      axilWriteSlave <= r.axilWriteSlave;
      axilReadSlave  <= r.axilReadSlave;
      emuEnable      <= r.emuEnable;
      dataEnable     <= r.dataEnable;

   end process comb;

   seq : process (axilClk) is
   begin
      if (rising_edge(axilClk)) then
         r <= rin after TPD_G;
      end if;
   end process seq;

   U_pulseCount : entity work.SynchronizerVector
      generic map (
         TPD_G   => TPD_G,
         WIDTH_G => 16)
      port map (
         clk     => clk160MHz,
         dataIn  => r.pulseCount,
         dataOut => pulseCount);

   U_pulseWidth : entity work.SynchronizerVector
      generic map (
         TPD_G   => TPD_G,
         WIDTH_G => 16)
      port map (
         clk     => clk160MHz,
         dataIn  => r.pulseWidth,
         dataOut => pulseWidth);

   U_pulsePeriod : entity work.SynchronizerVector
      generic map (
         TPD_G   => TPD_G,
         WIDTH_G => 16)
      port map (
         clk     => clk160MHz,
         dataIn  => r.pulsePeriod,
         dataOut => pulsePeriod);

   U_continuous : entity work.Synchronizer
      generic map (
         TPD_G => TPD_G)
      port map (
         clk     => clk160MHz,
         dataIn  => r.continuous,
         dataOut => continuous);

   U_oneShot : entity work.SynchronizerOneShot
      generic map (
         TPD_G => TPD_G)
      port map (
         clk     => clk160MHz,
         dataIn  => r.oneShot,
         dataOut => oneShot);

   U_deserSampleEdge : entity work.Synchronizer
      generic map (
         TPD_G => TPD_G)
      port map (
         clk     => clk160MHz,
         dataIn  => r.deserSampleEdge,
         dataOut => deserSampleEdge);

   U_renable : entity work.Synchronizer
      generic map (
         TPD_G => TPD_G)
      port map (
         clk     => clk160MHz,
         dataIn  => r.renable,
         dataOut => renable);

   U_rstbRam : entity work.RstSync
      generic map (
         TPD_G          => TPD_G,
         IN_POLARITY_G  => '0',         -- 0 for active low
         OUT_POLARITY_G => '0',         -- 0 for active low
         OUT_REG_RST_G  => false)
      port map (
         clk      => clk160MHz,
         asyncRst => r.rstbRam,
         syncRst  => rstbRam);

   U_rstbRead : entity work.RstSync
      generic map (
         TPD_G          => TPD_G,
         IN_POLARITY_G  => '0',         -- 0 for active low
         OUT_POLARITY_G => '0',         -- 0 for active low
         OUT_REG_RST_G  => false)
      port map (
         clk      => clk160MHz,
         asyncRst => r.rstbRead,
         syncRst  => rstbRead);

   U_rstbTdc : entity work.RstSync
      generic map (
         TPD_G          => TPD_G,
         IN_POLARITY_G  => '0',         -- 0 for active low
         OUT_POLARITY_G => '0',         -- 0 for active low
         OUT_REG_RST_G  => false)
      port map (
         clk      => clk160MHz,
         asyncRst => r.rstbTdc,
         syncRst  => rstbTdc);

   U_rstbCounter : entity work.RstSync
      generic map (
         TPD_G          => TPD_G,
         IN_POLARITY_G  => '0',         -- 0 for active low
         OUT_POLARITY_G => '0',         -- 0 for active low
         OUT_REG_RST_G  => false)
      port map (
         clk      => clk160MHz,
         asyncRst => r.rstbCounter,
         syncRst  => rstbCounter);

   U_ckWrConfig : entity work.SynchronizerVector
      generic map (
         TPD_G   => TPD_G,
         WIDTH_G => CK_WR_CONFIG_SIZE_C)
      port map (
         clk     => clk160MHz,
         dataIn  => r.ckWrConfig,
         dataOut => ckWrConfig);

   process(clk160MHz)
   begin
      if rising_edge(clk160MHz) then
         if (ckWrConfig = 0) then
            ckWr <= '0' after TPD_G;
         else
            ckWr <= ckWrCnt(conv_integer(ckWrConfig)-1) after TPD_G;
         end if;
         ckWrCnt <= ckWrCnt + 1 after TPD_G;
      end if;
   end process;

   U_ckWriteAsic : entity work.OutputBufferReg
      generic map (
         TPD_G => TPD_G)
      port map (
         C => clk160MHz,
         I => ckWr,
         O => ckWriteAsic);

end mapping;
