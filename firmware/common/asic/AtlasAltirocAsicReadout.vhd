-------------------------------------------------------------------------------
-- File       : AtlasAltirocAsicReadout.vhd
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
use work.AxiLitePkg.all;
use work.AxiStreamPkg.all;
use work.SsiPkg.all;
use work.Pgp3Pkg.all;

entity AtlasAltirocAsicReadout is
   generic (
      TPD_G : time := 1 ns);
   port (
      -- Readout Ports
      renable         : out sl;         -- RENABLE
      rstbRead        : out sl;         -- RSTB_READ
      doutP           : in  sl;         -- DOUT_P
      doutN           : in  sl;         -- DOUT_N
      rdClkP          : out sl;         -- FPGA_CK_40_P
      rdClkN          : out sl;         -- FPGA_CK_40_M      
      -- Trigger Interface (clk160MHz domain)
      readoutStart    : in  sl;
      readoutBusy     : out sl;
      -- Probe Interface (clk160MHz domain)
      probeValid      : out sl;
      probeIbData     : out slv(739 downto 0);
      probeObData     : in  slv(739 downto 0);
      probeBusy       : in  sl;
      -- Streaming ASIC Data Interface (axilClk domain)
      axilClk         : in  sl;
      axilRst         : in  sl;
      mDataMaster     : out AxiStreamMasterType;
      mDataSlave      : in  AxiStreamSlaveType;
      -- AXI-Lite Interface (clk160MHz domain)
      clk160MHz       : in  sl;
      rst160MHz       : in  sl;
      axilReadMaster  : in  AxiLiteReadMasterType;
      axilReadSlave   : out AxiLiteReadSlaveType;
      axilWriteMaster : in  AxiLiteWriteMasterType;
      axilWriteSlave  : out AxiLiteWriteSlaveType);
end AtlasAltirocAsicReadout;

architecture rtl of AtlasAltirocAsicReadout is

   constant HDR_SIZE_C : positive := 2;

   constant AXIS_CONFIG_C : AxiStreamConfigType := ssiAxiStreamConfig(4);  -- 32-bit AXI stream interface

   type StateType is (
      IDLE_S,
      HDR_S,
      PROBE_CONFIG_S,
      PROBE_TO_RST_DLY_S,
      RST_S,
      RST_TO_RCK_DLY_S,
      RCK_HIGH_CYCLE_S,
      RCK_LOW_CYCLE_S,
      SEND_DATA_S);

   type RegType is record
      cntRst             : sl;
      invertRck          : sl;
      invertDout         : sl;
      txDataBitReverse   : sl;
      forceStart         : sl;
      sendData           : sl;
      tValid             : sl;
      enProbeWrite       : sl;
      testPattern        : sl;
      renable            : sl;
      rstbRead           : sl;
      rdClk              : sl;
      probeValid         : sl;
      probeIbData        : slv(740 downto 1);
      probeCache         : slv(740 downto 1);
      cnt                : slv(11 downto 0);
      probeToRstDly      : slv(11 downto 0);
      rstPulseWidth      : slv(11 downto 0);
      rstToReadDly       : slv(11 downto 0);
      rckHighWidth       : slv(11 downto 0);
      rckLowWidth        : slv(11 downto 0);
      seqCnt             : slv(31 downto 0);
      header             : Slv32Array(HDR_SIZE_C-1 downto 0);
      rdCnt              : slv(8 downto 0);
      rdSize             : slv(8 downto 0);
      startPix           : slv(4 downto 0);
      stopPix            : slv(4 downto 0);
      pixIndex           : slv(4 downto 0);
      bitCnt             : slv(7 downto 0);
      bitSize            : slv(7 downto 0);
      bitSizeFirst       : slv(7 downto 0);
      txData             : slv(20 downto 0);
      txDataDebug        : slv(20 downto 0);
      restoreProbeConfig : sl;
      txMaster           : AxiStreamMasterType;
      axilReadSlave      : AxiLiteReadSlaveType;
      axilWriteSlave     : AxiLiteWriteSlaveType;
      state              : StateType;
   end record RegType;
   constant REG_INIT_C : RegType := (
      cntRst             => '0',
      invertRck          => '0',
      invertDout         => '1',
      txDataBitReverse   => '0',
      forceStart         => '0',
      sendData           => '1',
      tValid             => '1',
      enProbeWrite       => '1',
      testPattern        => '0',
      renable            => '0',
      rstbRead           => '1',
      rdClk              => '0',
      probeValid         => '0',
      probeIbData        => (others => '0'),
      probeCache         => (others => '0'),
      cnt                => (others => '0'),
      probeToRstDly      => x"000",
      rstPulseWidth      => x"00f",
      rstToReadDly       => x"00f",
      rckHighWidth       => toSlv(3, 12),
      rckLowWidth        => toSlv(3, 12),
      seqCnt             => (others => '0'),
      header             => (others => (others => '0')),
      rdCnt              => (others => '0'),
      rdSize             => toSlv(399,9),
      startPix           => toSlv(0, 5),
      stopPix            => toSlv(24, 5),
      pixIndex           => toSlv(0, 5),
      bitCnt             => (others => '0'),
      bitSize            => toSlv(20, 8),
      bitSizeFirst       => toSlv(20, 8),
      txData             => (others => '0'),
      txDataDebug        => (others => '0'),
      restoreProbeConfig => '0',
      txMaster           => AXI_STREAM_MASTER_INIT_C,
      axilReadSlave      => AXI_LITE_READ_SLAVE_INIT_C,
      axilWriteSlave     => AXI_LITE_WRITE_SLAVE_INIT_C,
      state              => IDLE_S);

   signal r   : RegType := REG_INIT_C;
   signal rin : RegType;

   signal rdClk   : sl;
   signal dout    : sl;
   signal txSlave : AxiStreamSlaveType;

