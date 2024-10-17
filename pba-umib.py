PBA_NAT_POOLS = ["pool-1", "pool-2"]
CHASSIS_CLUSTER = False

from jnpr.junos import Device
from math import ceil


def is_aa_cluster(dev):
    """checks if the device is default A/A operational mode (practically dual-AP) chassis cluster
    A/P is explicit set chassis cluster redundancy-mode active-backup"""
    rpc_output = dev.rpc.get_chassis_cluster_detail_information()
    if rpc_output.findall(".//operational")[0].text == "active-active":
        return True
    else:
        return False


def set_mib(instance, object_value):
    """set MIB objects"""
    dev.rpc.request_snmp_utility_mib_set(
        object_type="counter64", instance=instance, object_value=str(object_value)
    )


with Device() as dev:
    """retrieve PBA number of used and total blocks for specific pools and total"""
    pba_blocks_total = 0
    pba_blocks_used = 0

    if CHASSIS_CLUSTER:
        aa_cluster = is_aa_cluster(dev)
    else:
        aa_cluster = False

    for pba_nat_pool in PBA_NAT_POOLS:
        result = dev.rpc.retrieve_source_nat_pool_information(
            normalize=True, pool_name=pba_nat_pool
        )
        pool_pba_blocks_total = result.findall(".//source-pool-blk-total")[0].text
        pool_pba_blocks_used = result.findall(".//source-pool-blk-used")[0].text

        # jnxUtilCounter64Value."pba_blocks_pool-1_total" = 4032
        snmp_counter_name = "pba_blocks_" + pba_nat_pool + "_total"
        set_mib(snmp_counter_name, pool_pba_blocks_total)

        # jnxUtilCounter64Value."pba_blocks_pool-1_used" = 292
        snmp_counter_name = "pba_blocks_" + pba_nat_pool + "_used"
        set_mib(snmp_counter_name, pool_pba_blocks_used)

        # jnxUtilCounter64Value."pba_blocks_pool-1_used_perc" = 8

        pba_pool_used_perc = (
            int(pool_pba_blocks_used) / int(pool_pba_blocks_total)
        ) * 100
        snmp_counter_name = "pba_blocks_" + pba_nat_pool + "_used_perc"
        set_mib(snmp_counter_name, ceil(pba_pool_used_perc))

        if aa_cluster:
            # jnxUtilCounter64Value."pba_blocks_pool-1_total_node" = 2772
            snmp_counter_name = "pba_blocks_" + pba_nat_pool + "_total_node"
            set_mib(snmp_counter_name, (int(pool_pba_blocks_total) // 2))

            # jnxUtilCounter64Value."pba_blocks_pool-1_used_perc_node" = 0
            pba_pool_used_perc = (
                int(pool_pba_blocks_used) / (int(pool_pba_blocks_total) // 2)
            ) * 100
            snmp_counter_name = "pba_blocks_" + pba_nat_pool + "_used_perc_node"
            set_mib(snmp_counter_name, ceil(pba_pool_used_perc))

        pba_blocks_total += int(pool_pba_blocks_total)
        pba_blocks_used += int(pool_pba_blocks_used)

    # jnxUtilCounter64Value."pba_blocks_total" = 4032
    set_mib("pba_blocks_total", pba_blocks_total)
    # jnxUtilCounter64Value."pba_blocks_used" = 292
    set_mib("pba_blocks_used", pba_blocks_used)
    # jnxUtilCounter64Value."pba_blocks_used_perc" = 8
    pba_blocks_used_perc = (int(pba_blocks_used) / int(pba_blocks_total)) * 100
    set_mib("pba_blocks_used_perc", ceil(pba_blocks_used_perc))

    if aa_cluster:
        # jnxUtilCounter64Value."pba_blocks_total_node" = 2772
        set_mib("pba_blocks_total_node", pba_blocks_total // 2)
        # jnxUtilCounter64Value."pba_blocks_used_perc_node" = 0
        pba_blocks_used_perc = (
            int(pba_blocks_used) / (int(pba_blocks_total) // 2)
        ) * 100
        set_mib("pba_blocks_used_perc_node", ceil(pba_blocks_used_perc))
