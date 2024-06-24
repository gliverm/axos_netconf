"""
Prototype for SSH protocol communication

Design Notes:
* asyncssh to outsource thread mgmt and future looking
* coroutine: a method that can be entered, exited, and resumed at
    many different points
* Use of await
* coroutine used for concurrency - cooperative multitasking
* NOT preemptive multitasking inolving OS
* coroutine lighter than a thread
"""

import asyncio
import asyncssh
import time
import sys

# import logging

from app.lib.protocol_base.ssh.errors import SshAuthenticationError


class SshClient:
    """Asyncssh used for SSH connections"""

    def __init__(self, hostname, username, password, port=22, timeout=30):
        """Initialize the SSHClient object"""
        self.hostname = hostname
        self.port = port
        self.username = username
        self.password = password
        self.timeout = timeout
        self.conn = None

    async def __aenter__(self):
        """Context manager entry"""
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        await self.close()

    async def connect(self):
        """Connect to the device"""
        try:
            self.conn = await asyncssh.connect(
                host=self.hostname,
                port=self.port,
                username=self.username,
                password=self.password,
                known_hosts=None,  # Disable host key checking
                connect_timeout=self.timeout,
                login_timeout=self.timeout,
            )
        except asyncssh.misc.PermissionDenied as err:
            raise SshAuthenticationError(
                f"Failed to connect to {self.hostname}:{self.port}:{err}"
            ) from err

    async def send_command_and_print_output(self, command):
        """Run command and print the output to stdout returning result data.
        Intended for single command use
        Each line of the command's output is printed in real-time.
        Each command is run in a separate process/session (aka login for each command)
        Elapsed time is time to run command and print output.
        Line count includes all printed lines including blank lines
        """
        if self.conn is None:
            await self.connect()

        start_time = time.perf_counter()
        # create_process is a coroutine wrapper around create_session
        process = await self.conn.create_process(
            command, term_type="xterm", encoding="utf-8"
        )
        # Read and print each line of the command's output in real-time
        line_count = 0
        async for line in process.stdout:
            line_count += 1
            print(line, end="")

        await process.wait_closed()
        elapsed_time = time.perf_counter() - start_time
        return {"elapsed_time": elapsed_time, "line_count": line_count}

    async def start_shell(self):
        if self.conn is None:
            await self.connect()

        await self.conn.run(
            term_type="xterm",
            stdin=sys.stdin,
            stdout=sys.stdout,
            stderr=sys.stderr,
        )

    async def close(self):
        """Close the connection""" ""
        if self.conn is not None:
            self.conn.close()
            await self.conn.wait_closed()
            self.conn = None


async def main():
    """Main entry point to test out the SSHClient class"""

    # Note: IF you use a hostname vs an IP there could be some delay due to
    # DNS resolution. Behavior observed using Mac via VPN.

    # hostname = "cf2-gliverm.calix.local"  #cafe machine
    # hostname = "10.136.0.154"
    # username = "cafetest"
    # password = "cafetest"
    # command = "ls"

    # Note to self: can't use async/await outside of a coroutine
    try:
        async with SshClient(hostname, username, password) as ssh_client:
            # Example of running a single command
            print(f"command: {command}")
            rslt_data = await ssh_client.send_command_and_print_output(command)
            print(f'elapsed_time: {rslt_data["elapsed_time"]}')
            print(f'line_count: {rslt_data["line_count"]}')

            # Example of starting an interactive shell
            # await ssh_client.start_shell()
            # asyncio.get_event_loop().run_until_complete(start_shell())

    except SshAuthenticationError as err:
        print(f"Error: {err}")


if __name__ == "__main__":
    asyncio.run(main())
    print("stop")


# ------------------------------
# Boneyard

# # Enable this on debug request
# asyncssh.logging.set_debug_level(2)
# asyncssh.logging.set_log_level(logging.DEBUG)
# asyncssh.logging.set_sftp_log_level(logging.DEBUG)
# logging.basicConfig(
#     level=logging.DEBUG, format="%(asctime)s %(levelname)-8s [%(name)s] %(message)s"
# )


# async def run_command_and_print_output(hostname, username, password, command, timeout=30):
#     """ Run command and print the output to stdout
#     """

#     async with asyncssh.connect(
#         host=hostname,
#         username=username,
#         password=password,
#         known_hosts=None,  # Disable host key checking
#         client_keys=None,  # Disable client key negotiation
#         connect_timeout=timeout,
#         login_timeout=timeout,
#     ) as conn:
#         # term_type needed so output is like what is on a terminal
#         process = await conn.create_process(
#             command, term_type="xterm", encoding="utf-8"
#         )

#         # Read and print each line of the command's output in real-time
#         async for line in process.stdout:
#             print(line, end="")

#         await process.wait_closed()

# asyncio.run(run_command_and_print_output(hostname, username, password, command))

# async def start_server(self):

#     await self.conn.run(
#         term_type="xterm",
#         stdin=sys.stdin,
#         stdout=sys.stdout,
#         stderr=sys.stderr,
#     )

# async def start_shell(self):
#     if self.conn is None:
#         await self.connect()

#     await self.conn.wait_until_ready()

#     process = await self.conn.create_process(
#         term_type="xterm",
#         term_size=(80, 24),
#         encoding="utf-8"
#     )

#     await process.stdout.drain()

#     while True:
#         user_input = input()
#         if user_input.lower() == "exit":
#             process.stdinwrite.eof()
#             await process.wait.closed()
#             break
#         process.stdinwrite(user_input + '\n')
#         await process.stdin.drain()