begin

   U_RegisteredInput : entity work.InputBufferReg
      generic map (
         TPD_G       => TPD_G,
         DIFF_PAIR_G => true)
      port map (
         C  => clk160MHz,
         I  => doutP,
         IB => doutN,
         Q1 => dout);

   comb : process (axilReadMaster, axilWriteMaster, dout, probeBusy,
                   probeObData, r, readoutStart, rst160MHz, txSlave) is
      variable v       : RegType;
      variable axilEp  : AxiLiteEndPointType;
      variable rdSize  : slv(8 downto 0);
      variable stopPix : slv(4 downto 0);
   begin
      -- Latch the current value
      v := r;

      -- Update local variables (in used in cased changed during readout)
      rdSize  := r.header(0)(20 downto 12);
      stopPix := r.header(0)(31 downto 27);

      -- Reset strobes
      v.probeValid := '0';
      v.cntRst     := '0';
      v.forceStart := '0';

      -- Check the flow control
      if txSlave.tReady = '1' then
         v.txMaster := AXI_STREAM_MASTER_INIT_C;
      end if;

      -- Check for counter reset
      if r.cntRst = '1' then
         v.seqCnt := (others => '0');
      end if;

      ----------------------------------------------------------------------      
      -- Determine the transaction type
      axiSlaveWaitTxn(axilEp, axilWriteMaster, axilReadMaster, v.axilWriteSlave, v.axilReadSlave);

      axiSlaveRegister (axilEp, x"00", 0, v.startPix);
      axiSlaveRegister (axilEp, x"04", 0, v.stopPix);
      axiSlaveRegister (axilEp, x"08", 0, v.rdSize);
      axiSlaveRegisterR(axilEp, x"0C", 0, r.seqCnt);
      axiSlaveRegister (axilEp, x"10", 0, v.probeToRstDly);
      axiSlaveRegister (axilEp, x"14", 0, v.rstPulseWidth);
      axiSlaveRegister (axilEp, x"18", 0, v.rstToReadDly);
      axiSlaveRegister (axilEp, x"1C", 0, v.rckHighWidth);
      axiSlaveRegister (axilEp, x"20", 0, v.rckLowWidth);
      axiSlaveRegister (axilEp, x"24", 0, v.restoreProbeConfig);
      axiSlaveRegisterR(axilEp, x"28", 0, r.bitSize);
      axiSlaveRegisterR(axilEp, x"28", 8, r.bitSizeFirst);
      axiSlaveRegister (axilEp, x"2C", 0, v.testPattern);
      axiSlaveRegister (axilEp, x"30", 0, v.sendData);
      axiSlaveRegister (axilEp, x"34", 0, v.enProbeWrite);
      axiSlaveRegisterR(axilEp, x"38", 0, r.txDataDebug);
      axiSlaveRegister (axilEp, x"3C", 0, v.invertDout);
      axiSlaveRegister (axilEp, x"3C", 1, v.invertRck);
      axiSlaveRegister (axilEp, x"40", 0, v.txDataBitReverse);

      axiSlaveRegister (axilEp, x"F8", 0, v.forceStart);
      axiSlaveRegister (axilEp, x"FC", 0, v.cntRst);

      -- Closeout the transaction
      axiSlaveDefault(axilEp, v.axilWriteSlave, v.axilReadSlave, AXI_RESP_DECERR_C);
      ----------------------------------------------------------------------      

      -- State Machine      
      case (r.state) is
         ----------------------------------------------------------------------      
         when IDLE_S =>
            -- Cache the current probe value
            v.probeCache := probeObData;

            -- Check for trigger
            if (readoutStart = '1') or (r.forceStart = '1') then

               --------------------------------------------------------------
               --                   Generate the header                    --
               --------------------------------------------------------------               
               -- HDR[0]: Format Version, start and stop
               v.header(0)(11 downto 0)  := x"001";  -- Version = 0x1   
               v.header(0)(21 downto 12) := '0' & r.rdSize;
               v.header(0)(26 downto 22) := r.startPix;
               v.header(0)(31 downto 27) := r.stopPix;
               -- HDR[1]: Sequence counter
               v.header(1)               := r.seqCnt;
               --------------------------------------------------------------               

               -- Set the flag
               v.renable  := '1';
               v.tValid   := r.sendData;
               -- Increment the counter
               v.seqCnt   := r.seqCnt + 1;
               -- Set the index pointer
               v.pixIndex := r.startPix;
               -- Next state
               v.state    := HDR_S;
            end if;
         ----------------------------------------------------------------------      
         when HDR_S =>
            -- Check if ready to move data
            if (v.txMaster.tValid = '0') then
               -- Move data
               v.txMaster.tValid             := r.tValid;
               v.txMaster.tData(31 downto 0) := r.header(conv_integer(r.cnt));
               -- Increment the counter
               v.cnt                         := r.cnt + 1;
               -- Check if SOF
               if (r.cnt = 0) then
                  ssiSetUserSof(AXIS_CONFIG_C, v.txMaster, '1');
               end if;
               -- Check the counter size
               if (r.cnt = (HDR_SIZE_C-1)) then
                  -- Reset the counter
                  v.cnt   := (others => '0');
                  -- Next state
                  v.state := PROBE_CONFIG_S;
               end if;
            end if;
         ----------------------------------------------------------------------      
         when PROBE_CONFIG_S =>
            -- Check if need to start the transaction
            if (r.cnt = 0) then

               -- Check if probe module ready 
               if (probeBusy = '0') then

                  -- Configure the probe bus
                  v.probeValid := r.enProbeWrite;

                  -- Reset all the probe values to default 
                  v.probeIbData(740 downto 1) := (others => '0');

                  -- Check the pixel range
                  if (r.pixIndex < 5) then  -- Check for PIX[4:0] range
                     -- EN_dout<0:4> = 0x1 and en_probe_dig<0:4> = EN_dout<0:4>
                     v.probeIbData(15 downto 11) := "00001";
                     v.probeIbData(10 downto 6)  := "00001";

                  elsif (r.pixIndex < 10) then  -- Check for PIX[9:5] range
                     -- EN_dout<0:4> = 0x2 and en_probe_dig<0:4> = EN_dout<0:4>
                     v.probeIbData(15 downto 11) := "00010";
                     v.probeIbData(10 downto 6)  := "00010";

                  elsif (r.pixIndex < 15) then  -- Check for PIX[14:10] range
                     -- EN_dout<0:4> = 0x4 and en_probe_dig<0:4> = EN_dout<0:4>
                     v.probeIbData(15 downto 11) := "00100";
                     v.probeIbData(10 downto 6)  := "00100";

                  elsif (r.pixIndex < 20) then  -- Check for PIX[19:15] range
                     -- EN_dout<0:4> = 0x8 and en_probe_dig<0:4> = EN_dout<0:4>
                     v.probeIbData(15 downto 11) := "01000";
                     v.probeIbData(10 downto 6)  := "01000";

                  else                  -- Check for PIX[24:20] range
                     -- EN_dout<0:4> = 0x10 and en_probe_dig<0:4> = EN_dout<0:4>
                     v.probeIbData(15 downto 11) := "10000";
                     v.probeIbData(10 downto 6)  := "10000";
                  end if;

                  -- Set probe_dig_out_disc[pixIndex] = 0x1
                  v.probeIbData(18+(29*conv_integer(r.pixIndex))) := '1';

                  -- Set toa_busy[pixIndex] = 0x1
                  v.probeIbData(40+(29*conv_integer(r.pixIndex))) := '1';

                  -- Set en_read[pixIndex] = 0x1
                  v.probeIbData(44+(29*conv_integer(r.pixIndex))) := '1';

                  -- Increment the counter
                  v.cnt := r.cnt + 1;

               end if;

            -- Check the counter size
            elsif (r.cnt = 255) then
               -- Check if transfer completed
               if (probeBusy = '0') then
                  -- Reset the counter
                  v.cnt   := (others => '0');
                  -- Next state
                  v.state := PROBE_TO_RST_DLY_S;
               end if;
            else
               -- Increment the counter
               v.cnt := r.cnt + 1;
            end if;
         ----------------------------------------------------------------------      
         when PROBE_TO_RST_DLY_S =>
            -- Increment the counter
            v.cnt := r.cnt + 1;
            -- Check the counter size
            if (r.cnt = r.probeToRstDly) then
               -- Reset the counter
               v.cnt   := (others => '0');
               -- Next state
               v.state := RST_S;
            end if;
         ----------------------------------------------------------------------      
         when RST_S =>
            -- Set the flag
            v.rstbRead := '0';
            -- Increment the counter
            v.cnt      := r.cnt + 1;
            -- Check the counter size
            if (r.cnt = r.rstPulseWidth) then
               -- Reset the counter
               v.cnt   := (others => '0');
               -- Next state
               v.state := RST_TO_RCK_DLY_S;
            end if;
         ----------------------------------------------------------------------      
         when RST_TO_RCK_DLY_S =>
            -- Set the flag
            v.rstbRead := '1';
            -- Increment the counter
            v.cnt      := r.cnt + 1;
            -- Check the counter size
            if (r.cnt = r.rstToReadDly) then
               -- Reset the counter
               v.cnt   := (others => '0');
               -- Next state
               v.state := RCK_HIGH_CYCLE_S;
            end if;
         ----------------------------------------------------------------------      
         when RCK_HIGH_CYCLE_S =>
            -- Set the flag
            v.rdClk := '1';
            -- Increment the counter
            v.cnt   := r.cnt + 1;
            -- Check the counter size
            if (r.cnt = r.rckHighWidth) then
               -- Reset the counter
               v.cnt   := (others => '0');
               -- Next state
               v.state := RCK_LOW_CYCLE_S;
            end if;
         ----------------------------------------------------------------------      
         when RCK_LOW_CYCLE_S =>
            -- Set the flag
            v.rdClk := '0';
            -- Increment the counter
            v.cnt   := r.cnt + 1;
            -- Check the counter size
            if (r.cnt = r.rckLowWidth) then

               -- Reset the counter
               v.cnt := (others => '0');

               -- Load the shift register
               if (r.invertDout = '0') then
                  v.txData := dout & r.txData(20 downto 1);
               else
                  v.txData := not(dout) & r.txData(20 downto 1);
               end if;

               -- Check the counter
               if (r.rdCnt = 0 and r.bitCnt = r.bitSizeFirst) or (r.rdCnt /= 0 and r.bitCnt = r.bitSize) then
                  -- Reset the counter
                  v.bitCnt := (others => '0');
                  -- -- Check for bit reversal
                  -- if (r.txDataBitReverse = '1') then
                     -- v.txData := bitReverse(v.txData);
                  -- end if;
                  -- Next state
                  v.state := SEND_DATA_S;
               else
                  -- Increment the counter
                  v.bitCnt := r.bitCnt + 1;
                  -- Next state
                  v.state  := RCK_HIGH_CYCLE_S;
               end if;

            end if;
         ----------------------------------------------------------------------      
         when SEND_DATA_S =>
            -- Check if ready to move data
            if (v.txMaster.tValid = '0') then

               -- Reset the output data bus
               v.txMaster.tData := (others => '0');

               -- Forward the data
               v.txMaster.tValid              := r.tValid;
               v.txMaster.tData(20 downto 0)  := r.txData;
               v.txMaster.tData(28 downto 24) := r.pixIndex;

               -- Check for test pattern insertion
               if (r.testPattern = '1') then
                  v.txMaster.tData(1 downto 0)  := "01";  -- SOF
                  v.txMaster.tData(20 downto 2) := (others => '0');
               end if;

               -- Latch the value for debugging
               v.txDataDebug := r.txData;

               -- Reset the shift register
               v.txData := (others => '0');

               -- Increment the counter
               v.rdCnt := r.rdCnt + 1;

               -- Check the read size
               if (r.rdCnt = rdSize) then

                  -- Reset the counter
                  v.rdCnt := (others => '0');

                  -- Increment the counter
                  v.pixIndex := r.pixIndex + 1;

                  -- Check the pixel index
                  if (r.pixIndex >= stopPix) then
                     -- Set the EOF flag
                     v.txMaster.tLast := '1';
                     -- Restore the probe bus
                     v.probeValid     := r.restoreProbeConfig;
                     v.probeIbData    := r.probeCache;
                     -- Reset the flag
                     v.renable        := '0';
                     -- Next state
                     v.state          := IDLE_S;
                  else
                     -- Next state
                     v.state := PROBE_CONFIG_S;
                  end if;

               else
                  -- Next state
                  v.state := RCK_HIGH_CYCLE_S;
               end if;

            end if;
      ----------------------------------------------------------------------      
      end case;

      -- Outputs
      axilWriteSlave <= r.axilWriteSlave;
      axilReadSlave  <= r.axilReadSlave;
      readoutBusy    <= r.renable;
      probeValid     <= r.probeValid;
      probeIbData    <= r.probeIbData;

      if (r.invertRck = '0') then
         rdClk <= r.rdClk;
      else
         rdClk <= not(r.rdClk);
      end if;

      -- Reset
      if (rst160MHz = '1') then
         v                    := REG_INIT_C;
         -- Don't touch register configurations
         v.startPix           := r.startPix;
         v.stopPix            := r.stopPix;
         v.rdSize             := r.rdSize;
         v.probeToRstDly      := r.probeToRstDly;
         v.rstPulseWidth      := r.rstPulseWidth;
         v.rstToReadDly       := r.rstToReadDly;
         v.rckHighWidth       := r.rckHighWidth;
         v.rckLowWidth        := r.rckLowWidth;
         v.restoreProbeConfig := r.restoreProbeConfig;
         v.bitSize            := r.bitSize;
         v.bitSizeFirst       := r.bitSizeFirst;
         v.testPattern        := r.testPattern;
         v.sendData           := r.sendData;
         v.enProbeWrite       := r.enProbeWrite;
         v.invertDout         := r.invertDout;
         v.invertRck          := r.invertRck;
         v.txDataBitReverse   := r.txDataBitReverse;
      end if;


      -- Register the variable for next clock cycle
      rin <= v;

   end process comb;

   seq : process (clk160MHz) is
   begin
      if rising_edge(clk160MHz) then
         r <= rin after TPD_G;
      end if;
   end process seq;

   U_renable : entity work.OutputBufferReg
      generic map (
         TPD_G => TPD_G)
      port map (
         C => clk160MHz,
         I => r.renable,
         O => renable);

   U_rstbRead : entity work.OutputBufferReg
      generic map (
         TPD_G => TPD_G)
      port map (
         C => clk160MHz,
         I => r.rstbRead,
         O => rstbRead);

   U_rdClk : entity work.OutputBufferReg
      generic map (
         TPD_G       => TPD_G,
         DIFF_PAIR_G => true)
      port map (
         C  => clk160MHz,
         I  => rdClk,
         O  => rdClkP,
         OB => rdClkN);

   FIFO_TX : entity work.AxiStreamFifoV2
      generic map (
         -- General Configurations
         TPD_G               => TPD_G,
         SLAVE_READY_EN_G    => true,
         VALID_THOLD_G       => 256,
         VALID_BURST_MODE_G  => true,
         -- FIFO configurations
         BRAM_EN_G           => true,
         GEN_SYNC_FIFO_G     => false,
         FIFO_ADDR_WIDTH_G   => 9,
         -- AXI Stream Port Configurations
         SLAVE_AXI_CONFIG_G  => AXIS_CONFIG_C,
         MASTER_AXI_CONFIG_G => PGP3_AXIS_CONFIG_C)
      port map (
         -- Slave Port
         sAxisClk    => clk160MHz,
         sAxisRst    => rst160MHz,
         sAxisMaster => r.txMaster,
         sAxisSlave  => txSlave,
         -- Master Port
         mAxisClk    => axilClk,
         mAxisRst    => axilRst,
         mAxisMaster => mDataMaster,
         mAxisSlave  => mDataSlave);

end rtl;
