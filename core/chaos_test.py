import threading
from reservations.services import create_reservation

success = 0
fail = 0

def run():
    global success, fail
    try:
        create_reservation(1, 1, 'chaos')
        success += 1
    except:
        fail += 1

threads = [threading.Thread(target=run) for _ in range(50)]
[t.start() for t in threads]
[t.join() for t in threads]

print('Success:', success)
print('Fail:', fail)


# import threading
# import requests
# import concurrent.futures

# # আপনার লোকাল সার্ভার ইউআরএল
# API_URL = "http://127.0.0.1:8000/api/reservations/"
# PRODUCT_ID = 1  # ধরে নিচ্ছি এই প্রোডাক্টের স্টক ৫টি

# def make_purchase():
#     """এপিআই-তে একটি রিকোয়েস্ট পাঠায়"""
#     try:
#         response = requests.post(API_URL, json={
#             "product_id": PRODUCT_ID,
#             "quantity": 1
#         }, timeout=5)
#         return response.status_code
#     except Exception as e:
#         return 500

# def run_chaos_test():
#     succeeded = 0
#     failed = 0
#     total_attempts = 50

#     print(f"🚀 Starting Chaos Test: Firing {total_attempts} parallel requests...")

#     # ৫০টি থ্রেড একসাথে চালানোর জন্য ThreadPoolExecutor ব্যবহার করছি
#     with concurrent.futures.ThreadPoolExecutor(max_workers=50) as executor:
#         # সকল রিকোয়েস্ট ফায়ার করা হচ্ছে
#         futures = [executor.submit(make_purchase) for _ in range(total_attempts)]
        
#         for future in concurrent.futures.as_completed(futures):
#             status = future.result()
#             if status == 200:
#                 succeeded += 1
#             else:
#                 failed += 1

#     print("\n--- 🏁 Chaos Test Results ---")
#     print(f"✅ Succeeded attempts: {succeeded}")
#     print(f"❌ Failed attempts:    {failed}")
    
#     # ফাইনাল স্টক ভেরিফিকেশন (এটি সরাসরি ডাটাবেস বা অন্য এপিআই থেকে চেক করতে পারেন)
#     print("\n--- 📦 Final Stock Numbers ---")
#     # উদাহরণস্বরূপ একটি GET রিকোয়েস্ট করে স্টক প্রিন্ট করতে পারেন
#     # print(f"Available Stock: {final_available}")
#     # print(f"Reserved Stock:  {final_reserved}")

# if __name__ == "__main__":
#     run_chaos_test()