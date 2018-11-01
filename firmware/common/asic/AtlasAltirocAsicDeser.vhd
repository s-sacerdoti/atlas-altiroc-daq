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
      -- Serial Interface
      deserClk        : in  sl;
      deserRst        : in  sl;
      deserSampleEdge : in  sl;  -- '0' = rising_edge, '1' = falling_edge          
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

   type StateType is (
      IDLE_S,
      START_S,
      DATA_S);

   type RegType is record
      dout     : sl;
      cnt      : natural range 0 to 18;
      shiftReg : slv(18 downto 0);
      seqCnt   : slv(12 downto 0);
      txMaster : AxiStreamMasterType;
      state    : StateType;
   end record RegType;
   constant REG_INIT_C : RegType := (
      dout     => '0',
      cnt      => 0,
      shiftReg => (others => '0'),
      seqCnt   => (others => '0'),
      txMaster => AXI_STREAM_MASTER_INIT_C,
      state    => IDLE_S);

   signal r   : RegType := REG_INIT_C;
   signal rin : RegType;

   signal txMaster : AxiStreamMasterType;
   signal txSlave  : AxiStreamSlaveType;

   signal Q1 : sl;
   signal Q2 : sl;

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

   comb : process (Q1, Q2, deserRst, deserSampleEdge, r, txSlave) is
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
      if (deserSampleEdge = '0') then
         v.dout := Q1;
      -- Else using falling_edge sample
      else
         v.dout := Q2;
      end if;

      -- State Machine
      case r.state is
         ----------------------------------------------------------------------
         when IDLE_S =>
            -- Check for first start bit
            if (r.dout = '1') then
               -- Next state
               v.state := START_S;
            end if;
         ----------------------------------------------------------------------
         when START_S =>
            -- Check for second start bit
            if (r.dout = '0') then
               -- Next state
               v.state := DATA_S;
            -- Else return back to IDLE (false start)
            else
               -- Next state
               v.state := IDLE_S;
            end if;
         ----------------------------------------------------------------------
         when DATA_S =>
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
            -- Update the shift register
            v.shiftReg := r.dout & r.shiftReg(18 downto 1);
            -- Check for last shift
            if (r.cnt = 18) then
               -- Reset the counter
               v.cnt := 0;
               -- Check if ready to move data
               if (v.txMaster.tValid = '0') then
                  -- Forward the data
                  v.txMaster.tValid              := '1';
                  v.txMaster.tData(31 downto 19) := r.seqCnt;
                  v.txMaster.tData(18 downto 0)  := v.shiftReg;
                  ssiSetUserSof(AXIS_CONFIG_C, v.txMaster, '1');  -- Tag as start of frame (SOF)
                  v.txMaster.tLast               := '1';  -- Tag as end of frame (EOF)
               end if;
               -- Increment the sequence counter
               v.seqCnt := r.seqCnt + 1;
               -- Next state
               v.state  := IDLE_S;
            else
               -- Increment the counter
               v.cnt := r.cnt + 1;
            end if;
      ----------------------------------------------------------------------
      end case;

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
