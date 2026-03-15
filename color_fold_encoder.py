def expand_rgb_to_fold_state(r, g, b):
    # Tri-vector expansion — values only
    expanded_rgb = [r * 3, g * 3, b * 3]

    # Single 8-bit binary per channel — 24 bits total
    # This is the T pin — RGB color plane
    binary_r = f"{r:08b}"
    binary_g = f"{g:08b}"
    binary_b = f"{b:08b}"
    folded_binary = binary_r + binary_g + binary_b

    return {
        "rgb_folded": expanded_rgb,
        "binary_folded": folded_binary
    }
