-------------------------------------------------------------------------------
-- File       : AtlasAltirocAsicGpio.vhd
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

entity AtlasAltirocAsicGpio is
   generic (
      TPD_G : time := 1 ns);
   port (
      -- GPIO Ports
      rstbRam         : out sl;               -- RSTB_RAM
      rstCounter      : out sl;               -- RST_COUNTER
      rstbTdc         : out sl;               -- RSTB_TDC
      rstbDll         : out sl;               -- RSTB_DLL
      digProbe        : in  slv(1 downto 0);  -- DIGITAL_PROBE[2:1]
      dlyCal          : out Slv12Array(1 downto 0);
      pllClkSel       : out slv(1 downto 0);
      -- AXI-Lite Interface (axilClk domain)
      axilClk         : in  sl;
      axilRst         : in  sl;
      axilReadMaster  : in  AxiLiteReadMasterType;
      axilReadSlave   : out AxiLiteReadSlaveType;
      axilWriteMaster : in  AxiLiteWriteMasterType;
      axilWriteSlave  : out AxiLiteWriteSlaveType);
end AtlasAltirocAsicGpio;

architecture mapping of AtlasAltirocAsicGpio is

   type RegType is record
      rstbRam        : sl;
      rstCounter     : sl;
      rstbTdc        : sl;
      rstbDll        : sl;
      dlyCal         : Slv12Array(1 downto 0);
      pllClkSel      : slv(1 downto 0);
      axilReadSlave  : AxiLiteReadSlaveType;
      axilWriteSlave : AxiLiteWriteSlaveType;
   end record;

   constant REG_INIT_C : RegType := (
      rstbRam        => '1',
      rstCounter     => '0',
      rstbTdc        => '1',
      rstbDll        => '1',
      dlyCal         => (0 => (others => '0'), 1 => (others => '1')),
      pllClkSel      => (others => '0'),
      axilReadSlave  => AXI_LITE_READ_SLAVE_INIT_C,
      axilWriteSlave => AXI_LITE_WRITE_SLAVE_INIT_C);

   signal r   : RegType := REG_INIT_C;
   signal rin : RegType;

begin

   comb : process (axilReadMaster, axilRst, axilWriteMaster, digProbe, r) is
      variable v      : RegType;
      variable axilEp : AxiLiteEndPointType;
   begin
      -- Latch the current value
      v := r;

      -- Determine the transaction type
      axiSlaveWaitTxn(axilEp, axilWriteMaster, axilReadMaster, v.axilWriteSlave, v.axilReadSlave);

      axiSlaveRegister (axilEp, x"00", 0, v.rstbRam);
      axiSlaveRegister (axilEp, x"04", 0, v.rstCounter);
      axiSlaveRegister (axilEp, x"08", 0, v.rstbTdc);
      axiSlaveRegister (axilEp, x"0C", 0, v.rstbDll);
      axiSlaveRegisterR(axilEp, x"10", 0, digProbe);
      axiSlaveRegister (axilEp, x"14", 0, v.dlyCal(0));
      axiSlaveRegister (axilEp, x"18", 0, v.dlyCal(1));
      axiSlaveRegister (axilEp, x"1C", 0, v.pllClkSel);

      -- Closeout the transaction
      axiSlaveDefault(axilEp, v.axilWriteSlave, v.axilReadSlave, AXI_RESP_DECERR_C);

      -- Outputs
      axilWriteSlave <= r.axilWriteSlave;
      axilReadSlave  <= r.axilReadSlave;
      rstbRam        <= r.rstbRam;
      rstCounter     <= r.rstCounter;
      rstbTdc        <= r.rstbTdc;
      rstbDll        <= r.rstbDll;
      pllClkSel      <= r.pllClkSel;
      dlyCal         <= r.dlyCal;

      -- -- Update the upper 2-bit to make the output linear w.r.t. the cascading delay modules
      -- for i in 1 downto 0 loop
         -- dlyCal(i)(9 downto 0) <= r.dlyCal(i)(9 downto 0);
         -- dlyCal(i)(10)         <= r.dlyCal(i)(10) or r.dlyCal(i)(11);
         -- dlyCal(i)(11)         <= r.dlyCal(i)(11);
      -- end loop;

      -- Reset
      if (axilRst = '1') then
         v := REG_INIT_C;
      end if;

      -- Register the variable for next clock cycle
      rin <= v;

   end process comb;

   seq : process (axilClk) is
   begin
      if (rising_edge(axilClk)) then
         r <= rin after TPD_G;
      end if;
   end process seq;

end mapping;
