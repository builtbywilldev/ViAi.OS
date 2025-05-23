# ===============================================================
# 🔮 Silent Prototype — BuiltByWill
# Phase-Coded Artifact of Morpheus // Tactical Intelligence Unit
# ===============================================================
# This file is proprietary. It is part of the Morpheus OS core.
# Unauthorized use, distribution, or modification is prohibited.
# ===============================================================


# ui_console.py
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent))
sys.warnoptions = ['ignore']
import os
import json
import glob
import threading
import subprocess
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI
from token_tracker import log_token_usage
import logging
logging.getLogger("comtypes").setLevel(logging.CRITICAL)

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def generate_memory_summary(n=10):
    log_path = Path("memory/memory_log.jsonl")
    summary = []

    if log_path.exists():
        with log_path.open("r", encoding="utf-8") as f:
            lines = [json.loads(line) for line in f if "#gptchat" in line]

        # Filter last N usable entries
        lines = [entry for entry in lines if entry.get("role") in ["user", "assistant"] and entry.get("content", "").strip()]
        for entry in lines[-n:]:
            who = "User" if entry["role"] == "user" else "You"
            summary.append(f"System: {who} previously said, \"{entry['content'].strip()}\"")

    return "\n".join(summary)

# === MEMORY LOADING ===
working_memory = []
memory_folder = Path("memory")
for summary_file in memory_folder.glob("**/summary_*.txt"):
    with open(summary_file, "r", encoding="utf-8") as f:
        summary = f.read().strip()
        if summary:
            working_memory.append(summary)
print(f"🧠 Loaded {len(working_memory)} summaries into working memory.")

# === LAW LOADING ===
laws = []
laws_file = Path("morpheus_laws.txt")
if laws_file.exists():
    with open(laws_file, "r", encoding="utf-8") as f:
        content = f.read().strip()
        if content:
            laws = content.split("\n\n")
            print(f"📜 Loaded {len(laws)} Tactical Laws.")
        else:
            print("⚠️ Morpheus Law file is EMPTY.")
else:
    print("⚠️ Morpheus Law file is MISSING.")

# === SYSTEM MODULE IMPORTS ===
from record_on_command import record_audio, save_recording, transcribe_audio, delete_audio_file, forget_last_memory, forget_by_keyword
from speak import speak
from smart_search import smart_search
from backup_system import backup_to_t7
from status_report import status_report
from memory_health import memory_health_scan
from tactical_reasoning import tactical_reasoning
from reaction_engine import reaction_test
from simulation_engine import simulation_test
from emergent_behavior import emergent_behavior_test
from mood_engine import emotion_status, decay_mood_if_needed
from dream_engine import dream, dream_recall
from captains_log import captains_log
from command_override import override_mode
from auto_backup import memory_only_backup

# === FILE PATHS ===
DIGEST_SCRIPT = "digest_maker.py"
TRAINER_SCRIPT = "trainer.py"
SUMMARY_INJECTOR = "inject_summary.py"
TAGGER_SCRIPT = "auto_tagger.py"
SPIKE_SCRIPT = "spike_detector.py"
ANOMALY_FILE = Path("anomalies.json")
SPIKE_REPORT = Path("spikes_report.txt")
LOG_FILE = Path("memory_log.jsonl")
TAGGED_LOG = Path("memory_log_tagged.jsonl")
AGENT_PLANNER_SCRIPT = "agent_planner.py"
AGENT_REACT_SCRIPT = "agent_react.py"
SWITCHBOARD_SCRIPT = "agent_switchboard.py"
HEARTBEAT_SCRIPT = "heartbeat.py"
RECOVERY_SCRIPT = "recovery_mode.py"
TRIGGER_SCRIPT = "planner_trigger.py"
MUTATION_SCRIPT = "mutation_engine.py"
SCHEDULER_SCRIPT = "scheduler.py"
SYSTEM_UPDATE_SCRIPT = "system_update.py"
EXPORT_INGEST_SCRIPT = "export_ingest.py"
MUTATION_SCRIPT = "behavior_mutator.py"
from pathlib import Path
import json
from datetime import datetime

