#!/usr/bin/python3

import asyncio;
from p3_network_library import *;
import aiofiles;
import aiocsv;
import re;

async def recover_errdisable_ports(network_device_details_dict):
    async with ssh(network_device_details_dict) as connection:
        command_results_str = await connection.exec_sequence_of_commands(("enable:",f"{network_device_details_dict['password']}:#", "show interfaces | include GigabitEthernet0/3"), 1);
        if not re.search(r"GigabitEthernet0/3 is up, line protocol is up", command_results_str):
            await connection.exec_sequence_of_commands(("configure terminal:)#","interface GigabitEthernet0/3:)#", "no shutdown", "end"), 1);
            return "with change";
        else:
            return "without change";
        
async def main(tasks=list(), workers=list()):
    async with aiofiles.open("/home/adm1n/recover_errdisable_ports/hosts") as file:
        async for network_device_details_dict in aiocsv.AsyncDictReader(file):
            tasks.append(network_device_details_dict);
    for task in tasks:
        workers.append(asyncio.Task(recover_errdisable_ports(task)));
    for network_device_details_dict, result in zip(tasks, await asyncio.gather(*workers, return_exceptions=True)):
        async with aiofiles.open("/tmp/recover_errdisable_ports.log", "a") as file:
            if isinstance(result, Exception):
                await file.write(f"[{network_device_details_dict['hostname']} - {time_now()}] failed - {result}\n");
            else:
                await file.write(f"[{network_device_details_dict['hostname']} - {time_now()}] completed - {result}\n");
        
if "__main__" in __name__:
    asyncio.run(main());
    