def test_loop(pause, allow_to_pause):
    for pixel_number in _pixel_range:
        print('Enabling pixel '+str(pixel_number))
        top.Fpga[0].Asic.SlowControl.EN_ck_SRAM[pixel_number].set(0x1)
        top.Fpga[0].Asic.SlowControl.disable_pa[pixel_number].set(0x0)
        top.Fpga[0].Asic.SlowControl.ON_discri[pixel_number].set(0x1)
        top.Fpga[0].Asic.Readout.StartPix = pixel_number
        top.Fpga[0].Asic.Readout.LastPix = pixel_number

        threshold_value = _threshold_value_range.start
        while threshold_value < _threshold_value_range.stop
            filename = 'ThresholdScanData/data_thresholdScan_'+str(pixel_number)+'_'+str(threshold_value)+'.dat'
            try: os.remove(filename)
            except OSError: pass

            print('changing DAC10bit to ' + str(threshold_value))
            top.Fpga[0].Asic.SlowControl.DAC10bit = threshold_value
            top.dataWriter._writer.open(filename)
            top.Fpga[0].Asic.Trig.EnableReadout = 1

            print('File ' + filename + ' open, readout enabled, waiting for frames...')
            testing_was_paused = False
            while top.dataWriter.getFrameCount() < _frames_to_record: allow_to_pause(pause)
                time.sleep(1)
                if pause[0]:
                    testing_was_paused = True
                    while pause[0]: time.sleep(0.5)
                
            top.Fpga[0].Asic.Trig.EnableReadout = 0
            top.dataWriter._writer.close()

            if testing_was_paused:
                backup_filename = 'ThresholdScanData/incomplete_data_thresholdScan_'+str(pixel_number)+'_'+str(threshold_value)+'.dat'
                print('Testing unpaused. Backing up incomplete dat file to ' + filename)
                os.rename(filename, backup_filename)
                print('Redoing iteration: ' + str(threshold_value))
            else:
                print('Frames recieved. Readout disabled and file closed')
                threshold_value += _threshold_value_range.step

        print('Disabling pixel ' + str(pixel_number))
        top.Fpga[0].Asic.SlowControl.EN_ck_SRAM[pixel_number].set(0x0)
        top.Fpga[0].Asic.SlowControl.disable_pa[pixel_number].set(0x1)
        top.Fpga[0].Asic.SlowControl.ON_discri[pixel_number].set(0x0)
