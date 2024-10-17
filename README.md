# SRX PBA Utility MIB
sample script for loading basic PBA stats to  SNMP Utility MIB. 
Prior Junos release 23.4 no PBA stats exist in MIB.

version 0.10

NAT pool specific and totals also taking into account chassis cluster specifics:
```
jnxUtilCounter64Value."pba_blocks_pool-1_total" = 5544
jnxUtilCounter64Value."pba_blocks_pool-1_total_node" = 2772
jnxUtilCounter64Value."pba_blocks_pool-1_used" = 0
jnxUtilCounter64Value."pba_blocks_pool-1_used_perc" = 0
jnxUtilCounter64Value."pba_blocks_pool-1_used_perc_node" = 0
jnxUtilCounter64Value."pba_blocks_total" = 5544
jnxUtilCounter64Value."pba_blocks_total_node" = 2772
jnxUtilCounter64Value."pba_blocks_used" = 0
jnxUtilCounter64Value."pba_blocks_used_perc" = 0
jnxUtilCounter64Value."pba_blocks_used_perc_node" = 0
```


For initial manual execution copy pba-umib.py to:

`/var/db/scripts/op/`


And adjust **PBA_NAT_POOLS** list and **CHASSIS_CLUSTER** variables.


Junos settings for manual execution (preferably in a Junos group):
```
set system scripts op file pba-umib.py command pba-umib
set system scripts language python3
```


Then on Junos CLI run:

`op pba-umib`


To list on-box utility mib use:

`show snmp mib walk jnxUtil ascii`


For timed execution copy/hardlink pba-umib.py to:

`/var/db/scripts/event/`


Sample junos settings for scheduled execution (preferably in a Junos group):
```
set system login user python-script-user class super-user
set event-options generate-event two_minutes time-interval 120
set event-options policy pba-umib events two_minutes
set event-options policy pba-umib then event-script pba-umib.py
set event-options event-script file pba-umib.py python-script-user python-script-user
```


to avoid CSCRIPT_SECURITY_WARNING event log about unsigned script:

```
set event-options event-script file pba-umib.py checksum sha-256 + output from: % sha256 pba-umib.py
set system scripts op file pba-umib.py checksum sha-256
