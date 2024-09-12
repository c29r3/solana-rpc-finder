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
   python solana_rpc_finder.py
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
        "pubkey": "6FwJf2j...",
        "rpc": "http://192.168.1.10:8899",
        "latency": 50.23
    },
    {
        "pubkey": "8HwKj3m...",
        "rpc": "http://192.168.1.12:8899",
        "latency": 45.67
    }
]
```

## Requirements

- Python 3.7+
- Modules: `requests`, `tqdm`, `concurrent.futures`

## License

This project is licensed under the GNU General Public License v3.0. See the [LICENSE](LICENSE) file for details.
