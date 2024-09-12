# Solana RPC Finder

**Solana RPC Finder** is a tool that helps discover available RPC nodes in the Solana network.

## Table of Contents
- [Description](#description)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [Output Format](#output-format)
- [Requirements](#requirements)
- [License](#license)

## Description

The script performs the following tasks:
- Retrieves the list of all cluster nodes from one or more initial RPCs.
- Checks the availability of each node based on its IP and port.
- Filters nodes with active RPC servers.
- Supports multithreading to speed up node discovery and verification.
- Saves the list of active nodes to the `active_nodes.json` file for later use.

## Installation

1. Clone the repository:
   ```bash
   git clone <your repository URL>
   ```

2. Navigate to the project directory:
   ```bash
   cd solana-rpc-finder
   ```

3. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Configuration

You can configure the following parameters inside the script:

- `INITIAL_RPC_NODES`: A list of initial RPC nodes to scan (by default, the official Solana node).
- `DEFAULT_PORT`: The default port for checking RPC nodes (8899).
- `RETRY_COUNT`: The number of retry attempts to fetch cluster nodes.
- `SCAN_NULL_RPC_NODES`: Specifies whether to scan nodes with a missing `rpc` field.
- Multithreading parameters:
  - `MAX_RPC_FETCH_WORKERS`: Number of threads for fetching nodes from initial RPCs.
  - `MAX_NODE_CHECK_WORKERS`: Number of threads for checking node availability.

## Usage

1. Run the script:

   ```bash
   python main.py
   ```

2. The script will perform the following steps:
   - Load nodes from the `active_nodes.json` file (if it exists).
   - Fetch nodes from the initial RPCs.
   - Check node availability and save active nodes to the `active_nodes.json` file.

3. After completion, all active nodes will be saved to the `active_nodes.json` file.

## Output Format

The `active_nodes.json` file contains a list of active nodes in JSON format. Example:

```json
[
    {
        "featureSet": 4215500110,
        "gossip": "192.168.0.2:8000",
        "pubkey": "7mF8NZ...",
        "pubsub": "192.168.0.2:8900",
        "rpc": "192.168.0.2:8899",
        "shredVersion": 50093,
        "tpu": "192.168.0.2:8012",
        "tpuQuic": "192.168.0.2:8018",
        "version": "1.18.23",
        "latency": 218.30987930297852
    },
    {
        "featureSet": 4215500110,
        "gossip": "192.168.0.3:8000",
        "pubkey": "9ubTvP...",
        "pubsub": "192.168.0.3:8900",
        "rpc": "192.168.0.3:8899",
        "shredVersion": 50093,
        "tpu": "192.168.0.3:8003",
        "tpuQuic": "192.168.0.3:8009",
        "version": "1.18.22",
        "latency": 210.6649875640869
    }
]
```

## Requirements

- Python 3.7+
- Modules: `requests`, `tqdm`, `concurrent.futures`

## License

This project is licensed under the GNU General Public License v3.0. See the [LICENSE](LICENSE) file for details.
