-------------------------------------------------------------------------------
-- File       : AtlasAltirocAsicTdcClk.vhd
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

entity AtlasAltirocAsicTdcClk is
   generic (
      TPD_G : time := 1 ns);
   port (
      -- TDC Clock
      tdcClkSel       : out sl;         -- MUX_CLK_SEL 
      fpgaTdcClkP     : out sl;         -- FPGA_CK_40_P
      fpgaTdcClkN     : out sl;         -- FPGA_CK_40_M    
      -- AXI-Lite Interface (axilClk domain)
      clk160MHz       : in  sl;
      rst160MHz       : in  sl;
      axilReadMaster  : in  AxiLiteReadMasterType;
      axilReadSlave   : out AxiLiteReadSlaveType;
      axilWriteMaster : in  AxiLiteWriteMasterType;
      axilWriteSlave  : out AxiLiteWriteSlaveType);
end AtlasAltirocAsicTdcClk;

architecture mapping of AtlasAltirocAsicTdcClk is

   type RegType is record
      fpgaTdcClk     : sl;
      fpgaTdcClkCnt  : slv(7 downto 0);
      fpgaTdcClkHigh : slv(7 downto 0);
      fpgaTdcClkLow  : slv(7 downto 0);
      tdcClkSel      : sl;
      axilReadSlave  : AxiLiteReadSlaveType;
      axilWriteSlave : AxiLiteWriteSlaveType;
   end record;

   constant REG_INIT_C : RegType := (
      fpgaTdcClk     => '0',
      fpgaTdcClkCnt  => (others => '0'),
      fpgaTdcClkHigh => (others => '0'),
      fpgaTdcClkLow  => (others => '0'),
      tdcClkSel      => '0',
      axilReadSlave  => AXI_LITE_READ_SLAVE_INIT_C,
      axilWriteSlave => AXI_LITE_WRITE_SLAVE_INIT_C);

   signal r   : RegType := REG_INIT_C;
   signal rin : RegType;

begin

   comb : process (axilReadMaster, axilWriteMaster, r, rst160MHz) is
      variable v      : RegType;
      variable axilEp : AxiLiteEndPointType;
   begin
      -- Latch the current value
      v := r;

      -- Determine the transaction type
      axiSlaveWaitTxn(axilEp, axilWriteMaster, axilReadMaster, v.axilWriteSlave, v.axilReadSlave);

      axiSlaveRegister (axilEp, x"0", 0, v.tdcClkSel);
      axiSlaveRegister (axilEp, x"4", 0, v.fpgaTdcClkHigh);
      axiSlaveRegister (axilEp, x"8", 0, v.fpgaTdcClkLow);

      -- Closeout the transaction
      axiSlaveDefault(axilEp, v.axilWriteSlave, v.axilReadSlave, AXI_RESP_DECERR_C);

      -- Increment the counter
      v.fpgaTdcClkCnt := r.fpgaTdcClkCnt + 1;

      -- Check for high-to-low transition
      if (r.fpgaTdcClk = '1') and (v.fpgaTdcClkHigh = r.fpgaTdcClkCnt) then
         -- Reset counter
         v.fpgaTdcClkCnt := (others => '0');
         -- Set the flag
         v.fpgaTdcClk    := '0';

      -- Check for low-to-high transition
      elsif (r.fpgaTdcClk = '0') and (v.fpgaTdcClkLow = r.fpgaTdcClkCnt) then
         -- Reset counter
         v.fpgaTdcClkCnt := (others => '0');
         -- Set the flag
         v.fpgaTdcClk    := '1';

      -- Check for change in configuration
      elsif (r.fpgaTdcClkHigh /= v.fpgaTdcClkHigh) or (r.fpgaTdcClkLow /= v.fpgaTdcClkLow) then
         -- Reset counter
         v.fpgaTdcClkCnt := (others => '0');
      end if;

      -- Reset
      if (rst160MHz = '1') then
         v                := REG_INIT_C;
         -- Don't touch register configurations
         v.tdcClkSel      := r.tdcClkSel;
         v.fpgaTdcClkHigh := r.fpgaTdcClkHigh;
         v.fpgaTdcClkLow  := r.fpgaTdcClkLow;
      end if;

      -- Register the variable for next clock cycle
      rin <= v;

      -- Outputs
      axilWriteSlave <= r.axilWriteSlave;
      axilReadSlave  <= r.axilReadSlave;
      tdcClkSel      <= r.tdcClkSel;

   end process comb;

   seq : process (clk160MHz) is
   begin
      if (rising_edge(clk160MHz)) then
         r <= rin after TPD_G;
      end if;
   end process seq;

   U_fpgaTdcClk : entity work.OutputBufferReg
      generic map (
         TPD_G       => TPD_G,
         DIFF_PAIR_G => true)
      port map (
         C  => clk160MHz,
         I  => r.fpgaTdcClk,
         O  => fpgaTdcClkP,
         OB => fpgaTdcClkN);

end mapping;
