# receiver.py
import json

def receive_results(queue):
    # Wait for the sender process to put the results in the queue
    results_json = queue.get()

    # Parse JSON
    results_parsed = json.loads(results_json)

    # Print received JSON
    print('------------- The Reciver Process --------------')
    print(json.dumps(results_parsed, indent=4))
