#!/usr/bin/env python3
"""Extract fields from a ULog file and output as CSV."""

import sys
import argparse
import csv

try:
    from pyulog import ULog
except ImportError:
    print("Error: pyulog is required. Install it with: pip install pyulog", file=sys.stderr)
    sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description="Extract fields from a ULog file and output as CSV",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  px4-ulog flight.ulg vehicle_local_position x,y,z
  px4-ulog flight.ulg vehicle_local_position x,y,z -t   # include timestamp
  px4-ulog flight.ulg sensor_accel x,y,z --instance 1
  px4-ulog --list flight.ulg
  px4-ulog --list flight.ulg vehicle_local_position
        """
    )
    
    parser.add_argument("ulog_file", help="Path to the ULog file")
    parser.add_argument("message", nargs="?", help="Message name (e.g., vehicle_local_position)")
    parser.add_argument("fields", nargs="?", help="Comma-separated field names (e.g., x,y,z)")
    parser.add_argument("--instance", "-i", type=int, default=0,
                        help="Multi-instance index (default: 0)")
    parser.add_argument("--list", "-l", action="store_true",
                        help="List available messages and their fields")
    parser.add_argument("--no-header", action="store_true",
                        help="Don't print CSV header row")
    parser.add_argument("--timestamp", "-t", action="store_true",
                        help="Include timestamp column in output")
    
    args = parser.parse_args()
    
    # Load the ULog file
    try:
        ulog = ULog(args.ulog_file)
    except Exception as e:
        print(f"Error reading ULog file: {e}", file=sys.stderr)
        sys.exit(1)
    
    # List mode
    if args.list:
        list_messages(ulog, args.message)
        return
    
    # Extract mode - require message and fields
    if not args.message or not args.fields:
        parser.error("message and fields are required (unless using --list)")
    
    extract_fields(ulog, args.message, args.fields, args.instance, not args.no_header, args.timestamp)


def list_messages(ulog: ULog, filter_message: str = None):
    """List available messages and their fields."""
    messages = {}
    
    for data in ulog.data_list:
        name = data.name
        if name not in messages:
            messages[name] = {
                'fields': list(data.data.keys()),
                'instances': []
            }
        messages[name]['instances'].append(data.multi_id)
    
    if filter_message:
        # Show fields for a specific message
        if filter_message not in messages:
            print(f"Message '{filter_message}' not found in ULog file", file=sys.stderr)
            print(f"Available messages: {', '.join(sorted(messages.keys()))}", file=sys.stderr)
            sys.exit(1)
        
        msg_info = messages[filter_message]
        print(f"Message: {filter_message}")
        print(f"Instances: {msg_info['instances']}")
        print(f"Fields:")
        for field in sorted(msg_info['fields']):
            print(f"  {field}")
    else:
        # List all messages
        print("Available messages:")
        for name in sorted(messages.keys()):
            instances = messages[name]['instances']
            instance_str = f" (instances: {instances})" if len(instances) > 1 else ""
            print(f"  {name}{instance_str}")


def extract_fields(ulog: ULog, message: str, fields_str: str, instance: int, print_header: bool, include_timestamp: bool):
    """Extract specified fields from a message and output as CSV."""
    fields = [f.strip() for f in fields_str.split(",")]
    
    # Find the message data
    data = None
    for d in ulog.data_list:
        if d.name == message and d.multi_id == instance:
            data = d
            break
    
    if data is None:
        available = [d.name for d in ulog.data_list]
        print(f"Message '{message}' (instance {instance}) not found", file=sys.stderr)
        print(f"Available messages: {', '.join(sorted(set(available)))}", file=sys.stderr)
        sys.exit(1)
    
    # Verify fields exist
    available_fields = list(data.data.keys())
    for field in fields:
        if field not in available_fields:
            print(f"Field '{field}' not found in message '{message}'", file=sys.stderr)
            print(f"Available fields: {', '.join(sorted(available_fields))}", file=sys.stderr)
            sys.exit(1)
    
    # Output CSV
    writer = csv.writer(sys.stdout)
    
    if print_header:
        header = ["timestamp"] + fields if include_timestamp else fields
        writer.writerow(header)
    
    # Get number of samples
    n_samples = len(data.data["timestamp"])
    
    for i in range(n_samples):
        row = []
        if include_timestamp:
            row.append(data.data["timestamp"][i])
        for field in fields:
            row.append(data.data[field][i])
        writer.writerow(row)


if __name__ == "__main__":
    main()

