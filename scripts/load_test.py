"""Concurrent-user load test for NFR-01 / NFR-03.

Start the app first (python run.py), then:
    python scripts/load_test.py --users 10 --requests 5

Each simulated user keeps its own session, loads the home page to get a CSRF token and asks questions.
"""
import argparse
import http.cookiejar
import json
import re
import statistics
import threading
import time
import urllib.request

QUESTIONS = [
    "My landlord is not returning my security deposit after I vacated the flat.",
    "I ordered a phone online and received a damaged product. The seller refuses a refund.",
    "Someone took money from my account through a UPI fraud call.",
    "My employer has not paid my salary for two months.",
    "The police are refusing to register my complaint about a theft.",
]


def simulate_user(base, n_requests, timings, errors, user_index):
    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()))
    try:
        html = opener.open(base + "/", timeout=30).read().decode("utf-8")
        token = re.search(r'name="csrf-token" content="([^"]+)"', html).group(1)
    except Exception as exc:  # noqa: BLE001 - report any failure
        errors.append(f"user {user_index}: could not load home page ({exc})")
        return
    for i in range(n_requests):
        question = QUESTIONS[(user_index + i) % len(QUESTIONS)]
        request = urllib.request.Request(
            base + "/api/query",
            data=json.dumps({"question": question}).encode(),
            headers={"Content-Type": "application/json", "X-CSRF-Token": token},
            method="POST",
        )
        started = time.perf_counter()
        try:
            data = json.loads(opener.open(request, timeout=60).read())
            if data.get("question") != question:
                errors.append(f"user {user_index}: received an answer for a different question")
            timings.append(time.perf_counter() - started)
        except Exception as exc:  # noqa: BLE001
            errors.append(f"user {user_index}: request failed ({exc})")


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--url", default="http://127.0.0.1:5000")
    parser.add_argument("--users", type=int, default=10)
    parser.add_argument("--requests", type=int, default=5, help="questions per user")
    args = parser.parse_args()

    timings, errors = [], []
    threads = [threading.Thread(target=simulate_user, args=(args.url, args.requests, timings, errors, u))
               for u in range(args.users)]
    started = time.perf_counter()
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    total = time.perf_counter() - started

    print(f"Users: {args.users}, requests: {len(timings)} succeeded, {len(errors)} failed, total time {total:.1f}s")
    if timings:
        ordered = sorted(timings)
        p95 = ordered[max(0, int(len(ordered) * 0.95) - 1)]
        print(f"Response time: avg {statistics.mean(timings):.2f}s, p95 {p95:.2f}s, max {max(timings):.2f}s")
    for e in errors[:10]:
        print("  ERROR", e)
    raise SystemExit(1 if errors else 0)


if __name__ == "__main__":
    main()