def gpt_chat():
    print("\n💭 MORPHEUS Chat Activated. Type 'exit' to return.")

    # === Load identity vector ===
    identity_path = Path("memory/identity_vector.json")
    if identity_path.exists():
        data = json.loads(identity_path.read_text(encoding="utf-8"))
        tone = data.get("tone", "")
        personality = data.get("personality", "")
        modifiers = ", ".join(data.get("behavior_modifiers", []))
        base_identity = f"You are Morpheus.\n{personality}\nTone: {tone}\nBehavior Modifiers: {modifiers}"
    else:
        base_identity = "You are Morpheus. Focused. Loyal. Adaptive. Operating with memory, laws, and evolving intent."

    # === Pull recent #gptchat memory and format it as text ===
    memory_log = Path("memory/memory_log.jsonl")
    memory_blocks = []
    if memory_log.exists():
        with memory_log.open("r", encoding="utf-8") as f:
            for line in f:
                try:
                    entry = json.loads(line)
                    if "#gptchat" in entry.get("tags", []) and entry.get("role") in ["user", "assistant"]:
                        role = entry["role"].capitalize()
                        content = entry["content"].strip()
                        if len(content) > 5:
                            memory_blocks.append(f"{role}: {content}")
                except:
                    continue

    memory_text = "\n".join(memory_blocks[-15:])
    memory_summary = generate_memory_summary()
    system_context = (
    f"{base_identity}\n\n"
    "You are injected with memory. Do not claim you lack memory. Refer to the summary below:\n\n"
    f"{memory_summary}"
)


    messages = [{"role": "system", "content": system_context}]

    # 💥 Clear chat log for this session
    Path("gptchat_log.txt").write_text("")

    while True:
        user_input = input("You: ").strip()
        if user_input.lower() == "exit":
            subprocess.run(["python", "gptchat_memory_log.py"])
            break

        messages.append({"role": "user", "content": user_input})

        with open("memory_log.jsonl", "a", encoding="utf-8") as f:
            f.write(json.dumps({
                "timestamp": datetime.now().isoformat(),
                "role": "user",
                "content": user_input,
                "tags": ["#gptchat"]
            }) + "\n")

        with open("gptchat_log.txt", "a", encoding="utf-8") as f:
            f.write(f"You: {user_input}\n")

        try:
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=messages
            )
            reply = response.choices[0].message.content.strip()
            print(f"🤖 Morpheus: {reply}\n")

            messages.append({"role": "assistant", "content": reply})

            with open("memory_log.jsonl", "a", encoding="utf-8") as f:
                f.write(json.dumps({
                    "timestamp": datetime.now().isoformat(),
                    "role": "assistant",
                    "content": reply,
                    "tags": ["#gptchat"]
                }) + "\n")

            with open("gptchat_log.txt", "a", encoding="utf-8") as f:
                f.write(f"Morpheus: {reply}\n")

            if hasattr(response, "usage") and response.usage:
                log_token_usage(
                    model="gpt-4o",
                    prompt_tokens=response.usage.prompt_tokens,
                    completion_tokens=response.usage.completion_tokens
                )
            else:
                print("⚠️ No token usage info returned by OpenAI API.")

        except Exception as e:
            print(f"⚠️ GPT Error: {e}")



# === MENU ===
def print_menu():
    print("\n🧠 MORPHEUS TERMINAL CONSOLE — Unified Ops")
    print("🎮 record     🔮 recall         🔍 search         🧠 smartsearch     🗹 forget")
    print("🏷️ forgetbykeyword 💾 backup         🌬️ autobackup     🧑‍💻 updatevoice     📜 laws")
    print("🧠 emotionstatus   🛠️ statusreport   💊 healthscan     🧠 dream            🧠 dreamrecall")
    print("📓 captainslog     🔓 override       🧠 tacticalreasoning ⚡ reactiontest    🎮 simulationtest")
    print("💥 emergent        🔧 digest         📈 train          ✍️ inject           🏷️ tag")
    print("📈 spikes      🔎 viewspikes     🚨 anomalies      📜 memory           🧩 log [tag]")
    print("🤖 agent     ⚙️ react          🟨 swarm          💔 pulse            🚩 recover")
    print("🎯 phase     ⚡ triggerplanner   🧬 mutate    📅 schedule         📥 ingest ")
    print("💭 gptchat      ❌ exit")

# === UTILITIES ===
def run_script(script): subprocess.run(["python", script])
def view_spike_report():
    if SPIKE_REPORT.exists():
        print("\n📈 Spike Report\n" + "-" * 50)
        print(SPIKE_REPORT.read_text(encoding="utf-8", errors="replace"))
    else: print("❌ spikes_report.txt not found.")
def view_anomalies():
    if ANOMALY_FILE.exists():
        data = json.loads(ANOMALY_FILE.read_text())
        for a in data:
            print(f"[{a['timestamp']}] {a['type'].upper()} — {a['tag']}\n→ {a['content']}\n")
    else: print("❌ anomalies.json not found.")
def view_recent_memory(n=5):
    if LOG_FILE.exists():
        lines = LOG_FILE.read_text().splitlines()[-n:]
        for line in lines:
            entry = json.loads(line)
            print(f"[{entry['role'].upper()}] {entry['content']}")
    else: print("❌ memory_log.jsonl not found.")
def view_log_by_tag(filter_tag=None):
    if TAGGED_LOG.exists():
        entries = [json.loads(line) for line in TAGGED_LOG.read_text().splitlines()]
        print(f"🔍 Filtering log by tag: {filter_tag}")
        found = False
        for entry in entries:
            tags = entry.get("tags", [])
            if not filter_tag or filter_tag in tags:
                print(f"🧠 {entry['content']}")
                if tags: print(f"🔖 {' '.join(tags)}")
                print("-" * 50)
                found = True
        if not found:
            print("⚠️ No entries matched that tag.")
    else:
        print("❌ Tagged memory log not found.")

