-------------------------------------------------------------------------------
-- File       : AtlasAltirocPkg.vhd
-- Company    : SLAC National Accelerator Laboratory
-------------------------------------------------------------------------------
-- Description: ATLAS ALTIROC VHDL Package
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

package AtlasAltirocPkg is

   type AtlasAltirocConfigType is record
      pllRst  : sl;
      dlyData : slv(9 downto 0);
      clkSel  : slv(1 downto 0);
   end record;
   constant ALTIROC_CONFIG_INIT_C : AtlasAltirocConfigType := (
      pllRst  => '0',
      dlyData => (others => '0'),
      clkSel  => "00");

   type AtlasAltirocStatusType is record
      intPllLocked : sl;
      extPllLocked : sl;
   end record;
   constant ALTIROC_STATUS_INIT_C : AtlasAltirocStatusType := (
      intPllLocked => '0',
      extPllLocked => '0');

end package;
