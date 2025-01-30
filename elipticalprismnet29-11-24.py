import cadquery as cq
import numpy as np
import matplotlib.pyplot as plt
import os
import logging
import sys
import traceback
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend


# Configure logging with explicit path
#log_path = os.path.join(os.path.expanduser('~/Documents'), 'lampshade.log')
#Save to a relative path
log_path = "elipticalprism_net.log"  # This will create the log file in your current directory

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_path),
        logging.StreamHandler(sys.stdout)
    ]
)

# Import parameters
MAJOR_AXIS = 12
MINOR_AXIS = 4
HEIGHT = 25
SHELL_THICKNESS = 0.1
CUT1_ANGLE = 45  # First cut angle
CUT2_ANGLE = 45  # Second cut angle
CUT1_START_HEIGHT = 3  # Height where first cut starts and ends
CUT2_START_HEIGHT = 1  # Height where second cut starts and ends

def calculate_net_geometry():
    try:
        logging.info("Starting geometry calculation")
        
        # Get path for output
        save_path = os.path.expanduser('.')
        pdf_file = os.path.join(save_path, 'elipticalprism_net_export.pdf')
        logging.info(f"Output path: {pdf_file}")

        # Create base ellipse
        base = cq.Workplane("XY").ellipse(MINOR_AXIS, MAJOR_AXIS)
        perimeter = base.edges().objects[0].Length()
        logging.debug(f"Perimeter calculated: {perimeter}")
        
        # Calculate points for unwrapped view starting at major vertex
        t = np.linspace(0, perimeter, 200)
        
        # Calculate amplitudes based on cut angles
        amplitude1 = MAJOR_AXIS * np.tan(np.radians(CUT1_ANGLE))
        amplitude2 = MAJOR_AXIS * np.tan(np.radians(CUT2_ANGLE))
        
        # Calculate cut lines starting at major vertex (phase shift = -π/2)
        cut1_y = CUT1_START_HEIGHT + amplitude1 * (1 + np.sin(2*np.pi*t/perimeter - np.pi/2))
        cut2_y = CUT2_START_HEIGHT + amplitude2 * (1 + np.sin(2*np.pi*t/perimeter + np.pi/2))
        
        # Clip heights to maximum prism height and minimum of 0
        cut1_y = np.minimum(np.maximum(cut1_y, 0), HEIGHT)
        cut2_y = np.minimum(np.maximum(cut2_y, 0), HEIGHT)
        
        logging.info("Creating plot")
        # Create plot with specified size for A4 landscape
        fig, ax = plt.subplots(figsize=(11.69, 8.27))
        
        # Draw bottom edge
        plt.plot([0, perimeter], [0, 0], 'b-', linewidth=2, label='Bottom Edge')
        
        # Draw cut lines
        plt.plot(t, cut1_y, 'r-', linewidth=2, label=f'Cut 1 ({CUT1_ANGLE}°)')
        plt.plot(t, cut2_y, 'r--', linewidth=2, label=f'Cut 2 ({CUT2_ANGLE}°)')
        
        # Enhanced formatting
        ax.set_aspect('equal')
        plt.grid(True, linestyle='--', alpha=0.7)
        plt.xlabel('Width (mm)', fontsize=12)
        plt.ylabel('Height (mm)', fontsize=12)
        plt.title('Lampshade Net with Height-Limited Cuts', fontsize=14, pad=20)
        
        # Place legend outside the plot area
        plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        plt.tight_layout()
        
        # Add dimensions and scale
        plt.text(0, -2, f'Major Axis: {MAJOR_AXIS}mm', fontsize=10)
        plt.text(perimeter/2, -2, f'Minor Axis: {MINOR_AXIS}mm', fontsize=10)
        
        logging.info("Saving PDF...")
        plt.savefig(pdf_file, 
                    bbox_inches='tight', 
                    orientation='landscape', 
                    dpi=300,
                    metadata={'Creator': 'Lampshade Generator',
                             'Title': 'Lampshade Cutting Template'},
                    transparent=False,
                    facecolor='white',
                    edgecolor='none')
        logging.info(f"PDF saved to: {pdf_file}")
        
        plt.show()
        
    except Exception as e:
        logging.error(f"Error occurred: {str(e)}")
        logging.error(traceback.format_exc())
        sys.exit(1)

if __name__ == "__main__":
    try:
        logging.info("Starting net generation")
        calculate_net_geometry()
    except Exception as e:
        logging.error(f"Main execution error: {str(e)}")
        logging.error(traceback.format_exc())
        sys.exit(1)