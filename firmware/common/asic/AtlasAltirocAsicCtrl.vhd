-------------------------------------------------------------------------------
-- File       : AtlasAltirocAsicCtrl.vhd
-- Company    : SLAC National Accelerator Laboratory
-- Created    : 2018-09-14
-- Last update: 2018-09-14
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
      renable        : sl;
      rstbRam        : sl;
      rstbRead       : sl;
      rstbTdc        : sl;
      rstbCounter    : sl;
      ckWrConfig     : slv(CK_WR_CONFIG_SIZE_C-1 downto 0);
      axilReadSlave  : AxiLiteReadSlaveType;
      axilWriteSlave : AxiLiteWriteSlaveType;
   end record;

   constant REG_INIT_C : RegType := (
      renable        => '0',
      rstbRam        => '1',
      rstbRead       => '1',
      rstbTdc        => '1',
      rstbCounter    => '1',
      ckWrConfig     => (others => '0'),
      axilReadSlave  => AXI_LITE_READ_SLAVE_INIT_C,
      axilWriteSlave => AXI_LITE_WRITE_SLAVE_INIT_C);

   signal r   : RegType := REG_INIT_C;
   signal rin : RegType;

   signal ckWr       : sl                                  := '0';
   signal ckWrConfig : slv(CK_WR_CONFIG_SIZE_C-1 downto 0) := (others => '0');
   signal ckWrCnt    : slv(CK_WR_CONFIG_SIZE_C-1 downto 0) := (others => '0');

begin

   comb : process (axilReadMaster, axilRst, axilWriteMaster, r) is
      variable v      : RegType;
      variable axilEp : AxiLiteEndPointType;
   begin
      -- Latch the current value
      v := r;

      -- Determine the transaction type
      axiSlaveWaitTxn(axilEp, axilWriteMaster, axilReadMaster, v.axilWriteSlave, v.axilReadSlave);

      axiSlaveRegister(axilEp, x"800", 0, v.renable);
      axiSlaveRegister(axilEp, x"804", 0, v.rstbRam);
      axiSlaveRegister(axilEp, x"808", 0, v.rstbRead);
      axiSlaveRegister(axilEp, x"80C", 0, v.rstbTdc);
      axiSlaveRegister(axilEp, x"810", 0, v.rstbCounter);
      axiSlaveRegister(axilEp, x"814", 0, v.ckWrConfig);

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

   end process comb;

   seq : process (axilClk) is
   begin
      if (rising_edge(axilClk)) then
         r <= rin after TPD_G;
      end if;
   end process seq;

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
         ckWriteAsic <= ckWr;
         if (ckWrConfig = 0) then
            ckWr    <= '0'                           after TPD_G;
            ckWrCnt <= toSlv(1, CK_WR_CONFIG_SIZE_C) after TPD_G;
         else
            if ckWrCnt = ckWrConfig then
               ckWr    <= not(ckWr)                     after TPD_G;
               ckWrCnt <= toSlv(1, CK_WR_CONFIG_SIZE_C) after TPD_G;
            else
               ckWrCnt <= ckWrCnt + 1 after TPD_G;
            end if;
         end if;
      end if;
   end process;

end mapping;
