-------------------------------------------------------------------------------
-- File       : AtlasAltirocAsicShiftReg.vhd
-- Company    : SLAC National Accelerator Laboratory
-- Created    : 2018-09-07
-- Last update: 2018-11-20
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

entity AtlasAltirocAsicShiftReg is
   generic (
      TPD_G            : time     := 1 ns;
      SHIFT_REG_SIZE_G : positive := 16;
      CLK_PERIOD_G     : real     := 6.4E-9;   -- 156.25 MHz = 1/6.4E-9
      SCLK_PERIOD_G    : real     := 1.0E-6);  -- 1MHz = 1/1.0E-6    
   port (
      -- ASIC Ports
      srin            : out sl;
      rstb            : out sl;
      ck              : out sl;
      srout           : in  sl;
      -- AXI-Lite Interface (axilClk domain)
      axilClk         : in  sl;
      axilRst         : in  sl;
      axilReadMaster  : in  AxiLiteReadMasterType;
      axilReadSlave   : out AxiLiteReadSlaveType;
      axilWriteMaster : in  AxiLiteWriteMasterType;
      axilWriteSlave  : out AxiLiteWriteSlaveType);
end AtlasAltirocAsicShiftReg;

architecture mapping of AtlasAltirocAsicShiftReg is

   constant SCLK_HALF_PERIOD_C : positive := integer(SCLK_PERIOD_G / (2.0*CLK_PERIOD_G));

   constant WRD_SIZE_C : natural := (SHIFT_REG_SIZE_G/32)+1;

   type StateType is (
      IDLE_S,
      SHIFT_S,
      SAMPLE_S,
      DONE_S);

   type RegType is record
      rstL           : sl;
      sclk           : sl;
      data           : slv((32*WRD_SIZE_C) downto 0);
      shiftReg       : slv(SHIFT_REG_SIZE_G-1 downto 0);
      readback       : slv(SHIFT_REG_SIZE_G-1 downto 0);
      clkCnt         : natural range 0 to SCLK_HALF_PERIOD_C;
      cnt            : natural range 0 to SHIFT_REG_SIZE_G-1;
      axilReadSlave  : AxiLiteReadSlaveType;
      axilWriteSlave : AxiLiteWriteSlaveType;
      state          : StateType;
   end record;

   constant REG_INIT_C : RegType := (
      rstL           => '1',
      sclk           => '0',
      data           => (others => '0'),
      shiftReg       => (others => '0'),
      readback       => (others => '0'),
      clkCnt         => 0,
      cnt            => 0,
      axilReadSlave  => AXI_LITE_READ_SLAVE_INIT_C,
      axilWriteSlave => AXI_LITE_WRITE_SLAVE_INIT_C,
      state          => IDLE_S);

   signal r   : RegType := REG_INIT_C;
   signal rin : RegType;

   signal shiftIn : sl;
   signal rstL    : sl;