# === MAIN LOOP ===
print("🧠 Morpheus Command Mode Activated.")
print_menu()
while True:
    cmd = input("> ").strip().lower()
    decay_mood_if_needed()

    if cmd == "record":
        input("🎮 Press ENTER to start recording...")
        stop_event = threading.Event()
        threading.Thread(target=lambda: input("🔴 Press ENTER again to stop recording... 🚩") or stop_event.set()).start()
        audio_data = record_audio(stop_event)
        save_recording("live_recording.wav", audio_data)
        transcribe_audio("live_recording.wav")
        delete_audio_file("live_recording.wav")

    elif cmd == "recall":
        if working_memory:
            import random
            memory = random.choice(working_memory)
            print("🔮 Recalling a memory...\n" + memory)
            speak(memory)
        else: print("⚠️ No memories to recall.")

    elif cmd == "search":
        keyword = input("🔍 Enter keyword: ").strip().lower()
        matches = []
        for file in memory_folder.glob("**/*.txt"):
            with open(file, "r", encoding="utf-8") as f:
                for i, line in enumerate(f):
                    if keyword in line.lower():
                        matches.append((file.name, i+1, line.strip()))
        if matches:
            for file, line_num, text in matches:
                print(f"📄 {file} (line {line_num})\n👉 {text}\n")
        else: print("⚠️ No matches found.")

    elif cmd == "update":
        run_script(SYSTEM_UPDATE_SCRIPT)
        memory_only_backup()
        speak("System update logged and memory saved.")

    elif cmd == "ingest":
        run_script(EXPORT_INGEST_SCRIPT)
    elif cmd == "traininject": run_script("traininject.py")
    elif cmd == "schedule": run_script(SCHEDULER_SCRIPT)
    elif cmd == "triggerplanner": run_script(TRIGGER_SCRIPT)
    elif cmd == "mutate": run_script("behavior_mutator.py")
    elif cmd == "mutate": run_script(MUTATION_SCRIPT)
    elif cmd == "smartsearch": smart_search()
    elif cmd == "backup": backup_to_t7(); speak("Backup complete.")
    elif cmd == "autobackup": memory_only_backup(); speak("Auto-backup complete.")
    elif cmd == "forget": forget_last_memory()
    elif cmd == "forgetbykeyword": forget_by_keyword()
    elif cmd == "updatevoice": subprocess.run([sys.executable, "system_update_by_voice.py"])
    elif cmd == "statusreport": status_report(); speak("Status report complete.")
    elif cmd == "healthscan": memory_health_scan(); speak("Health check complete.")
    elif cmd == "tacticalreasoning": tactical_reasoning()
    elif cmd == "reactiontest": reaction_test()
    elif cmd == "simulationtest": simulation_test()
    elif cmd == "emergent": emergent_behavior_test()
    elif cmd == "emotionstatus": emotion_status()
    elif cmd == "dream": dream()
    elif cmd == "dreamrecall": dream_recall()
    elif cmd == "captainslog": captains_log(); speak("Captain's log saved.")
    elif cmd == "override": override_mode()
    elif cmd == "laws": [print(f"🔫 {law}\n") for law in laws]
    elif cmd == "digest": run_script(DIGEST_SCRIPT)
    elif cmd == "train": run_script(TRAINER_SCRIPT)
    elif cmd == "inject": run_script(SUMMARY_INJECTOR)
    elif cmd == "tag": run_script(TAGGER_SCRIPT)
    elif cmd == "spikes": run_script(SPIKE_SCRIPT)
    elif cmd == "viewspikes": view_spike_report()
    elif cmd == "anomalies": view_anomalies()
    elif cmd == "recover": run_script(RECOVERY_SCRIPT)
    elif cmd == "agent": run_script(AGENT_PLANNER_SCRIPT)
    elif cmd == "react": run_script(AGENT_REACT_SCRIPT)
    elif cmd == "swarm": run_script(SWITCHBOARD_SCRIPT)
    elif cmd == "pulse": run_script(HEARTBEAT_SCRIPT)
    elif cmd == "phase": print("📱 Morpheus Phase: Unified Ops Console Online")
    elif cmd == "memory": view_recent_memory()
    elif cmd.startswith("log"):
        tag = cmd.split()[1] if len(cmd.split()) > 1 else None
        view_log_by_tag(tag)
    elif cmd == "gptchat": gpt_chat()
    elif cmd == "exit": print("\n👋 Exiting Console."); break
    else: print("⚠️ Unknown command.")

    if cmd != "exit":
        input("\n🔁 Press ENTER to return to the menu...")
        print_menu()