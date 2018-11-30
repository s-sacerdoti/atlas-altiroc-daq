-------------------------------------------------------------------------------
-- File       : AtlasAltirocAsicDeser.vhd
-- Company    : SLAC National Accelerator Laboratory
-------------------------------------------------------------------------------
-- Description: ASIC Deserializer 
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
use work.AxiStreamPkg.all;
use work.SsiPkg.all;
use work.Pgp3Pkg.all;

entity AtlasAltirocAsicDeser is
   generic (
      TPD_G : time := 1 ns);
   port (
      -- Control Interface
      readoutEnable   : in  sl;
      emuEnable       : in  sl;
      emuTrig         : in  sl;
      -- Serial Interface
      deserClk        : in  sl;
      deserRst        : in  sl;
      deserSampleEdge : in  sl;  -- '0' = rising_edge, '1' = falling_edge          
      deserInvert     : in  sl;
      doutP           : in  sl;         -- DOUT_P
      doutN           : in  sl;         -- DOUT_N      
      -- Master AXI Stream Interface
      mAxisClk        : in  sl;
      mAxisRst        : in  sl;
      mAxisMaster     : out AxiStreamMasterType;
      mAxisSlave      : in  AxiStreamSlaveType);
end AtlasAltirocAsicDeser;

architecture rtl of AtlasAltirocAsicDeser is

   constant AXIS_CONFIG_C : AxiStreamConfigType := ssiAxiStreamConfig(4);  -- 32-bit AXI stream interface

   type RegType is record
      dout      : sl;
      doutArray : slv(22 downto 0);
      aligned   : slv(3 downto 0);
      cnt       : natural range 0 to 22;
      seqCnt    : slv(12 downto 0);
      tData     : slv(31 downto 0);
      txMaster  : AxiStreamMasterType;
   end record RegType;
   constant REG_INIT_C : RegType := (
      dout      => '0',
      doutArray => (others => '0'),
      aligned   => (others => '0'),
      cnt       => 0,
      seqCnt    => (others => '0'),
      tData     => (others => '0'),
      txMaster  => AXI_STREAM_MASTER_INIT_C);

   signal r   : RegType := REG_INIT_C;
   signal rin : RegType;

   signal txMaster : AxiStreamMasterType;
   signal txSlave  : AxiStreamSlaveType;

   signal Q1 : sl;
   signal Q2 : sl;

   signal runEnable       : sl;
   signal emulationEnable : sl;
   signal emulationTrig   : sl;
   signal edgeSelect      : sl;
   signal invertData      : sl;

   attribute dont_touch                    : string;
   attribute dont_touch of r               : signal is "TRUE";
   attribute dont_touch of Q1              : signal is "TRUE";
   attribute dont_touch of Q2              : signal is "TRUE";
   attribute dont_touch of runEnable       : signal is "TRUE";
   attribute dont_touch of emulationEnable : signal is "TRUE";
   attribute dont_touch of emulationTrig   : signal is "TRUE";
   attribute dont_touch of invertData      : signal is "TRUE";

