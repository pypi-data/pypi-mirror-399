#!/usr/bin/env python3
"""
SudoDog Benchmark - AI Agent Testing Tool

Usage:
    sudodog-benchmark              Run interactive benchmark
    sudodog-benchmark --help       Show help
    sudodog-benchmark --version    Show version
"""

import sys
import os
import time
import json
import hashlib
import platform
import argparse
from typing import Optional, List, Dict, Any

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from sudodog.scanner.scanner import scan_for_shadow_agents, DetectedAgent
from sudodog.benchmark.tester import AgentTester
from sudodog.benchmark.api import BenchmarkAPI
from sudodog.benchmark.display import Display

VERSION = "1.0.1"

# ASCII Art Banner
BANNER = r"""
   _____ __  ______  ____  ____  ____  ______
  / ___// / / / __ \/ __ \/ __ \/ __ \/ ____/
  \__ \/ / / / / / / / / / / / / / / / / __
 ___/ / /_/ / /_/ / /_/ / /_/ / /_/ / /_/ /
/____/\____/_____/\____/\____/\____/\____/

         B E N C H M A R K   v{version}
"""


def get_machine_id() -> str:
    """Generate a unique machine identifier for rate limiting."""
    try:
        node = str(platform.node())
        mac = str(hex(uuid.getnode())) if 'uuid' in dir() else ''
        system = platform.system()
        machine = platform.machine()

        raw_id = f"{node}-{mac}-{system}-{machine}"
        return hashlib.sha256(raw_id.encode()).hexdigest()[:16]
    except:
        return hashlib.sha256(os.urandom(32)).hexdigest()[:16]


def clear_screen():
    """Clear the terminal screen."""
    os.system('cls' if os.name == 'nt' else 'clear')


def select_agent(agents: List[DetectedAgent]) -> Optional[DetectedAgent]:
    """Let user select an agent to benchmark."""
    display = Display()

    if not agents:
        display.warning("No AI agents detected running on this machine.")
        display.info("\nMake sure your agent is running, then try again.")
        display.info("Tip: Start your agent in another terminal window first.")
        return None

    display.header("DETECTED AGENTS")
    print()

    for i, agent in enumerate(agents, 1):
        conf_pct = int(agent.confidence * 100)
        conf_bar = display.progress_bar(conf_pct, 100, width=10)

        print(f"  [{i}] {agent.suspected_framework.upper()}")
        print(f"      PID: {agent.pid}")
        print(f"      Confidence: {conf_bar} {conf_pct}%")
        print(f"      Command: {agent.command_line[:50]}{'...' if len(agent.command_line) > 50 else ''}")
        print()

    while True:
        try:
            choice = input(f"  Select agent to benchmark (1-{len(agents)}) or 'q' to quit: ").strip()

            if choice.lower() == 'q':
                return None

            idx = int(choice) - 1
            if 0 <= idx < len(agents):
                return agents[idx]
            else:
                print(f"  Please enter a number between 1 and {len(agents)}")
        except ValueError:
            print("  Please enter a valid number")
        except (EOFError, KeyboardInterrupt):
            return None


def create_agent_from_pid(pid: int) -> Optional[DetectedAgent]:
    """Create a DetectedAgent from a PID."""
    try:
        if sys.platform == "linux":
            with open(f'/proc/{pid}/cmdline', 'r') as f:
                cmdline = f.read().replace('\x00', ' ').strip()
            with open(f'/proc/{pid}/comm', 'r') as f:
                comm = f.read().strip()

            # Try to detect framework from command line or environment
            framework = detect_framework_from_pid(pid, cmdline)

            return DetectedAgent(
                pid=pid,
                process_name=comm,
                command_line=cmdline,
                suspected_framework=framework,
                confidence=0.8,
                indicators=["Manually specified via --agent-pid"]
            )
        else:
            # For other platforms, create minimal agent
            return DetectedAgent(
                pid=pid,
                process_name="unknown",
                command_line="",
                suspected_framework="unknown",
                confidence=0.5,
                indicators=["Manually specified via --agent-pid"]
            )
    except (FileNotFoundError, PermissionError) as e:
        return None


def detect_framework_from_pid(pid: int, cmdline: str) -> str:
    """Detect the AI framework from process environment and command line."""
    cmdline_lower = cmdline.lower()

    # Check command line patterns
    framework_keywords = {
        'langchain': ['langchain', 'langsmith'],
        'autogpt': ['autogpt', 'auto-gpt', 'autogen'],
        'crewai': ['crewai', 'crew_ai'],
        'claude': ['claude', 'anthropic'],
        'openai': ['openai', 'gpt-4', 'gpt-3'],
        'llama': ['llama', 'llama_index', 'llamaindex'],
    }

    for framework, keywords in framework_keywords.items():
        for keyword in keywords:
            if keyword in cmdline_lower:
                return framework

    # Check environment variables on Linux
    try:
        if sys.platform == "linux":
            with open(f'/proc/{pid}/environ', 'r') as f:
                environ = f.read()

            env_framework_map = {
                'LANGCHAIN_API_KEY': 'langchain',
                'LANGCHAIN_TRACING': 'langchain',
                'OPENAI_API_KEY': 'openai',
                'ANTHROPIC_API_KEY': 'claude',
                'AUTOGEN_': 'autogpt',
            }

            for env_var, framework in env_framework_map.items():
                if env_var in environ:
                    return framework
    except:
        pass

    return "unknown"


