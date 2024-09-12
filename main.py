import requests
import json
import os
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm
from time import sleep

# List of initial working RPC nodes to scan
INITIAL_RPC_NODES = [
    "https://api.mainnet-beta.solana.com"
]

# Configuration parameters
DEFAULT_PORT = 8899
GET_CLUSTER_NODES_METHOD = {"jsonrpc": "2.0", "id": 1, "method": "getClusterNodes"}
GET_SLOT_METHOD = {"jsonrpc": "2.0", "id": 1, "method": "getSlot"}
RETRY_COUNT = 2  # Number of retries for get_cluster_nodes
SCAN_NULL_RPC_NODES = True  # Set this to False to skip nodes with "rpc": null

# Worker settings
MAX_RPC_FETCH_WORKERS = 15  # Number of workers for fetching nodes from initial RPCs
MAX_NODE_CHECK_WORKERS = 100  # Number of workers for checking node availability


# Function to get the IP from any available field
def get_ip_from_node(node):
    # Try to get IP from the "rpc" field first, if it's not available, try other fields
    ip_sources = ["rpc", "tvu", "gossip", "serve_repair", "pubsub"]
    for source in ip_sources:
        ip = node.get(source)
        if ip:
            return ip.split(":")[0]  # Return IP part without the port
    return None  # Return None if no IP was found


# Function to load RPC nodes from active_nodes.json
def load_active_nodes():
    if os.path.exists("active_nodes.json"):
        print("Loading active nodes from 'active_nodes.json'...")
        try:
            with open("active_nodes.json", "r") as f:
                active_nodes = json.load(f)
                # Extract unique RPC URLs from the active nodes (only valid "rpc" field)
                rpc_urls = list({f"http://{node['rpc']}" for node in active_nodes if node.get("rpc")})
                return rpc_urls
        except Exception as e:
            print(f"Error loading active_nodes.json: {e}")
            return []
    return []


# Function to get cluster nodes from an RPC with retries
def get_cluster_nodes(rpc_url):
    for attempt in range(RETRY_COUNT + 1):
        try:
            response = requests.post(rpc_url, json=GET_CLUSTER_NODES_METHOD, timeout=10)
            return response.json().get('result', [])
        except Exception as e:
            print(f"Error fetching getClusterNodes from {rpc_url} on attempt {attempt + 1}: {e}")
            if attempt < RETRY_COUNT:
                sleep(2)  # Wait before retrying
            else:
                return []


# Function to check if a node is available
def check_node(ip, port=DEFAULT_PORT):
    try:
        start_time = time.time()
        url = f"http://{ip}:{port}"
        response = requests.post(url, json=GET_SLOT_METHOD, timeout=2)
        latency = (time.time() - start_time) * 1000  # Convert latency to milliseconds
        if response.status_code == 200:
            return {"ip": ip, "port": port, "latency": latency, "is_active": True}
        else:
            return {"ip": ip, "port": port, "latency": None, "is_active": False}
    except Exception:
        return {"ip": ip, "port": port, "latency": None, "is_active": False}


# Function to check all nodes' availability and update RPC field if necessary
def check_all_nodes(nodes, scan_null_rpc_nodes=True):
    active_nodes = []
    with ThreadPoolExecutor(max_workers=MAX_NODE_CHECK_WORKERS) as executor:
        future_to_node = {
            executor.submit(
                check_node,
                get_ip_from_node(node),
                DEFAULT_PORT if node.get("rpc") is None else int(node["rpc"].split(":")[-1])
            ): node
            for node in nodes if (scan_null_rpc_nodes or node.get("rpc") is not None)
        }

        for future in tqdm(as_completed(future_to_node), total=len(future_to_node), desc="Checking nodes", unit="node"):
            result = future.result()
            node_data = future_to_node[future]
            if result["is_active"]:
                node_data["latency"] = result["latency"]
                # If the node's "rpc" field is null and scan_null_rpc_nodes is True, replace it with "ip:port"
                if node_data.get("rpc") is None and scan_null_rpc_nodes:
                    node_data["rpc"] = f"{result['ip']}:{result['port']}"
                active_nodes.append(node_data)  # Сохраняем все данные ноды, включая остальные поля
    return active_nodes


# Function to get new nodes from active nodes
def get_new_nodes(active_nodes):
    new_nodes = []
    for node in tqdm(active_nodes, desc="Fetching new nodes", unit="node"):
        try:
            response = requests.post(f"http://{node['ip']}:{node['port']}", json=GET_CLUSTER_NODES_METHOD, timeout=5)
            cluster_nodes = response.json().get('result', [])
            for new_node in cluster_nodes:
                if not any(n['pubkey'] == new_node['pubkey'] for n in active_nodes):
                    new_nodes.append(new_node)
        except Exception:
            continue
    return new_nodes


# Function to save the final list of active nodes to a file
def save_active_nodes(active_nodes, filename="active_nodes.json"):
    with open(filename, "w") as f:
        json.dump(active_nodes, f, indent=4)


if __name__ == "__main__":
    print("Fetching all nodes from initial RPCs...")

    # Load RPC URLs from active_nodes.json
    loaded_rpc_nodes = load_active_nodes()
    INITIAL_RPC_NODES.extend(loaded_rpc_nodes)  # Add loaded nodes to the initial RPC list
    INITIAL_RPC_NODES = list(set(INITIAL_RPC_NODES))  # Remove duplicates

    all_nodes = []

    # Fetch nodes from each initial RPC with configured number of workers
    with ThreadPoolExecutor(max_workers=MAX_RPC_FETCH_WORKERS) as executor:
        future_to_rpc = {executor.submit(get_cluster_nodes, rpc_url): rpc_url for rpc_url in INITIAL_RPC_NODES}

        for future in tqdm(as_completed(future_to_rpc), total=len(future_to_rpc),
                           desc="Fetching nodes from initial RPCs", unit="RPC"):
            nodes = future.result()
            if nodes:
                all_nodes.extend(nodes)

    # removing duplicates
    all_nodes = {entry['pubkey']: entry for entry in all_nodes}.values()
    # save all founder cluster nodes
    save_active_nodes(list(all_nodes), filename='full_cluster.json')
    print(f"Found {len(all_nodes)} nodes. Filtering for unique nodes...")

    # Filter nodes for unique IP and RPC combinations and check their availability
    active_nodes = check_all_nodes(all_nodes, scan_null_rpc_nodes=SCAN_NULL_RPC_NODES)
    print(f"Active nodes: {len(active_nodes)}")

    # Check additional nodes fetched from active nodes
    new_nodes = get_new_nodes(active_nodes)
    if new_nodes:
        print(f"Found {len(new_nodes)} new nodes. Checking their availability...")
        active_nodes += check_all_nodes(new_nodes, scan_null_rpc_nodes=SCAN_NULL_RPC_NODES)

    # Save the final list of active nodes
    save_active_nodes(active_nodes)
    print(f"The final list of active nodes is saved to 'active_nodes.json'.")
