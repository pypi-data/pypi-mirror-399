# LCM-Foxglove Bridge (Modular)

This is a modular implementation of the LCM to Foxglove WebSocket bridge, organized into logical components for better maintainability and extensibility.

## Architecture

The bridge is split into the following components:

### Core Components

- **`bridge.py`** - Main orchestrator that coordinates all components
- **`models.py`** - Data classes and type definitions (`TopicInfo`, `LcmMessage`)
- **`config.py`** - Configuration constants, hardcoded schemas, and logging setup

### Functional Components

- **`topic_discovery.py`** - Discovers LCM topics and their schemas
- **`schema_generator.py`** - Generates JSON schemas from ROS message definitions
- **`message_converter.py`** - Converts LCM messages to Foxglove-compatible format
- **`message_processor.py`** - Threaded message processing and queuing

### Entry Points

- **`__main__.py`** - CLI entry point with argument parsing
- **`test_bridge.py`** - Test script for the modular bridge

## Usage

### Running the Bridge

```bash
# From the foxglove_bridge directory
python -m foxglove_bridge --host 0.0.0.0 --port 8765 --debug

# Or run the test script
python test_bridge.py
```

### Command Line Arguments

- `--host`: WebSocket server host (default: 0.0.0.0)
- `--port`: WebSocket server port (default: 8765)
- `--debug`: Enable verbose debug output
- `--map-file`: JSON file mapping topic names to schema types
- `--threads`: Number of threads for message processing (default: 8)

### Using as a Library

```python
from foxglove_bridge import LcmFoxgloveBridge

bridge = LcmFoxgloveBridge(
    host="localhost",
    port=8765,
    debug=True,
    num_threads=4
)

await bridge.run()
```

## Features

- **Modular Design**: Each component has a single responsibility
- **Threaded Processing**: Multi-threaded message processing for performance
- **Rate Limiting**: Automatic rate limiting for high-frequency topics
- **Message Prioritization**: TF and point cloud messages get higher priority
- **Schema Caching**: Efficient schema generation and caching
- **Extensible**: Easy to add new message converters or modify behavior

## Message Support

The bridge supports the same message types as the original implementation:

- `sensor_msgs/Image`
- `sensor_msgs/CompressedImage`
- `sensor_msgs/JointState`
- `sensor_msgs/PointCloud2`
- `tf2_msgs/TFMessage`
- Generic LCM messages (with automatic schema generation)

## Configuration

### Hardcoded Schemas

The bridge includes hardcoded schemas for common ROS message types in `config.py`. These are optimized for Foxglove compatibility.

### Schema Mapping

You can provide a JSON file mapping bare topic names to schema types:

```json
{
  "joint_states": "sensor_msgs.JointState",
  "camera/image": "sensor_msgs.Image",
  "tf": "tf2_msgs.TFMessage"
}
```

## Performance Features

- **Message Batching**: Processes messages in batches for efficiency
- **Queue Management**: Separate queues for different stages of processing
- **High-Frequency Detection**: Automatically detects and rate-limits high-frequency topics
- **Message Deduplication**: Caches message hashes to avoid processing duplicates

## Error Handling

- Graceful fallback to generic conversion if specialized converters fail
- Comprehensive logging with configurable verbosity
- Proper cleanup on shutdown

## Differences from Original

This modular implementation maintains full compatibility with the original `lcm_foxglove_bridge.py` while offering:

- **Better Organization**: Components are separated by responsibility
- **Easier Testing**: Individual components can be tested in isolation
- **Improved Maintainability**: Changes to one component don't affect others
- **Enhanced Extensibility**: New features can be added without modifying existing code