begin

   U_srout : entity work.InputBufferReg
      generic map (
         TPD_G => TPD_G)
      port map (
         C  => axilClk,
         I  => srout,
         Q1 => shiftIn);

   comb : process (axilReadMaster, axilRst, axilWriteMaster, r, shiftIn) is
      variable v             : RegType;
      variable axilStatus    : AxiLiteStatusType;
      variable axilWriteResp : slv(1 downto 0);
      variable axilReadResp  : slv(1 downto 0);
      variable wrIdx         : natural;
      variable rdIdx         : natural;

   begin
      -- Latch the current value
      v := r;

      -- Update the variables
      axilWriteResp := AXI_RESP_OK_C;
      axilReadResp  := AXI_RESP_OK_C;
      wrIdx         := conv_integer(axilWriteMaster.awaddr(11 downto 2));
      rdIdx         := conv_integer(axilReadMaster.araddr(11 downto 2));

      -- Determine the transaction type
      axiSlaveWaitTxn(axilWriteMaster, axilReadMaster, v.axilWriteSlave, v.axilReadSlave, axilStatus);

      -- State Machine      
      case (r.state) is
         ----------------------------------------------------------------------      
         when IDLE_S =>
            -- Check for a write request
            if (axilStatus.writeEnable = '1') then
               if (axilWriteMaster.awaddr(11 downto 0) = x"FFC") then
                  v.rstL := axilWriteMaster.wdata(0);
               else
                  v.data((32*wrIdx)+31 downto (32*wrIdx)) := axilWriteMaster.wdata;
                  -- Cache the data bus
                  v.shiftReg                              := v.data(SHIFT_REG_SIZE_G-1 downto 0);
                  -- Next state
                  v.state                                 := SAMPLE_S;
               end if;
               -- Send AXI-Lite response
               axiSlaveWriteResponse(v.axilWriteSlave, axilWriteResp);
            -- Check for a read request            
            elsif (axilStatus.readEnable = '1') then
               if (axilReadMaster.araddr(11 downto 0) = x"FFC") then
                  v.axilReadSlave.rdata(0) := r.rstL;
               else
                  v.axilReadSlave.rdata := r.data((32*rdIdx)+31 downto (32*rdIdx));
               end if;
               -- Send AXI-Lite Response
               axiSlaveReadResponse(v.axilReadSlave, axilReadResp);
            end if;
         ----------------------------------------------------------------------      
         when SAMPLE_S =>
            -- Wait half a clock period
            if (r.clkCnt = SCLK_HALF_PERIOD_C) then
               -- Reset the counter
               v.clkCnt   := 0;
               -- Set clock high
               v.sclk     := '1';
               -- Shift the output data
               v.readback := r.readback(SHIFT_REG_SIZE_G-1 downto 1) & shiftIn;
               -- Next state
               v.state    := SHIFT_S;
            else
               -- Increment the counter
               v.clkCnt := r.clkCnt + 1;
            end if;
         ----------------------------------------------------------------------      
         when SHIFT_S =>
            -- Wait half a clock period
            if (r.clkCnt = SCLK_HALF_PERIOD_C) then
               -- Reset the counter
               v.clkCnt   := 0;
               -- Set clock low
               v.sclk     := '0';
               -- Shift the output data
               v.shiftReg := r.shiftReg(SHIFT_REG_SIZE_G-2 downto 0) & '0';
               -- Check the shift counter
               if (r.cnt = (SHIFT_REG_SIZE_G-1)) then
                  -- Reset the counter
                  v.cnt   := 0;
                  -- Next state
                  v.state := DONE_S;
               else
                  -- Increment the counter
                  v.cnt   := r.cnt + 1;
                  -- Next state
                  v.state := SAMPLE_S;
               end if;
            else
               -- Increment the counter
               v.clkCnt := r.clkCnt + 1;
            end if;
         ----------------------------------------------------------------------      
         when DONE_S =>
            -- Wait half a clock period
            if (r.clkCnt = SCLK_HALF_PERIOD_C) then
               -- Reset the counter
               v.clkCnt                            := 0;
               ----------------------------------------------------------------      
               -- Appears to be a bug in the ASIC with feedback of the shift 
               -- register output to update the firmware's local v.data cache.  
               -- Commenting out this part of the code such that only the 
               -- software can update the firmware's local v.data cache.  
               ----------------------------------------------------------------      
               -- -- Update the data bus
               -- v.data(SHIFT_REG_SIZE_G-1 downto 0) := r.readback(SHIFT_REG_SIZE_G-1 downto 1) & shiftIn;
               ----------------------------------------------------------------      
               -- Next state
               v.state                             := IDLE_S;
            else
               -- Increment the counter
               v.clkCnt := r.clkCnt + 1;
            end if;
      ----------------------------------------------------------------------      
      end case;

      -- Reset
      if (axilRst = '1') then
         v := REG_INIT_C;
      end if;

      -- Register the variable for next clock cycle
      rin <= v;

      -- Outputs
      axilWriteSlave <= r.axilWriteSlave;
      axilReadSlave  <= r.axilReadSlave;
      rstL           <= r.rstL and not(axilRst);

   end process comb;

   seq : process (axilClk) is
   begin
      if (rising_edge(axilClk)) then
         r <= rin after TPD_G;
      end if;
   end process seq;

   U_srin : entity work.OutputBufferReg
      generic map (
         TPD_G => TPD_G)
      port map (
         C => axilClk,
         I => r.shiftReg(SHIFT_REG_SIZE_G-1),
         O => srin);

   U_rstb : entity work.OutputBufferReg
      generic map (
         TPD_G => TPD_G)
      port map (
         C => axilClk,
         I => rstL,
         O => rstb);

   U_ck : entity work.OutputBufferReg
      generic map (
         TPD_G => TPD_G)
      port map (
         C => axilClk,
         I => r.sclk,
         O => ck);

end mapping;
