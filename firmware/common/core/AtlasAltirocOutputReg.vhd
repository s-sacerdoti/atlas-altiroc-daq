-------------------------------------------------------------------------------
-- File       : AtlasAltirocOutputReg.vhd
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

entity AtlasAltirocOutputReg is
   generic (
      TPD_G : time := 1 ns);
   port (
      clk : in  sl;
      I   : in  sl;
      O   : out sl);
end AtlasAltirocOutputReg;

architecture rtl of AtlasAltirocOutputReg is

   signal reg : sl;

begin

   U_ODDR : ODDR
      port map (
         C  => clk,
         Q  => reg,
         CE => '1',
         D1 => I,
         D2 => I,
         R  => '0',
         S  => '0');

   U_OBUF : OBUF
      port map (
         I => reg,
         O => O);

end rtl;
