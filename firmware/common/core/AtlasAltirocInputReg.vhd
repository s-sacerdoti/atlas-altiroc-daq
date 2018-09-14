-------------------------------------------------------------------------------
-- File       : AtlasAltirocInputReg.vhd
-- Company    : SLAC National Accelerator Laboratory
-- Created    : 2018-09-07
-- Last update: 2018-09-12
-------------------------------------------------------------------------------
-- Description: Output Registers
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

library unisim;
use unisim.vcomponents.all;

entity AtlasAltirocInputReg is
   generic (
      TPD_G : time := 1 ns);
   port (
      clk : in  sl;
      I   : in  sl;
      O   : out sl);
end AtlasAltirocInputReg;

architecture rtl of AtlasAltirocInputReg is

   signal reg : sl;

begin

   U_IBUFDS : IBUF
      port map (
         I => I,
         O => reg);

   U_IDDR : IDDR
      port map (
         Q1 => O,
         Q2 => open,
         C  => clk,
         CE => '1',
         D  => reg,
         R  => '0',
         S  => '0');

end rtl;
