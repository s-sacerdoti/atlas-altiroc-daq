alias batch_1100='python scripts/DevGui.py --ip $fpga_ab $fpga_ad --userYaml config/asic_config_B13_master_ch10DAC430_scope.yml config/asic_config_B18_slave_ch5DAC420.yml --liveDisplay True --refClkSel ExtSmaClk ExtSmaClk'
alias batch_1101='python scripts/DevGui.py --ip $fpga_ab $fpga_ad --userYaml config/asic_config_B13_master_ch10DAC450_scope.yml config/asic_config_B18_slave_ch5DAC420.yml --liveDisplay True --refClkSel ExtSmaClk ExtSmaClk'
alias batch_1200='python scripts/DevGui.py --ip $fpga_ab $fpga_ad --userYaml config/asic_config_B13_master_ch13DAC430_scope.yml config/asic_config_B18_slave_ch5DAC420.yml --liveDisplay True --refClkSel ExtSmaClk ExtSmaClk'
alias batch_1201='python scripts/DevGui.py --ip $fpga_ab $fpga_ad --userYaml config/asic_config_B13_master_ch13DAC450_scope.yml config/asic_config_B18_slave_ch5DAC420.yml --liveDisplay True --refClkSel ExtSmaClk ExtSmaClk'

alias ch_dac='python scripts/DevGui.py --ip $fpga_ab $fpga_ad --userYaml config/asic_config_B13_master_oneCH.yml config/asic_config_B18_slave_allON.yml --liveDisplay True --refClkSel ExtSmaClk ExtSmaClk'
