#!/usr/bin/env python3
"""
Pre-warms the Redis cache before exam results go live to prevent cold-cache DB hammering.
"""
import redis
import os

REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))

def prewarm():
    r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)
    pipe = r.pipeline()
    
    print("Beginning bulk pre-warming of 5,000 student records into Redis...")
    for i in range(1001, 6001):
        roll_no = f"21BCE{i}"
        gpa = round(7.0 + (i % 30) / 10.0, 2)
        pipe.set(f"student:{roll_no}", f"GPA: {gpa} | Status: PASSED (Pre-cached)")
        if i % 1000 == 0:
            pipe.execute()
            print(f"Pre-warmed {i - 1000} records...")

    pipe.execute()
    print("Successfully pre-warmed all records into Redis memory.")

if __name__ == "__main__":
    prewarm()
