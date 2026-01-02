import qrcode
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import os
import argparse


def qr_mask(row, col, mask_pattern):
    """
    returns 0 or 1 whether the data bit should be flipped
    according to a mask_pattern, doesn't check for bit type
    """
    if mask_pattern == 0:  # (row + col) % 2 == 0
        mask = (row + col) % 2 == 0
    elif mask_pattern == 1:  # row % 2 == 0
        mask = row % 2 == 0
    elif mask_pattern == 2:  # col % 3 == 0
        mask = col % 3 == 0
    elif mask_pattern == 3:  # (row + col) % 3 == 0
        mask = (row + col) % 3 == 0
    elif mask_pattern == 4:  # ((row // 2) + (col // 3)) % 2 == 0
        mask = ((row // 2) + (col // 3)) % 2 == 0
    elif mask_pattern == 5:  # ((row * col) % 2) + ((row * col) % 3) == 0
        mask = ((row * col) % 2) + ((row * col) % 3) == 0
    elif mask_pattern == 6:  # (((row * col) % 2) + ((row * col) % 3)) % 2 == 0
        mask = (((row * col) % 2) + ((row * col) % 3)) % 2 == 0
    elif mask_pattern == 7:  # (((row + col) % 2) + ((row * col) % 3)) % 2 == 0
        mask = (((row + col) % 2) + ((row * col) % 3)) % 2 == 0
    return mask


def enumerate_qr_bits(matrix, version, ec_level, length, mask_pattern):
    """Enumerate all bits in a QR code following the snake/zigzag pattern

    Returns a list of tuples (row, col, bit_index, byte_index, bit_in_byte, bit_type)
    where:
    - row, col: Position in the matrix
    - bit_index: Overall bit index (0 to total_bits-1)
    - byte_index: Which byte this bit belongs to (0 to total_bytes-1)
    - bit_in_byte: Position within the byte (0 to 7, where 0 is MSB)
    - bit_type: What type of bit this is (mode, length, data, padding, etc.)
    """
    size = len(matrix)
    unmasked_matrix = [[bit for bit in row] for row in matrix]

    # Create a map to track which modules are part of the finder patterns, etc.
    # We'll use a numpy array for easier manipulation
    reserved_map = np.zeros((size, size), dtype=bool)
    reserved_bits = []

    # Mark finder patterns and separators (top-left, top-right, bottom-left)
    # Top-left finder pattern and separators
    reserved_map[0:9, 0:9] = True
    for x in range(8):
        for y in range(8):
            reserved_bits.append((x, y, -1, -1, -1, "finder_pattern"))

    # Top-right finder pattern and separators
    reserved_map[0:9, size - 8 : size] = True
    for x in range(8):
        for y in range(8):
            reserved_bits.append((x + size - 8, y, -1, -1, -1, "finder_pattern"))

    # Bottom-left finder pattern and separators
    reserved_map[size - 8 : size, 0:9] = True
    for x in range(8):
        for y in range(8):
            reserved_bits.append((x, y + size - 8, -1, -1, -1, "finder_pattern"))

    # Version + error correction level information
    for i in range(6):
        reserved_bits.append((i, 8, 14 - i, -1, -1, "format_info"))
        reserved_bits.append((8, i, i, -1, -1, "format_info"))

    reserved_bits.append((7, 8, 8, -1, -1, "format_info"))
    reserved_bits.append((8, 7, 6, -1, -1, "format_info"))
    reserved_bits.append((8, 8, 7, -1, -1, "format_info"))

    for i in range(8):
        reserved_bits.append((8, i + 9 + 4 * version, i + 7, -1, -1, "format_info"))
        if i > 0:
            reserved_bits.append((i + 9 + 4 * version, 8, 7 - i, -1, -1, "format_info"))

    # Mark alignment patterns for version 2+
    if version >= 2:
        alignment_centers = [(size - 7, size - 7)]
        # Mark each alignment pattern area
        for center_y, center_x in alignment_centers:
            for i in range(-2, 3):
                for j in range(-2, 3):
                    y, x = center_y + i, center_x + j
                    if 0 <= y < size and 0 <= x < size:
                        reserved_map[y, x] = True
                        reserved_bits.append((y, x, -1, -1, -1, "alignment_pattern"))

    # Dark module (always black)
    reserved_map[size - 8, 8] = True
    reserved_bits.append((size - 8, 8, -1, -1, -1, "dark_module"))

    # Synchronization lines
    for i in range(4 * version + 1):
        reserved_map[i + 8, 6] = True
        reserved_map[6, i + 8] = True
        reserved_bits.append((i + 8, 6, -1, -1, -1, "timing_pattern"))
        reserved_bits.append((6, i + 8, -1, -1, -1, "timing_pattern"))

    # Version information area for version 7+
    if version >= 7:
        # Mark version information areas
        reserved_map[size - 11 : size - 8, 0:6] = True  # Bottom-left
        reserved_map[0:6, size - 11 : size - 8] = True  # Top-right

    # QR codes follow a specific zigzag pattern with 2-bit width
    # The pattern moves in zigzags upward and downward through column pairs
    # For version 2, the pattern starts at the bottom-right and follows a zigzag pattern

    modules = []  # This will store the coordinates in the correct order

    # Loop through the QR code in 2×2 blocks from right to left
    # For each column pair, we move from bottom to top in zigzag pattern

    current_block = []
    blocks = []
    upwords = True
    # Process each column pair from right to left
    x_range = [size - 1 - 2 * i for i in range(size // 2)]
    for i in range(3):
        x_range[-i - 1] -= 1

    def block_length(x):
        return 4 if x in {0, length + 2} else 8

    for x in x_range:
        y_range = range(size - 1, -1, -1) if upwords else range(size)
        for y in y_range:
            for x_delta in [0, -1]:
                if not reserved_map[y, x + x_delta]:
                    current_block.append((y, x + x_delta, len(modules)))
                    modules.append((y, x + x_delta))
                    unmasked_matrix[y][x + x_delta] = matrix[y][x + x_delta] ^ qr_mask(
                        y, x + x_delta, mask_pattern
                    )
                if len(current_block) == block_length(len(blocks)):
                    blocks.append(current_block)
                    current_block = []
        upwords = not upwords
    capacity = get_data_bytes(version, ec_level)

    for x, y, _ in current_block:
        reserved_bits.append((x, y, -1, -1, -1, "data"))
    # Now that we have the module sequence, assign bit indices
    bits = []

    final_blocks = [[]]
    # Format
    for j, (row, col, index) in enumerate(blocks[0]):
        bits.append((row, col, index, 1, j, "mode_indicator"))
        final_blocks[-1].append(bits[-1])
    final_blocks.append([])
    # Length
    for j, (row, col, index) in enumerate(blocks[1]):
        bits.append((row, col, index, 2, j, "length_field"))
        final_blocks[-1].append(bits[-1])

    # Process each module and assign bit information
    for i, block in enumerate(blocks[2:]):
        final_blocks.append([])
        if i <= capacity:
            block_type = "data"
        else:
            block_type = "error_correction"
        for j, (row, col, index) in enumerate(block):
            bits.append((row, col, index, i, j, block_type))
            final_blocks[-1].append(bits[-1])

    return bits, final_blocks, reserved_bits, unmasked_matrix


def get_data_codewords_for_version(version):
    """Get the number of data codewords for a given version with M error correction"""
    # These are the data codeword capacities for QR codes with error correction level M
    # Values from the QR code specification
    data_codewords = {
        1: 16,
        2: 28,
        3: 44,
        4: 64,
        5: 86,
        6: 108,
        7: 130,
        8: 156,
        9: 192,
        10: 224,
        # Add more versions as needed
    }
    return data_codewords.get(version, 100)  # Default to 100 if version not found


def get_data_bytes(version: int, error_correction_level: str) -> int:
    """Get the number of data bytes for a given version and error correction level in byte mode

    Args:
        version (int): QR code version (1-40)
        error_correction_level (str): Error correction level ('L', 'M', 'Q', 'H')

    Returns:
        int: Number of data bytes available for byte mode encoding
    """
    # QR Code capacity table for data bits (from ISO/IEC 18004:2015)
    # Values represent total data bits for each version and error correction level
    capacity_table = {
        1: {"L": 152, "M": 128, "Q": 104, "H": 72},
        2: {"L": 272, "M": 224, "Q": 176, "H": 128},
        3: {"L": 440, "M": 352, "Q": 272, "H": 208},
        4: {"L": 640, "M": 512, "Q": 384, "H": 288},
        5: {"L": 864, "M": 688, "Q": 496, "H": 368},
        6: {"L": 1088, "M": 864, "Q": 608, "H": 480},
        7: {"L": 1328, "M": 1032, "Q": 712, "H": 528},
        8: {"L": 1576, "M": 1232, "Q": 856, "H": 640},
        9: {"L": 1840, "M": 1456, "Q": 992, "H": 720},
        10: {"L": 2128, "M": 1688, "Q": 1152, "H": 832},
        11: {"L": 2440, "M": 1928, "Q": 1304, "H": 928},
        12: {"L": 2752, "M": 2200, "Q": 1504, "H": 1056},
        13: {"L": 3088, "M": 2472, "Q": 1704, "H": 1168},
        14: {"L": 3440, "M": 2768, "Q": 1960, "H": 1328},
        15: {"L": 3808, "M": 3072, "Q": 2216, "H": 1488},
        16: {"L": 4184, "M": 3392, "Q": 2504, "H": 1648},
        17: {"L": 4576, "M": 3728, "Q": 2792, "H": 1840},
        18: {"L": 4976, "M": 4072, "Q": 3080, "H": 2032},
        19: {"L": 5392, "M": 4432, "Q": 3384, "H": 2272},
        20: {"L": 5824, "M": 4808, "Q": 3688, "H": 2512},
        21: {"L": 6272, "M": 5200, "Q": 3992, "H": 2752},
        22: {"L": 6736, "M": 5608, "Q": 4320, "H": 3024},
        23: {"L": 7216, "M": 6032, "Q": 4648, "H": 3296},
        24: {"L": 7712, "M": 6472, "Q": 4976, "H": 3568},
        25: {"L": 8224, "M": 6928, "Q": 5336, "H": 3872},
        26: {"L": 8752, "M": 7400, "Q": 5704, "H": 4176},
        27: {"L": 9296, "M": 7888, "Q": 6072, "H": 4480},
        28: {"L": 9856, "M": 8392, "Q": 6440, "H": 4784},
        29: {"L": 10432, "M": 8912, "Q": 6808, "H": 5088},
        30: {"L": 11024, "M": 9448, "Q": 7208, "H": 5424},
        31: {"L": 11632, "M": 10000, "Q": 7608, "H": 5760},
        32: {"L": 12256, "M": 10568, "Q": 8008, "H": 6128},
        33: {"L": 12904, "M": 11144, "Q": 8408, "H": 6496},
        34: {"L": 13568, "M": 11728, "Q": 8832, "H": 6896},
        35: {"L": 14248, "M": 12328, "Q": 9256, "H": 7296},
        36: {"L": 14944, "M": 12936, "Q": 9680, "H": 7728},
        37: {"L": 15656, "M": 13560, "Q": 10104, "H": 8160},
        38: {"L": 16384, "M": 14200, "Q": 10528, "H": 8624},
        39: {"L": 17128, "M": 14848, "Q": 10952, "H": 9088},
        40: {"L": 17888, "M": 15512, "Q": 11376, "H": 9576},
    }

    # Mode indicator (4 bits) + character count indicator (8, 16, or 16 bits for byte mode)
    # For versions 1-9: 8 bits for character count
    # For versions 10-26: 16 bits for character count
    # For versions 27-40: 16 bits for character count
    if version >= 1 and version <= 9:
        overhead_bits = 4 + 8  # Mode indicator + character count indicator
    elif version >= 10 and version <= 26:
        overhead_bits = 4 + 16  # Mode indicator + character count indicator
    elif version >= 27 and version <= 40:
        overhead_bits = 4 + 16  # Mode indicator + character count indicator
    else:
        raise ValueError("Invalid QR code version. Must be between 1 and 40.")

    if error_correction_level not in ["L", "M", "Q", "H"]:
        raise ValueError(
            "Invalid error correction level. Must be 'L', 'M', 'Q', or 'H'."
        )

    if version not in capacity_table:
        raise ValueError("Invalid QR code version. Must be between 1 and 40.")

    # Get total data bits for this version and error correction level
    total_data_bits = capacity_table[version][error_correction_level]

    # Subtract overhead bits to get available data bits for actual content
    available_data_bits = total_data_bits - overhead_bits

    # Convert to bytes (8 bits per byte)
    data_bytes = available_data_bits // 8

    return data_bytes


def visualize_bit_pattern(
    matrix,
    bits,
    blocks,
    reserved_bits,
    output_path,
    ec_level,
    verbose=False,
    mode="colors",
    display_type="bit_indices",
    mask_pattern=-1,
    logo_radius=0,
    logo_path="",
    legend=False,
):
    """Create a visualization of the bit enumeration pattern"""
    size = len(matrix)
    scale = 60  # Size of each module in pixels
    margin = 2  # Margin around the QR code

    # Colors for different bit types
    if mode == "colors":
        bit_type_colors = {
            "mode_indicator": (255, 128, 0),  # Orange
            "length_field": (255, 0, 255),  # Magenta
            "data": (0, 128, 255),  # Blue
            "error_correction": (255, 215, 0),  # gold
            "finder_pattern": (255, 0, 0),  # Red
            "alignment_pattern": (0, 150, 0),  # Green
            "timing_pattern": (255, 4, 78),  #
            "format_info": (0, 0, 0),  # Black
            "dark_module": (100, 0, 0),  # Dark Red
            "default": (0, 0, 0),  # Black
            "background": (255, 255, 255),
            "padding": (0, 0, 0),
        }
    else:
        bit_type_colors = {
            "mode_indicator": (0, 0, 0),
            "length_field": (0, 0, 0),
            "data": (0, 0, 0),
            "error_correction": (0, 0, 0),
            "finder_pattern": (0, 0, 0),
            "alignment_pattern": (0, 0, 0),
            "timing_pattern": (0, 0, 0),
            "format_info": (0, 0, 0),
            "dark_module": (0, 0, 0),
            "default": (0, 0, 0),
            "background": (0, 0, 0),
            "padding": (0, 0, 0),
        }

    version = (size - 17) // 4
    # Create an RGB image
    img_size = (size + 2 * margin) * scale
    # Add space at the bottom for the legend
    legend_height = 0
    if legend:
        legend_height = scale * 8
    img = Image.new("RGB", (img_size, img_size + legend_height), color="white")
    draw = ImageDraw.Draw(img)
    if not verbose:
        for row in range(size):
            for col in range(size):
                if not matrix[row][col]:
                    continue
                y = (row + margin) * scale
                x = (col + margin) * scale
                draw.rectangle([x, y, x + scale - 1, y + scale - 1], fill="black")
        if logo_radius > 0 and logo_path != "":
            overlay = Image.open(logo_path).convert("RGBA")
            overlay = overlay.resize(
                (int(scale * logo_radius * 2), int(scale * logo_radius * 2))
            )
            img.paste(
                overlay,
                (
                    int((margin - logo_radius) * scale + scale * size * 0.5),
                    int((margin - logo_radius) * scale + scale * size * 0.5),
                ),
                overlay,
            )
        img.save(output_path)
        return

    # Try to load a font, fall back to default if not available
    try:
        # Use a much larger font for ASCII mode
        if display_type == "ascii":
            font = ImageFont.load_default(int(scale * 0.8))
        else:
            font = ImageFont.load_default(scale // 3)

        legend_font = ImageFont.load_default(scale // 1.5)
    except IOError:
        font = ImageFont.load_default()
        legend_font = font

    # Now draw all modules with appropriate colors
    for row, col, _, _, _, cell_type in reserved_bits:
        x = (col + margin) * scale
        y = (row + margin) * scale

        if not matrix[row][col]:
            color = "white"
        else:
            color = bit_type_colors[cell_type]
        # Draw the module
        draw.rectangle(
            [x, y, x + scale - 1, y + scale - 1], fill=color, outline="#DDDDDD"
        )

    # Now overlay the bits with color coding and numbers
    # Create a mapping for quick lookup
    bit_map = {
        (row, col): (bit_idx, byte_idx, bit_in_byte, bit_type)
        for row, col, bit_idx, byte_idx, bit_in_byte, bit_type in bits
    }

    # Create a byte map for ASCII display
    byte_map = {}
    if display_type == "ascii":
        # Group bits by byte_idx
        byte_bits = {}
        byte_types = {}
        for row, col, bit_idx, byte_idx, bit_in_byte, bit_type in bits:
            if bit_type in {"data", "error_correction"}:
                if byte_idx not in byte_bits:
                    byte_bits[byte_idx] = [None] * 8
                # Store the bit value and position
                byte_bits[byte_idx][bit_in_byte] = (row, col, matrix[row][col])
                byte_types[byte_idx] = bit_type

        # Unmask the bits based on the provided mask pattern
        for byte_idx, byte_data in byte_bits.items():
            if None not in byte_data:
                byte_value = 0
                for i, (row, col, bit) in enumerate(byte_data):
                    if mask_pattern != -1:
                        bit = (bit ^ 1) if qr_mask(row, col, mask_pattern) else bit
                    byte_value |= bit << (7 - i)

                # Map each position in this byte to the ASCII character
                if byte_types[byte_idx] == "data":
                    char = chr(byte_value) if 32 <= byte_value <= 126 else "."
                    if byte_value in {17, 236}:
                        char = str(byte_value)
                else:
                    char = "E"

                # For better character display, we'll pick one bit position to show the character
                # Instead of using a fixed position like 3, we'll use the middle bits in each byte
                center_bit = 3  # Default center bit (position 3 or 4 is usually good)

                # Make sure we have the position (sometimes bytes can have missing bits)
                while center_bit >= 0 and byte_data[center_bit] is None:
                    center_bit -= 1
                if center_bit < 0:
                    center_bit = 0

                for i, data in enumerate(byte_data):
                    if data is not None:  # Skip any None entries
                        row, col, _ = data
                        if i == center_bit:
                            # Mark this as the character display position
                            byte_map[(row, col)] = (
                                byte_idx,
                                char,
                                True,
                            )  # True = center position
                        else:
                            byte_map[(row, col)] = (
                                byte_idx,
                                char,
                                False,
                            )  # Not the center
    # First pass: Draw colored modules with bit numbers or ASCII
    for row in range(size):
        for col in range(size):
            if (row, col) in bit_map:
                bit_idx, byte_idx, bit_in_byte, bit_type = bit_map[(row, col)]

                # Position for rectangle
                x = (col + margin) * scale
                y = (row + margin) * scale

                # Determine the color based on bit type
                color = bit_type_colors.get(bit_type, bit_type_colors["default"])

                # Draw the colored rectangle
                if display_type == "ascii" and (row, col) in byte_map:
                    _, _, is_center = byte_map[(row, col)]
                    # For ASCII mode, use special background colors
                    if is_center:  # Character display position
                        # Bright background for the character position for better readability
                        highlight_color = (
                            255,
                            240,
                            150,
                        )  # Brighter yellow for character center
                    else:
                        # Subtle background for other bits in the byte
                        if matrix[row][col]:
                            highlight_color = (230, 230, 230)  # Light gray
                        else:
                            highlight_color = (245, 245, 245)  # Very light gray
                    draw.rectangle(
                        [x, y, x + scale - 1, y + scale - 1], fill=highlight_color
                    )
                else:
                    # Standard coloring for bit indices mode and non-character positions
                    if matrix[row][col]:
                        # For black modules, use the bit type color
                        draw.rectangle([x, y, x + scale - 1, y + scale - 1], fill=color)
                    else:
                        # For white modules, use a lighter version of the color
                        light_color = tuple(min(255, c + 128) for c in color)
                        draw.rectangle(
                            [x, y, x + scale - 1, y + scale - 1], fill=light_color
                        )

                # Position for text
                x_center = x + scale // 2
                y_center = y + scale // 2

                # Determine text color
                if display_type == "ascii" and (row, col) in byte_map:
                    # For ASCII mode, always use black text for better visibility
                    text_color = "black"
                else:
                    # For bit indices mode, determine based on background brightness
                    brightness = sum(color) / 3
                    text_color = (
                        "white" if brightness < 128 and matrix[row][col] else "black"
                    )

                # Draw text based on display type
                if display_type == "ascii" and (row, col) in byte_map:
                    b_idx, char, is_center = byte_map[(row, col)]
                    if is_center:  # Only show character at the center position
                        text = char  # Just show the character without byte number
                    else:
                        text = ""  # No text for other bits in the same byte
                elif display_type != "ascii":  # Default bit indices display
                    if bit_type == "mode_indicator":
                        text = f"M:{bit_in_byte}"
                    elif bit_type == "length_field":
                        text = f"L:{bit_in_byte}"
                    else:
                        text = f"{byte_idx}:{bit_in_byte}"

                # Center the text
                text_bbox = draw.textbbox((0, 0), text, font=font)
                text_width = text_bbox[2] - text_bbox[0]
                text_height = text_bbox[3] - text_bbox[1]
                text_x = x_center - text_width // 2
                text_y = y_center - text_height // 2
                draw.text(
                    (text_x - text_bbox[0], text_y - text_bbox[1]),
                    text,
                    fill=text_color,
                    font=font,
                )

    # Format info
    if display_type != "ascii":
        for row, col, idx, _, _, bit_type in reserved_bits:
            if bit_type != "format_info":
                continue

            x = (col + margin) * scale
            y = (row + margin) * scale
            x_center = x + scale // 2
            y_center = y + scale // 2
            text_color = "white" if matrix[row][col] else "black"
            text = str(idx)
            text_bbox = draw.textbbox((0, 0), text, font=font)
            text_width = text_bbox[2] - text_bbox[0]
            text_height = text_bbox[3] - text_bbox[1]
            text_x = x_center - text_width // 2
            text_y = y_center - text_height // 2
            draw.text(
                (text_x - text_bbox[0], text_y - text_bbox[1]),
                text,
                fill=text_color,
                font=font,
            )

    # Second pass: Draw block borders based on the provided block partitioning

    # Colors for different block types
    block_colors = {
        "mode_indicator": (255, 50, 50),  # Red
        "length_field": (255, 50, 50),  # red
        "data": (255, 50, 50),  # red
        "error_correction": (53, 184, 33),  # green
        "byte": (255, 50, 50),  # red
        "format_info": (255, 0, 255),  # magenta
    }

    # Add byte border color to bit_type_colors for the legend
    if display_type == "ascii":
        bit_type_colors["byte_border"] = block_colors["byte"]

    if display_type == "ascii":
        # For ASCII display, we group by bytes instead of blocks
        byte_positions = {}
        for row, col, bit_idx, byte_idx, bit_in_byte, bit_type in bits:
            if (
                bit_type == "data"
                or bit_type == "mode_indicator"
                or bit_type == "length_field"
                or bit_type == "error_correction"
            ):
                if byte_idx not in byte_positions:
                    byte_positions[byte_idx] = []
                byte_positions[byte_idx].append((row, col))

        # Draw borders for each byte group
        border_width = max(1, scale // 15)  # Adjust width based on scale

        data_bytes = get_data_bytes(version=version, error_correction_level=ec_level)
        for byte_idx, positions in byte_positions.items():
            block_type = "data" if byte_idx <= data_bytes else "error_correction"
            border_color = block_colors[block_type]

            # Draw borders around each module where it doesn't have a neighbor in the same byte
            for row, col in positions:
                # Calculate module pixel coordinates
                x = (col + margin) * scale
                y = (row + margin) * scale

                # Check the four possible neighbors (top, right, bottom, left)
                neighbors = [
                    (row - 1, col),
                    (row, col + 1),
                    (row + 1, col),
                    (row, col - 1),
                ]

                # Draw borders where there's no neighbor in the same byte
                for i, (n_row, n_col) in enumerate(neighbors):
                    # If this position is not in the same byte, draw a border
                    if (n_row, n_col) not in positions:
                        # Draw appropriate border segment
                        if i == 0:  # Top
                            draw.line(
                                [(x, y + 1), (x + scale, y + 1)],
                                fill=border_color,
                                width=border_width,
                            )
                        elif i == 1:  # Right
                            draw.line(
                                [(x + scale - 1, y), (x + scale - 1, y + scale)],
                                fill=border_color,
                                width=border_width,
                            )
                        elif i == 2:  # Bottom
                            draw.line(
                                [(x, y + scale - 1), (x + scale, y + scale - 1)],
                                fill=border_color,
                                width=border_width,
                            )
                        elif i == 3:  # Left
                            draw.line(
                                [(x + 1, y), (x + 1, y + scale)],
                                fill=border_color,
                                width=border_width,
                            )
    else:
        # Standard block-based display (original behavior)
        for block_idx, block in enumerate(blocks):
            # Skip empty blocks
            if not block:
                continue

            # Determine block type and color
            if block_idx == 0:
                block_type = "mode_indicator"
            elif block_idx == 1:
                block_type = "length_field"
            elif block_idx < 28:
                block_type = "data"
            else:
                block_type = "error_correction"

            border_color = block_colors.get(block_type, block_colors[block_type])
            border_width = max(1, scale // 15)  # Adjust width based on scale

            # For each module in the block, draw borders where it doesn't have neighbors in the same block
            module_positions = [(module[0], module[1]) for module in block]

            # Draw borders around each module where it doesn't have a neighbor in the same block
            for module in block:
                row, col = module[0], module[1]

                # Calculate module pixel coordinates
                x = (col + margin) * scale
                y = (row + margin) * scale

                # Check the four possible neighbors (top, right, bottom, left)
                neighbors = [
                    (row - 1, col),
                    (row, col + 1),
                    (row + 1, col),
                    (row, col - 1),
                ]

                # Draw borders where there's no neighbor in the same block
                for i, (n_row, n_col) in enumerate(neighbors):
                    # If this position is not in the same block, draw a border
                    if (n_row, n_col) not in module_positions:
                        # Draw appropriate border segment
                        if i == 0:  # Top
                            draw.line(
                                [(x, y), (x + scale, y)],
                                fill=border_color,
                                width=border_width,
                            )
                        elif i == 1:  # Right
                            draw.line(
                                [(x + scale, y), (x + scale, y + scale)],
                                fill=border_color,
                                width=border_width,
                            )
                        elif i == 2:  # Bottom
                            draw.line(
                                [(x, y + scale), (x + scale, y + scale)],
                                fill=border_color,
                                width=border_width,
                            )
                        elif i == 3:  # Left
                            draw.line(
                                [(x, y), (x, y + scale)],
                                fill=border_color,
                                width=border_width,
                            )

    # Format info
    if display_type != "ascii":
        draw.rectangle(
            [
                scale * (margin),
                scale * (margin + 8),
                scale * (margin + 6),
                scale * (margin + 9),
            ],
            outline=block_colors["format_info"],
            width=4,
        )
        draw.rectangle(
            [
                scale * (margin + 7),
                scale * (margin + 8),
                scale * (margin + 9),
                scale * (margin + 9),
            ],
            outline=block_colors["format_info"],
            width=4,
        )
        draw.rectangle(
            [
                scale * (margin + 8),
                scale * (margin),
                scale * (margin + 9),
                scale * (margin + 6),
            ],
            outline=block_colors["format_info"],
            width=4,
        )
        draw.rectangle(
            [
                scale * (margin + 8),
                scale * (margin + 7),
                scale * (margin + 9),
                scale * (margin + 8),
            ],
            outline=block_colors["format_info"],
            width=4,
        )
        draw.rectangle(
            [
                scale * (margin + size - 8),
                scale * (margin + 8),
                scale * (margin + size),
                scale * (margin + 9),
            ],
            outline=block_colors["format_info"],
            width=4,
        )
        draw.rectangle(
            [
                scale * (margin + 8),
                scale * (margin + size - 7),
                scale * (margin + 9),
                scale * (margin + size),
            ],
            outline=block_colors["format_info"],
            width=4,
        )

    # Draw legend
    legend_y = img_size

    # Set the legend title based on display type
    if display_type == "ascii":
        title_text = "QR Code Content (byte:char)"
    else:  # bit_indices
        title_text = "QR Code Bit Layout (byte:bit)"

    draw.text(
        (scale, legend_y),
        title_text,
        fill="black",
        font=legend_font,
    )
    legend_y += scale * 1.5

    # Add legend for each bit type
    if mode == "colors":
        # Define legend labels based on display type
        if display_type == "ascii":
            legend_labels = {
                "mode_indicator": "Mode Indicator (M:char)",
                "length_field": "Length Field (L:char)",
                "data": "Data (byte:char)",
                "padding_17": "Data padding, 10001000",
                "padding_236": "Data padding, 11101100",
                "error_correction": "Error correction",
                "byte_border": "Byte Boundary",
                "finder_pattern": "Finder Pattern",
                "alignment_pattern": "Alignment Pattern",
                "timing_pattern": "Timing Pattern",
                "format_info": "Format Information",
                "dark_module": "Dark Module",
            }
        else:  # bit_indices
            legend_labels = {
                "mode_indicator": "Mode Indicator (M:bit)",
                "length_field": "Length Field (L:bit)",
                "data": "Data (byte:bit)",
                "padding_17": "Data padding, 10001000",
                "padding_236": "Data padding, 11101100",
                "error_correction": "Error correction",
                "finder_pattern": "Finder Pattern",
                "alignment_pattern": "Alignment Pattern",
                "timing_pattern": "Timing Pattern",
                "format_info": "Format Information",
                "dark_module": "Dark Module",
            }

        # Filter out 'default' and 'background' entries
        filtered_colors = {
            k: v
            for k, v in bit_type_colors.items()
            if k not in ("default", "background")
        }

        # Calculate layout parameters
        items_per_row = 3
        item_width = img_size // items_per_row
        row_height = scale * 1.5
        padding = scale

        # Draw legend items in a grid layout
        for i, (bit_type, color) in enumerate(filtered_colors.items()):
            # Calculate position
            row = i // items_per_row
            col = i % items_per_row

            x = padding + col * item_width
            y = legend_y + row * row_height

            # Draw color sample
            draw.rectangle([x, y, x + scale, y + scale], fill=color)

            # Add label
            label = legend_labels.get(bit_type, bit_type)
            draw.text(
                (x + scale * 1.5, y + scale // 4), label, fill="black", font=legend_font
            )

    if logo_radius > 0:
        overlay = Image.open(logo_path).convert("RGBA")
        overlay = overlay.resize(
            (int(scale * logo_radius * 2), int(scale * logo_radius * 2))
        )
        temp = Image.new("RGBA", img.size, (0, 0, 0, 0))
        mask = Image.new("L", overlay.size, 128)
        temp.paste(
            overlay,
            (
                int((margin - logo_radius) * scale + scale * size * 0.5),
                int((margin - logo_radius) * scale + scale * size * 0.5),
            ),
            mask,
        )
        img = Image.alpha_composite(img.convert("RGBA"), temp)
    img.save(output_path)
    return img


def main():
    # Set up argument parser
    parser = argparse.ArgumentParser(
        description="Generate a QR code with detailed visualization", prog="qr-verbose"
    )
    parser.add_argument("data", help="The data to encode in the QR code")
    parser.add_argument(
        "-v", "--version", type=int, default=2, help="QR code version (1-40)"
    )
    parser.add_argument(
        "-e",
        "--error-correction",
        choices=["L", "M", "Q", "H"],
        default="M",
        help="Error correction level (L=7%%, M=15%%, Q=25%%, H=30%%)",
    )
    parser.add_argument(
        "-m",
        "--mask-pattern",
        type=int,
        default=0,
        choices=range(-1, 8),
        help="Mask pattern (0-7) or -1 to show unmasked data",
    )
    parser.add_argument(
        "-o", "--output", required=True, help="Output file name for the QR code image"
    )
    parser.add_argument(
        "-t",
        "--mode",
        default="regular",
        help="'regular' for simple QR code generation without verbose information, 'bw' for black-white output with minimum visual information while being scannable by common QR readers, 'color' for color output, will contain more visual information, 'ascii' for ASCII output, usefull for byte encoding visualization",
        choices=["regular", "bw", "color", "ascii"],
    )
    parser.add_argument(
        "--logo-path", help="Path to logo image to embed in QR code", default=""
    )
    parser.add_argument(
        "--logo-radius",
        type=float,
        default=0.0,
        help="Radius of logo in QR code modules",
    )

    # Parse arguments
    args = parser.parse_args()

    # Map error correction level strings to qrcode constants
    error_correction_map = {
        "L": qrcode.constants.ERROR_CORRECT_L,
        "M": qrcode.constants.ERROR_CORRECT_M,
        "Q": qrcode.constants.ERROR_CORRECT_Q,
        "H": qrcode.constants.ERROR_CORRECT_H,
    }

    # Generate the QR code
    qr = qrcode.QRCode(
        version=args.version,
        error_correction=error_correction_map[args.error_correction],
        box_size=20,
        mask_pattern=max(args.mask_pattern, 0),
        border=0,
    )

    qr.add_data(args.data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    img.save(args.output)

    # Get the matrix and convert to 1s and 0s
    matrix = qr.get_matrix()
    matrix = [[1 if x else 0 for x in row] for row in matrix]

    # Get the actual version used
    actual_version = qr.version
    print(f"QR Code Version: {actual_version}")

    # Enumerate the bits in the QR code
    bits, blocks, reserved_bits, unmasked_matrix = enumerate_qr_bits(
        matrix, actual_version, args.error_correction, len(args.data), qr.mask_pattern
    )

    # Count bits by type
    bit_type_counts = {}
    for _, _, _, _, _, bit_type in bits:
        bit_type_counts[bit_type] = bit_type_counts.get(bit_type, 0) + 1

    BLACK = "\033[40m  \033[0m"
    WHITE = "\033[47m  \033[0m"
    for row in matrix:
        for x in row:
            print(WHITE if x == 0 else BLACK, end="")
        print()

    # Print bit type statistics
    print("\nBit type statistics:")
    for bit_type, count in bit_type_counts.items():
        print(f"{bit_type}: {count} bits")

    if args.mask_pattern == -1:
        matrix = unmasked_matrix

    visualize_bit_pattern(
        matrix,
        bits,
        blocks,
        reserved_bits,
        ec_level=args.error_correction,
        verbose=args.mode != "regular",
        mode="bw" if args.mode == "bw" else "colors",
        display_type=args.mode if args.mode != "regular" else "regular",
        mask_pattern=args.mask_pattern,
        logo_path=args.logo_path,
        logo_radius=args.logo_radius,
        output_path=args.output,
    )


if __name__ == "__main__":
    main()
