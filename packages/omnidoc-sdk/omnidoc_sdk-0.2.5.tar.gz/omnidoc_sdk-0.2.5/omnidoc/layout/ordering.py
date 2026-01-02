def order_blocks(blocks):
    """
    Orders blocks top-to-bottom, left-to-right.
    Handles multi-column layouts.
    """
    return sorted(
        blocks,
        key=lambda b: (
            round(b.block.y_1 / 40),  # vertical buckets
            b.block.x_1               # left to right
        )
    )