def run_benchmark(agent: DetectedAgent, display: Display, duration: int = 30) -> Optional[Dict[str, Any]]:
    """Run the benchmark test on the selected agent."""
    display.header("RUNNING BENCHMARK")
    print()

    tester = AgentTester(agent)

    # Phase 1: Capture baseline
    display.status("Analyzing agent configuration...")
    time.sleep(0.5)
    config = tester.analyze_config()
    display.success("Configuration analyzed")

    # Phase 2: Monitor behavior
    display.status(f"Monitoring agent behavior ({duration} seconds)...")
    print()
    print("  Tip: Interact with your agent now to generate test data!")
    print()

    # Show countdown using the duration parameter
    for remaining in range(duration, 0, -1):
        progress = ((duration - remaining) / duration) * 100
        bar = display.progress_bar(int(progress), 100, width=30)
        print(f"\r  {bar} {remaining}s remaining  ", end='', flush=True)

        # Capture metrics during monitoring
        tester.capture_metrics()
        time.sleep(1)

    print()
    display.success("Behavior monitoring complete")

    # Phase 3: Collect results
    display.status("Collecting results...")
    results = tester.get_results()
    display.success("Results collected")

    return results


def analyze_locally(results: Dict[str, Any]) -> Dict[str, Any]:
    """Perform local analysis based on actual metrics."""
    metrics = results.get("metrics", {})

    good = []
    needs_work = []
    score = 70  # Base score

    # Analyze CPU usage
    cpu_avg = metrics.get("cpu_avg", 0)
    cpu_max = metrics.get("cpu_max", 0)
    if cpu_avg < 20:
        good.append("Low CPU usage - efficient processing")
        score += 5
    elif cpu_avg > 50:
        needs_work.append(f"High CPU usage ({cpu_avg:.1f}%) - consider optimization")
        score -= 5

    # Analyze memory usage
    memory_mb = metrics.get("memory_mb", 0)
    if memory_mb < 200:
        good.append("Low memory footprint")
        score += 5
    elif memory_mb > 500:
        needs_work.append(f"High memory usage ({memory_mb:.0f}MB) - check for memory leaks")
        score -= 5

    # Analyze network connections
    network_conns = metrics.get("network_connections", 0)
    if network_conns > 0:
        good.append(f"Active API connections ({network_conns})")
        score += 5
    else:
        needs_work.append("No API connections detected during monitoring")

    # Analyze API calls
    api_calls = metrics.get("api_calls", 0)
    if api_calls > 0:
        good.append(f"Made {api_calls} API calls during test")
        score += 5

    # Check if process was stable
    samples = metrics.get("samples", 0)
    if samples > 25:
        good.append("Agent remained stable during monitoring")
        score += 5
    elif samples < 10:
        needs_work.append("Agent may have crashed or stopped during monitoring")
        score -= 10

    # Default messages if no specific issues found
    if not good:
        good.append("Benchmark completed successfully")
    if not needs_work:
        needs_work.append("Consider running a longer benchmark for more detailed analysis")

    # Clamp score
    score = max(20, min(95, score))

    # Calculate grade
    if score >= 90: grade = "A+"
    elif score >= 85: grade = "A"
    elif score >= 80: grade = "B+"
    elif score >= 75: grade = "B"
    elif score >= 70: grade = "C+"
    elif score >= 65: grade = "C"
    elif score >= 60: grade = "D"
    else: grade = "F"

    return {
        "id": hashlib.sha256(json.dumps(results).encode()).hexdigest()[:12],
        "score": score,
        "grade": grade,
        "summary": {
            "good": good,
            "needs_work": needs_work
        },
        "report_url": None,
        "badge_url": None,
        "offline": True
    }


def submit_results(results: Dict[str, Any], machine_id: str, display: Display) -> Optional[Dict[str, Any]]:
    """Submit benchmark results to SudoDog API."""
    display.status("Submitting to SudoDog for analysis...")

    api = BenchmarkAPI()

    try:
        response = api.submit_benchmark(results, machine_id)
        display.success("Analysis complete!")
        return response
    except Exception as e:
        display.error(f"Failed to submit results: {e}")
        display.info("Running local analysis instead...")
        return analyze_locally(results)


