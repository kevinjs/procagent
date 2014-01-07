import cpu
import mem
import net
import load
import util


if __name__=='__main__':
    cpu_info = cpu.CPUInfo()
    cpu_usage = cpu.CPUUsage()
    mem_info = mem.MemInfo()
    net_info = net.NetStat()
    load_info = load.LoadStat()

    util.print_list(cpu_info)
    util.print_list(cpu_usage)
    util.print_list(mem_info)
    util.print_list(net_info)
    util.print_list(load_info)