begin

   U_RegisteredInput : entity work.InputBufferReg
      generic map (
         TPD_G       => TPD_G,
         DIFF_PAIR_G => true)
      port map (
         C  => deserClk,
         I  => doutP,
         IB => doutN,
         Q1 => Q1,
         Q2 => Q2);

   U_emuTrig : entity work.SynchronizerOneShot
      generic map (
         TPD_G => TPD_G)
      port map (
         clk     => deserClk,
         dataIn  => emuTrig,
         dataOut => emulationTrig);

   U_SyncVec : entity work.SynchronizerVector
      generic map (
         TPD_G   => TPD_G,
         WIDTH_G => 4)
      port map (
         clk        => deserClk,
         -- Input
         dataIn(0)  => deserSampleEdge,
         dataIn(1)  => emuEnable,
         dataIn(2)  => readoutEnable,
         dataIn(3)  => deserInvert,
         -- Output
         dataOut(0) => edgeSelect,
         dataOut(1) => emulationEnable,
         dataOut(2) => runEnable,
         dataOut(3) => invertData);

   comb : process (Q1, Q2, deserRst, edgeSelect, emulationEnable,
                   emulationTrig, invertData, r, runEnable, txSlave) is
      variable v      : RegType;
      variable i      : natural;
      variable sofDet : sl;
   begin
      -- Latch the current value
      v := r;

      -- Check the flow control
      if txSlave.tReady = '1' then
         v.txMaster.tValid := '0';
      end if;

      -- Check if using rising_edge sample
      if (edgeSelect = '0') then
         v.dout := Q1 xor invertData;
      -- Else using falling_edge sample
      else
         v.dout := Q2 xor invertData;
      end if;

      -- Create a shift register array
      v.doutArray := r.dout & r.doutArray(22 downto 1);

      -- Emulation data taking mode
      if (emulationEnable = '1') then

         -- Check for trigger and ready to move data
         if (emulationTrig = '1') then
            -- Check if ready to move data
            if (v.txMaster.tValid = '0') then
               -- Forward the data
               v.txMaster.tValid              := '1';
               v.txMaster.tData(31 downto 19) := r.seqCnt;
               v.txMaster.tData(18 downto 0)  := (others => '0');
            end if;
            -- Increment the sequence counter
            v.seqCnt := r.seqCnt + 1;
         end if;

         -- Reset the flags
         v.aligned := x"0";

         -- Reset the counter
         v.cnt := 0;

      else

        -------------------------------------------------------------------
        -- 21 bits of each pixel SRAM are read and serialized at 320 MHz, 
        -- the serial data will be transmitted at a max. freq. of 320 MHz.
        -------------------------------------------------------------------
        -- The start of the frame is identified by the first two bits, 
        -- which are "1 0 " followed by the 19 bits corresponding to: 
        --       TOA<0:6>,
        --       TOA<7> = overflow
        --       TOT<0:8>
        --       TOT<9> = overflow
        -------------------------------------------------------------------

         -- Check for the last bit of the frame
         if (r.cnt = 20) then

            -- Check for two SOF markers 22 cycles apart
            if (r.doutArray(22 downto 21) = "01") and (r.doutArray(1 downto 0) = "01") then

               -- Reset the counter
               v.cnt := 0;

               -- Alignment detected
               v.aligned := r.aligned(2 downto 0) & '1';

               -- Check for Readout Enable (RENABLE) and alignment detected 4 times or more
               if (runEnable = '1') and (r.aligned = x"F") then

                  -- Check if ready to move data
                  if (v.txMaster.tValid = '0') then
                     -- Forward the data
                     v.txMaster.tValid              := '1';
                     v.txMaster.tData(31 downto 19) := r.seqCnt;
                     v.txMaster.tData(18 downto 0)  := r.doutArray(20 downto 2);
                  end if;

                  -- Increment the sequence counter
                  v.seqCnt := r.seqCnt + 1;

               end if;

            else
               -- Reset the flags
               v.aligned := x"0";
            end if;

         else
            -- Increment the counter
            v.cnt := r.cnt + 1;
         end if;

      end if;

      -- Only Sending 1 word frames
      ssiSetUserSof(AXIS_CONFIG_C, v.txMaster, '1');  -- Tag as start of frame (SOF)
      v.txMaster.tLast := '1';          -- Tag as end of frame (EOF)

      -- Tap for chipscope debugging signal
      v.tData := v.txMaster.tData(31 downto 0);

      -- Outputs       
      txMaster <= r.txMaster;

      -- Reset
      if (deserRst = '1') then
         v := REG_INIT_C;
      end if;

      -- Register the variable for next clock cycle
      rin <= v;

   end process comb;

   seq : process (deserClk) is
   begin
      if rising_edge(deserClk) then
         r <= rin after TPD_G;
      end if;
   end process seq;

   FIFO_TX : entity work.AxiStreamFifoV2
      generic map (
         -- General Configurations
         TPD_G               => TPD_G,
         SLAVE_READY_EN_G    => true,
         VALID_THOLD_G       => 1,
         -- FIFO configurations
         BRAM_EN_G           => false,
         GEN_SYNC_FIFO_G     => false,
         FIFO_ADDR_WIDTH_G   => 4,
         -- AXI Stream Port Configurations
         SLAVE_AXI_CONFIG_G  => AXIS_CONFIG_C,
         MASTER_AXI_CONFIG_G => PGP3_AXIS_CONFIG_C)
      port map (
         -- Slave Port
         sAxisClk    => deserClk,
         sAxisRst    => deserRst,
         sAxisMaster => txMaster,
         sAxisSlave  => txSlave,
         -- Master Port
         mAxisClk    => mAxisClk,
         mAxisRst    => mAxisRst,
         mAxisMaster => mAxisMaster,
         mAxisSlave  => mAxisSlave);

end rtl;
