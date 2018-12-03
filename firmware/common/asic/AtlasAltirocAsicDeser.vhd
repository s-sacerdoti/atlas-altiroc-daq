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
      dataDropped     : out sl;
      -- Serial Interface
      deserClk        : in  sl;
      deserRst        : in  sl;
      deserSampleEdge : in  sl;  -- '0' = rising_edge, '1' = falling_edge          
      deserInvert     : in  sl;
      deserSlip       : in  sl;
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
      runEnable   : sl;
      dataDropped : sl;
      dout        : sl;
      doutArray   : slv(22 downto 0);
      aligned     : slv(3 downto 0);
      cnt         : natural range 0 to 22;
      seqCnt      : slv(12 downto 0);
      tData       : slv(31 downto 0);
      txMaster    : AxiStreamMasterType;
   end record RegType;
   constant REG_INIT_C : RegType := (
      runEnable   => '0',
      dataDropped => '0',
      dout        => '0',
      doutArray   => (others => '0'),
      aligned     => (others => '0'),
      cnt         => 0,
      seqCnt      => (others => '0'),
      tData       => (others => '0'),
      txMaster    => AXI_STREAM_MASTER_INIT_C);

   signal r   : RegType := REG_INIT_C;
   signal rin : RegType;

   signal txMaster : AxiStreamMasterType;
   signal txSlave  : AxiStreamSlaveType;

   signal Q1 : sl;
   signal Q2 : sl;

   signal runEnable       : sl;
   signal emulationEnable : sl;
   signal emulationTrig   : sl;

   -- attribute dont_touch                    : string;
   -- attribute dont_touch of r               : signal is "TRUE";
   -- attribute dont_touch of Q1              : signal is "TRUE";
   -- attribute dont_touch of Q2              : signal is "TRUE";
   -- attribute dont_touch of runEnable       : signal is "TRUE";
   -- attribute dont_touch of emulationEnable : signal is "TRUE";
   -- attribute dont_touch of emulationTrig   : signal is "TRUE";

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
         WIDTH_G => 2)
      port map (
         clk        => deserClk,
         -- Input
         dataIn(0)  => emuEnable,
         dataIn(1)  => readoutEnable,
         -- Output
         dataOut(0) => emulationEnable,
         dataOut(1) => runEnable);

   comb : process (Q1, Q2, deserInvert, deserRst, deserSampleEdge, deserSlip,
                   emulationEnable, emulationTrig, r, runEnable, txSlave) is
      variable v      : RegType;
      variable i      : natural;
      variable sofDet : sl;
   begin
      -- Latch the current value
      v := r;

      -- Reset strobes
      v.dataDropped := '0';

      -- Check the flow control
      if txSlave.tReady = '1' then
         v.txMaster.tValid := '0';
         v.txMaster.tLast  := '0';
         v.txMaster.tUser  := (others => '0');
      end if;

      -- Check if using rising_edge sample
      if (deserSampleEdge = '0') then
         v.dout := Q1 xor deserInvert;
      -- Else using falling_edge sample
      else
         v.dout := Q2 xor deserInvert;
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
               -- Only Sending 1 word frames
               ssiSetUserSof(AXIS_CONFIG_C, v.txMaster, '1');  -- Tag as start of frame (SOF)
               v.txMaster.tLast := '1';       -- Tag as end of frame (EOF)         
            else
               -- Drop data due to back pressure
               v.dataDropped := '1';
            end if;

            -- Increment the sequence counter
            v.seqCnt := r.seqCnt + 1;

         end if;

         -- Reset the flags
         v.aligned := x"0";

         -- Reset the counter
         v.cnt := 0;

         -- Reset cache
         v.runEnable := '0';

      -- Check if not bit slipping
      elsif (deserSlip = '0') then

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

               -- Check for alignment detected 4 times or more
               if (r.aligned = x"F") then

                  -- Make delayed copy cache
                  v.runEnable := runEnable;

                  -- Check for Readout Enable (RENABLE)
                  if (runEnable = '1') or (r.runEnable = '1') then

                     -- Check if ready to move data
                     if (v.txMaster.tValid = '0') then

                        -- Forward the data
                        v.txMaster.tValid              := '1';
                        v.txMaster.tData(31 downto 19) := r.seqCnt;
                        v.txMaster.tData(18 downto 0)  := r.doutArray(20 downto 2);

                        -- Check for SOF condition
                        if (r.runEnable = '0') and (runEnable = '1') then
                           ssiSetUserSof(AXIS_CONFIG_C, v.txMaster, '1');
                        end if;

                        -- Check for EOF condition
                        if (r.runEnable = '1') and (runEnable = '0') then
                           v.txMaster.tLast := '1';
                        end if;

                     else
                        -- Drop data due to back pressure
                        v.dataDropped := '1';
                     end if;

                     -- Increment the sequence counter
                     v.seqCnt := r.seqCnt + 1;

                  end if;

               end if;

            else
               -- Reset the flags
               v.aligned   := x"0";
               -- Reset cache
               v.runEnable := '0';
            end if;

         else
            -- Increment the counter
            v.cnt := r.cnt + 1;
         end if;

      end if;

      -- Tap for chipscope debugging signal
      v.tData := v.txMaster.tData(31 downto 0);

      -- Outputs       
      txMaster    <= r.txMaster;
      dataDropped <= r.dataDropped;

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
         BRAM_EN_G           => true,
         GEN_SYNC_FIFO_G     => false,
         FIFO_ADDR_WIDTH_G   => 9,
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
