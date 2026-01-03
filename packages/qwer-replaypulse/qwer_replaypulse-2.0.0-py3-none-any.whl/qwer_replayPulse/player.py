import subprocess
import os
from collections import deque
import json


class ReplayPulse:
    def __init__(self, conf):
        self.conf = conf
        self.rbln_list = []
        self.cmd_list = []
        self.env = os.environ.copy()

    def make_cmd(self):
        cmd = []
        if self.conf.type == "replay":
            cmd.append("rblntrace")
            cmd.append("retrace")
            cmd.append("--get_perf=3")
            cmd.append("-e")
            cmd.append(f"{self.conf.e}")
            cmd.append(f"{self.conf.file}")
            cmd.append("-d")

            if type(self.conf.d) is int:
                self.rbln_list.append(f"{self.conf.d}")
            elif type(self.conf.d) is list:
                self.rbln_list = self.conf.d
            else:
                if self.conf.d == "all":
                    self.rbln_list = range(int(self.conf.rbln_cnt))

            for rbln in self.rbln_list:
                cmd.append(f"{rbln}")
                self.cmd_list.append(list(cmd))
                cmd.pop(-1)

        elif self.conf.type == "retrace":
            #self.env["RBLNTHUNK_PERF"] = "1"
            cmd.append("rblntrace")
            cmd.append(f"{self.conf.type}")
            cmd.append("-e")
            cmd.append(f"{self.conf.e}")
            cmd.append("--get_perf=3")
            cmd.append(f"{self.conf.file}")
            self.cmd_list.append(cmd)
            self.rbln_list = self.conf.group_dict[self.conf.g]

    def run(self, cmd, is_finished, is_failed, idx, output_dict):
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            env=self.env
        )

        last_three_lines = deque(maxlen=3)
        first_lines = []
        called_function_state = False
        waited_function_state = False
        if process.stdout:
            for line in process.stdout:
                clean_line = line.strip()
                if not clean_line: continue

                if line.startswith("Perf (waited inferences) : infer.No "):
                    waited_function_state = True
                    continue
                if line.startswith("Perf (called inferences) : infer.No "):
                    called_fucntion_state = True
                    continue

                if not waited_function_state and not called_function_state:
                    first_lines.append(clean_line)

                last_three_lines.append(clean_line)
                if clean_line.startswith("Report: "):
                    parts = clean_line.split(' ')
                    if not parts[1].startswith('PASSED'):
                        is_failed.value = True
        process.wait()

        final_output = first_lines + list(last_three_lines)

        with is_finished.get_lock():
            is_finished.value = True

        output_dict[self.rbln_list[idx]] = "\n".join(final_output)
