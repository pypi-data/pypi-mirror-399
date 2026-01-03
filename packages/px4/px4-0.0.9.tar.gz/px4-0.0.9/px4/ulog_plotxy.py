#!/usr/bin/env python3
"""Plot x/y position from a ULog file."""

import sys
import argparse

try:
    from pyulog import ULog
except ImportError:
    print("Error: pyulog is required. Install it with: pip install pyulog", file=sys.stderr)
    sys.exit(1)

try:
    import matplotlib.pyplot as plt
except ImportError:
    print("Error: matplotlib is required. Install it with: pip install matplotlib", file=sys.stderr)
    sys.exit(1)

import numpy as np


def main():
    parser = argparse.ArgumentParser(
        description="Plot x/y position from a ULog file",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  px4-ulog-plotxy flight.ulg
  px4-ulog-plotxy flight.ulg --save plot.png
  px4-ulog-plotxy flight.ulg --save plot.png --dpi 300
  px4-ulog-plotxy flight.ulg --velocity        # Include speed subplot
        """
    )
    
    parser.add_argument("ulog_file", help="Path to the ULog file")
    parser.add_argument("--save", "-s", help="Save plot to file instead of displaying")
    parser.add_argument("--dpi", type=int, default=150,
                        help="DPI for saved image (default: 150)")
    parser.add_argument("--no-reference", action="store_true",
                        help="Don't plot raptor_status reference position")
    parser.add_argument("--velocity", "-v", action="store_true",
                        help="Show velocity subplot below the XY plot")
    
    args = parser.parse_args()
    
    # Load the ULog file
    try:
        ulog = ULog(args.ulog_file)
    except Exception as e:
        print(f"Error reading ULog file: {e}", file=sys.stderr)
        sys.exit(1)
    
    plot_xy(ulog, args.save, not args.no_reference, args.velocity, args.dpi)


def get_message_data(ulog: ULog, message: str, instance: int = 0):
    """Get data for a specific message and instance."""
    for d in ulog.data_list:
        if d.name == message and d.multi_id == instance:
            return d
    return None


def plot_xy(ulog: ULog, save_path: str = None, plot_reference: bool = True, show_velocity: bool = False, dpi: int = 150):
    """Plot x/y position from vehicle_local_position and optionally raptor_status."""
    
    # Get vehicle_local_position data
    vlp_data = get_message_data(ulog, "vehicle_local_position")
    
    if vlp_data is None:
        print("Error: vehicle_local_position message not found in ULog file", file=sys.stderr)
        sys.exit(1)
    
    x = vlp_data.data.get("x")
    y = vlp_data.data.get("y")
    timestamp = vlp_data.data.get("timestamp")
    
    if x is None or y is None:
        print("Error: x or y field not found in vehicle_local_position", file=sys.stderr)
        sys.exit(1)
    
    # Convert to numpy arrays
    x = np.array(x)
    y = np.array(y)
    timestamp = np.array(timestamp)
    
    # Create figure with or without velocity subplot
    if show_velocity:
        fig, (ax_xy, ax_vel) = plt.subplots(2, 1, figsize=(10, 12), 
                                             height_ratios=[3, 1], 
                                             gridspec_kw={'hspace': 0.25})
    else:
        fig, ax_xy = plt.subplots(figsize=(10, 10))
    
    # Plot vehicle_local_position
    ax_xy.plot(y, x, label="vehicle_local_position", linewidth=1.5, color="#2563eb")
    
    # Mark start and end points
    ax_xy.scatter([y[0]], [x[0]], color="#22c55e", s=100, zorder=5, marker="o", label="Start")
    ax_xy.scatter([y[-1]], [x[-1]], color="#ef4444", s=100, zorder=5, marker="s", label="End")
    
    # Try to get raptor_status reference position
    if plot_reference:
        raptor_data = get_message_data(ulog, "raptor_status")
        
        if raptor_data is not None:
            ref_x = raptor_data.data.get("internal_reference_position[0]")
            ref_y = raptor_data.data.get("internal_reference_position[1]")
            active = raptor_data.data.get("active")
            
            if ref_x is not None and ref_y is not None and active is not None:
                # Convert to numpy arrays
                ref_x = np.array(ref_x)
                ref_y = np.array(ref_y)
                active = np.array(active, dtype=bool)
                
                # Only plot where active is true
                ref_x_active = ref_x.copy()
                ref_y_active = ref_y.copy()
                ref_x_active[~active] = np.nan
                ref_y_active[~active] = np.nan
                
                ax_xy.plot(ref_y_active, ref_x_active, label="raptor_status reference", 
                       linewidth=1.5, linestyle="--", color="#f97316", alpha=0.8)
            elif ref_x is None or ref_y is None:
                print("Note: internal_reference_position[0/1] not found in raptor_status", 
                      file=sys.stderr)
            else:
                print("Note: active field not found in raptor_status", 
                      file=sys.stderr)
        else:
            print("Note: raptor_status message not found (skipping reference plot)", 
                  file=sys.stderr)
    
    # Configure XY plot
    ax_xy.set_xlabel("Y position [m]", fontsize=12)
    ax_xy.set_ylabel("X position [m]", fontsize=12)
    ax_xy.set_title("X/Y Position", fontsize=14)
    ax_xy.legend(loc="best")
    ax_xy.grid(True, alpha=0.3)
    
    # Set equal aspect ratio so x and y have the same scale
    ax_xy.set_aspect("equal", adjustable="box")
    
    # Velocity subplot
    if show_velocity:
        # Calculate velocity from position differences
        # Timestamp is in microseconds
        dt = np.diff(timestamp) / 1e6  # Convert to seconds
        dx = np.diff(x)
        dy = np.diff(y)
        
        # Calculate speed (magnitude of velocity)
        speed = np.sqrt(dx**2 + dy**2) / dt
        
        # Time axis (relative to start, in seconds)
        time_s = (timestamp - timestamp[0]) / 1e6
        time_mid = (time_s[:-1] + time_s[1:]) / 2  # Midpoint times for velocity
        
        ax_vel.plot(time_mid, speed, linewidth=1.0, color="#2563eb", label="vehicle_local_position")
        
        # Plot reference velocity if available
        if plot_reference:
            raptor_data = get_message_data(ulog, "raptor_status")
            
            if raptor_data is not None:
                ref_x = raptor_data.data.get("internal_reference_position[0]")
                ref_y = raptor_data.data.get("internal_reference_position[1]")
                ref_timestamp = raptor_data.data.get("timestamp")
                active = raptor_data.data.get("active")
                
                if ref_x is not None and ref_y is not None and active is not None:
                    ref_x = np.array(ref_x)
                    ref_y = np.array(ref_y)
                    ref_timestamp = np.array(ref_timestamp)
                    active = np.array(active, dtype=bool)
                    
                    # Calculate reference velocity
                    ref_dt = np.diff(ref_timestamp) / 1e6
                    ref_dx = np.diff(ref_x)
                    ref_dy = np.diff(ref_y)
                    ref_speed = np.sqrt(ref_dx**2 + ref_dy**2) / ref_dt
                    
                    # Time axis for reference (relative to vehicle_local_position start)
                    ref_time_s = (ref_timestamp - timestamp[0]) / 1e6
                    ref_time_mid = (ref_time_s[:-1] + ref_time_s[1:]) / 2
                    
                    # Active mask for velocity (use AND of consecutive active states)
                    active_vel = active[:-1] & active[1:]
                    
                    # Mask inactive regions with NaN
                    ref_speed_active = ref_speed.copy()
                    ref_speed_active[~active_vel] = np.nan
                    
                    ax_vel.plot(ref_time_mid, ref_speed_active, linewidth=1.0, 
                               linestyle="--", color="#f97316", alpha=0.8, 
                               label="raptor_status reference")
        
        ax_vel.set_xlabel("Time [s]", fontsize=12)
        ax_vel.set_ylabel("Speed [m/s]", fontsize=12)
        ax_vel.set_title("Horizontal Speed", fontsize=12)
        ax_vel.legend(loc="best")
        ax_vel.grid(True, alpha=0.3)
        ax_vel.set_xlim(time_s[0], time_s[-1])
        ax_vel.set_ylim(bottom=0)
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=dpi, bbox_inches="tight")
        print(f"Plot saved to: {save_path}")
    else:
        plt.show()


if __name__ == "__main__":
    main()

