#!/bin/bash
create -f clock.sv -o count_sec count_min count_hrs -or [5:0] [5:0] [5:0]
plug -f up_counter.sv -n Sec;plug -f up_counter.sv -n Min,plug -f up_counter.sv -n Hrs

#connect -i Sec -ip clk en reset clr count_max count -op clk en reset clr_sec count_max count_sec
#connect -i Min -ip clk en reset clr count_max count -op clk en reset clr_min count_max count_min
#connect -i Hr -ip clk en reset clr count_max count -op clk en reset clr_hrs count_max_hrs count_hrs
