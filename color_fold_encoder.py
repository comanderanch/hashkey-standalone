def expand_rgb_to_fold_state(r, g, b):
    # Tri-vector expansion
    expanded_rgb = [r * 3, g * 3, b * 3]
    
    # Convert to 8-bit binary and double
    binary_r = f"{r:08b}" * 2
    binary_g = f"{g:08b}" * 2
    binary_b = f"{b:08b}" * 2

    folded_binary = binary_r + binary_g + binary_b
    
    return {
        "rgb_folded": expanded_rgb,
        "binary_folded": folded_binary
    }

