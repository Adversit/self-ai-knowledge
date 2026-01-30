import subprocess
import sys
import json
import uuid
from datetime import datetime
from typing import Callable, Any
from pathlib import Path

from .config import get_config

class SubprocessWrapper:
    def __init__(self, on_message: Callable[[dict], None]):
        self.on_message = on_message
        self.config = get_config()

    def run(
        self,
        command: str,
        agent: str,
        project: str | None = None,
        tags: list[str] | None = None,
    ) -> dict:
        """Run agent CLI in interactive mode, capturing all I/O."""
        
        session_id = datetime.now().strftime("%Y-%m-%dT%H-%M-%S") + f"-{agent}"
        start_time = datetime.now()
        messages = []

        try:
            proc = subprocess.Popen(
                command,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
            )

            # Add system message indicating recording started
            sys_msg = {
                "role": "system",
                "content": f"[AI Context Vault] Recording session {session_id} - {agent}",
                "timestamp": start_time.isoformat(),
            }
            messages.append(sys_msg)
            self.on_message({
                "type": "message",
                "session_id": session_id,
                "message": sys_msg,
            })

            while True:
                line = proc.stdout.readline()
                if not line and proc.poll() is not None:
                    break

                timestamp = datetime.now()
                content = line.rstrip("\n")

                # Determine role (heuristic: assistant output)
                msg = {
                    "role": "assistant",
                    "content": content,
                    "timestamp": timestamp.isoformat(),
                }
                messages.append(msg)
                self.on_message({
                    "type": "message",
                    "session_id": session_id,
                    "message": msg,
                })

                # Also print to stdout for visibility
                print(content)

        except KeyboardInterrupt:
            proc.terminate()

        end_time = datetime.now()
        
        # Close stdin if still open
        if proc.stdin and not proc.stdin.closed:
            proc.stdin.close()

        session_data = {
            "session_id": session_id,
            "created_at": start_time.isoformat(),
            "model_source": agent,
            "model_variant": None,
            "entry_point": "cli",
            "project": project,
            "tags": tags or [],
            "messages": messages,
            "summaries": {},
        }

        self.on_message({
            "type": "session_end",
            "session_id": session_id,
            "data": session_data,
        })

        return session_data

    def run_with_user_input(
        self,
        command: str,
        agent: str,
        user_inputs: list[str] | None = None,
        project: str | None = None,
        tags: list[str] | None = None,
    ) -> dict:
        """Run with predefined user inputs (for testing/automation)."""
        
        session_id = datetime.now().strftime("%Y-%m-%dT%H-%M-%S") + f"-{agent}"
        start_time = datetime.now()
        messages = []

        try:
            proc = subprocess.Popen(
                command,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
            )

            sys_msg = {
                "role": "system",
                "content": f"[AI Context Vault] Recording session {session_id} - {agent}",
                "timestamp": start_time.isoformat(),
            }
            messages.append(sys_msg)

            input_idx = 0
            while True:
                line = proc.stdout.readline()
                if not line and proc.poll() is not None:
                    break

                timestamp = datetime.now()
                content = line.rstrip("\n")

                msg = {
                    "role": "assistant",
                    "content": content,
                    "timestamp": timestamp.isoformat(),
                }
                messages.append(msg)
                self.on_message({
                    "type": "message",
                    "session_id": session_id,
                    "message": msg,
                })
                print(content)

                # Send user input if available
                if user_inputs and input_idx < len(user_inputs):
                    user_input = user_inputs[input_idx] + "\n"
                    proc.stdin.write(user_input)
                    proc.stdin.flush()
                    
                    user_msg = {
                        "role": "user",
                        "content": user_inputs[input_idx],
                        "timestamp": datetime.now().isoformat(),
                    }
                    messages.append(user_msg)
                    input_idx += 1

        except Exception as e:
            proc.terminate()
            raise e

        end_time = datetime.now()
        if proc.stdin and not proc.stdin.closed:
            proc.stdin.close()

        session_data = {
            "session_id": session_id,
            "created_at": start_time.isoformat(),
            "model_source": agent,
            "model_variant": None,
            "entry_point": "cli",
            "project": project,
            "tags": tags or [],
            "messages": messages,
            "summaries": {},
        }

        self.on_message({
            "type": "session_end",
            "session_id": session_id,
            "data": session_data,
        })

        return session_data