def show_results(response: Dict[str, Any], display: Display):
    """Display the benchmark results."""
    print()
    display.header("BENCHMARK RESULTS")
    print()

    score = response.get("score", 0)
    grade = response.get("grade", "?")

    # Score visualization
    score_bar = display.progress_bar(score, 100, width=30)

    print(f"  Overall Score: {score}/100 ({grade})")
    print(f"  {score_bar}")
    print()

    # Good things
    summary = response.get("summary", {})
    good = summary.get("good", [])
    if good:
        display.success("What's working well:")
        for item in good:
            print(f"    + {item}")
        print()

    # Needs improvement
    needs_work = summary.get("needs_work", [])
    if needs_work:
        display.warning("Areas for improvement:")
        for item in needs_work:
            print(f"    - {item}")
        print()

    # Links
    report_url = response.get("report_url")
    badge_url = response.get("badge_url")

    print()
    display.header("NEXT STEPS")
    print()

    if response.get("offline"):
        print("  You're in offline mode. Connect to the internet for:")
        print("    - Detailed AI-powered analysis")
        print("    - Shareable report link")
        print("    - Certification badge")
        print()
        print("  Visit: https://sudodog.com")
    else:
        if report_url:
            print(f"  Full Report:  {report_url}")
        if badge_url:
            print(f"  Get Badge:    {badge_url}")
        print()
        print("  Share your score on Twitter!")
        print("  Monitor continuously: https://sudodog.com/dashboard")


def main():
    """Main entry point for the benchmark tool."""
    parser = argparse.ArgumentParser(
        description="SudoDog Benchmark - Test and score your AI agents",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  sudodog-benchmark                    Run interactive benchmark
  sudodog-benchmark --json             Output results as JSON
  sudodog-benchmark --no-submit        Run locally without submitting to API
  sudodog-benchmark --agent-pid 12345  Benchmark a specific process
  sudodog-benchmark --duration 60      Monitor for 60 seconds
        """
    )
    parser.add_argument('--version', action='version', version=f'sudodog-benchmark {VERSION}')
    parser.add_argument('--json', action='store_true', help='Output results as JSON')
    parser.add_argument('--no-submit', action='store_true', help='Run locally without API submission')
    parser.add_argument('--duration', type=int, default=30, help='Monitoring duration in seconds (default: 30)')
    parser.add_argument('--agent-pid', type=int, help='PID of agent to benchmark (skips detection)')

    args = parser.parse_args()

    # JSON mode implies non-interactive
    non_interactive = args.json

    display = Display()
    machine_id = get_machine_id()

    # Show banner
    if not args.json:
        clear_screen()
        print(BANNER.format(version=VERSION))
        print()

    try:
        # If PID specified, use that directly
        if args.agent_pid:
            agent = create_agent_from_pid(args.agent_pid)
            if not agent:
                if args.json:
                    print(json.dumps({"error": f"Process {args.agent_pid} not found or not accessible"}))
                else:
                    display.error(f"Process {args.agent_pid} not found or not accessible")
                return 1
            if not args.json:
                display.success(f"Using specified agent: {agent.suspected_framework} (PID {agent.pid})")
        else:
            # Step 1: Scan for agents
            if not args.json:
                display.status("Scanning for AI agents...")

            agents = scan_for_shadow_agents(quiet=True)

            if not args.json:
                display.success(f"Found {len(agents)} agent(s)")
                print()

            # Step 2: Select agent
            if len(agents) == 0:
                if args.json:
                    print(json.dumps({"error": "No agents detected"}))
                else:
                    display.warning("No AI agents detected!")
                    print()
                    print("  Make sure your agent is running before starting the benchmark.")
                    print("  Start your agent in another terminal, then run this tool again.")
                    print()
                    print("  Tip: Use --agent-pid <PID> to benchmark a specific process.")
                    print()
                return 1

            if len(agents) == 1:
                agent = agents[0]
                if not args.json:
                    display.info(f"Auto-selected: {agent.suspected_framework} (PID {agent.pid})")
            else:
                if args.json:
                    # In JSON mode with multiple agents, just use first one
                    agent = agents[0]
                else:
                    agent = select_agent(agents)
                    if not agent:
                        print("\n  Benchmark cancelled.")
                        return 0

        if not args.json:
            print()

        # Step 3: Run benchmark with specified duration
        results = run_benchmark(agent, display, duration=args.duration)

        if not results:
            if args.json:
                print(json.dumps({"error": "Benchmark failed"}))
            else:
                display.error("Benchmark failed to complete")
            return 1

        # Step 4: Submit results
        if not args.json:
            print()

        if args.no_submit:
            response = analyze_locally(results)
        else:
            response = submit_results(results, machine_id, display)

        # Step 5: Show results
        if args.json:
            print(json.dumps(response, indent=2))
        else:
            show_results(response, display)
            print()
            # No more "Press Enter to exit" - just exit cleanly

        return 0

    except KeyboardInterrupt:
        if not args.json:
            print("\n\n  Benchmark cancelled.")
        return 0
    except Exception as e:
        if args.json:
            print(json.dumps({"error": str(e)}))
        else:
            display.error(f"An error occurred: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
