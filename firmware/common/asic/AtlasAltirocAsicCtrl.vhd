-------------------------------------------------------------------------------
-- File       : AtlasAltirocAsicCtrl.vhd
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

entity AtlasAltirocAsicCtrl is
   generic (
      TPD_G : time := 1 ns);
   port (
      -- ASIC Interface
      clk40MHz        : in  sl;
      rst40MHz        : in  sl;
      clk160MHz       : in  sl;
      rst160MHz       : in  sl;
      deserClk        : in  sl;
      deserRst        : in  sl;
      rstbRam         : out sl;         -- RSTB_RAM
      rstbRead        : out sl;         -- RSTB_READ
      rstbTdc         : out sl;         -- RSTB_TDC
      ckWriteAsic     : out sl;         -- CK_WRITE_ASIC
      deserSampleEdge : out sl;
      deserInvert     : out sl;
      deserSlip       : out sl;
      continuous      : out sl;
      oneShot         : out sl;
      invRstCnt       : out sl;
      pulseCount      : out slv(15 downto 0);
      pulseWidth      : out slv(15 downto 0);
      pulsePeriod     : out slv(15 downto 0);
      pulseDelay      : out slv(15 downto 0);
      readDelay       : out slv(15 downto 0);
      readDuration    : out slv(15 downto 0);
      rstCntMask      : out slv(1 downto 0);
      rstTdcMask      : out slv(1 downto 0);
      emuEnable       : out sl;
      dataWordDet     : in  sl;
      hitDet          : in  sl;
      dataBus         : in  slv(31 downto 0);
      dataDropped     : in  sl;
      forwardData     : out sl;
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
      dataDropCnt     : slv(31 downto 0);
      dataWordCnt     : slv(31 downto 0);
      hitCnt          : slv(31 downto 0);
      continuous      : sl;
      oneShot         : sl;
      invRstCnt       : sl;
      pulseCount      : slv(15 downto 0);
      pulseWidth      : slv(15 downto 0);
      pulsePeriod     : slv(15 downto 0);
      pulseDelay      : slv(15 downto 0);
      readDelay       : slv(15 downto 0);
      readDuration    : slv(15 downto 0);
      rstCntMask      : slv(1 downto 0);
      rstTdcMask      : slv(1 downto 0);
      deserSampleEdge : sl;
      deserInvert     : sl;
      deserSlip       : sl;
      rstbRam         : sl;
      rstbRead        : sl;
      rstbTdc         : sl;
      ckWrConfig      : slv(CK_WR_CONFIG_SIZE_C-1 downto 0);
      emuEnable       : sl;
      forwardData     : sl;
      cntRst          : sl;
      axilReadSlave   : AxiLiteReadSlaveType;
      axilWriteSlave  : AxiLiteWriteSlaveType;
   end record;

   constant REG_INIT_C : RegType := (
      dataDropCnt     => (others => '0'),
      dataWordCnt     => (others => '0'),
      hitCnt          => (others => '0'),
      continuous      => '0',
      oneShot         => '0',
      invRstCnt       => '0',
      pulseCount      => toSlv(1, 16),
      pulseWidth      => toSlv(1, 16),
      pulsePeriod     => toSlv(2, 16),
      pulseDelay      => toSlv(4, 16),
      readDelay       => toSlv(8, 16),
      readDuration    => toSlv(1024, 16),
      rstCntMask      => "11",
      rstTdcMask      => "01",
      deserSampleEdge => '0',
      deserInvert     => '0',
      deserSlip       => '0',
      rstbRam         => '1',
      rstbRead        => '1',
      rstbTdc         => '1',
      ckWrConfig      => (others => '0'),
      emuEnable       => '0',
      forwardData     => '0',           -- Don't forward by default
      cntRst          => '0',
      axilReadSlave   => AXI_LITE_READ_SLAVE_INIT_C,
      axilWriteSlave  => AXI_LITE_WRITE_SLAVE_INIT_C);

   signal r   : RegType := REG_INIT_C;
   signal rin : RegType;

   signal dataDropDet : sl;
   signal ckWr        : sl                                       := '0';
   signal ckWrConfig  : slv(CK_WR_CONFIG_SIZE_C-1 downto 0)      := (others => '0');
   signal ckWrCnt     : slv((2**CK_WR_CONFIG_SIZE_C)-1 downto 0) := (others => '0');

   -- attribute dont_touch         : string;
   -- attribute dont_touch of ckWr : signal is "TRUE";   

begin

   U_dataDropped : entity work.SynchronizerOneShot
      generic map (
         TPD_G => TPD_G)
      port map (
         clk     => axilClk,
         dataIn  => dataDropped,
         dataOut => dataDropDet);

   comb : process (axilReadMaster, axilRst, axilWriteMaster, dataBus,
                   dataDropDet, dataWordDet, hitDet, r) is
      variable v      : RegType;
      variable axilEp : AxiLiteEndPointType;
   begin
      -- Latch the current value
      v := r;

      -- Reset strobes
      v.cntRst    := '0';
      v.oneShot   := '0';
      v.deserSlip := '0';


      -- Check for counter reset
      if (r.cntRst = '1') then

         -- Reset the counters
         v.dataWordCnt := (others => '0');
         v.hitCnt      := (others => '0');
         v.dataDropCnt := (others => '0');

      else

         if (dataWordDet = '1') then
            -- Increment the counter
            v.dataWordCnt := r.dataWordCnt + 1;
         end if;

         if (hitDet = '1') then
            -- Increment the counter
            v.hitCnt := r.hitCnt + 1;
         end if;

         if (dataDropDet = '1') then
            -- Increment the counter
            v.dataDropCnt := r.dataDropCnt + 1;
         end if;

      end if;

      -- Determine the transaction type
      axiSlaveWaitTxn(axilEp, axilWriteMaster, axilReadMaster, v.axilWriteSlave, v.axilReadSlave);

      -- axiSlaveRegister(axilEp, x"800", 0, v.renable);
      axiSlaveRegister(axilEp, x"804", 0, v.rstbRam);
      axiSlaveRegister(axilEp, x"808", 0, v.rstbRead);
      axiSlaveRegister(axilEp, x"80C", 0, v.rstbTdc);
      -- axiSlaveRegister(axilEp, x"810", 0, v.rstbCounter);
      axiSlaveRegister(axilEp, x"814", 0, v.ckWrConfig);

      axiSlaveRegister (axilEp, x"8FC", 0, v.deserSlip);
      axiSlaveRegister (axilEp, x"900", 0, v.deserSampleEdge);
      axiSlaveRegister (axilEp, x"900", 1, v.deserInvert);
      axiSlaveRegister (axilEp, x"904", 0, v.emuEnable);
      axiSlaveRegister (axilEp, x"908", 0, v.forwardData);
      axiSlaveRegisterR(axilEp, x"90C", 0, r.dataWordCnt);
      axiSlaveRegisterR(axilEp, x"910", 0, r.hitCnt);
      axiSlaveRegisterR(axilEp, x"914", 0, dataBus);
      axiSlaveRegisterR(axilEp, x"918", 0, r.dataDropCnt);

      axiSlaveRegister(axilEp, x"A00", 0, v.pulseCount);
      axiSlaveRegister(axilEp, x"A04", 0, v.pulseWidth);
      axiSlaveRegister(axilEp, x"A08", 0, v.pulsePeriod);
      axiSlaveRegister(axilEp, x"A0C", 0, v.continuous);
      axiSlaveRegister(axilEp, x"A10", 0, v.oneShot);
      axiSlaveRegister(axilEp, x"A14", 0, v.pulseDelay);
      axiSlaveRegister(axilEp, x"A18", 0, v.readDelay);
      axiSlaveRegister(axilEp, x"A1C", 0, v.readDuration);
      axiSlaveRegister(axilEp, x"A20", 0, v.rstCntMask);
      axiSlaveRegister(axilEp, x"A24", 0, v.invRstCnt);
      axiSlaveRegister(axilEp, x"A28", 0, v.rstTdcMask);

      axiSlaveRegister(axilEp, x"FFC", 0, v.cntRst);

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
      forwardData    <= r.forwardData;

   end process comb;

   seq : process (axilClk) is
   begin
      if (rising_edge(axilClk)) then
         r <= rin after TPD_G;
      end if;
   end process seq;

   U_pulseCount : entity work.SynchronizerFifo
      generic map (
         TPD_G        => TPD_G,
         DATA_WIDTH_G => 16)
      port map (
         wr_clk => axilClk,
         din    => r.pulseCount,
         rd_clk => clk40MHz,
         dout   => pulseCount);

   U_pulseWidth : entity work.SynchronizerFifo
      generic map (
         TPD_G        => TPD_G,
         DATA_WIDTH_G => 16)
      port map (
         wr_clk => axilClk,
         din    => r.pulseWidth,
         rd_clk => clk160MHz,
         dout   => pulseWidth);

   U_pulsePeriod : entity work.SynchronizerFifo
      generic map (
         TPD_G        => TPD_G,
         DATA_WIDTH_G => 16)
      port map (
         wr_clk => axilClk,
         din    => r.pulsePeriod,
         rd_clk => clk40MHz,
         dout   => pulsePeriod);

   U_pulseDelay : entity work.SynchronizerFifo
      generic map (
         TPD_G        => TPD_G,
         DATA_WIDTH_G => 16)
      port map (
         wr_clk => axilClk,
         din    => r.pulseDelay,
         rd_clk => clk40MHz,
         dout   => pulseDelay);

   U_readDelay : entity work.SynchronizerFifo
      generic map (
         TPD_G        => TPD_G,
         DATA_WIDTH_G => 16)
      port map (
         wr_clk => axilClk,
         din    => r.readDelay,
         rd_clk => clk40MHz,
         dout   => readDelay);

   U_readDuration : entity work.SynchronizerFifo
      generic map (
         TPD_G        => TPD_G,
         DATA_WIDTH_G => 16)
      port map (
         wr_clk => axilClk,
         din    => r.readDuration,
         rd_clk => clk40MHz,
         dout   => readDuration);

   U_rstCntMask : entity work.SynchronizerVector
      generic map (
         TPD_G   => TPD_G,
         WIDTH_G => 2)
      port map (
         clk     => clk40MHz,
         dataIn  => r.rstCntMask,
         dataOut => rstCntMask);

   U_rstTdcMask : entity work.SynchronizerVector
      generic map (
         TPD_G   => TPD_G,
         WIDTH_G => 2)
      port map (
         clk     => clk40MHz,
         dataIn  => r.rstTdcMask,
         dataOut => rstTdcMask);

   U_invRstCnt : entity work.Synchronizer
      generic map (
         TPD_G => TPD_G)
      port map (
         clk     => clk40MHz,
         dataIn  => r.invRstCnt,
         dataOut => invRstCnt);

   U_continuous : entity work.Synchronizer
      generic map (
         TPD_G => TPD_G)
      port map (
         clk     => clk40MHz,
         dataIn  => r.continuous,
         dataOut => continuous);

   U_oneShot : entity work.SynchronizerOneShot
      generic map (
         TPD_G => TPD_G)
      port map (
         clk     => clk40MHz,
         dataIn  => r.oneShot,
         dataOut => oneShot);

   U_deserSampleEdge : entity work.Synchronizer
      generic map (
         TPD_G => TPD_G)
      port map (
         clk     => deserClk,
         dataIn  => r.deserSampleEdge,
         dataOut => deserSampleEdge);

   U_deserInvert : entity work.Synchronizer
      generic map (
         TPD_G => TPD_G)
      port map (
         clk     => deserClk,
         dataIn  => r.deserInvert,
         dataOut => deserInvert);

   U_deserSlip : entity work.SynchronizerOneShot
      generic map (
         TPD_G => TPD_G)
      port map (
         clk     => deserClk,
         dataIn  => r.deserSlip,
         dataOut => deserSlip);

   U_rstbRam : entity work.RstSync
      generic map (
         TPD_G          => TPD_G,
         IN_POLARITY_G  => '0',         -- 0 for active low
         OUT_POLARITY_G => '0',         -- 0 for active low
         OUT_REG_RST_G  => false)
      port map (
         clk      => clk40MHz,
         asyncRst => r.rstbRam,
         syncRst  => rstbRam);

   U_rstbRead : entity work.RstSync
      generic map (
         TPD_G          => TPD_G,
         IN_POLARITY_G  => '0',         -- 0 for active low
         OUT_POLARITY_G => '0',         -- 0 for active low
         OUT_REG_RST_G  => false)
      port map (
         clk      => clk40MHz,
         asyncRst => r.rstbRead,
         syncRst  => rstbRead);

   U_rstbTdc : entity work.Synchronizer
      generic map (
         TPD_G => TPD_G)
      port map (
         clk     => clk40MHz,
         dataIn  => r.rstbTdc,
         dataOut => rstbTdc);

   U_ckWrConfig : entity work.SynchronizerVector
      generic map (
         TPD_G   => TPD_G,
         WIDTH_G => CK_WR_CONFIG_SIZE_C)
      port map (
         clk     => clk40MHz,
         dataIn  => r.ckWrConfig,
         dataOut => ckWrConfig);

   process(clk40MHz)
   begin
      if rising_edge(clk40MHz) then
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
         C => clk40MHz,
         I => ckWr,
         O => ckWriteAsic);

end mapping;
