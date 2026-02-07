"""
Market Movers - RFID Handler
Manages RFID scanning with PiicoDev RFID Module
"""

try:
    from PiicoDev_RFID import PiicoDev_RFID
    from PiicoDev_Unified import sleep_ms
    RFID_AVAILABLE = True
    import time
except ImportError:
    print("WARNING: PiicoDev_RFID not found. Running in simulation mode.")
    RFID_AVAILABLE = False
    import time

class RFIDHandler:
    """Handles RFID tag reading"""
    
    def __init__(self):
        self.reader = None
        self.last_scan_id = None
        self.last_scan_time = 0
        self.scan_cooldown = 0.5  # Prevent duplicate scans within 0.5 seconds
        
        if RFID_AVAILABLE:
            try:
                self.reader = PiicoDev_RFID()
                print("✓ RFID reader initialized")
            except Exception as e:
                print(f"✗ RFID initialization failed: {e}")
                self.reader = None
        else:
            print("✗ RFID module not available (simulation mode)")
    
    def check_for_scan(self):
        """
        Check if a tag is present and return its ID
        Returns: RFID ID string or None
        """
        if not RFID_AVAILABLE or not self.reader:
            # Simulation mode - no actual scanning
            return None
        
        try:
            if self.reader.tagPresent():
                rfid_id = self.reader.readID()
                
                # Check cooldown to prevent duplicate scans
                current_time = time.time()
                if rfid_id == self.last_scan_id and (current_time - self.last_scan_time) < self.scan_cooldown:
                    return None  # Ignore duplicate scan
                
                # Valid new scan
                self.last_scan_id = rfid_id
                self.last_scan_time = current_time
                
                return rfid_id
        except Exception as e:
            print(f"RFID scan error: {e}")
        
        return None
    
    def wait_for_scan(self, timeout=1000):
        """
        Wait for a tag scan with timeout
        Returns: RFID ID string or None if timeout
        """
        if not RFID_AVAILABLE or not self.reader:
            return None
        
        start_time = time.time()
        
        while (time.time() - start_time) < timeout:
            rfid_id = self.check_for_scan()
            if rfid_id:
                return rfid_id
            
            if RFID_AVAILABLE:
                sleep_ms(100)
            else:
                time.sleep(0.1)
        
        return None  # Timeout
    
    def reset_last_scan(self):
        """Reset the last scan to allow re-scanning the same card"""
        self.last_scan_id = None
        self.last_scan_time = 0


# Simulation mode for testing without hardware
class SimulatedRFIDHandler:
    """
    Simulated RFID handler for testing without hardware
    Use keyboard input to simulate card scans
    """
    
    def __init__(self):
        self.last_scan_id = None
        self.pending_scan = None
        print("✓ Simulated RFID handler initialized")
        print("  Type card IDs in terminal to simulate scans")
    
    def check_for_scan(self):
        """Check for simulated scan (would read from input queue)"""
        if self.pending_scan:
            scan = self.pending_scan
            self.pending_scan = None
            return scan
        return None
    
    def simulate_scan(self, card_id):
        """Manually trigger a scan (for testing)"""
        self.pending_scan = card_id
    
    def reset_last_scan(self):
        """Reset scan state"""
        self.last_scan_id = None


# Factory function
def create_rfid_handler(simulate=False):
    """
    Create appropriate RFID handler
    Args:
        simulate: If True, use simulated handler even if hardware available
    """
    if simulate or not RFID_AVAILABLE:
        return SimulatedRFIDHandler()
    else:
        return RFIDHandler()
