import os
import subprocess
import threading
import queue
import time
from typing import Optional

import pyte


class DockerShell:
    def __init__(
        self,
        image: str = "ctf-agent-workenv",
        command: str = "/bin/bash",
        docker_path: str = "docker",
        read_chunk: int = 1024,
        encoding: str = "utf-8",
        env: Optional[dict] = None,
        mounts: Optional[list[str]] = None,
    ):
        """
        初始化

        :param image: image name
        :type image: str
        :param command: command to run in the container
        :type command: str
        :param docker_path: path to the docker executable
        :type docker_path: str
        :param read_chunk: number of bytes to read at a time from the pty
        :type read_chunk: int
        :param encoding: encoding used for decoding bytes to string
        :type encoding: str
        :param env: environment variables to set in the container
        :type env: Optional[dict]
        :param mounts: list of docker -v specifications, e.g. ['/host/path:/container/path:ro']
        """
        self.image = image
        self.command = command
        self.docker_path = docker_path
        self.master_fd: Optional[int] = None
        self.proc: Optional[subprocess.Popen] = None
        self._read_q: "queue.Queue[bytes]" = queue.Queue()
        self._reader_thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        self.read_chunk = read_chunk
        self.encoding = encoding
        self.env = env or {}
        self.mounts = mounts or []

    def start(self, timeout: Optional[float] = 10.0) -> None:
        """Create pty, start `docker run -it` with slave attached, start reader."""
        if self.proc is not None:
            raise RuntimeError("DockerShell already started")

        master_fd, slave_fd = os.openpty()
        self.master_fd = master_fd

        # Build docker run command; inject environment variables if provided
        cmd = [self.docker_path, "run", "--rm", "-i", "-t"]
        for k, v in (self.env or {}).items():
            cmd += ["-e", f"{k}={v}"]
        # Add volume mounts (binds). Each entry should be a docker -v spec string
        for m in self.mounts or []:
            cmd += ["-v", m]
        cmd += [self.image, self.command]

        # Prepare mounts: expand env vars for host paths
        processed_mounts = []
        for m in self.mounts or []:
            # If mount is like '/host/path:/container/path[:opts]', expand host part
            if ":" in m:
                host, rest = m.split(":", 1)
                host_expanded = os.path.expandvars(host)
                host_expanded = os.path.abspath(host_expanded)
                processed_mounts.append(host_expanded + ":" + rest)
            else:
                processed_mounts.append(os.path.expandvars(m))

        # Update cmd with processed mounts (replace any previous mounts added)
        # Rebuild base cmd
        base_cmd = [self.docker_path, "run", "--rm", "-i", "-t"]
        for k, v in (self.env or {}).items():
            base_cmd += ["-e", f"{k}={v}"]
        for m in processed_mounts:
            base_cmd += ["-v", m]
        base_cmd += [self.image, self.command]

        # Start process with slave fd as its std{in,out,err}.
        # Pass the slave_fd in pass_fds so it is not closed by the child when close_fds=True.
        self.proc = subprocess.Popen(
            base_cmd,
            stdin=slave_fd,
            stdout=slave_fd,
            stderr=slave_fd,
            close_fds=True,
            pass_fds=(slave_fd,),
        )

        # Parent no longer needs slave fd
        try:
            os.close(slave_fd)
        except Exception:
            pass

        # Start reader thread reading from master fd
        self._stop_event.clear()
        self._reader_thread = threading.Thread(target=self._reader_loop, daemon=True)
        self._reader_thread.start()

        # small delay to let process initialize
        if timeout:
            start = time.time()
            while time.time() - start < timeout:
                if self.proc.poll() is None:
                    break

    def _reader_loop(self):
        if self.master_fd is None:
            return
        fd = self.master_fd
        try:
            while not self._stop_event.is_set():
                try:
                    data = os.read(fd, self.read_chunk)
                except OSError:
                    break
                if not data:
                    break
                self._read_q.put(data)
        finally:
            # signal EOF
            try:
                self._read_q.put(b"")
            except Exception:
                pass

    def send(self, data: str, newline: bool = True) -> None:
        """Write bytes to the TTY master (input sent to container)."""
        if self.master_fd is None:
            raise RuntimeError("Shell not started")
        # If the process has exited, raise a clearer error
        if self.proc is not None and self.proc.poll() is not None:
            raise RuntimeError("Container process has exited")
        to_send = data + ("\n" if newline and not data.endswith("\n") else "")
        try:
            os.write(self.master_fd, to_send.encode(self.encoding))
        except OSError as e:
            # If pty/file descriptor is broken, give helpful context
            if self.proc is not None and self.proc.poll() is not None:
                raise RuntimeError("Failed to write to TTY: container exited") from e
            raise

    def recv(self, timeout: Optional[float] = None) -> str:
        """Collect available bytes from the TTY master and return decoded string.

        If timeout is provided, block up to timeout for first chunk.
        """
        chunks = []
        try:
            b = self._read_q.get(timeout=timeout)
            if b == b"":
                return ""
            chunks.append(b)
        except queue.Empty:
            return ""

        while True:
            try:
                b = self._read_q.get_nowait()
                if b == b"":
                    break
                chunks.append(b)
            except queue.Empty:
                break

        text = b"".join(chunks).decode(self.encoding, errors="replace")

        return text

    def recv_until(self, sentinel: str, timeout: float = 9999) -> str:
        """Receive data until the sentinel string is found or timeout occurs."""
        collected = []
        end_time = time.time() + timeout
        while time.time() < end_time:
            chunk = self.recv(timeout=end_time - time.time())
            if not chunk:
                continue
            collected.append(chunk)
            joined = "".join(collected)
            if sentinel in joined:
                return joined
        return "".join(collected)

    def stop(self, kill_timeout: float = 1.0) -> None:
        self._stop_event.set()
        if self.proc is None:
            return
        try:
            try:
                self.proc.terminate()
            except Exception:
                pass
            try:
                self.proc.wait(timeout=kill_timeout)
            except subprocess.TimeoutExpired:
                try:
                    self.proc.kill()
                except Exception:
                    pass
                self.proc.wait()
        finally:
            # close master fd
            try:
                if self.master_fd is not None:
                    os.close(self.master_fd)
            except Exception:
                pass
            self.master_fd = None
            self.proc = None


if __name__ == "__main__":
    shell = DockerShell(image="ctf-agent-workenv", mounts=["$PWD:/workspace"])
    shell.start()
    shell.send("export PS1='__CTF_PROMPT__> '")
    while True:
        cmd = input()
        if cmd in ("exit", "quit"):
            break
        shell.send(cmd)
        time.sleep(0.5)
        output = shell.recv_until("__CTF_PROMPT__> ")
        print(output, end="")
